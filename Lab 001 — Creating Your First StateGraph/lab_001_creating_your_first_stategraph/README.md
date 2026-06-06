# Lab 001 — Creating Your First StateGraph

## Learning Objectives

By the end of this lab, you will:

- Understand what a LangGraph graph is
- Create your first minimal StateGraph
- Execute a linear workflow
- Observe how state flows between nodes

---

## Concept Overview

LangGraph is a framework for building **stateful graph-based workflows**.

At its core:

- **Nodes** = Python functions
- **Edges** = execution flow
- **State** = shared dictionary passed between nodes

This is the simplest possible graph:

```
START → node_hello → END
```

---

## Prerequisites

Install dependencies:

```bash
!pip install langgraph langchain-core
```

---

## Explanation

### 1. Define State

We define a minimal shared state:

- `message`: a string passed through nodes

Think of state as the **memory of the system**.

```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    message: str
```

### 2. Create a Node

- **Input**: current state
- **Output**: updated state
- We append text to demonstrate transformation

#### Important rule:
> Nodes must return partial or full state updates

```python
def node_hello(state: State) -> State:
    return {
        "message": state["message"] + " from LangGraph"
    }
```

### 3. Build the Graph

We define:

- One node
- One linear flow:
  - START → hello_node → END

This is the simplest LangGraph possible.

```python
builder = StateGraph(State)

builder.add_node("hello_node", node_hello)

builder.add_edge(START, "hello_node")
builder.add_edge("hello_node", END)
```

### 4. Compile Graph

**Compilation:**

- Validates structure
- Locks graph definition
- Prepares runtime engine

Think: "build step before execution"

```python
graph = builder.compile()
```

### 5. Run the Graph

```python
result = graph.invoke({
    "message": "Hello"
})
print(result)
```

**Expected output:**

```python
{
    "message": "Hello from LangGraph"
}
```

### 6. Understand Execution Flow

| Step | State |
|------|-------|
| Initial state | `{"message": "Hello"}` |
| After `node_hello` | `{"message": "Hello from LangGraph"}` |
| Final state | Same as above (no further transformations) |

---

## Key Concepts Learned

- A LangGraph is a **state transformation pipeline**
- Nodes are pure functions (input → output)
- State is passed and updated step-by-step
- Graph defines *control flow*, not logic inside nodes