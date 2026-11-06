import logging
import sys

from mcp.server.fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
)

mcp = FastMCP("first-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.resource("app://info")
def get_app_info() -> str:
    """Return application information."""
    return "Welcome to MCP Lab! This is our first MCP resource."


@mcp.prompt()
def product_analysis(product_name: str, price: float) -> str:
    """Generate a product analysis prompt."""
    return (
        f"Analyze this product: {product_name}. "
        f"Its price is {price}. "
        "Evaluate its value, features, and suitability for customers."
    )


if __name__ == "__main__":
    mcp.run()