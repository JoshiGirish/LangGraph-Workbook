# Lab 032 — Checkpoint Inspection

## Lab Intro

In the previous labs we learned:

- Checkpoints store workflow state
- Threads isolate workflow executions
- `InMemorySaver` can persist checkpoints during runtime

Now we explore one of the most powerful capabilities of LangGraph:

> **Checkpoint Inspection**

Checkpoint inspection allows us to:

- view the current workflow state
- inspect execution progress
- understand what happened before a failure
- debug workflow behavior
- audit state transitions

Think of it as:

```text
Looking inside a running workflow
```

instead of treating the graph as a black box.

---

## Enterprise Analogy

Imagine a loan approval workflow:

```text
Submit
   ↓
Identity Check
   ↓
Credit Check
   ↓
Approval
```

A customer calls support asking:

```text
"Where is my application?"
```

Without checkpoint inspection:

```text
No visibility ❌
```

With checkpoint inspection:

```text
Current State:
Credit Check Completed
Awaiting Approval ✔
```

---

## Key Idea

A checkpoint contains:

```text
State Snapshot
+
Execution Metadata
+
Thread Context
```

Checkpoint inspection allows us to retrieve and examine this information.

---

## Lab Code

from typing import Optional

from pydantic import BaseModel

from langgraph.graph import StateGraph
from langgraph.graph import START, END

from langgraph.checkpoint.memory import InMemorySaver


# -------------------------
# State Model
# -------------------------

class State(BaseModel):
    order_id: str

    status: Optional[str] = None

    validated: bool = False

    charged: bool = False


# -------------------------
# Node 1
# -------------------------

def validate_order(state: State):

    return {
        "status": "validated",
        "validated": True
    }


# -------------------------
# Node 2
# -------------------------

def charge_payment(state: State):

    return {
        "status": "charged",
        "charged": True
    }


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "validate_order",
    validate_order
)

builder.add_node(
    "charge_payment",
    charge_payment
)

builder.add_edge(
    START,
    "validate_order"
)

builder.add_edge(
    "validate_order",
    "charge_payment"
)

builder.add_edge(
    "charge_payment",
    END
)


# -------------------------
# Checkpointer
# -------------------------

checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)


# -------------------------
# Thread Config
# -------------------------

config = {
    "configurable": {
        "thread_id": "order-1001"
    }
}


# -------------------------
# Execute Workflow
# -------------------------

result = graph.invoke(
    {
        "order_id": "ORD-1001"
    },
    config=config
)

print("FINAL RESULT")
print(result)


# -------------------------
# Inspect Latest Checkpoint
# -------------------------

snapshot = graph.get_state(config)

print("\nLATEST CHECKPOINT")

print(snapshot.values)

---

## Expected Output

```python
FINAL RESULT

{
    'order_id': 'ORD-1001',
    'status': 'charged',
    'validated': True,
    'charged': True
}

LATEST CHECKPOINT

{
    'order_id': 'ORD-1001',
    'status': 'charged',
    'validated': True,
    'charged': True
}
```

---

## Explanation

## What Is Checkpoint Inspection?

Checkpoint inspection allows us to query:

```text
What does the workflow currently know?
```

Instead of:

```text
Only seeing final output
```

we can inspect:

```text
Saved execution state
```

inside a thread.

---

## Step 1 — Execute Workflow

The workflow runs:

```text
validate_order
   ↓
charge_payment
```

Final state becomes:

```python
{
    "status": "charged",
    "validated": True,
    "charged": True
}
```

---

## Step 2 — Retrieve State Snapshot

We use:

```python
snapshot = graph.get_state(config)
```

LangGraph:

1. locates thread
2. loads latest checkpoint
3. returns state snapshot

---

## Step 3 — Inspect Values

Checkpoint values are available via:

```python
snapshot.values
```

Result:

```python
{
    "order_id": "ORD-1001",
    "status": "charged",
    "validated": True,
    "charged": True
}
```

This represents the latest persisted workflow state.

---

## Why Inspection Matters

### Debugging

Suppose a workflow fails:

```text
validate_order ✔
charge_payment ❌
```

Inspection shows:

```text
exactly where failure occurred
```

---

### Operational Visibility

Support teams can answer:

```text
What stage is this workflow in?
```

without re-running anything.

---

### Auditing

You can verify:

```text
Which steps completed?
```

and

```text
What data existed at that point?
```

---

## Mental Model

Without inspection:

```text
Workflow = black box
```

With inspection:

```text
Workflow = observable system
```

---

## Understanding StateSnapshot

`graph.get_state()` returns a snapshot object.

Commonly used field:

```python
snapshot.values
```

which contains:

```text
Current persisted state
```

The snapshot may also include internal metadata used by LangGraph for execution management.

---

## Enterprise Example

### Insurance Claim Processing

```text
Claim Submitted
   ↓
Documents Verified
   ↓
Fraud Review
   ↓
Approval
```

Checkpoint inspection can reveal:

```text
Current Stage:
Fraud Review
```

without restarting the workflow.

---

## Common Mistakes

### 1. Confusing final output with checkpoint state

Final output:

```text
returned by invoke()
```

Checkpoint:

```text
stored by checkpointer
```

These are related but not identical concepts.

---

### 2. Forgetting thread_id

Inspection requires:

```python
graph.get_state(config)
```

and the correct thread configuration.

---

### 3. Assuming only failures need inspection

Checkpoint inspection is useful even when workflows succeed.

It provides:

```text
observability
```

for production systems.

---

## Checkpointing vs Checkpoint Inspection

### Checkpointing

```text
Save state
```

---

### Inspection

```text
Read state
```

Relationship:

```text
Checkpointing creates snapshots
Inspection retrieves snapshots
```

---

## Key Takeaways

- Checkpoint inspection allows you to view persisted workflow state.
- `graph.get_state()` retrieves the latest checkpoint for a thread.
- Inspection improves debugging, observability, and auditing.
- A checkpoint snapshot represents the workflow's current state.
- Threads and checkpoints work together to provide execution visibility.
- Checkpoint inspection is a foundational capability for replay and time travel, which are introduced next.