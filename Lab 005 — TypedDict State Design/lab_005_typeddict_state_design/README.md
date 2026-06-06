# Lab 005 — TypedDict State Design

## Learning Objectives

By the end of this lab, you will:

- Understand why LangGraph uses state
- Define a state schema using `TypedDict`
- Create workflows that read and update state
- Understand the relationship between state and nodes

---

## Concept Overview

State is the central concept in LangGraph.

Every node:
- Receives the current state
- Performs some work
- Returns state updates

A state schema defines the structure of data that flows through the graph.

One of the simplest ways to define state is with `TypedDict`.

```python
from typing_extensions import TypedDict
class State(TypedDict):
    message: str
```

This tells LangGraph that the workflow state contains a field named `message`.

---

## Workflow Diagram

```text
START
|
greet
|
END
```

---

## Step 1 — Imports

```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph import START, END
```

---

## Step 2 — Define State

```python
class State(TypedDict):
    message: str
```

The state contains a single field:

```python
{
    "message": "Hello"
}
```

---

## Step 3 — Create a Node

```python
def greet(state: State):
    return {
        "message": f"Hello {state['message']}"
    }
```

The node receives the current state:

```python
{
    "message": "LangGraph"
}
```

and returns an updated state:

```python
{
    "message": "Hello LangGraph"
}
```

---

## Step 4 — Build the Graph

```python
builder = StateGraph(State)
builder.add_node("greet", greet)
builder.add_edge(START, "greet")
builder.add_edge("greet", END)
```

---

## Step 5 — Compile the Graph

```python
graph = builder.compile()
```

---

## Step 6 — Execute the Graph

```python
result = graph.invoke(
    {
        "message": "LangGraph"
    }
)
result
```

**Expected output:**

```python
{
    "message": "Hello LangGraph"
}
```

---

## Understanding the State Flow

### Initial State

```python
{
    "message": "LangGraph"
}
```

### Input to greet

```python
{
    "message": "LangGraph"
}
```

### Output from greet

```python
{
    "message": "Hello LangGraph"
}
```

### Final State

```python
{
    "message": "Hello LangGraph"
}
```

---

## Working with Multiple Fields

State can contain more than one field.

```python
class State(TypedDict):
    first_name: str
    last_name: str
```

Example input:

```python
{
    "first_name": "John",
    "last_name": "Doe"
}
```

Node:

```python
def build_name(state: State):
    return {
        "full_name": f"{state['first_name']} {state['last_name']}"
    }
```

As workflows grow, the state often contains many fields shared across nodes.

---

## Experiment

Extend the state schema:

```python
class State(TypedDict):
    name: str
    age: int
```

Create a node that generates a profile message.

Example output:

```python
{
    "profile": "John is 30 years old"
}
```

---

## Lab Challenge

Create a workflow with the following state:

```python
class State(TypedDict):
    product: str
    price: float
```

**Requirements:**
- Create a node that generates a summary.
- Build and compile the graph.
- Execute the workflow.
- Return a new field named `description`.

**Example:**

```python
{
    "description": "Laptop costs $1200"
}
```

---

## Key Takeaways

- State is the data shared between nodes.
- `TypedDict` defines the structure of state.
- Nodes receive state as input.
- Nodes return state updates.
- State evolves as the workflow executes.
- Well-designed state schemas make workflows easier to maintain.

---

## Next Lab

Lab 006 — Pydantic State Design
```