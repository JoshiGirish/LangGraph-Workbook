# Lab 007 — State Updates Between Nodes

## Learning Objectives

By the end of this lab, you will:

- Understand how nodes modify graph state
- Learn how state is passed between nodes
- Observe state evolution during graph execution
- Build a multi-step workflow that updates shared state

---

## Concept Overview

LangGraph workflows revolve around a shared state object.

Each node:

1. Receives the current state
2. Performs some work
3. Returns state updates

The graph automatically merges these updates into the shared state and passes the updated state to the next node.

```text
State
  ↓
Node A
  ↓
Updated State
  ↓
Node B
  ↓
Updated State
```

This pattern allows nodes to collaborate through a common state model.

---

## Workflow Diagram

```text
START
   |
collect_name
   |
create_greeting
   |
END
```

---

## State Evolution

Initial state:

```python
{
    "name": "Alice"
}
```

After first node:

```python
{
    "name": "Alice",
    "processed": True
}
```

After second node:

```python
{
    "name": "Alice",
    "processed": True,
    "greeting": "Hello Alice"
}
```

---

## Step 1 — Imports

```python
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph import START, END
```

### Explanation

We import:

- `TypedDict` to define the shared graph state
- `StateGraph` to create the workflow
- `START` and `END` to define execution boundaries

---

## Step 2 — Define State

```python
class State(TypedDict, total=False):
    name: str
    processed: bool
    greeting: str
```

### Discussion

The state begins with only a `name` field.

Additional fields such as:

- `processed`
- `greeting`

will be added by nodes during execution.

Using `total=False` allows fields to be added gradually as the workflow progresses.

---

## Step 3 — Create Node 1

```python
def collect_name(state: State):
    print("Node 1 received:", state)

    return {
        "processed": True
    }
```

### Discussion

This node receives the current state and adds a new field.

Input:

```python
{
    "name": "Alice"
}
```

Output:

```python
{
    "processed": True
}
```

LangGraph automatically merges this update into the existing state.

---

## Step 4 — Create Node 2

```python
def create_greeting(state: State):
    print("Node 2 received:", state)

    return {
        "greeting": f"Hello {state['name']}"
    }
```

### Discussion

This node uses data stored in state and creates a greeting.

Input:

```python
{
    "name": "Alice",
    "processed": True
}
```

Output:

```python
{
    "greeting": "Hello Alice"
}
```

The greeting is merged into the shared state.

---

## Step 5 — Build the Graph

```python
builder = StateGraph(State)

builder.add_node(
    "collect_name",
    collect_name
)

builder.add_node(
    "create_greeting",
    create_greeting
)

builder.add_edge(
    START,
    "collect_name"
)

builder.add_edge(
    "collect_name",
    "create_greeting"
)

builder.add_edge(
    "create_greeting",
    END
)
```

### Discussion

The graph executes sequentially:

```text
START
   ↓
collect_name
   ↓
create_greeting
   ↓
END
```

Each node receives the latest version of the state.

---

## Step 6 — Compile the Graph

```python
graph = builder.compile()
```

### Discussion

Compilation validates:

- State schema
- Node registrations
- Graph connectivity
- Execution flow

The resulting graph is ready for execution.

---

## Step 7 — Execute the Graph

```python
result = graph.invoke(
    {
        "name": "Alice"
    }
)

print(result)
```

---

## Expected Output

```python
{
    "name": "Alice",
    "processed": True,
    "greeting": "Hello Alice"
}
```

---

## Understanding State Merging

Node 1 returns:

```python
{
    "processed": True
}
```

LangGraph merges:

```python
{
    "name": "Alice"
}
```

with:

```python
{
    "processed": True
}
```

Result:

```python
{
    "name": "Alice",
    "processed": True
}
```

---

Node 2 returns:

```python
{
    "greeting": "Hello Alice"
}
```

Merged state becomes:

```python
{
    "name": "Alice",
    "processed": True,
    "greeting": "Hello Alice"
}
```

---

## Internal State Walkthrough

### Initial State

```python
{
    "name": "Alice"
}
```

---

### After collect_name

```python
{
    "name": "Alice",
    "processed": True
}
```

---

### After create_greeting

```python
{
    "name": "Alice",
    "processed": True,
    "greeting": "Hello Alice"
}
```

---

### Final State

```python
{
    "name": "Alice",
    "processed": True,
    "greeting": "Hello Alice"
}
```

---

## Updating Existing Fields

Nodes can overwrite existing values.

Example:

```python
def update_name(state):
    return {
        "name": state["name"].upper()
    }
```

Input:

```python
{
    "name": "Alice"
}
```

Output:

```python
{
    "name": "ALICE"
}
```

Final state:

```python
{
    "name": "ALICE"
}
```

When a node returns a value for an existing field, the new value replaces the previous one.

---

## Key Takeaways

- Nodes receive the current graph state.
- Nodes return partial state updates.
- LangGraph automatically merges updates into the shared state.
- Later nodes can use data created by earlier nodes.
- Fields can be added gradually as the workflow executes.
- Understanding state evolution is fundamental to building larger LangGraph applications.