# Lab 069 — MCP Tool Discovery

## Lab Intro

In Lab 068, we successfully connected to an MCP server:

```text
Connect
   ↓
Initialize
```

However, we still don't know:

```text
What tools are available?
```

One of MCP's most powerful features is:

> **Tool Discovery**

Unlike traditional integrations where developers manually hardcode available APIs, MCP allows clients to dynamically discover capabilities at runtime.

This means an agent can connect to an unfamiliar server and immediately learn:

```text
What tools exist
What inputs they require
How they should be used
```

without prior knowledge.

---

## Key Idea

Traditional API integration:

```text
Developer reads documentation
         ↓
Writes custom code
         ↓
Calls API
```

MCP integration:

```text
Connect
   ↓
Discover Tools
   ↓
Use Tools
```

The server describes its own capabilities.

---

## Enterprise Analogy

Imagine joining a new company.

Instead of receiving a giant manual, you ask:

```text
What systems do I have access to?
```

The company responds:

```text
CRM
Analytics Platform
Ticketing System
Knowledge Base
```

Now you know what services are available.

MCP tool discovery works exactly the same way.

---

## Why Tool Discovery Matters

Without discovery:

```text
Client must know everything beforehand
```

With discovery:

```text
Client learns capabilities dynamically
```

This enables:

- reusable agents
- plug-and-play integrations
- adaptive workflows

---

# Example MCP Server

Let's begin with a simple MCP server.

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

This server exposes:

```text
lookup_customer()
create_ticket()
```

as MCP tools.

---

# Discovering Tools

Now let's connect and inspect them.

## Client Code

import sys
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

server_params = StdioServerParameters(
    command=sys.executable,
    args=["server.py"],
)

async def main():

    # ----------------------------------
    # Connect to MCP Server
    # ----------------------------------

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(
            read_stream,
            write_stream
        ) as session:

            await session.initialize()

            tools = await session.list_tools()

            print(tools)


await main()

---

## Example Output

```text
[
  Tool(
      name='lookup_customer',
      description='',
      inputSchema=...
  ),

  Tool(
      name='create_ticket',
      description='',
      inputSchema=...
  )
]
```

The client automatically learns what tools exist.

---

## What Is list_tools()?

This MCP method requests:

```text
All available tool definitions
```

from the server.

Conceptually:

```text
Client:
What tools do you offer?
```

```text
Server:
lookup_customer
create_ticket
```

---

## Understanding Tool Metadata

Every MCP tool exposes metadata.

Example:

```text
Tool Name
Description
Input Schema
```

This allows agents to understand how to use the tool.

---

## Example Tool Definition

Conceptually:

```json
{
  "name": "lookup_customer",
  "description": "Retrieve customer information",
  "inputSchema": {
    "customer_id": "string"
  }
}
```

This provides everything needed to invoke the tool.

---

## Why Schemas Matter

The schema tells the agent:

```text
What parameters exist
Which are required
Expected data types
```

Without schemas:

```text
Tool usage becomes guesswork.
```

With schemas:

```text
Tool invocation becomes reliable.
```

---

# Inspecting Individual Tools

You can iterate through discovered tools.

```python
tools = await session.list_tools()

for tool in tools.tools:

    print("Name:", tool.name)

    print("Description:", tool.description)

    print("Schema:", tool.inputSchema)

    print("-" * 40)
```

---

## Example Output

```text
Name: lookup_customer

Description:
Retrieve customer information

Schema:
{
  "customer_id": "string"
}

--------------------------------

Name: create_ticket

Description:
Create support ticket

Schema:
{
  "title": "string",
  "priority": "string"
}
```

Now the client understands how each tool should be used.

---

# Tool Discovery Workflow

The process looks like:

```text
Connect
   ↓
Initialize
   ↓
List Tools
   ↓
Inspect Schemas
   ↓
Choose Tool
   ↓
Invoke Tool
```

This is the foundation of dynamic tool use.

---

## Dynamic Agent Behavior

Imagine connecting to two different servers.

### Server A

```text
search_documents
summarize_document
```

---

### Server B

```text
create_invoice
lookup_customer
```

The agent does not need hardcoded knowledge.

It simply:

```text
Discover → Understand → Use
```

This is a major MCP advantage.

---

## MCP vs Traditional APIs

### Traditional API

Developer manually writes:

```python
create_ticket(...)
lookup_customer(...)
```

and maintains those integrations.

---

### MCP

Agent asks:

```text
What tools exist?
```

and adapts automatically.

---

## Enterprise Benefits

### 1. Reduced Maintenance

New tools automatically appear.

---

### 2. Faster Integration

No manual API mapping required.

---

### 3. Reusable Agents

Same agent can work across:

```text
CRM
ERP
Analytics
Support Systems
```

---

### 4. Self-Describing Systems

Servers document themselves.

---

## Real MCP Discovery Example

Imagine an enterprise MCP server exposes:

```text
lookup_customer
create_order
cancel_order
refund_order
```

An AI assistant connects and immediately understands:

```text
Available actions
Required inputs
Usage patterns
```

without custom coding.

---

## Common Mistakes

### 1. Skipping Initialization

Bad:

```python
await session.list_tools()
```

before:

```python
await session.initialize()
```

---

Correct:

```python
initialize()
```

first.

---

### 2. Ignoring Schemas

Bad:

```text
Call tool blindly
```

---

Better:

```text
Inspect schema first
```

---

### 3. Missing Tool Descriptions

Tool descriptions help agents decide:

```text
When to use a tool
```

Always provide clear descriptions.

---

### 4. Hardcoding Tool Names

Avoid assumptions such as:

```python
tool_name = "search"
```

Instead:

```text
Discover dynamically
```

---

## Mental Model

Think of MCP tool discovery as:

```text
Reading a menu before ordering food
```

You first inspect:

```text
Available options
```

before deciding:

```text
What to use
```

---

## Architecture

```text
                Client
                   │
                   ▼
           initialize()
                   │
                   ▼
             list_tools()
                   │
                   ▼
      ┌─────────────────────┐
      │ MCP Server          │
      ├─────────────────────┤
      │ lookup_customer()   │
      │ create_ticket()     │
      │ search_docs()       │
      └─────────────────────┘
```

---

## Why This Matters

Tool discovery is one of the defining capabilities of MCP.

It enables:

```text
Dynamic integrations
Adaptive agents
Portable workflows
```

instead of relying on fixed, hardcoded APIs.

This makes AI systems significantly more flexible and maintainable.

---

## Key Takeaways

- MCP servers expose self-describing tools.
- `list_tools()` allows clients to discover capabilities dynamically.
- Tool schemas explain how tools should be invoked.
- Discovery removes the need for hardcoded integrations.
- MCP enables adaptive and reusable agents.
- Tool metadata includes names, descriptions, and input schemas.
- Dynamic discovery is a core MCP capability.
- Understanding available tools is the first step before invoking them.