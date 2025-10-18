"""Script to visualize the LangGraph structure without executing it."""

from colorama import Fore, Style, init
from main import build_graph

# Initialize colorama
init(autoreset=True)


def main():
    """Generate and save graph visualization."""
    print(f"\n{Fore.BLUE}Generating graph visualization...{Style.RESET_ALL}")
    
    # Build the graph
    graph = build_graph()
    
    # Save graph visualization
    try:
        graph_image = graph.get_graph().draw_mermaid_png()
        with open("graph_visualization.png", "wb") as f:
            f.write(graph_image)
        print(f"{Fore.GREEN}✓ Graph visualization saved to graph_visualization.png{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Open the image to see the parallel execution structure:{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}open graph_visualization.png{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  Make sure grandalf is installed: pip install grandalf{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()

