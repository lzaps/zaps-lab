"""FastAPI server with streaming support for parallel tools execution."""

import asyncio
import time
import json
import uuid
from datetime import datetime
from typing import AsyncIterator, Dict, Any, Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from state import GraphState
from tools import (
    AVAILABLE_TOOLS, 
    register_stop_event, 
    trigger_stop, 
    cleanup_stop_event,
    InterruptibleToolWrapper
)


# Global event queue for streaming
event_queue = asyncio.Queue()

# Track active executions
active_executions: Set[str] = set()
active_executions_lock = asyncio.Lock()


def log_event(event_type: str, tool_name: str = None, **data):
    """Log an event to the streaming queue."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    event = {
        "timestamp": timestamp,
        "event_type": event_type,
        "tool_name": tool_name,
        **data
    }
    # Non-blocking put
    try:
        event_queue.put_nowait(event)
    except asyncio.QueueFull:
        pass


class ToolWrapperWithLogging:
    """
    Wrapper that combines InterruptibleToolWrapper with event logging.
    
    This wrapper:
    1. Makes tools interruptible using InterruptibleToolWrapper
    2. Logs events to the streaming queue for real-time updates
    """
    
    def __init__(self, tool_class, tool_name):
        """
        Initialize wrapper.
        
        Args:
            tool_class: The tool class to instantiate and wrap
            tool_name: Name of the tool for logging
        """
        # Create tool instance
        tool_instance = tool_class()
        
        # Wrap it with InterruptibleToolWrapper
        self.interruptible_tool = InterruptibleToolWrapper(
            tool_instance, 
            tool_name,
            check_interval=0.5
        )
        
        self.tool_name = tool_name
        self.tool_instance = tool_instance
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool with logging and interruption support."""
        # Log start
        log_event("tool_start", self.tool_name, 
                 delay=self.tool_instance.delay)
        
        # Execute tool (interruptible)
        start_time = time.time()
        result = self.interruptible_tool(state)
        duration = time.time() - start_time
        
        # Log completion or interruption
        status = result["tool_results"][0]["status"]
        if status == "interrupted":
            log_event("tool_interrupted", self.tool_name,
                     duration=duration,
                     result=result["tool_results"][0]["result"])
        else:
            log_event("tool_complete", self.tool_name,
                     duration=duration,
                     result=result["tool_results"][0]["result"])
        
        return result


