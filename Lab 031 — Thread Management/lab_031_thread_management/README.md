# Lab 031 — Thread Management

## Lab Intro

In Lab 030, we introduced checkpointing using:

```text
InMemorySaver + thread_id
```

Now we go deeper into a core production concept:

> **Thread Management**

A thread in LangGraph represents a **single isolated execution timeline** with its own:

- state history
- checkpoints
- execution progress
- memory context

Think of it as:

```text
One workflow instance = One thread
```

---

## Key Idea

Without threads:

```text
All executions share state ❌
```

With threads:

```text
Each workflow has isolated memory ✔
```

---

## Enterprise Analogy

Imagine a banking system:

- Customer A applies for a loan
- Customer B applies for a loan

If both share the same thread:

```text
Data leaks between customers ❌
```

With threads:

```text
Customer A → thread A
Customer B → thread B
```

Each process is isolated and safe.

---

## Lab Code

from typing import Optional
from pydantic import BaseModel

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


# -------------------------
# State Model
# -------------------------

class State(BaseModel):
    user_id: str
    stage: Optional[str] = None
    visits: int = 0


# -------------------------
# Node — Track User Progress
# -------------------------

def track_progress(state: State):
    return {
        "stage": "tracked",
        "visits": state.visits + 1
    }


# -------------------------
# Node — Process Request
# -------------------------

def process_request(state: State):
    return {
        "stage": "processed"
    }


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node("track_progress", track_progress)
builder.add_node("process_request", process_request)

builder.add_edge(START, "track_progress")
builder.add_edge("track_progress", "process_request")
builder.add_edge("process_request", END)


# -------------------------
# Checkpointer
# -------------------------

checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)


# -------------------------
# Run Thread A
# -------------------------

config_a = {
    "configurable": {
        "thread_id": "user-A"
    }
}

print("RUN — Thread A")

result_a1 = graph.invoke(
    {
        "user_id": "A"
    },
    config=config_a
)

print(result_a1)


# -------------------------
# Run Thread B
# -------------------------

config_b = {
    "configurable": {
        "thread_id": "user-B"
    }
}

print("\nRUN — Thread B")

result_b1 = graph.invoke(
    {
        "user_id": "B"
    },
    config=config_b
)

print(result_b1)


# -------------------------
# Resume Thread A (same thread)
# -------------------------

print("\nRESUME — Thread A")

result_a2 = graph.invoke(
    result_a1,
    config=config_a
)

print(result_a2)

---

## Expected Output

```python
RUN — Thread A

{
    'user_id': 'A',
    'stage': 'processed',
    'visits': 1
}

RUN — Thread B

{
    'user_id': 'B',
    'stage': 'processed',
    'visits': 1
}

RESUME — Thread A

{
    'user_id': 'A',
    'stage': 'processed',
    'visits': 1
}
```

---

## Explanation

## What Is a Thread?

A thread is:

> a unique execution context for a graph run

It contains:

- state history
- checkpoints
- execution position
- memory isolation boundary

---

## Step 1 — Why Threads Matter

We define two users:

```text
user-A → thread A
user-B → thread B
```

Each has:

- separate state
- separate checkpoint history
- no shared memory

---

## Step 2 — Thread Isolation

### Thread A

```python
thread_id = "user-A"
```

Tracks:

```text
visits = 1
stage = processed
```

---

### Thread B

```python
thread_id = "user-B"
```

Tracks independently:

```text
visits = 1
stage = processed
```

No interference occurs.

---

## Step 3 — State Accumulation Per Thread

Each thread maintains its own:

```python
visits += 1
```

This means:

```text
Thread A counter ≠ Thread B counter
```

---

## Step 4 — Resume Execution

When we rerun:

```python
graph.invoke(result_a1, config=config_a)
```

LangGraph:

1. looks up thread_id
2. loads latest checkpoint
3. resumes execution state
4. continues safely

No reset occurs.

---

## Why Thread Management Matters

### 1. Multi-user systems

Each user gets isolated workflow execution.

---

### 2. SaaS applications

Example:

```text
1000 users → 1000 threads
```

No data leakage.

---

### 3. Agent systems

Each agent conversation:

```text
one thread per conversation
```

---

### 4. Debugging

You can inspect:

```text
thread-A vs thread-B execution paths
```

---

## Mental Model

Without threads:

```text
Single global execution context ❌
```

With threads:

```text
Many isolated timelines ✔
```

Each thread is a:

```text
mini execution universe
```

---

## Common Mistakes

### 1. Reusing thread_id incorrectly

Bad:

```python
same thread_id for all users
```

Result:

```text
state collision ❌
```

---

### 2. Expecting cross-thread sharing

Threads are:

```text
isolated by design
```

---

### 3. Ignoring thread lifecycle

In-memory threads:

```text
lost when process restarts
```

(persistent storage comes later)

---

## Thread vs Checkpoint

### Thread

```text
Identity container for execution
```

---

### Checkpoint

```text
Saved state snapshot inside a thread
```

Relationship:

```text
Thread → contains checkpoints
```

---

## Key Takeaways

- A thread represents an isolated execution instance in LangGraph.
- Each thread has its own checkpoint history and state.
- `thread_id` is required to separate workflows.
- Threads enable multi-user, multi-session systems safely.
- Thread management is foundational for production-grade LangGraph applications.