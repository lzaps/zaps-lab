"""Simulated tools with varying execution times for parallel execution demonstration."""

import time
import random
import threading
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from queue import Queue, Empty
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Global registry for stop events per execution
_stop_events: Dict[str, threading.Event] = {}
_stop_events_lock = threading.Lock()


def register_stop_event(execution_id: str) -> threading.Event:
    """Register a new stop event for an execution."""
    with _stop_events_lock:
        event = threading.Event()
        _stop_events[execution_id] = event
        return event


def get_stop_event(execution_id: str) -> Optional[threading.Event]:
    """Get the stop event for an execution."""
    with _stop_events_lock:
        return _stop_events.get(execution_id)


def trigger_stop(execution_id: str) -> bool:
    """Trigger stop for an execution."""
    with _stop_events_lock:
        event = _stop_events.get(execution_id)
        if event:
            event.set()
            return True
        return False


def cleanup_stop_event(execution_id: str):
    """Clean up stop event after execution completes."""
    with _stop_events_lock:
        _stop_events.pop(execution_id, None)


class InterruptibleToolWrapper:
    """
    Universal wrapper that makes any tool interruptible.
    
    This wrapper executes the original tool in a separate thread and monitors
    for stop signals. Works with any blocking operation: sleep, API calls, 
    database queries, etc.
    
    The original tool continues running in the background after interruption,
    but its result is discarded.
    """
    
    def __init__(self, tool_instance: Any, tool_name: str, check_interval: float = 0.5):
        """
        Initialize the wrapper.
        
        Args:
            tool_instance: The original tool instance to wrap
            tool_name: Name of the tool (for logging)
            check_interval: How often to check for stop signal (seconds)
        """
        self.tool = tool_instance
        self.tool_name = tool_name
        self.check_interval = check_interval
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with interruption support.
        
        Args:
            state: The graph state containing execution_id
            
        Returns:
            Tool result dict with status 'success' or 'interrupted'
        """
        execution_id = state.get("execution_id", "")
        stop_event = get_stop_event(execution_id)
        
        # Queues for result and exceptions
        result_queue: Queue = Queue()
        exception_queue: Queue = Queue()
        start_time = time.time()
        
        def run_tool():
            """Execute the original tool in a thread."""
            try:
                result = self.tool(state)
                result_queue.put(result)
            except Exception as e:
                exception_queue.put(e)
        
        # Start tool execution in separate thread
        thread = threading.Thread(target=run_tool, daemon=True)
        thread.start()
        
        # Monitor thread and check for stop signal
        while thread.is_alive():
            # Check if stop was requested
            if stop_event and stop_event.is_set():
                duration = time.time() - start_time
                # Thread continues but we return interrupted status
                print(f"{Fore.RED}[{get_timestamp()}] 🛑 {self.tool_name} interrupted after {duration:.2f}s{Style.RESET_ALL}")
                
                return {
                    "tool_results": [{
                        "tool": self.tool_name,
                        "duration": duration,
                        "result": "Interrupted",
                        "status": "interrupted"
                    }]
                }
            
            # Wait for thread with timeout to allow checking stop signal
            thread.join(timeout=self.check_interval)
        
        # Thread finished, get the result
        duration = time.time() - start_time
        
        # Check if there was an exception
        if not exception_queue.empty():
            exception = exception_queue.get()
            print(f"{Fore.RED}[{get_timestamp()}] ❌ {self.tool_name} failed: {exception}{Style.RESET_ALL}")
            return {
                "tool_results": [{
                    "tool": self.tool_name,
                    "duration": duration,
                    "result": f"Error: {str(exception)}",
                    "status": "error"
                }]
            }
        
        # Get the result
        if not result_queue.empty():
            return result_queue.get()
        
        # Should not happen, but handle gracefully
        print(f"{Fore.RED}[{get_timestamp()}] ⚠️ {self.tool_name} returned no result{Style.RESET_ALL}")
        return {
            "tool_results": [{
                "tool": self.tool_name,
                "duration": duration,
                "result": "No result from tool",
                "status": "error"
            }]
        }


def get_timestamp() -> str:
    """Get formatted timestamp."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log_tool_start(tool_name: str, color: str = Fore.CYAN):
    """Log when a tool starts execution."""
    print(f"{color}[{get_timestamp()}] 🚀 {tool_name} started{Style.RESET_ALL}\n")


