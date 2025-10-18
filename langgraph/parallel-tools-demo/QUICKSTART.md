# Quick Start Guide

## Fast Setup (Automated)

```bash
cd /Users/l.zappa/workspace/zaps-lab/langgraph/parallel-tools-demo
./setup.sh
```

Then run:
```bash
source venv/bin/activate
python main.py
```

## Manual Setup

```bash
# 1. Navigate to project
cd /Users/l.zappa/workspace/zaps-lab/langgraph/parallel-tools-demo

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate environment
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the demo
python main.py
```

## What You'll See

The demo will execute 5 tools in parallel with real-time progress tracking:

1. **Initialization**: Shows query and tools being launched
2. **Execution**: Real-time updates as each tool starts (🚀) and completes (✅)
3. **Summary**: Comprehensive statistics showing parallel vs sequential performance

## Features Demonstrated

- ⚡ **Fast Tool** (10-15s): Weather Check
- ⏱️ **Medium Tools** (15-20s): Database Query, API Call
- 🐌 **Slow Tools** (25-30s): ML Inference, Data Processing

## Expected Results

- **Parallel execution**: ~30 seconds total (slowest tool determines duration)
- **Sequential would take**: ~100+ seconds (sum of all tools)
- **Time saved**: ~70% faster with parallelization (saves over 1 minute!)

## Customization

Edit `tools.py` to:
- Add more tools
- Change execution times
- Modify output colors
- Customize tool behaviors

See `README.md` for detailed documentation.

