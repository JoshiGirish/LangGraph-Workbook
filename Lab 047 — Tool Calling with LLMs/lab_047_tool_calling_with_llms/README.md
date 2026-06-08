# Lab 047 — Tool Calling with LLMs

## Lab Intro

In Lab 046, we created a Tool Node that directly called a Python function.

The workflow looked like:

```text
Graph → Tool → Result
```

But there was one limitation:

```text
The graph always decided which tool to execute.
```

Modern AI agents work differently.

Instead of hardcoding tool usage, we allow the LLM to decide:

```text
Should I answer directly?
OR
Should I use a tool?
```

This capability is known as:

> **Tool Calling**

Tool calling allows an LLM to request execution of external functions whenever it needs additional information or computation.

---

## Key Idea

Without tool calling:

```text
User → LLM → Response
```

With tool calling:

```text
User
  ↓
LLM
  ↓
Tool Request
  ↓
Tool Execution
  ↓
Tool Result
  ↓
LLM Final Response
```

The model becomes capable of taking actions.

---

## Enterprise Analogy

Imagine a customer support representative.

A customer asks:

```text
What is the status of order 12345?
```

The representative does not memorize all orders.

Instead:

```text
Customer Question
       ↓
Representative
       ↓
Order Lookup System
       ↓
Result Returned
       ↓
Final Answer
```

Tool calling follows exactly the same pattern.

The LLM decides when external information is required.

---

## Lab Code

from typing import Annotated

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from typing_extensions import TypedDict


# -------------------------
# Tool
# -------------------------

@tool
def calculator(expression: str) -> str:
    """
    Evaluate a simple math expression.
    """
    return str(eval(expression))


# -------------------------
# State
# -------------------------

class State(TypedDict):
    messages: Annotated[list, add_messages]


# -------------------------
# LLM with Tool
# -------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

tools = [calculator]

llm_with_tools = llm.bind_tools(tools)


# -------------------------
# Chatbot Node
# -------------------------

def chatbot(state: State):
    response = llm_with_tools.invoke(
        state["messages"]
    )

    return {
        "messages": [response]
    }


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "chatbot",
    chatbot
)

builder.add_edge(
    START,
    "chatbot"
)

builder.add_edge(
    "chatbot",
    END
)

graph = builder.compile()


# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "messages": [
            (
                "user",
                "What is 125 * 8?"
            )
        ]
    }
)

print(result["messages"][-1])

---

## Example Output

```python
AIMessage(
    content='',
    tool_calls=[
        {
            'name': 'calculator',
            'args': {
                'expression': '125 * 8'
            }
        }
    ]
)
```

---

## Explanation

## What Is Tool Calling?

Tool calling allows an LLM to produce:

```text
Tool Request
```

instead of a final answer.

For example:

User asks:

```text
What is 125 * 8?
```

The model may generate:

```python
{
    "tool": "calculator",
    "expression": "125 * 8"
}
```

rather than immediately producing:

```text
1000
```

---

## Step 1 — Define a Tool

LangChain tools use the `@tool` decorator:

```python
@tool
def calculator(expression: str):
```

The docstring becomes part of the tool description.

```python
"""
Evaluate a simple math expression.
"""
```

This description helps the model decide when to use the tool.

---

## Step 2 — Register Tools

Create a tool list:

```python
tools = [calculator]
```

Bind tools to the model:

```python
llm_with_tools = llm.bind_tools(
    tools
)
```

Now the LLM knows:

```text
Available Tool:
calculator(expression)
```

---

## Step 3 — Invoke the Model

Inside the node:

```python
response = llm_with_tools.invoke(
    state["messages"]
)
```

The model receives:

```text
User Message
+
Tool Definitions
```

and decides whether a tool is needed.

---

## Step 4 — Inspect Tool Calls

Instead of text output:

```text
1000
```

the model may return:

```python
AIMessage(
    content="",
    tool_calls=[...]
)
```

The tool call contains:

```python
{
    "name": "calculator",
    "args": {
        "expression": "125 * 8"
    }
}
```

This is the LLM requesting execution.

---

## Important Observation

At this stage:

```text
The tool has NOT executed yet.
```

The model only produced:

```text
A request to execute the tool
```

Execution happens later.

---

## Tool Calling Lifecycle

```text
User Message
      │
      ▼
LLM
      │
      ▼
Tool Call Generated
      │
      ▼
Tool Executes
      │
      ▼
Tool Result
      │
      ▼
LLM Produces Final Answer
```

In this lab we only cover:

```text
LLM → Tool Request
```

The next lab will complete the full cycle.

---

## Why Tool Calling Matters

Without tool calling:

```text
LLM only reasons from training data
```

With tool calling:

```text
LLM can interact with external systems
```

Examples:

```text
Search Engine
Database
Calculator
Weather API
CRM System
Inventory Service
Email Platform
```

This enables real-world automation.

---

## Tool Selection by the Model

The model decides based on:

### User Request

```text
What is 25 * 4?
```

Tool likely needed.

---

### Tool Description

```python
"""
Evaluate a simple math expression.
"""
```

The clearer the description:

```text
The better tool selection becomes.
```

---

### Available Tools

If the model sees:

```text
calculator
weather
search
database
```

it chooses the most relevant one.

---

## Common Mistakes

### 1. Forgetting bind_tools()

Bad:

```python
response = llm.invoke(...)
```

No tools available.

---

Good:

```python
llm.bind_tools(tools)
```

---

### 2. Poor Tool Descriptions

Bad:

```python
"""
Do stuff
"""
```

The model cannot understand its purpose.

---

Good:

```python
"""
Evaluate a simple math expression.
"""
```

Clear and specific.

---

### 3. Assuming Tool Calls Execute Automatically

Many beginners expect:

```text
LLM requests tool
```

to automatically become:

```text
Tool executes
```

This is not true.

The model only generates:

```text
Tool instructions
```

Execution must still happen.

---

## Mental Model

Think of tool calling as:

```text
LLM raises a hand and says:

"I need this tool."
```

The model is not executing the tool.

It is requesting access to the tool.

---

## Architecture

```text
User
 │
 ▼
LLM
 │
 ▼
Tool Call Request
 │
 ▼
(Execution Layer)
 │
 ▼
Tool Result
 │
 ▼
LLM
 │
 ▼
Final Answer
```

Tool calling is the communication protocol between the LLM and external systems.

---

## Key Takeaways

- Tool calling allows an LLM to request external functionality.
- Tools are registered using the `@tool` decorator.
- `bind_tools()` exposes available tools to the model.
- The model can generate structured tool calls instead of text responses.
- A tool call is only a request; execution has not yet occurred.
- Tool calling is the foundation of agent architectures.
- In the next lab, we will execute tool calls using LangGraph's built-in ToolNode and create a complete ReAct-style workflow.