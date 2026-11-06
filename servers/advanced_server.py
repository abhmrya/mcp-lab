import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Any
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP, Context
from mcp.shared.exceptions import McpError
from mcp.types import SamplingMessage, TextContent

class ProductOutput(BaseModel):
    product_id: int
    name: str
    price: float
    in_stock: bool

class ConfirmDeletionInput(BaseModel):
    confirm: bool


from mcp.server.fastmcp import FastMCP, Context


logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    """Manage application startup and shutdown."""

    logger.info("MCP server is starting...")

    app_data = {
        "application": "MCP Lab",
        "status": "running",
    }

    try:
        yield app_data
    finally:
        logger.info("MCP server is shutting down...")


mcp = FastMCP(
    "advanced-mcp-server",
    lifespan=app_lifespan,
)


@mcp.tool()
def get_server_info() -> dict:
    """Return basic server information."""

    return {
        "application": "MCP Lab",
        "feature": "Lifespan",
        "status": "working",
    }



@mcp.tool()
def get_lifespan_data(ctx: Context) -> dict:
    """Read application data initialized during server startup."""

    app_data = ctx.request_context.lifespan_context

    return {
        "application": app_data["application"],
        "status": app_data["status"],
    }


@mcp.tool()
def get_product_details(product_id: int) -> ProductOutput:
    """Return product information in a structured format."""

    return ProductOutput(
        product_id=product_id,
        name="Laptop",
        price=55000.0,
        in_stock=True,
    )

@mcp.tool()
async def run_progress_task(ctx: Context, steps: int = 5) -> dict:
    """Demonstrate progress notifications for a long-running task."""

    if steps < 1 or steps > 10:
        raise ValueError("steps must be between 1 and 10")

    for current in range(1, steps + 1):
        await ctx.report_progress(
            progress=current,
            total=steps,
            message=f"Completed step {current} of {steps}",
        )

        await asyncio.sleep(1)

    return {
        "status": "completed",
        "steps": steps,
    }


@mcp.tool()
async def confirm_product_deletion(ctx: Context, product_name: str) -> dict:
    """Ask the user before deleting a product."""

    result = await ctx.elicit(
        message=f"Do you want to delete {product_name}?",
        schema=ConfirmDeletionInput,
    )

    if result.action == "accept":
        if result.data.confirm:
            return {
                "status": "confirmed",
                "message": f"{product_name} deletion approved",
            }

        return {
            "status": "cancelled",
            "message": "Deletion was not approved",
        }

    return {
        "status": "cancelled",
        "message": "User declined or dismissed the request",
    }


@mcp.tool()
async def generate_product_description(
    product_name: str,
    ctx: Context,
) -> str:
    """Generate a product description using client-side AI sampling."""

    prompt = (
        f"Write a short and attractive product description "
        f"for {product_name}. Keep it under 50 words."
    )

    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=prompt,
                ),
            )
        ],
        max_tokens=100,
    )

    if result.content.type == "text":
        return result.content.text

    return "The AI returned a non-text response."


if __name__ == "__main__":
    mcp.run()
