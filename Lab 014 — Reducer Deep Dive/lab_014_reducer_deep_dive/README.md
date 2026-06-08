# Lab 014 — Reducer Deep Dive

## Lab Intro

In earlier labs, we learned that reducers control how LangGraph merges updates to the same state field.

We used simple reducers like `add`, but real systems require a deeper understanding of:

- how multiple nodes update the same field
- how order of execution affects results
- how custom reducer logic is implemented
- how reducers behave in real-world workflows like logs, counters, and message streams

In this lab, we build a small event tracking system and implement multiple reducer strategies to understand state merging at a deeper level.

Workflow:

```text
START
   |
event_1
   |
event_2
   |
event_3
   |
END
```

---

## Lab Code

```python
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph import START, END


# Custom reducer: keeps last value (overwrite behavior)
def last_value(current, new):
    return new


# Custom reducer: keeps both values as a formatted log string
def log_append(current, new):
    if not current:
        return new
    return current + " | " + new


# State with multiple reducer strategies
class State(TypedDict):
    counter: Annotated[int, lambda x, y: x + y]
    status: Annotated[str, last_value]
    logs: Annotated[str, log_append]


# Node 1
def event_1(state: State):
    return {
        "counter": 1,
        "status": "event_1",
        "logs": "E1 started"
    }


# Node 2
def event_2(state: State):
    return {
        "counter": 2,
        "status": "event_2",
        "logs": "E2 processed"
    }


# Node 3
def event_3(state: State):
    return {
        "counter": 3,
        "status": "event_3",
        "logs": "E3 completed"
    }


# Build graph
builder = StateGraph(State)

builder.add_node("event_1", event_1)
builder.add_node("event_2", event_2)
builder.add_node("event_3", event_3)

builder.add_edge(START, "event_1")
builder.add_edge("event_1", "event_2")
builder.add_edge("event_2", "event_3")
builder.add_edge("event_3", END)

graph = builder.compile()


# Execute graph
result = graph.invoke({})

print(result)
```

Expected Output (approx):

```python
{
    'counter': 6,
    'status': 'event_3',
    'logs': 'E1 started | E2 processed | E3 completed'
}
```

---

## Explanation

### What Is Happening in This Lab?

This lab demonstrates **three different reducer behaviors at the same time**:

| Field   | Reducer Type        | Behavior |
|--------|---------------------|----------|
| counter | sum reducer         | adds values |
| status  | last_value reducer  | overwrites |
| logs    | log_append reducer  | accumulates text |

This mirrors real production systems where different fields require different merge strategies.

---

## Step 1 — Custom Reducers

### Overwrite Reducer

```python
def last_value(current, new):
    return new
```

This ensures only the latest value is stored.

Used for:

- status fields
- flags
- classifications

---

### Log Append Reducer

```python
def log_append(current, new):
    if not current:
        return new
    return current + " | " + new
```

This builds a continuous log history.

Used for:

- debugging trails
- audit logs
- execution traces

---

### Built-in Sum Reducer

```python
lambda x, y: x + y
```

Used for numeric accumulation.

---

## Step 2 — State Design

```python
class State(TypedDict):
    counter: Annotated[int, lambda x, y: x + y]
    status: Annotated[str, last_value]
    logs: Annotated[str, log_append]
```

This shows that:

- each field can have its own reducer
- reducers define merging behavior per field
- state is no longer "flat replacement", but "merge-aware"

---

## Step 3 — Event Nodes

Each node contributes partial updates:

### event_1

```python
{
    "counter": 1,
    "status": "event_1",
    "logs": "E1 started"
}
```

### event_2

```python
{
    "counter": 2,
    "status": "event_2",
    "logs": "E2 processed"
}
```

### event_3

```python
{
    "counter": 3,
    "status": "event_3",
    "logs": "E3 completed"
}
```

---

## Step 4 — Reducer Behavior in Action

### Counter (Sum Reducer)

```
1 + 2 + 3 = 6
```

Final:

```python
6
```

---

### Status (Overwrite Reducer)

Each update replaces the previous value:

```
event_1 → event_2 → event_3
```

Final:

```python
"event_3"
```

---

### Logs (Append Reducer)

```
E1 started
  |
E2 processed
  |
E3 completed
```

Final:

```python
"E1 started | E2 processed | E3 completed"
```

---

## Step 5 — Graph Flow

```text
START
   ↓
event_1
   ↓
event_2
   ↓
event_3
   ↓
END
```

Each node contributes updates to the same shared state, but merging depends on reducer logic.

---

## State Evolution

### Initial State

```python
{}
```

---

### After event_1

```python
{
    "counter": 1,
    "status": "event_1",
    "logs": "E1 started"
}
```

---

### After event_2

```python
{
    "counter": 3,
    "status": "event_2",
    "logs": "E1 started | E2 processed"
}
```

---

### After event_3

```python
{
    "counter": 6,
    "status": "event_3",
    "logs": "E1 started | E2 processed | E3 completed"
}
```

---

## Why This Matters

Reducers are essential for:

### 1. Multi-Agent Systems
Multiple agents writing to shared memory

### 2. Parallel Execution
Multiple branches updating same state fields

### 3. Logging & Auditing
Maintaining execution history

### 4. Aggregation Pipelines
Summarizing distributed outputs

### 5. Production Reliability
Preventing accidental overwrites

---

## Key Takeaways

- Each state field can have its own reducer logic.
- Reducers define how updates are merged, not replaced.
- Different fields require different merging strategies.
- Logs, counters, and status fields behave differently by design.
- Understanding reducers is critical for parallel and multi-agent workflows.
- LangGraph state is fundamentally a **merge system**, not a simple dictionary.