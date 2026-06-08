# Lab 019 — Reusable Node Components

## Lab Intro

As workflows grow, you'll quickly notice that many nodes perform similar tasks:

- formatting text
- validating inputs
- enriching data
- generating summaries
- calling APIs

Copying and pasting node logic across graphs leads to:

- duplicated code
- inconsistent behavior
- maintenance challenges

A better approach is to build **reusable node components**.

Reusable nodes are designed to:

- be configurable
- work across multiple graphs
- encapsulate a single responsibility
- reduce duplication

In this lab, we'll create a reusable greeting node factory that can generate multiple node behaviors from the same implementation.

Workflow:

```text
START
   |
formal_greeting
   |
casual_greeting
   |
END
```

---

## Lab Code

```python
from typing import Optional

from pydantic import BaseModel

from langgraph.graph import StateGraph
from langgraph.graph import START, END


# -------------------------
# State Model
# -------------------------
class State(BaseModel):
    name: str
    greeting: Optional[str] = None


# -------------------------
# Reusable Node Factory
# -------------------------
def create_greeting_node(style: str):

    def greeting_node(state: State):

        if style == "formal":
            message = (
                f"Good day, {state.name}."
            )

        elif style == "casual":
            message = (
                f"Hey {state.name}!"
            )

        else:
            message = (
                f"Hello {state.name}"
            )

        return {
            "greeting": message
        }

    return greeting_node


# Create reusable node instances
formal_greeting = create_greeting_node(
    "formal"
)

casual_greeting = create_greeting_node(
    "casual"
)


# -------------------------
# Build Graph
# -------------------------
builder = StateGraph(State)

builder.add_node(
    "formal_greeting",
    formal_greeting
)

builder.add_node(
    "casual_greeting",
    casual_greeting
)

builder.add_edge(
    START,
    "formal_greeting"
)

builder.add_edge(
    "formal_greeting",
    "casual_greeting"
)

builder.add_edge(
    "casual_greeting",
    END
)

graph = builder.compile()


# -------------------------
# Execute Graph
# -------------------------
result = graph.invoke(
    {
        "name": "Alice"
    }
)

print(result)
```

Expected Output:

```python
{
    'name': 'Alice',
    'greeting': 'Hey Alice!'
}
```

---

## Explanation

### What Is a Reusable Node Component?

Instead of writing:

```python
def node_a(...):
```

```python
def node_b(...):
```

```python
def node_c(...):
```

with nearly identical logic, we create a single reusable implementation:

```python
create_greeting_node(...)
```

that generates multiple node instances.

This follows the same principles used in software engineering:

- abstraction
- modularity
- reusability

---

## Step 1 — Define the State

```python
class State(BaseModel):
    name: str
    greeting: Optional[str] = None
```

Our workflow stores:

- user name
- generated greeting

---

## Step 2 — Create a Node Factory

```python
def create_greeting_node(style: str):
```

This is not a node itself.

Instead, it returns a node.

Think of it as:

```text
Node Generator
      ↓
Creates Actual Nodes
```

---

## Step 3 — Generate Dynamic Behavior

Inside the factory:

```python
if style == "formal":
```

returns:

```python
Good day, Alice.
```

---

```python
elif style == "casual":
```

returns:

```python
Hey Alice!
```

---

This allows one implementation to support many behaviors.

---

## Step 4 — Create Node Instances

```python
formal_greeting = create_greeting_node(
    "formal"
)
```

Creates:

```text
Formal Greeting Node
```

---

```python
casual_greeting = create_greeting_node(
    "casual"
)
```

Creates:

```text
Casual Greeting Node
```

Both use identical code internally.

---

## Step 5 — Register Nodes

```python
builder.add_node(
    "formal_greeting",
    formal_greeting
)

builder.add_node(
    "casual_greeting",
    casual_greeting
)
```

LangGraph treats them as completely separate nodes.

---

## Step 6 — Execution Flow

```text
START
   ↓
formal_greeting
   ↓
casual_greeting
   ↓
END
```

---

### Initial State

```python
{
    "name": "Alice"
}
```

---

### After formal_greeting

```python
{
    "name": "Alice",
    "greeting": "Good day, Alice."
}
```

---

### After casual_greeting

```python
{
    "name": "Alice",
    "greeting": "Hey Alice!"
}
```

The second node overwrites the greeting.

---

### Final State

```python
{
    "name": "Alice",
    "greeting": "Hey Alice!"
}
```

---

## Real-World Reusable Node Patterns

### Validation Nodes

```python
create_validation_node(...)
```

Examples:

- email validation
- age validation
- schema validation

---

### API Nodes

```python
create_api_node(...)
```

Examples:

- CRM integration
- Payment systems
- Search services

---

### LLM Nodes

```python
create_llm_node(...)
```

Examples:

- summarizer
- classifier
- reviewer

---

### Logging Nodes

```python
create_logger(...)
```

Reusable across many workflows.

---

### Tool Nodes

```python
create_tool_node(...)
```

Used heavily in agent systems.

---

## Why Reusable Nodes Matter

Without reusable nodes:

```text
Many Nodes
↓
Duplicated Logic
↓
Maintenance Problems
```

With reusable nodes:

```text
Shared Component
↓
Multiple Node Instances
↓
Consistent Behavior
```

This becomes increasingly important as graphs grow into:

- multi-agent systems
- enterprise workflows
- production applications

---

## Key Takeaways

- Reusable node components reduce code duplication.
- Node factories can generate multiple node behaviors from one implementation.
- Reusable nodes improve maintainability and consistency.
- LangGraph nodes are just Python functions, making them easy to abstract.
- Reusability becomes increasingly valuable in large workflows.
- Production systems often contain libraries of reusable node components.