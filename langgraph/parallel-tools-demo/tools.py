"""Simulated tools with varying execution times for parallel execution demonstration."""

import time
import random
from datetime import datetime
from typing import Dict, Any
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


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
        
        # Simulate work
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
        
        # Simulate work
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
        
        # Simulate work
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
        
        # Simulate work
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
        
        # Simulate work
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

