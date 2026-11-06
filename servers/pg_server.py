
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from psycopg.rows import dict_row

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from project root
load_dotenv(BASE_DIR / ".env")

mcp = FastMCP("postgres-database-server")


def get_connection():
    """Create a connection to PostgreSQL."""

    password = os.getenv("POSTGRES_PASSWORD")

    if not password:
        raise RuntimeError("POSTGRES_PASSWORD is not configured")

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5434")),
        dbname=os.getenv("POSTGRES_DB", "shopdb"),
        user=os.getenv("POSTGRES_USER", "mcpuser"),
        password=password,
        row_factory=dict_row,
    )


@mcp.tool()
def list_pg_products() -> list[dict]:
    """Get all products from PostgreSQL."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, name, price, category
            FROM products
            ORDER BY id
            """
        ).fetchall()

        return [dict(row) for row in rows]


@mcp.tool()
def get_pg_product(product_id: int) -> dict | None:
    """Get a product from PostgreSQL using its ID."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, name, price, category
            FROM products
            WHERE id = %s
            """,
            (product_id,),
        ).fetchone()

        return dict(row) if row else None


if __name__ == "__main__":
    mcp.run()
