# Parallel Tools Execution Demo with LangGraph

This project demonstrates parallel tool execution in LangGraph with simulated tools that have varying execution times. It showcases real-time progress tracking with colored console output and comprehensive execution summaries.

## Features

- 🚀 **Parallel Execution**: 5 tools execute simultaneously using LangGraph's fan-out/fan-in pattern
- ⏱️ **Varying Execution Times**: Tools simulate different complexity levels (fast, medium, slow)
- 🎨 **Real-time Progress Tracking**: Colored console output showing when each tool starts and completes
- 📊 **Execution Summary**: Detailed statistics comparing parallel vs sequential execution
- 🏗️ **Clean Architecture**: Separation of concerns with dedicated modules for state, tools, and graph logic

## Tools Overview

The demo includes 5 simulated tools with realistic long execution times:

### Fast Tool (10-15 seconds)
- **Weather Check**: Simulates weather API call

### Medium Tools (15-20 seconds)
- **Database Query**: Simulates database query execution
- **API Call**: Simulates external API call

### Slow Tools (25-30 seconds)
- **ML Inference**: Simulates machine learning model inference
- **Data Processing**: Simulates large dataset processing

## Project Structure

```
parallel-tools-demo/
├── main.py              # Main execution script with graph setup
├── tools.py             # Tool definitions with simulated delays
├── state.py             # LangGraph state schema definition
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd /Users/l.zappa/workspace/zaps-lab/langgraph/parallel-tools-demo
python3 -m venv venv
```

### 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set OpenAI API Key (Optional)

While this demo doesn't use LLMs, you can extend it to include LLM summarization:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Usage

### Run the Demo (Console)

```bash
python main.py
```

### Run the Streaming API (Recommended!)

```bash
python api.py
```

Then test with:
- **Postman**: `GET http://localhost:8000/execute?query=test`
- **Browser**: http://localhost:8000/docs (Swagger UI)
- **curl**: `curl -N http://localhost:8000/execute?query=test`

See [API_GUIDE.md](API_GUIDE.md) for complete API documentation.

### Expected Output

The script will display:

1. **Initialization**: Shows the query and number of tools being launched
2. **Real-time Progress**: As tools execute in parallel, you'll see:
   - 🚀 Start messages with timestamps (colored by tool speed)
   - ✅ Completion messages with duration (green)
3. **Execution Summary**: A comprehensive table showing:
   - All tool results sorted by duration
   - Speed indicators (⚡ fast, ⏱️ medium, 🐌 slow)
   - Statistics comparing parallel vs sequential execution
   - Time saved by parallel execution

### Example Output

```
================================================================================
                    PARALLEL TOOLS EXECUTION DEMO
================================================================================

[14:23:45.123] 📋 Query: Execute all tools to gather comprehensive information
[14:23:45.124] 🚀 Launching 5 tools in parallel...

[14:23:45.125] 🚀 Weather Check started
[14:23:45.126] 🚀 Database Query started
[14:23:45.127] 🚀 API Call started
[14:23:45.128] 🚀 ML Inference started
[14:23:45.129] 🚀 Data Processing started

[14:23:57.342] ✅ Weather Check completed in 12.22s
[14:24:02.573] ✅ Database Query completed in 17.45s
[14:24:04.244] ✅ API Call completed in 19.12s
[14:24:13.464] ✅ ML Inference completed in 28.34s
[14:24:14.796] ✅ Data Processing completed in 29.67s

================================================================================
                           EXECUTION SUMMARY
================================================================================

Tool Name                 Duration     Status     Result
--------------------------------------------------------------------------------
⚡ Weather Check          12.22s       success    Weather: Sunny, 22°C in Milan
⏱️ Database Query         17.45s       success    Found 1,247 matching records
⏱️ API Call               19.12s       success    API response: 200 OK
🐌 ML Inference           28.34s       success    ML prediction: Positive (0.94)
🐌 Data Processing        29.67s       success    Processed 50,000 rows

                                  Statistics:
  • Total execution time: 30.12s (with parallel execution)
  • Sequential time would be: 106.80s
  • Time saved: 76.68s (71.8% faster)
  • Average tool duration: 21.36s
  • Fastest tool: 12.22s
  • Slowest tool: 29.67s

✨ All tools completed successfully!
================================================================================
```

## How It Works

### LangGraph Architecture

The project uses LangGraph's StateGraph with a fan-out/fan-in pattern:

```
START → prepare_execution → [all 8 tools in parallel] → aggregate_results → END
```

1. **prepare_execution**: Initializes state and logs start
2. **Parallel Tools**: All 8 tools execute simultaneously
3. **aggregate_results**: Collects results and displays summary

### State Management

The `GraphState` TypedDict manages:
- `input_query`: User's initial query
- `tool_results`: Accumulated results using `operator.add` reducer
- `execution_summary`: Timing statistics
- `start_time`: Execution start timestamp

### Tool Implementation

Each tool:
1. Logs start with colored timestamp
2. Simulates work with `time.sleep()`
3. Logs completion with duration
4. Returns structured result to state

## Customization

### Add More Tools

Edit `tools.py` and add new tool classes following the pattern:

```python
class MyNewTool:
    def __init__(self):
        self.name = "My Tool"
        self.delay = random.uniform(2.0, 4.0)
        self.color = Fore.YELLOW
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        log_tool_start(self.name, self.color)
        start = time.time()
        time.sleep(self.delay)
        duration = time.time() - start
        log_tool_complete(self.name, duration, Fore.GREEN)
        
        return {
            "tool_results": [{
                "tool": self.name,
                "duration": duration,
                "result": "Your result here",
                "status": "success"
            }]
        }
```

Then add to `AVAILABLE_TOOLS` dictionary.

### Modify Execution Times

Edit the `self.delay` values in each tool class to simulate different execution times. Currently set to 10-30 seconds for dramatic parallel execution demonstration.

### Change Colors

Modify the `self.color` attribute in each tool using colorama colors:
- `Fore.CYAN` - Fast tools
- `Fore.YELLOW` - Medium tools
- `Fore.MAGENTA` - Slow tools

## Deactivate Environment

When done:

```bash
deactivate
```

## Key Concepts Demonstrated

1. **Parallel Execution in LangGraph**: Using conditional edges to fan-out to multiple nodes
2. **State Reduction**: Using `operator.add` to accumulate results from parallel nodes
3. **Real-time Feedback**: Progress tracking during long-running operations
4. **Performance Benefits**: Visual demonstration of parallel vs sequential execution

## Extending the Demo

### Add LLM Summarization

Add an OpenAI-powered summarization node that processes all tool results:

```python
from langchain_openai import ChatOpenAI

def llm_summary(state: GraphState) -> Dict[str, Any]:
    llm = ChatOpenAI(model="gpt-4")
    results_text = "\n".join([f"- {r['tool']}: {r['result']}" for r in state["tool_results"]])
    summary = llm.invoke(f"Summarize these tool results:\n{results_text}")
    print(f"\n{Fore.BLUE}LLM Summary: {summary.content}{Style.RESET_ALL}")
    return {}
```

### Add Error Handling

Wrap tool execution in try-except blocks to handle failures gracefully.

### Add Streaming Output

Use LangGraph's streaming capabilities to show results as they complete.

## License

This project is part of the zaps-lab workspace and follows the repository's license.

## Author

Created as a demonstration of LangGraph's parallel execution capabilities.

