# Graph Structure Visualization

## LangGraph Architecture

This document shows the parallel execution graph structure used in this demo.

## Flow Diagram

```
                    START
                      |
                      v
              prepare_execution
                      |
         +------------+------------+
         |            |            |
         v            v            v
    weather_check  database_   api_call
                    query
         |            |            |
         v            v            v
                ml_inference  data_processing
                      |            |
         +------------+------------+
                      |
                      v
              aggregate_results
                      |
                      v
                     END
```

## Detailed Structure

### 1. START → prepare_execution
- Initializes state
- Records start time
- Logs execution start
- Prints query and tool count

### 2. prepare_execution → [All 5 Tools]
**Conditional Edge Fan-Out**: Routes to all tools simultaneously

The 5 tools execute in parallel:

#### Fast Tool (10-15 seconds)
1. `weather_check` - Simulated weather API

#### Medium Tools (15-20 seconds)
2. `database_query` - Simulated DB query
3. `api_call` - Simulated external API

#### Slow Tools (25-30 seconds)
4. `ml_inference` - Simulated ML model
5. `data_processing` - Simulated data pipeline

Each tool:
- Logs start with colored timestamp
- Executes simulated work (`time.sleep`)
- Logs completion with duration
- Returns result to state using `operator.add` reducer

### 3. [All 5 Tools] → aggregate_results
**Fan-In**: Waits for all parallel tools to complete

### 4. aggregate_results → END
- Collects all results
- Sorts by duration
- Displays formatted table
- Calculates statistics
- Shows performance comparison

## State Flow

```python
Initial State:
{
    "input_query": "...",
    "tool_results": [],
    "execution_summary": None,
    "start_time": None
}

After prepare_execution:
{
    "input_query": "...",
    "tool_results": [],
    "execution_summary": {},
    "start_time": 1697548325.123
}

After each tool (results accumulate):
{
    "input_query": "...",
    "tool_results": [
        {"tool": "weather_check", "duration": 12.22, ...},
        {"tool": "database_query", "duration": 17.45, ...},
        ...
    ],
    "execution_summary": {},
    "start_time": 1697548325.123
}

Final State:
{
    "input_query": "...",
    "tool_results": [... all 5 results ...],
    "execution_summary": {
        "total_duration": 30.12,
        "sequential_duration": 106.80,
        "time_saved": 76.68,
        ...
    },
    "start_time": 1697548325.123
}
```

## Key LangGraph Concepts

### Fan-Out Pattern
```python
builder.add_conditional_edges(
    "prepare_execution",
    route_to_all_tools,  # Returns list of all tool names
    list(AVAILABLE_TOOLS.keys())
)
```

### State Accumulation
```python
class GraphState(TypedDict):
    tool_results: Annotated[list, operator.add]  # Append-only
```

### Fan-In Pattern
```python
for tool_name in AVAILABLE_TOOLS.keys():
    builder.add_edge(tool_name, "aggregate_results")
```

## Parallel Execution Benefits

### Sequential Execution Time
Sum of all individual tool durations:
```
12.22 + 17.45 + 19.12 + 28.34 + 29.67 = ~107 seconds
```

### Parallel Execution Time
Maximum of all individual tool durations (slowest tool):
```
max(12.22, 17.45, 19.12, 28.34, 29.67) = ~29.67 seconds
```
Plus small overhead for coordination = ~30 seconds total

### Performance Improvement
```
Time Saved = 107 - 30 = 77 seconds (~72% faster)
```

## Visualization Commands

The graph can be visualized using:

```python
from IPython.display import Image
graph = build_graph()
display(Image(graph.get_graph().draw_mermaid_png()))
```

Or exported to PNG:
```python
with open("graph_visualization.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())
```

## Customization Examples

### Add New Tool
```python
# In tools.py
class MyNewTool:
    def __init__(self):
        self.name = "My New Tool"
        self.delay = random.uniform(2.0, 3.0)
        self.color = Fore.BLUE
    
    def __call__(self, state):
        # Implementation
        pass

# Add to registry
AVAILABLE_TOOLS["my_new_tool"] = MyNewTool
```

The graph automatically adapts to include the new tool in parallel execution.

### Sequential Execution Instead
To execute tools sequentially instead of parallel:
```python
# Replace conditional_edges with simple edges
builder.add_edge("prepare_execution", "tool1")
builder.add_edge("tool1", "tool2")
builder.add_edge("tool2", "tool3")
# ... etc
```

This would demonstrate the performance difference!

