# Lab 012 — State Snapshots

## Lab Intro

As LangGraph workflows become more complex, debugging and understanding execution is no longer just about seeing the final output.

We often need to inspect the **state at different points in time**, not just at the end.

This is where **state snapshots** become useful.

A state snapshot is a captured version of the graph state at a specific point during execution. It allows us to:

- Inspect intermediate results
- Debug unexpected behavior
- Replay execution logic mentally
- Understand how data evolves over time

In this lab, we simulate snapshots by capturing state after each node execution using streaming.

Workflow:

```text
START
   |
step_1
   |
step_2
   |
step_3
   |
END
```

---

## Lab Code

```python
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph import START, END


# State Definition
class State(TypedDict, total=False):
    value: int
    history: list[str]


# Step 1
def step_1(state: State):
    new_value = state.get("value", 0) + 1

    return {
        "value": new_value,
        "history": ["step_1 executed"]
    }


# Step 2
def step_2(state: State):
    new_value = state["value"] * 2

    return {
        "value": new_value,
        "history": ["step_2 executed"]
    }


# Step 3
def step_3(state: State):
    new_value = state["value"] + 10

    return {
        "value": new_value,
        "history": ["step_3 executed"]
    }


# Build Graph
builder = StateGraph(State)

builder.add_node("step_1", step_1)
builder.add_node("step_2", step_2)
builder.add_node("step_3", step_3)

builder.add_edge(START, "step_1")
builder.add_edge("step_1", "step_2")
builder.add_edge("step_2", "step_3")
builder.add_edge("step_3", END)

graph = builder.compile()


# Execute with snapshots
snapshots = []

for event in graph.stream({"value": 1}):
    snapshots.append(event)
    print("SNAPSHOT:", event)

print("\nFINAL STATE")
print(snapshots[-1])
```

Expected Output (approx):

```python
SNAPSHOT: {'step_1': {'value': 2, 'history': ['step_1 executed']}}
SNAPSHOT: {'step_2': {'value': 4, 'history': ['step_2 executed']}}
SNAPSHOT: {'step_3': {'value': 14, 'history': ['step_3 executed']}}

FINAL STATE
{'step_3': {'value': 14, 'history': ['step_3 executed']}}
```

---

## Explanation

### What Is a State Snapshot?

A state snapshot is a record of the graph state at a specific moment during execution.

Instead of only seeing:

```python
FINAL OUTPUT
```

we can observe:

```text
Step-by-step state evolution
```

This is especially useful for debugging and understanding complex workflows.

---

## Step 1 — State Design

```python
class State(TypedDict, total=False):
    value: int
    history: list[str]
```

We track:

- `value`: numeric computation result
- `history`: trace of executed steps

---

## Step 2 — Step Nodes

Each node modifies the state in a predictable way.

### Step 1

```python
def step_1(state):
    return {
        "value": state.get("value", 0) + 1,
        "history": ["step_1 executed"]
    }
```

Transforms:

```python
1 → 2
```

---

### Step 2

```python
def step_2(state):
    return {
        "value": state["value"] * 2,
        "history": ["step_2 executed"]
    }
```

Transforms:

```python
2 → 4
```

---

### Step 3

```python
def step_3(state):
    return {
        "value": state["value"] + 10,
        "history": ["step_3 executed"]
    }
```

Transforms:

```python
4 → 14
```

---

## Step 3 — Graph Construction

```python
builder = StateGraph(State)

builder.add_node("step_1", step_1)
builder.add_node("step_2", step_2)
builder.add_node("step_3", step_3)

builder.add_edge(START, "step_1")
builder.add_edge("step_1", "step_2")
builder.add_edge("step_2", "step_3")
builder.add_edge("step_3", END)
```

Execution flow:

```text
START → step_1 → step_2 → step_3 → END
```

---

## Step 4 — Capturing Snapshots

```python
snapshots = []

for event in graph.stream({"value": 1}):
    snapshots.append(event)
    print("SNAPSHOT:", event)
```

Each `event` represents a **state snapshot after a node execution**.

This gives us visibility into intermediate states.

---

## State Snapshots (Conceptual View)

### Snapshot 1 (after step_1)

```python
{
    "step_1": {
        "value": 2,
        "history": ["step_1 executed"]
    }
}
```

---

### Snapshot 2 (after step_2)

```python
{
    "step_2": {
        "value": 4,
        "history": ["step_2 executed"]
    }
}
```

---

### Snapshot 3 (after step_3)

```python
{
    "step_3": {
        "value": 14,
        "history": ["step_3 executed"]
    }
}
```

---

## Step 5 — Final Snapshot

```python
print(snapshots[-1])
```

This gives the final execution state:

```python
{
    "step_3": {
        "value": 14,
        "history": ["step_3 executed"]
    }
}
```

---

## Why Snapshots Matter

Snapshots help when:

- Debugging complex workflows
- Understanding parallel execution
- Inspecting intermediate transformations
- Validating multi-step reasoning
- Auditing agent decisions

Without snapshots, you only see the final result, which hides important internal behavior.

---

## Key Takeaways

- State snapshots capture intermediate execution results in LangGraph.
- `graph.stream()` allows observation of state after each step.
- Snapshots are essential for debugging complex workflows.
- Each snapshot reflects state changes at a specific execution point.
- Streaming execution provides visibility into graph behavior in real time.
- Snapshots are especially useful for multi-node and multi-agent systems.