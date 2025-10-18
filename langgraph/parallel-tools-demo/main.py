"""Main execution script for parallel tools demonstration with LangGraph."""

import time
from typing import Sequence, Dict, Any
from colorama import Fore, Style, init
from datetime import datetime

from langgraph.graph import StateGraph, START, END

from state import GraphState
from tools import AVAILABLE_TOOLS, InterruptibleToolWrapper, register_stop_event, cleanup_stop_event

# Initialize colorama
init(autoreset=True)


def prepare_execution(state: GraphState) -> Dict[str, Any]:
    """Prepare the execution and log the start."""
    start_time = time.time()
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    print(f"\n{Fore.BLUE}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'PARALLEL TOOLS EXECUTION - 5 TOOLS':^80}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'=' * 80}{Style.RESET_ALL}")
    print(f"\n{Fore.WHITE}[{timestamp}] 📋 Query: {state['input_query']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}[{timestamp}] 🚀 Launching 5 tools in parallel...{Style.RESET_ALL}\n")
    
    return {
        "start_time": start_time,
        "tool_results": [],
        "execution_summary": {}
    }


def route_to_all_tools(state: GraphState) -> Sequence[str]:
    """Route to all available tools for parallel execution."""
    return list(AVAILABLE_TOOLS.keys())


def aggregate_results(state: GraphState) -> Dict[str, Any]:
    """Aggregate results from all tools and display summary."""
    end_time = time.time()
    total_duration = end_time - state["start_time"]
    
    print(f"\n{Fore.BLUE}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'EXECUTION SUMMARY':^80}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'=' * 80}{Style.RESET_ALL}\n")
    
    # Sort results by duration
    sorted_results = sorted(state["tool_results"], key=lambda x: x["duration"])
    
    # Display results table
    print(f"{Fore.WHITE}{'Tool Name':<25} {'Duration':<12} {'Status':<10} {'Result'}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{'-' * 80}{Style.RESET_ALL}")
    
    for result in sorted_results:
        tool_name = result["tool"]
        duration = f"{result['duration']:.2f}s"
        status = result["status"]
        tool_result = result["result"]
        
        # Color code by duration
        if result["duration"] < 3:
            color = Fore.GREEN
            speed = "⚡"
        elif result["duration"] < 5:
            color = Fore.YELLOW
            speed = "⏱️"
        else:
            color = Fore.MAGENTA
            speed = "🐌"
        
        print(f"{color}{speed} {tool_name:<23} {duration:<12} {status:<10} {tool_result}{Style.RESET_ALL}")
    
    # Calculate statistics
    durations = [r["duration"] for r in state["tool_results"]]
    avg_duration = sum(durations) / len(durations)
    fastest = min(durations)
    slowest = max(durations)
    
    print(f"\n{Fore.CYAN}{'Statistics:':^80}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  • Total execution time: {total_duration:.2f}s (with parallel execution){Style.RESET_ALL}")
    print(f"{Fore.WHITE}  • Sequential time would be: {sum(durations):.2f}s{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  • Time saved: {sum(durations) - total_duration:.2f}s ({((sum(durations) - total_duration) / sum(durations) * 100):.1f}% faster){Style.RESET_ALL}")
    print(f"{Fore.WHITE}  • Average tool duration: {avg_duration:.2f}s{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  • Fastest tool: {fastest:.2f}s{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  • Slowest tool: {slowest:.2f}s{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}✨ All tools completed successfully!{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'=' * 80}{Style.RESET_ALL}\n")
    
    return {
        "execution_summary": {
            "total_duration": total_duration,
            "sequential_duration": sum(durations),
            "time_saved": sum(durations) - total_duration,
            "avg_duration": avg_duration,
            "fastest": fastest,
            "slowest": slowest,
            "num_tools": len(state["tool_results"])
        }
    }


def build_graph(execution_id: str) -> StateGraph:
    """
    Build the LangGraph with parallel tool execution.
    
    Args:
        execution_id: Unique execution ID for stop functionality
    
    Returns:
        Compiled graph ready for execution
    """
    
    # Create the graph
    builder = StateGraph(GraphState)
    
    # Add preparation node
    builder.add_node("prepare_execution", prepare_execution)
    builder.add_edge(START, "prepare_execution")
    
    # Add all tool nodes wrapped for interruption support
    for tool_name, tool_class in AVAILABLE_TOOLS.items():
        tool_instance = tool_class()
        # Wrap with InterruptibleToolWrapper for stop support
        wrapped_tool = InterruptibleToolWrapper(
            tool_instance,
            tool_name,
            check_interval=0.5
        )
        builder.add_node(tool_name, wrapped_tool)
    
    # Add conditional edges for parallel execution
    # All tools will be executed in parallel after prepare_execution
    builder.add_conditional_edges(
        "prepare_execution",
        route_to_all_tools,
        list(AVAILABLE_TOOLS.keys())
    )
    
    # Add aggregation node
    builder.add_node("aggregate_results", aggregate_results)
    
    # All tools converge to aggregation node
    for tool_name in AVAILABLE_TOOLS.keys():
        builder.add_edge(tool_name, "aggregate_results")
    
    # End after aggregation
    builder.add_edge("aggregate_results", END)
    
    return builder.compile()


def main():
    """Main execution function."""
    import uuid
    
    # Generate execution ID (for consistency with API and stop support)
    execution_id = str(uuid.uuid4())
    
    # Register stop event (optional for console mode, but good for consistency)
    register_stop_event(execution_id)
    
    # Build the graph with execution ID
    graph = build_graph(execution_id)
    
    # Save graph visualization
    try:
        graph_image = graph.get_graph().draw_mermaid_png()
        with open("graph_visualization.png", "wb") as f:
            f.write(graph_image)
        print(f"{Fore.GREEN}✓ Graph visualization saved to graph_visualization.png{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"{Fore.YELLOW}⚠ Could not save graph visualization: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  Try: pip install grandalf{Style.RESET_ALL}\n")
    
    # Generate execution ID (for consistency with API)
    execution_id = str(uuid.uuid4())
    
    # Execute the graph
    initial_state = {
        "input_query": "Execute all tools to gather comprehensive information",
        "tool_results": [],
        "execution_summary": None,
        "start_time": None,
        "execution_id": execution_id
    }
    
    try:
        result = graph.invoke(initial_state)
        return result
    finally:
        # Cleanup stop event
        cleanup_stop_event(execution_id)


if __name__ == "__main__":
    main()

