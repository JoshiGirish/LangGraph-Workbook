from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Business Tools"
)


@mcp.tool()
def lookup_customer(
    customer_id: str
) -> str:

    return f"Customer: {customer_id}"


@mcp.tool()
def create_ticket(
    title: str,
    priority: str
) -> str:

    return f"Ticket created: {title}"


if __name__ == "__main__":
    mcp.run()