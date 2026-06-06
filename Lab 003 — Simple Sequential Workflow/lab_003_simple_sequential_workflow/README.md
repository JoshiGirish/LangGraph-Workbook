"# Lab 003 — Simple Sequential Workflow

## Learning Objectives

By the end of this lab, you will:

- Build a workflow with multiple nodes
- Understand how state moves through a graph
- Learn how nodes execute in sequence
- Observe state transformations at each step

---

## Concept Overview

A sequential workflow executes nodes one after another.

Each node receives the current state, performs some work, and returns an updated state.

```text
START
   |
   v
node_a
   |
   v
node_b
   |
   v
node_c
   |
   v
END
```

The output of one node becomes the input of the next node.

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

Our workflow will progressively build a message.

```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    message: str
```

### 2. Create the Nodes

#### Node A

```python
def node_a(state: State):
    return {
        "message": state["message"] + " A"
    }
```

#### Node B

```python
def node_b(state: State):
    return {
        "message": state["message"] + " B"
    }
```

#### Node C

```python
def node_c(state: State):
    return {
        "message": state["message"] + " C"
    }
```

Each node appends text to the existing message.

### 3. Build the Graph

```python
builder = StateGraph(State)

builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_node("node_c", node_c)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", "node_c")
builder.add_edge("node_c", END)
```

### 4. Compile the Graph

```python
graph = builder.compile()
```

### 5. Execute the Graph

```python
result = graph.invoke(
    {
        "message": "Start"
    }
)
print(result)
```

**Expected output:**

```python
{
    "message": "Start A B C"
}
```

### 6. Understand State Flow

| Step | State |
|------|-------|
| Initial state | `{"message": "Start"}` |
| After `node_a` | `{"message": "Start A"}` |
| After `node_b` | `{"message": "Start A B"}` |
| After `node_c` | `{"message": "Start A B C"}` |
| Final state | `{"message": "Start A B C"}` |

---

## Streaming Execution

Instead of waiting for the final result, we can observe execution step-by-step.

```python
for step in graph.stream(
    {
        "message": "Start"
    }
):
    print(step)
```

**Example output:**

```python
{'node_a': {'message': 'Start A'}}
{'node_b': {'message': 'Start A B'}}
{'node_c': {'message': 'Start A B C'}}
```

---

## Lab Challenge

Create a workflow that builds a sentence.

**Example:**

```text
START
   |
greeting
   |
subject
   |
ending
   |
 END
```

**Expected output:**

```python
{
    "message": "Hello LangGraph!"
}
```

---

## Key Takeaways

- Sequential workflows execute nodes one after another.
- State flows through the graph from node to node.
- Each node can update the state.
- The output of one node becomes the input of the next node.
- Streaming allows you to observe execution as it happens.

---

## Experiment

Add a fourth node.

```text
START
   |
node_a
   |
node_b
   |
node_c
   |
node_d
   |
 END
```

**Example:**

```python
def node_d(state: State):
    return {
        "message": state["message"] + " D"
    }
```"