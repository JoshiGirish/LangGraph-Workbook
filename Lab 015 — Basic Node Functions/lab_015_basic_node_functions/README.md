# Lab 015 — Basic Node Functions

## Lab Intro

In LangGraph, everything revolves around **nodes**.

A node is simply a Python function that:

- receives the current state
- performs some computation
- returns a partial state update

This makes nodes the fundamental building blocks of any workflow.

In this lab, we focus on the simplest possible nodes and how they transform state step-by-step in a linear graph.

Workflow:

```text
START
   |
add_user
   |
process_user
   |
END
```

---

## Lab Code

```python
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph import START, END


# State definition
class State(TypedDict, total=False):
    name: str
    greeting: str
    processed: bool


# Node 1 — add user
def add_user(state: State):
    return {
        "name": "Alice"
    }


# Node 2 — process user
def process_user(state: State):
    return {
        "greeting": f"Hello {state['name']}",
        "processed": True
    }


# Build graph
builder = StateGraph(State)

builder.add_node("add_user", add_user)
builder.add_node("process_user", process_user)

builder.add_edge(START, "add_user")
builder.add_edge("add_user", "process_user")
builder.add_edge("process_user", END)

graph = builder.compile()


# Execute graph
result = graph.invoke({})

print(result)
```

Expected Output:

```python
{
    "name": "Alice",
    "greeting": "Hello Alice",
    "processed": True
}
```

---

## Explanation

### What Is a Node?

A node is a function that transforms state:

```python
def node(state):
    return updated_state
```

It does three things:

1. Reads current state
2. Computes new values
3. Returns updates

LangGraph automatically merges these updates into the global state.

---

## Step 1 — add_user Node

```python
def add_user(state):
    return {
        "name": "Alice"
    }
```

This node initializes user data.

Even though input state is empty:

```python
{}
```

It outputs:

```python
{
    "name": "Alice"
}
```

This becomes part of the global state.

---

## Step 2 — process_user Node

```python
def process_user(state):
    return {
        "greeting": f"Hello {state['name']}",
        "processed": True
    }
```

This node depends on previous state:

- reads `name`
- creates a greeting
- marks processing as complete

Input state:

```python
{
    "name": "Alice"
}
```

Output update:

```python
{
    "greeting": "Hello Alice",
    "processed": True
}
```

---

## Step 3 — Graph Construction

```python
builder.add_node("add_user", add_user)
builder.add_node("process_user", process_user)

builder.add_edge(START, "add_user")
builder.add_edge("add_user", "process_user")
builder.add_edge("process_user", END)
```

Execution flow:

```text
START → add_user → process_user → END
```

Each node builds upon previous results.

---

## Step 4 — Execution Flow

Initial state:

```python
{}
```

After `add_user`:

```python
{
    "name": "Alice"
}
```

After `process_user`:

```python
{
    "name": "Alice",
    "greeting": "Hello Alice",
    "processed": True
}
```

Final state:

```python
{
    "name": "Alice",
    "greeting": "Hello Alice",
    "processed": True
}
```

---

## Why Basic Node Functions Matter

Nodes are the foundation of all LangGraph systems.

Every advanced concept builds on this:

- reducers
- memory systems
- tool calling
- multi-agent systems
- conditional routing

If you understand nodes, you understand LangGraph.

---

## Key Takeaways

- A node is a Python function that transforms state.
- Nodes receive full state and return partial updates.
- LangGraph merges node outputs into global state.
- Nodes can depend on previous node outputs.
- Every LangGraph system is built from nodes and edges.