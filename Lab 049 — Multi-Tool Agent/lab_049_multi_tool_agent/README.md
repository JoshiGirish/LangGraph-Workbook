# Lab 049 — Multi-Tool Agent

## Lab Intro

In Lab 048, we built our first ReAct agent.

The agent could:

```text
Reason
  ↓
Call Tool
  ↓
Observe Result
  ↓
Generate Answer
```

However, it only had access to a single tool:

```text
calculator
```

Real-world agents rarely operate with just one tool.

They typically have access to many capabilities:

- search tools
- database tools
- calculators
- CRM systems
- inventory systems
- weather APIs
- email systems

The challenge becomes:

> How does the LLM choose the correct tool?

This is where multi-tool agents come in.

---

## Key Idea

Single-tool agent:

```text
User
  ↓
LLM
  ↓
Calculator
```

Multi-tool agent:

```text
User
  ↓
LLM
  ↓
Choose Best Tool
  ↓
Execute Tool
  ↓
Answer
```

The model becomes responsible for tool selection.

---

## Enterprise Analogy

Imagine a customer support representative.

A customer asks:

```text
What is the status of order 1001?
```

The representative uses:

```text
Order Lookup System
```

Another customer asks:

```text
What is 250 × 18?
```

The representative uses:

```text
Calculator
```

Another customer asks:

```text
What products are available?
```

The representative uses:

```text
Inventory System
```

The same agent chooses different tools depending on the request.

A multi-tool LangGraph agent behaves exactly the same way.

---

## Lab Code

from typing import Annotated

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from langgraph.graph.message import (
    add_messages
)

from langgraph.prebuilt import ToolNode

from typing_extensions import TypedDict


# -------------------------
# Tool 1 - Calculator
# -------------------------

@tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    """
    return str(eval(expression))


# -------------------------
# Tool 2 - Inventory Lookup
# -------------------------

@tool
def inventory_lookup(product: str) -> str:
    """
    Lookup product availability.
    """

    inventory = {
        "laptop": "In Stock",
        "monitor": "Out of Stock",
        "keyboard": "Limited Stock"
    }

    return inventory.get(
        product.lower(),
        "Product Not Found"
    )


# -------------------------
# Tool 3 - Order Status
# -------------------------

@tool
def order_status(order_id: str) -> str:
    """
    Retrieve order status.
    """

    orders = {
        "1001": "Shipped",
        "1002": "Processing",
        "1003": "Delivered"
    }

    return orders.get(
        order_id,
        "Order Not Found"
    )


# -------------------------
# State
# -------------------------

class State(TypedDict):
    messages: Annotated[list, add_messages]


# -------------------------
# LLM
# -------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

tools = [
    calculator,
    inventory_lookup,
    order_status
]

llm_with_tools = llm.bind_tools(
    tools
)


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
# Tool Node
# -------------------------

tool_node = ToolNode(tools)


# -------------------------
# Router
# -------------------------

def route_tools(state: State):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "chatbot",
    chatbot
)

builder.add_node(
    "tools",
    tool_node
)

builder.add_edge(
    START,
    "chatbot"
)

builder.add_conditional_edges(
    "chatbot",
    route_tools
)

builder.add_edge(
    "tools",
    "chatbot"
)

graph = builder.compile()


# -------------------------
# Example Queries
# -------------------------

queries = [
    "What is 25 * 18?",
    "Is laptop available?",
    "What is the status of order 1001?"
]

for query in queries:

    print(f"\nUSER: {query}")

    result = graph.invoke(
        {
            "messages": [
                ("user", query)
            ]
        }
    )

    print(
        "AI:",
        result["messages"][-1].content
    )


---

## Example Output

```python
USER: What is 25 * 18?

AI: 25 multiplied by 18 equals 450.

USER: Is laptop available?

AI: The laptop is currently in stock.

USER: What is the status of order 1001?

AI: Order 1001 has been shipped.
```

---

## Explanation

## What Is a Multi-Tool Agent?

A multi-tool agent is an agent that can access:

```text
Multiple tools
```

rather than:

```text
A single tool
```

The LLM decides which tool best matches the user's request.

---

## Step 1 — Create Multiple Tools

We define three tools:

### Calculator

```python
@tool
def calculator(...)
```

Handles:

```text
Math calculations
```

---

### Inventory Lookup

```python
@tool
def inventory_lookup(...)
```

Handles:

```text
Product availability
```

---

### Order Status

```python
@tool
def order_status(...)
```

Handles:

```text
Order tracking
```

Each tool specializes in a different capability.

---

## Step 2 — Register All Tools

Instead of:

```python
tools = [calculator]
```

we use:

```python
tools = [
    calculator,
    inventory_lookup,
    order_status
]
```

The model now sees multiple available actions.

---

## Step 3 — Bind Tools to the Model

```python
llm_with_tools = llm.bind_tools(
    tools
)
```

The LLM receives:

```text
Tool: calculator
Tool: inventory_lookup
Tool: order_status
```

along with their descriptions.

These descriptions help guide tool selection.

---

## Step 4 — LLM Chooses a Tool

For:

```text
What is 25 * 18?
```

the model selects:

```text
calculator
```

---

For:

```text
Is laptop available?
```

the model selects:

```text
inventory_lookup
```

---

For:

```text
What is the status of order 1001?
```

the model selects:

```text
order_status
```

The routing logic does not choose the tool.

The model does.

---

## Step 5 — ToolNode Executes the Correct Tool

The built-in ToolNode examines:

```python
last_message.tool_calls
```

and automatically executes:

```text
calculator
```

or

```text
inventory_lookup
```

or

```text
order_status
```

depending on the generated tool call.

No manual dispatch logic is required.

---

## Execution Flow

```text
User Question
       │
       ▼
   Chatbot
       │
       ▼
Tool Call Generated
       │
       ▼
   ToolNode
       │
       ▼
Correct Tool Executes
       │
       ▼
Tool Result
       │
       ▼
   Chatbot
       │
       ▼
 Final Answer
```

---

## Why Tool Descriptions Matter

The model does not understand tools magically.

It relies heavily on:

```python
"""
Retrieve order status.
"""
```

and

```python
"""
Lookup product availability.
"""
```

Poor descriptions can lead to poor tool selection.

---

### Bad Example

```python
"""
Gets data.
"""
```

The model learns almost nothing.

---

### Better Example

```python
"""
Retrieve shipping status
for customer orders.
"""
```

The purpose is clear.

---

## Multiple Tools, Same Agent

A single agent can expose:

```text
Calculator
Search
Database
CRM
Weather API
Email Service
Inventory System
```

and dynamically choose among them.

This is one of the key strengths of agent architectures.

---

## Tool Selection Process

Internally, the model performs reasoning similar to:

```text
User wants order information.
```

↓

```text
Available tools:
- calculator
- inventory_lookup
- order_status
```

↓

```text
order_status seems most relevant.
```

↓

```text
Generate tool call.
```

---

## Common Mistakes

### 1. Overlapping Tool Descriptions

Bad:

```python
Tool A:
"Gets information"

Tool B:
"Gets information"
```

The model struggles to distinguish them.

---

Good:

```python
Tool A:
"Retrieve inventory availability"

Tool B:
"Retrieve order shipment status"
```

Clear separation of responsibility.

---

### 2. Too Many Unrelated Tools

Giving an agent dozens of poorly defined tools often reduces accuracy.

Prefer:

```text
Focused tool sets
```

whenever possible.

---

### 3. Manually Choosing Tools

Bad:

```python
if "order" in query:
```

This bypasses agent reasoning.

---

Better:

```text
Allow the model to decide.
```

This is the essence of tool-calling agents.

---

## Mental Model

Think of a multi-tool agent as:

```text
Specialist Dispatcher
```

The LLM receives a request and decides:

```text
Which specialist should handle this?
```

The chosen tool performs the action.

The result returns to the LLM.

The LLM then explains the outcome to the user.

---

## Architecture

```text
                ┌──────────────┐
                │     User     │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │     LLM      │
                └──────┬───────┘
                       │
              Tool Selection
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
 Calculator     Inventory Tool   Order Tool
       │               │               │
       └───────────────┼───────────────┘
                       │
                       ▼
                Tool Result
                       │
                       ▼
                ┌──────────────┐
                │     LLM      │
                └──────┬───────┘
                       │
                       ▼
                 Final Answer
```

---

## Key Takeaways

- Multi-tool agents can access several tools simultaneously.
- The LLM decides which tool should be used.
- Tool descriptions play a critical role in tool selection.
- `ToolNode` automatically executes the requested tool.
- The same ReAct architecture scales naturally from one tool to many tools.
- Multi-tool agents are the foundation of enterprise AI assistants and workflow automation systems.
- In the next lab, we will learn how to handle tool failures and build robust error recovery mechanisms for production-grade agents.