"""State definition for the parallel tools execution graph."""

import operator
from typing import Annotated, Optional
from typing_extensions import TypedDict


class GraphState(TypedDict):
    """State for the parallel tools execution graph."""
    
    # User's input query
    input_query: str
    
    # Accumulated results from all tools (append-only with operator.add)
    tool_results: Annotated[list, operator.add]
    
    # Execution summary with timing information
    execution_summary: Optional[dict]
    
    # Timestamp when execution started
    start_time: Optional[float]

