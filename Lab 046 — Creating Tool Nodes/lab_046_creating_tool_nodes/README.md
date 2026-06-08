# Lab 046 — Creating Tool Nodes

## Lab Intro

So far, our LangGraph workflows have consisted of nodes that directly execute Python functions.

However, modern AI agents often need access to external capabilities such as:

- calculators
- databases
- APIs
- search systems
- file operations

These external capabilities are called **tools**.

In LangGraph, tools are typically executed through specialized nodes known as:

> **Tool Nodes**

A Tool Node acts as the bridge between the graph and an external function.

---

## Key Idea

Regular node:

```text
State → Node → State Update
```

Tool node:

```text
State → Tool Call → Tool Result → State Update
```

The node's responsibility is no longer performing all work itself.

Instead:

```text
Node delegates work to a tool
```

---

## Enterprise Analogy

Imagine a customer service agent processing a refund request.

The agent may decide:

```text
"I need account information."
```

Instead of knowing everything directly, the agent calls:

```text
Customer Database Tool
```

The workflow becomes:

```text
Agent → Tool → Result → Continue
```

This is exactly how tool nodes operate inside agent systems.

---

## Lab Code

from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END


# -------------------------
# Tool
# -------------------------

def calculate_discount(price: float) -> float:
    """
    External business tool.
    """
    return price * 0.9


# -------------------------
# State
# -------------------------

class State(BaseModel):
    product_name: str
    original_price: float
    discounted_price: float | None = None


# -------------------------
# Tool Node
# -------------------------

def discount_tool_node(state: State):
    discounted = calculate_discount(
        state.original_price
    )

    return {
        "discounted_price": discounted
    }


# -------------------------
# Result Node
# -------------------------

def summarize(state: State):
    print(
        f"{state.product_name}: "
        f"{state.original_price} -> "
        f"{state.discounted_price}"
    )

    return {}


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "discount_tool",
    discount_tool_node
)

builder.add_node(
    "summarize",
    summarize
)

builder.add_edge(
    START,
    "discount_tool"
)

builder.add_edge(
    "discount_tool",
    "summarize"
)

builder.add_edge(
    "summarize",
    END
)

graph = builder.compile()


# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "product_name": "Laptop",
        "original_price": 1000
    }
)

print(result)

---

## Expected Output

```python
Laptop: 1000.0 -> 900.0

{
    'product_name': 'Laptop',
    'original_price': 1000.0,
    'discounted_price': 900.0
}
```

---

## Explanation

## What Is a Tool Node?

A tool node is simply a graph node whose primary purpose is:

```text
Call external functionality
```

Examples include:

- calculators
- APIs
- databases
- vector stores
- search engines
- file systems

Instead of embedding all logic inside the node:

```text
Node → Tool → Return Result
```

---

## Step 1 — Create a Tool

Our tool is a simple pricing function:

```python
def calculate_discount(price: float):
    return price * 0.9
```

Input:

```text
1000
```

Output:

```text
900
```

Although simple, this represents any external service.

---

## Step 2 — Create State

```python
class State(BaseModel):
    product_name: str
    original_price: float
    discounted_price: float | None = None
```

Initially:

```python
{
    "product_name": "Laptop",
    "original_price": 1000,
    "discounted_price": None
}
```

---

## Step 3 — Execute Tool Inside Node

```python
def discount_tool_node(state: State):
```

Call tool:

```python
discounted = calculate_discount(
    state.original_price
)
```

Store result:

```python
return {
    "discounted_price": discounted
}
```

The graph state is updated automatically.

---

## Step 4 — Consume Tool Output

The next node receives updated state:

```python
def summarize(state: State):
```

Now:

```python
state.discounted_price
```

contains:

```text
900.0
```

The tool result becomes part of graph memory.

---

## Execution Flow

```text
START
   │
   ▼
discount_tool
   │
   ▼
summarize
   │
   ▼
END
```

Detailed execution:

```text
Input State
      │
      ▼
Call Tool
      │
      ▼
Receive Result
      │
      ▼
Update State
      │
      ▼
Next Node
```

---

## Why Tool Nodes Matter

Tool nodes are the foundation of agent systems.

Without tools:

```text
LLM can only generate text
```

With tools:

```text
LLM can interact with systems
```

Examples:

```text
Agent → Search Tool
Agent → Database Tool
Agent → CRM Tool
Agent → Calculator Tool
Agent → Email Tool
```

This transforms an LLM from a chatbot into an actionable agent.

---

## Tool Nodes vs Regular Nodes

### Regular Node

```python
def node(state):
    # perform work directly
```

Everything happens inside the node.

---

### Tool Node

```python
def node(state):
    result = tool(...)
    return result
```

Work is delegated externally.

---

## Common Pattern

Many production systems follow:

```text
Agent
  ↓
Choose Tool
  ↓
Execute Tool
  ↓
Receive Result
  ↓
Continue Reasoning
```

This pattern powers:

- ReAct agents
- assistants
- workflow automation systems
- enterprise AI agents

---

## Common Mistakes

### 1. Mixing Tool Logic Into Node Logic

Bad:

```python
def node(state):
    # hundreds of lines of business logic
```

Better:

```python
def node(state):
    return tool(...)
```

Keep tools reusable.

---

### 2. Forgetting to Return State Updates

Bad:

```python
tool(...)
return {}
```

Result disappears.

---

Good:

```python
return {
    "discounted_price": value
}
```

---

### 3. Treating Tools as Graph Nodes

A tool is:

```text
Functionality
```

A node is:

```text
Execution step
```

A node may call one or many tools.

---

## Mental Model

Think of a Tool Node as:

```text
Graph Step
      │
      ▼
External Capability
      │
      ▼
Result Returned To State
```

The graph controls execution.

The tool performs specialized work.

---

## Key Takeaways

- Tool nodes allow LangGraph workflows to interact with external functionality.
- A tool can be a calculator, API, database, search system, or business service.
- Tool nodes typically call a tool and write the result back to state.
- Tools make agents capable of taking actions rather than only generating text.
- Tool nodes are the foundation for LLM-driven agents and ReAct workflows.
- In the next lab, we will connect tool nodes to LLM decision-making so models can decide when to use tools automatically.