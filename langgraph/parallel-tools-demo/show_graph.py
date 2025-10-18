"""Script to display the LangGraph structure as text."""

from colorama import Fore, Style, init
from main import build_graph

# Initialize colorama
init(autoreset=True)


def main():
    """Display graph structure."""
    print(f"\n{Fore.BLUE}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'LANGGRAPH PARALLEL EXECUTION STRUCTURE':^80}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'=' * 80}{Style.RESET_ALL}\n")
    
    # Build the graph
    graph = build_graph()
    
    # Get Mermaid diagram
    try:
        mermaid_text = graph.get_graph().draw_mermaid()
        print(f"{Fore.CYAN}Mermaid Diagram:{Style.RESET_ALL}\n")
        print(mermaid_text)
        
        # Save to file
        with open("graph_structure.mmd", "w") as f:
            f.write(mermaid_text)
        print(f"\n{Fore.GREEN}✓ Mermaid diagram saved to graph_structure.mmd{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  You can visualize it at: https://mermaid.live/{Style.RESET_ALL}\n")
        
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}\n")
    
    # Print text representation
    print(f"\n{Fore.CYAN}Text Representation:{Style.RESET_ALL}\n")
    print(f"{Fore.WHITE}START{Style.RESET_ALL}")
    print(f"  ↓")
    print(f"{Fore.GREEN}prepare_execution{Style.RESET_ALL} (initialize state)")
    print(f"  ↓")
    print(f"  ├─→ {Fore.CYAN}weather_check{Style.RESET_ALL}      (10-15s)")
    print(f"  ├─→ {Fore.YELLOW}database_query{Style.RESET_ALL}    (15-20s)")
    print(f"  ├─→ {Fore.YELLOW}api_call{Style.RESET_ALL}           (15-20s)")
    print(f"  ├─→ {Fore.MAGENTA}ml_inference{Style.RESET_ALL}       (25-30s)")
    print(f"  └─→ {Fore.MAGENTA}data_processing{Style.RESET_ALL}    (25-30s)")
    print(f"       ↓ (all converge)")
    print(f"{Fore.GREEN}aggregate_results{Style.RESET_ALL} (collect & summarize)")
    print(f"  ↓")
    print(f"{Fore.WHITE}END{Style.RESET_ALL}\n")
    
    print(f"{Fore.BLUE}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ All 5 tools execute in PARALLEL after prepare_execution{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Results are aggregated once all tools complete{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'=' * 80}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()