def log_tool_complete(tool_name: str, duration: float, color: str = Fore.GREEN):
    """Log when a tool completes execution."""
    print(f"{color}[{get_timestamp()}] ✅ {tool_name} completed in {duration:.2f}s{Style.RESET_ALL}")


class WeatherCheckTool:
    """Fast tool: Simulates weather API call (10-15 seconds)."""
    
    def __init__(self):
        self.name = "Weather Check"
        self.delay = random.uniform(10.0, 15.0)
        self.color = Fore.CYAN
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        log_tool_start(self.name, self.color)
        start = time.time()
        
        # Simulate work (could be API call, database query, etc.)
        time.sleep(self.delay)
        
        duration = time.time() - start
        log_tool_complete(self.name, duration, Fore.GREEN)
        
        return {
            "tool_results": [{
                "tool": self.name,
                "duration": duration,
                "result": f"Weather: Sunny, 22°C in Milan",
                "status": "success"
            }]
        }


class DatabaseQueryTool:
    """Medium tool: Simulates database query (15-20 seconds)."""
    
    def __init__(self):
        self.name = "Database Query"
        self.delay = random.uniform(15.0, 20.0)
        self.color = Fore.YELLOW
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        log_tool_start(self.name, self.color)
        start = time.time()
        
        # Simulate work (could be API call, database query, etc.)
        time.sleep(self.delay)
        
        duration = time.time() - start
        log_tool_complete(self.name, duration, Fore.GREEN)
        
        return {
            "tool_results": [{
                "tool": self.name,
                "duration": duration,
                "result": "Found 1,247 matching records in database",
                "status": "success"
            }]
        }


class APICallTool:
    """Medium tool: Simulates external API call (15-20 seconds)."""
    
    def __init__(self):
        self.name = "API Call"
        self.delay = random.uniform(15.0, 20.0)
        self.color = Fore.YELLOW
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        log_tool_start(self.name, self.color)
        start = time.time()
        
        # Simulate work (could be API call, database query, etc.)
        time.sleep(self.delay)
        
        duration = time.time() - start
        log_tool_complete(self.name, duration, Fore.GREEN)
        
        return {
            "tool_results": [{
                "tool": self.name,
                "duration": duration,
                "result": "API response: 200 OK - Data retrieved successfully",
                "status": "success"
            }]
        }


class MLInferenceTool:
    """Slow tool: Simulates machine learning model inference (25-30 seconds)."""
    
    def __init__(self):
        self.name = "ML Inference"
        self.delay = random.uniform(25.0, 30.0)
        self.color = Fore.MAGENTA
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        log_tool_start(self.name, self.color)
        start = time.time()
        
        # Simulate work (could be API call, database query, etc.)
        time.sleep(self.delay)
        
        duration = time.time() - start
        log_tool_complete(self.name, duration, Fore.GREEN)
        
        return {
            "tool_results": [{
                "tool": self.name,
                "duration": duration,
                "result": "ML prediction: Sentiment = Positive (confidence: 0.94)",
                "status": "success"
            }]
        }


class DataProcessingTool:
    """Slow tool: Simulates large dataset processing (25-30 seconds)."""
    
    def __init__(self):
        self.name = "Data Processing"
        self.delay = random.uniform(25.0, 30.0)
        self.color = Fore.MAGENTA
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        log_tool_start(self.name, self.color)
        start = time.time()
        
        # Simulate work (could be API call, database query, etc.)
        time.sleep(self.delay)
        
        duration = time.time() - start
        log_tool_complete(self.name, duration, Fore.GREEN)
        
        return {
            "tool_results": [{
                "tool": self.name,
                "duration": duration,
                "result": "Processed 50,000 rows - Average value: 42.7",
                "status": "success"
            }]
        }


# Tool registry - 5 tools for parallel execution
AVAILABLE_TOOLS = {
    "weather_check": WeatherCheckTool,
    "database_query": DatabaseQueryTool,
    "api_call": APICallTool,
    "ml_inference": MLInferenceTool,
    "data_processing": DataProcessingTool,
}