async def execute_graph_streaming(query: str, format: str = "json", keepalive: bool = True) -> AsyncIterator[str]:
    """Execute the graph and yield events as they happen."""
    
    # Generate unique execution ID
    execution_id = str(uuid.uuid4())
    
    # Register stop event for this execution
    register_stop_event(execution_id)
    
    # Track active execution
    async with active_executions_lock:
        active_executions.add(execution_id)
    
    # Log start
    log_event("execution_start", None, query=query, num_tools=len(AVAILABLE_TOOLS), execution_id=execution_id)
    
    start_event = {
        'event': 'execution_start', 
        'query': query, 
        'num_tools': len(AVAILABLE_TOOLS),
        'execution_id': execution_id
    }
    if format == "sse":
        yield f"data: {json.dumps(start_event)}\n\n"
    else:
        yield json.dumps(start_event) + "\n"
    
    # Build graph with wrapped tools
    from langgraph.graph import StateGraph, START, END
    from typing import Sequence
    
    builder = StateGraph(GraphState)
    
    # Prepare execution node
    def prepare_execution(state: GraphState) -> Dict[str, Any]:
        log_event("prepare", None)
        return {
            "start_time": time.time(),
            "tool_results": [],
            "execution_summary": {}
        }
    
    builder.add_node("prepare_execution", prepare_execution)
    builder.add_edge(START, "prepare_execution")
    
    # Add wrapped tool nodes
    # Tools are wrapped with InterruptibleToolWrapper for stop support
    # and ToolWrapperWithLogging for event streaming
    for tool_name, tool_class in AVAILABLE_TOOLS.items():
        wrapped_tool = ToolWrapperWithLogging(tool_class, tool_name)
        builder.add_node(tool_name, wrapped_tool)
    
    # Conditional edges for parallel execution
    def route_to_all_tools(state: GraphState) -> Sequence[str]:
        return list(AVAILABLE_TOOLS.keys())
    
    builder.add_conditional_edges(
        "prepare_execution",
        route_to_all_tools,
        list(AVAILABLE_TOOLS.keys())
    )
    
    # Aggregate node
    def aggregate_results(state: GraphState) -> Dict[str, Any]:
        end_time = time.time()
        total_duration = end_time - state["start_time"]
        
        sorted_results = sorted(state["tool_results"], key=lambda x: x["duration"])
        durations = [r["duration"] for r in state["tool_results"]]
        
        summary = {
            "total_duration": total_duration,
            "sequential_duration": sum(durations),
            "time_saved": sum(durations) - total_duration,
            "avg_duration": sum(durations) / len(durations),
            "fastest": min(durations),
            "slowest": max(durations),
            "num_tools": len(state["tool_results"]),
            "results": sorted_results
        }
        
        log_event("aggregate", None, summary=summary)
        
        return {"execution_summary": summary}
    
    builder.add_node("aggregate_results", aggregate_results)
    
    for tool_name in AVAILABLE_TOOLS.keys():
        builder.add_edge(tool_name, "aggregate_results")
    
    builder.add_edge("aggregate_results", END)
    
    graph = builder.compile()
    
    # Execute graph in background
    initial_state = {
        "input_query": query,
        "tool_results": [],
        "execution_summary": None,
        "start_time": None,
        "execution_id": execution_id
    }
    
    # Run graph in thread to not block
    import concurrent.futures
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = executor.submit(graph.invoke, initial_state)
    
    # Stream events as they come - with keep-alive to prevent buffering
    execution_complete = False
    seen_events = 0
    last_keepalive = time.time()
    keepalive_interval = 1.0  # Send keepalive every second
    
    while not execution_complete:
        try:
            # Wait for event with short timeout
            event = await asyncio.wait_for(event_queue.get(), timeout=0.1)
            seen_events += 1
            
            # Send event to client IMMEDIATELY
            if format == "sse":
                yield f"data: {json.dumps(event)}\n\n"
            else:
                yield json.dumps(event) + "\n"
            
            last_keepalive = time.time()
            
        except asyncio.TimeoutError:
            # Send keepalive comment to prevent buffering (if enabled)
            if keepalive:
                current_time = time.time()
                if current_time - last_keepalive >= keepalive_interval:
                    if format == "sse":
                        yield f": keepalive {current_time}\n\n"
                    else:
                        # For JSON format, send a comment line (ignored by parser)
                        yield f"# keepalive {current_time}\n"
                    last_keepalive = current_time
            
            # Check if execution is done
            if future.done():
                # Wait a bit more to catch any remaining events
                remaining = 0
                while not event_queue.empty() and remaining < 20:
                    try:
                        event = event_queue.get_nowait()
                        if format == "sse":
                            yield f"data: {json.dumps(event)}\n\n"
                        else:
                            yield json.dumps(event) + "\n"
                        remaining += 1
                    except:
                        break
                execution_complete = True
    
    # Send completion event
    completion_event = {
        'event': 'execution_complete', 
        'execution_id': execution_id,
        'timestamp': datetime.now().strftime("%H:%M:%S.%f")[:-3]
    }
    if format == "sse":
        yield f"data: {json.dumps(completion_event)}\n\n"
    else:
        yield json.dumps(completion_event) + "\n"
    
    # Cleanup
    executor.shutdown(wait=False)
    cleanup_stop_event(execution_id)
    async with active_executions_lock:
        active_executions.discard(execution_id)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events."""
    print("\n🚀 FastAPI server starting...")
    print("📡 Streaming endpoint: http://localhost:8000/execute")
    print("📝 Test with Postman or curl")
    print("   curl -N http://localhost:8000/execute?query=test\n")
    yield
    print("\n👋 Server shutting down...")


app = FastAPI(
    title="Parallel Tools Execution API",
    description="Streaming API for parallel LangGraph tools execution",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExecuteRequest(BaseModel):
    """Request model for execute endpoint."""
    query: str = "Execute all tools to gather comprehensive information"


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Parallel Tools Execution API",
        "version": "2.0.0",
        "endpoints": {
            "GET /execute": "Execute tools with streaming (query param)",
            "POST /execute": "Execute tools with streaming (JSON body)",
            "POST /stop/{execution_id}": "Stop a running execution",
            "GET /executions": "List active executions",
            "GET /tools": "List available tools",
            "GET /health": "Health check"
        },
        "example": "GET /execute?query=test or curl -N http://localhost:8000/execute?query=test",
        "tools": list(AVAILABLE_TOOLS.keys()),
        "streaming": "Server-Sent Events (SSE)",
        "features": {
            "parallel_execution": "All tools run in parallel",
            "real_time_streaming": "Events streamed as they happen",
            "stop_functionality": "Can interrupt running tools via /stop endpoint"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "tools_available": len(AVAILABLE_TOOLS),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/execute")
async def execute_get(query: str = "Execute all tools", format: str = "json", keepalive: bool = True):
    """
    Execute parallel tools with HTTP streaming response.
    
    Query parameters:
    - query: The query to process (default: "Execute all tools")
    - format: Response format - "json" (default, JSON Lines) or "sse" (Server-Sent Events)
    - keepalive: Send keepalive messages to prevent buffering (default: True)
    
    Returns streaming response with real-time updates.
    Each line is a JSON object representing an event.
    
    Test with:
    - Postman: GET http://localhost:8000/execute?query=test
    - curl: curl -N 'http://localhost:8000/execute?query=test'
    - No keepalive: curl -N 'http://localhost:8000/execute?query=test&keepalive=false'
    """
    media_type = "text/event-stream" if format == "sse" else "application/x-ndjson"
    
    return StreamingResponse(
        execute_graph_streaming(query, format, keepalive),
        media_type=media_type,
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked"
        }
    )


@app.post("/execute")
async def execute_post(request: ExecuteRequest, format: str = "json", keepalive: bool = True):
    """
    Execute parallel tools with HTTP streaming response.
    
    POST body:
    {
        "query": "Your query here"
    }
    
    Query parameters:
    - format: Response format - "json" (default, JSON Lines) or "sse" (Server-Sent Events)
    - keepalive: Send keepalive messages to prevent buffering (default: True)
    
    Returns streaming response with real-time updates.
    Each line is a JSON object representing an event.
    """
    media_type = "text/event-stream" if format == "sse" else "application/x-ndjson"
    
    return StreamingResponse(
        execute_graph_streaming(request.query, format, keepalive),
        media_type=media_type,
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked"
        }
    )


@app.get("/tools")
async def list_tools():
    """List available tools with their configurations."""
    tools_info = {}
    for name, tool_class in AVAILABLE_TOOLS.items():
        tool_instance = tool_class()
        tools_info[name] = {
            "name": tool_instance.name,
            "delay_range": f"{tool_instance.delay:.2f}s",
            "description": tool_class.__doc__ or "No description"
        }
    return {"tools": tools_info, "total": len(tools_info)}


@app.get("/executions")
async def list_executions():
    """List currently active executions."""
    async with active_executions_lock:
        executions = list(active_executions)
    return {
        "active_executions": executions,
        "count": len(executions),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/stop/{execution_id}")
async def stop_execution(execution_id: str):
    """
    Stop a running execution by its ID.
    
    This will interrupt all tools still running and force completion
    with partial results.
    
    Path parameters:
    - execution_id: The UUID of the execution to stop
    
    Returns:
    - success: Whether the stop was triggered
    - message: Description of the result
    """
    async with active_executions_lock:
        is_active = execution_id in active_executions
    
    if not is_active:
        raise HTTPException(
            status_code=404, 
            detail=f"Execution {execution_id} not found or already completed"
        )
    
    success = trigger_stop(execution_id)
    
    if success:
        return {
            "success": True,
            "execution_id": execution_id,
            "message": "Stop signal sent. Tools will be interrupted.",
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to trigger stop event"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

