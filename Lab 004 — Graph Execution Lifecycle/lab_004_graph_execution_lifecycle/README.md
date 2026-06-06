"# Lab 004 — Graph Execution Lifecycle

## Learning Objectives

By the end of this lab, you will:

- Understand how a LangGraph workflow executes
- Learn the lifecycle of a graph invocation
- Observe how state changes as nodes execute
- Use streaming to inspect execution step-by-step

---

## Concept Overview

When a graph is executed, LangGraph follows a predictable lifecycle.

```text
Input State
     |
     v
START
     |
     v
Node Execution
     |
     v
State Updates
     |
     v
END
     |
     v
Final State
```

At each step:

1. The current state is passed to a node.
2. The node performs work.
3. The node returns state updates.
4. LangGraph merges the updates into the current state.
5. Execution moves to the next node.

---

## Workflow Diagram

```text
START
   |
node_a
   |
node_b
   |
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
    print("Executing node_a")

    return {
        "message": state["message"] + " A"
    }
```

#### Node B

```python
def node_b(state: State):
    print("Executing node_b")

    return {
        "message": state["message"] + " B"
    }
```

### 3. Build the Graph

```python
builder = StateGraph(State)

builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)
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

**Console output:**

```text
Executing node_a
Executing node_b
```

**Final state:**

```python
{
    "message": "Start A B"
}
```

### 6. Understand What Happened

#### Initial State

```python
{
    "message": "Start"
}
```

#### Execution Begins

LangGraph starts at:

```text
START
```

#### Execute node_a

**Input:**

```python
{
    "message": "Start"
}
```

**Output:**

```python
{
    "message": "Start A"
}
```

**Updated state:**

```python
{
    "message": "Start A"
}
```

#### Execute node_b

**Input:**

```python
{
    "message": "Start A"
}
```

**Output:**

```python
{
    "message": "Start A B"
}
```

**Updated state:**

```python
{
    "message": "Start A B"
}
```

#### Reach END

Execution terminates.

**Final state:**

```python
{
    "message": "Start A B"
}
```

---

## Streaming Execution

Instead of waiting for the final result, we can watch the graph execute step-by-step.

**Example output:**

```python
{
    "node_a": {
        "message": "Start A"
    }
}

{
    "node_b": {
        "message": "Start A B"
    }
}
```

```python
for event in graph.stream(
    {
        "message": "Start"
    }
):
    print(event)
```

**Streaming is useful for:**

- Debugging
- Monitoring execution
- Understanding workflow behavior

---

## Visualize the Workflow

```python
from IPython.display import Image, display

display(
    Image(
        graph.get_graph().draw_mermaid_png()
    )
)
```

**Expected structure:**

```text
START
   |
node_a
   |
node_b
   |
  END
```

---

## Key Takeaways

- Graph execution always starts at `START`.
- Nodes execute according to graph topology.
- Each node receives the current state.
- Nodes return state updates.
- LangGraph updates the state after every node execution.
- Execution ends when the workflow reaches `END`.
- Streaming allows you to observe execution as it happens.

---

## Understanding What Happened

### Initial State

```python
{
    "message": "Start"
}
```

### Execution Begins

LangGraph starts at:

```text
START
```

### Execute node_a

**Input:**

```python
{
    "message": "Start"
}
```

**Output:**

```python
{
    "message": "Start A"
}
```

**Updated state:**

```python
{
    "message": "Start A"
}
```

### Execute node_b

**Input:**

```python
{
    "message": "Start A"
}
```

**Output:**

```python
{
    "message": "Start A B"
}
```

**Updated state:**

```python
{
    "message": "Start A B"
}
```

### Reach END

Execution terminates.

**Final state:**

```python
{
    "message": "Start A B"
}
```"