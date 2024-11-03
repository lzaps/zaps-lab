# Research Agent in LangGraph, retrieve information from different LLMs and web search LangGraph

Inspired by https://www.pinecone.io/learn/langgraph-research-agent/

**Research agents** are multi-step LLM agents that through multiple steps can produce in depth research reports on a topic of our choosing.

LangGraph agent that retrieve information form different LLMs and Tavily web search in order to respond to the request of the user.

I use JupyterLab for this example.

### How to Setup

1. Create Python env
```
python3 -m venv venv-langgraph
```
3. Activate env
```
source venv-langgraph/bin/activate
```
4. Install requirements
```
pip install -r requirements.txt
```
5. Run JupyterLab
```
jupyter lab
```

(exit from env)
```
deactivate
```
