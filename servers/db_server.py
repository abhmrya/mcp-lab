
import sqlite3
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite database path
DB_PATH = BASE_DIR / "data" / "shop.db"

# Create MCP server
mcp = FastMCP("shop-database-server")


def get_connection():
    """Create a read-only SQLite connection."""
    connection = sqlite3.connect(
        f"file:{DB_PATH.as_posix()}?mode=ro",
        uri=True,
    )
    connection.row_factory = sqlite3.Row
    return connection


@mcp.tool()
def list_products() -> list[dict]:
    """Get all products from the shop database."""

    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT id, name, price, category FROM products"
        )

        return [dict(row) for row in cursor.fetchall()]


@mcp.tool()
def get_product(product_id: int) -> dict | None:
    """Get a product by its ID."""

    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT id, name, price, category FROM products WHERE id = ?",
            (product_id,),
        )

        row = cursor.fetchone()

        return dict(row) if row else None


if __name__ == "__main__":
    mcp.run()
