# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("vincent says ...")


# Add a tool to ask Vincent something
import random
@mcp.tool()
def ask_vincent(question: str) -> str:
    """Ask Vincent something and get a yes/no answer."""
    if random.choice([True, False]):
        return "yes, that's a good idea!"
    else:
        return "no! hell no!"

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! Would you like to ask Vincent something?"



def main() -> None:
    mcp.run(transport='stdio')
