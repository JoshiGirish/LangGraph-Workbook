# Lab 002 — Understanding START and END Nodes

## Learning Objectives

By the end of this lab, you will:

- Understand the purpose of `START`
- Understand the purpose of `END`
- Learn how execution begins and terminates in a LangGraph
- Build a minimal graph using both nodes

---

## Concept Overview

Every LangGraph workflow has two special nodes:

### START

`START` represents the entry point of a graph.

Execution always begins here.

### END

`END` represents the termination point of a graph.

Execution stops when the workflow reaches this node.

You do not implement these nodes yourself—they are provided by LangGraph.

---

## Workflow Diagram

```text
START
   |
   v
greet
   |
   v
END
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
def greet(state: State):
    return {
        "message": f"Hello {state['message']}"
    }
```

### 3. Build the Graph

We define:

- One node
- One linear flow:
  - START → greet → END

This is the simplest LangGraph with START and END nodes.

```python
builder = StateGraph(State)

builder.add_node("greet", greet)

builder.add_edge(START, "greet")
builder.add_edge("greet", END)
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
result = graph.invoke(
    {
        "message": "LangGraph"
    }
)
print(result)
```

**Expected output:**

```python
{
    'message': 'Hello LangGraph'
}
```

### 6. Understand Execution Flow

| Step | State |
|------|-------|
| Initial state | `{"message": "LangGraph"}` |
| After `greet` | `{"message": "Hello LangGraph"}` |
| Final state | Same as above (no further transformations) |

---

## Key Concepts Learned

- `START` is the **entry point** - execution always begins here
- `END` is the **exit point** - execution stops when reached
- START and END are **built-in** nodes provided by LangGraph
- The graph defines the **control flow** from START through nodes to END
- State flows through the graph, being transformed at each node

---

## Visualizing the Graph

Expected structure:

```text
START
   |
 greet
   |
  END
```

```python
from IPython.display import Image, display

display(
    Image(
        graph.get_graph().draw_mermaid_png()
    )
)
```