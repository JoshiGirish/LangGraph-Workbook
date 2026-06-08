# Lab 068 — Connecting MCP Servers

## Lab Intro

In Lab 067, we introduced the:

> **Model Context Protocol (MCP)**

and learned that MCP provides a standardized way for AI applications to interact with:

- tools
- resources
- prompts
- external systems

through MCP servers.

However, understanding MCP conceptually is only the first step.

Now we will connect to an actual MCP server and inspect what it exposes.

This is the first practical MCP lab.

---

## Key Idea

An MCP workflow typically starts with:

```text
Connect
   ↓
Discover
   ↓
Use
```

Before an agent can call tools, it must first establish a connection to an MCP server.

---

## Enterprise Analogy

Imagine joining a company.

Before you can use:

```text
CRM
Ticketing System
Analytics Platform
```

you must first:

```text
Connect
Authenticate
Discover available services
```

MCP works similarly.

---

## MCP Connection Architecture

```text
Agent
   ↓
MCP Client
   ↓
MCP Server
   ↓
Tools / Resources / Prompts
```

The first step is creating the client-server connection.

---

## Lab Code

### Install MCP Packages

!pip install mcp


Depending on your MCP server implementation, you may also need:

!pip install langchain-mcp-adapters

---

### Example MCP Client Connection

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

            # Initialize connection

            await session.initialize()

            print("Connected to MCP Server")


await main()

---

## Expected Output

```text
Connected to MCP Server
```

If the server starts successfully, the client and server establish an MCP session.

---

## Explanation

## What Is Happening?

The client launches:

```python
stdio_client(...)
```

which starts an MCP server process.

The client and server then communicate through:

```text
stdin
stdout
```

This is the most common local MCP connection pattern.

---

## Step 1 — Start Server Process

```python
stdio_client(
    command="python",
    args=["server.py"]
)
```

This launches:

```text
python server.py
```

behind the scenes.

---

## Step 2 — Create Session

```python
ClientSession(
    read_stream,
    write_stream
)
```

The session manages:

- protocol messages
- requests
- responses
- tool calls

---

## Step 3 — Initialize

```python
await session.initialize()
```

Initialization performs the MCP handshake.

Conceptually:

```text
Client:
Hello
```

```text
Server:
Hello
```

```text
Client:
What capabilities do you support?
```

```text
Server:
Here are my capabilities.
```

---

## Why Initialization Matters

Without initialization:

```text
No capability negotiation
```

The client cannot reliably interact with the server.

Always initialize first.

---

# Creating a Simple MCP Server

To make the example complete, let's build a minimal server.

---

## Example Server

```python
from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    "Demo Server"
)


@mcp.tool()
def hello(name: str) -> str:
    return f"Hello {name}"


if __name__ == "__main__":
    mcp.run()
```

This server exposes:

```text
hello()
```

as an MCP tool.

---

## Server Architecture

```text
FastMCP
   ↓
Tool Registration
   ↓
Tool Exposure
```

The MCP framework automatically publishes registered tools.

---

## Local MCP Communication

The complete flow becomes:

```text
Client
   ↓
stdio
   ↓
MCP Server
   ↓
hello()
```

No custom protocol implementation is required.

---

## Understanding Transports

MCP supports multiple transport mechanisms.

---

### 1. STDIO

Used most commonly during development.

```text
Client ↔ Process
```

Example:

```text
python server.py
```

---

### 2. HTTP

Useful for remote deployments.

```text
Client ↔ HTTP Server
```

---

### 3. WebSocket

Useful for real-time communication.

```text
Client ↔ WebSocket Server
```

---

## Why STDIO Is Popular

Benefits:

```text
Simple
Fast
Local
No networking setup
```

This is why many MCP tutorials begin with STDIO.

---

## MCP Lifecycle

A typical MCP interaction follows:

```text
Start Server
      ↓
Connect
      ↓
Initialize
      ↓
Discover Capabilities
      ↓
Use Capabilities
      ↓
Close Session
```

In this lab we covered:

```text
Start
Connect
Initialize
```

The next lab will focus on:

```text
Discover Capabilities
```

---

## Common Errors

### 1. Server Not Running

Example:

```text
File not found
```

or

```text
Cannot launch process
```

Verify:

```text
server.py exists
```

---

### 2. Missing Initialization

Bad:

```python
session = ClientSession(...)
```

and immediately calling tools.

---

Correct:

```python
await session.initialize()
```

first.

---

### 3. Wrong Transport

Client and server must agree on:

```text
STDIO
HTTP
WebSocket
```

---

### 4. Dependency Issues

Ensure MCP packages are installed:

```bash
pip install mcp
```

---

## Mental Model

Think of connecting to an MCP server as:

```text
Opening a conversation
```

Before asking for tools or resources:

```text
Connect
Introduce yourself
Discover capabilities
```

Only then can meaningful work begin.

---

## Architecture

```text
             Client
                │
                ▼
      ┌─────────────────┐
      │ Client Session  │
      └────────┬────────┘
               │
         initialize()
               │
               ▼
      ┌─────────────────┐
      │   MCP Server    │
      └────────┬────────┘
               │
               ▼
      Tools / Resources
```

---

## Why This Matters

Every MCP-enabled application begins with:

```text
Connection
```

Whether you are building:

- AI assistants
- enterprise agents
- research systems
- autonomous workflows

the first step is always:

```text
Connect to an MCP server
```

and establish a valid MCP session.

---

## Key Takeaways

- MCP clients connect to MCP servers through transports such as STDIO.
- `ClientSession` manages communication with the server.
- `initialize()` performs the MCP handshake.
- MCP servers expose tools, resources, and prompts.
- STDIO is the most common local development transport.
- Connection and initialization are required before capability discovery.
- Establishing an MCP session is the foundation of all MCP interactions.