# Lab 030 — Using InMemorySaver

## Lab Intro

In Lab 029, we introduced the concept of checkpointing:

```text
Graph execution + saved state snapshots = resumable workflows
```

Now we move from theory to implementation.

In LangGraph, checkpointing is enabled using a **checkpointer**.

The simplest one is:

> **InMemorySaver**

It stores checkpoints in memory during runtime, allowing:

- state persistence across steps
- thread-based execution
- replay within the same session
- debugging and inspection

---

## Key Idea

Without a checkpointer:

```text
graph.invoke() → run → forget state
```

With `InMemorySaver`:

```text
graph.invoke() → run → save checkpoint → resume/replay possible
```

---

## Enterprise Analogy

Think of a customer support workflow:

```text
User Ticket → Analyze → Route → Resolve
```

Without checkpointing:

```text
If system crashes → ticket processing restarts ❌
```

With `InMemorySaver`:

```text
Resume exactly where it stopped ✔
```

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
    ticket_id: str
    step: Optional[str] = None
    processed: bool = False


# -------------------------
# Node 1 — Analyze Ticket
# -------------------------

def analyze_ticket(state: State):
    return {
        "step": "analyzed"
    }


# -------------------------
# Node 2 — Process Ticket
# -------------------------

def process_ticket(state: State):
    return {
        "step": "processed",
        "processed": True
    }


# -------------------------
# Node 3 — Resolve Ticket
# -------------------------

def resolve_ticket(state: State):
    return {
        "step": "resolved"
    }


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node("analyze_ticket", analyze_ticket)
builder.add_node("process_ticket", process_ticket)
builder.add_node("resolve_ticket", resolve_ticket)

builder.add_edge(START, "analyze_ticket")
builder.add_edge("analyze_ticket", "process_ticket")
builder.add_edge("process_ticket", "resolve_ticket")
builder.add_edge("resolve_ticket", END)


# -------------------------
# Add Checkpointer
# -------------------------

checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)


# -------------------------
# Execute with Thread ID
# -------------------------

config = {
    "configurable": {
        "thread_id": "ticket-1001"
    }
}

print("RUN 1 — First execution")

result_1 = graph.invoke(
    {
        "ticket_id": "TICKET-1001"
    },
    config=config
)

print(result_1)


# -------------------------
# Simulate Resume (same thread)
# -------------------------

print("\nRUN 2 — Resume from checkpoint")

result_2 = graph.invoke(
    result_1,
    config=config
)

print(result_2)

---

## Expected Output

```python
RUN 1 — First execution

{
    'ticket_id': 'TICKET-1001',
    'step': 'resolved',
    'processed': True
}

RUN 2 — Resume from checkpoint

{
    'ticket_id': 'TICKET-1001',
    'step': 'resolved',
    'processed': True
}
```

---

## Explanation

## What is InMemorySaver?

`InMemorySaver` is a built-in LangGraph checkpointer that:

- stores checkpoints in RAM
- tracks state per thread
- enables resume and replay
- is ideal for development and testing

---

## Step 1 — Enable Checkpointing

We attach it at compile time:

```python
checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)
```

This activates:

```text
checkpoint saving on every node execution
```

---

## Step 2 — Thread ID (Critical Concept)

We pass:

```python
config = {
    "configurable": {
        "thread_id": "ticket-1001"
    }
}
```

This means:

```text
All checkpoints belong to this thread
```

Each thread acts like an isolated execution session.

---

## Step 3 — First Execution

```text
analyze_ticket → process_ticket → resolve_ticket
```

At each step:

- state is updated
- checkpoint is saved internally

Final state:

```python
step = "resolved"
processed = True
```

---

## Step 4 — Second Execution (Same Thread)

When we call:

```python
graph.invoke(result_1, config=config)
```

LangGraph:

- detects existing thread
- loads latest checkpoint
- continues from last known state

Result:

```text
No recomputation needed (already completed)
```

---

## Important Insight

Even though we call `invoke()` again:

```text
It does NOT restart the workflow
```

Instead:

```text
It resumes from checkpoint history
```

---

## Why This Matters

### 1. Fault tolerance

If execution crashes:

```text
resume instead of restarting
```

---

### 2. Long-running workflows

Useful for:

- document processing
- AI pipelines
- multi-step approvals

---

### 3. Debugging

You can inspect intermediate states per thread.

---

### 4. Multi-user isolation

Each `thread_id`:

```text
has its own independent memory
```

---

## Mental Model

Without checkpointer:

```text
Function execution → stateless
```

With InMemorySaver:

```text
Thread → checkpointed state history → resumable execution
```

---

## Common Mistakes

### 1. Forgetting thread_id

Bad:

```text
No isolation between runs
```

---

### 2. Assuming persistence beyond runtime

`InMemorySaver`:

```text
❌ lost when program exits
```

(We will fix this in later labs)

---

### 3. Treating it as database

It is:

```text
runtime memory only
```

not persistent storage.

---

## Key Takeaways

- `InMemorySaver` enables checkpointing in LangGraph.
- It stores execution state in memory per thread.
- `thread_id` is required for isolating workflows.
- It allows resume, replay, and debugging.
- It is the foundation for persistent memory systems introduced later.