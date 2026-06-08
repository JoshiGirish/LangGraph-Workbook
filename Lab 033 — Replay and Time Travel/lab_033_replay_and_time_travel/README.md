# Lab 033 — Replay and Time Travel

## Lab Intro

In the previous labs we learned:

- Checkpointing saves workflow state
- Threads isolate workflow executions
- Checkpoint inspection lets us view saved state

Now we unlock one of the most powerful capabilities in LangGraph:

> **Replay and Time Travel**

Replay and Time Travel allow us to revisit previous execution states and understand exactly how a workflow reached its current state.

Think of it as:

```text
Git for workflow execution
```
or

```text
Video playback for a graph run
```

Instead of only seeing:

```text
Current State
```

we can inspect:

```text
Past States
```

and even re-execute from an earlier checkpoint.

---

## Enterprise Analogy

Imagine a fraud detection workflow:

```text
Transaction
    ↓
Risk Analysis
    ↓
Fraud Scoring
    ↓
Decision
```

A customer disputes a rejection.

The operations team asks:

```text
Why was this transaction blocked?
```

Replay allows us to see:

```text
State at Risk Analysis
State at Fraud Scoring
State at Final Decision
```

and reconstruct exactly what happened.

---

## Key Idea

Every checkpoint creates a historical snapshot:

```text
Checkpoint 1
Checkpoint 2
Checkpoint 3
Checkpoint 4
```

Together these form:

```text
Execution History
```

Replay allows us to:

```text
Move backward through that history
```

---

## Workflow

```text
START
   ↓
validate_order
   ↓
charge_payment
   ↓
ship_order
   ↓
END
```

Checkpoint timeline:

```text
CP1 → validated
CP2 → charged
CP3 → shipped
```

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

    shipped: bool = False


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
# Node 3
# -------------------------

def ship_order(state: State):

    return {
        "status": "shipped",
        "shipped": True
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

builder.add_node(
    "ship_order",
    ship_order
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
    "ship_order"
)

builder.add_edge(
    "ship_order",
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
# Thread Configuration
# -------------------------

config = {
    "configurable": {
        "thread_id": "order-1001"
    }
}


# -------------------------
# Execute Workflow
# -------------------------

graph.invoke(
    {
        "order_id": "ORD-1001"
    },
    config=config
)


# -------------------------
# View Checkpoint History
# -------------------------

history = list(
    graph.get_state_history(config)
)

print("CHECKPOINT HISTORY")

for checkpoint in history:

    print(
        checkpoint.values
    )

---

## Expected Output (Example)

```python
CHECKPOINT HISTORY

{
    'order_id': 'ORD-1001'
}

{
    'order_id': 'ORD-1001',
    'status': 'validated',
    'validated': True
}

{
    'order_id': 'ORD-1001',
    'status': 'charged',
    'validated': True,
    'charged': True
}

{
    'order_id': 'ORD-1001',
    'status': 'shipped',
    'validated': True,
    'charged': True,
    'shipped': True
}
```

---

## Explanation

## What Is Replay?

Replay means:

> Viewing the sequence of state changes that occurred during execution.

Instead of only seeing:

```text
Final Result
```

we can see:

```text
State 1
State 2
State 3
State 4
```

This provides a complete execution history.

---

## Step 1 — Workflow Execution

The workflow performs:

```text
validate_order
   ↓
charge_payment
   ↓
ship_order
```

Each node creates a new checkpoint.

---

## Step 2 — Retrieve History

We use:

```python
graph.get_state_history(config)
```

This returns:

```text
All saved checkpoints for the thread
```

ordered from newest to oldest (or vice versa depending on implementation/version).

---

## Step 3 — Inspect Historical States

Each checkpoint contains a snapshot of the workflow at a specific moment.

### Checkpoint 1

```python
{
    "order_id": "ORD-1001"
}
```

Initial state.

---

### Checkpoint 2

```python
{
    "status": "validated"
}
```

Validation completed.

---

### Checkpoint 3

```python
{
    "status": "charged"
}
```

Payment completed.

---

### Checkpoint 4

```python
{
    "status": "shipped"
}
```

Workflow completed.

---

## What Is Time Travel?

Time travel means:

> Returning to a previous checkpoint and treating it as the current state.

Conceptually:

```text
Current State
      ↓
Choose Older Checkpoint
      ↓
Resume Execution From There
```

---

## Visual Timeline

```text
CP1 → CP2 → CP3 → CP4
```

Current state:

```text
CP4
```

Time travel:

```text
CP4
 ↑
 |
Return to CP2
```

and continue execution from that point.

---

## Why Replay Matters

### Debugging

You can answer:

```text
What happened before the failure?
```

---

### Auditing

You can answer:

```text
Why was this decision made?
```

---

### Compliance

Many enterprise systems require:

```text
Historical traceability
```

of workflow execution.

---

### Agent Observability

For AI systems:

```text
Reasoning Step 1
Reasoning Step 2
Reasoning Step 3
```

can be replayed and inspected.

---

## Replay vs Inspection

### Inspection

```text
Show me latest state
```

Uses:

```python
graph.get_state()
```

---

### Replay

```text
Show me all historical states
```

Uses:

```python
graph.get_state_history()
```

---

## Enterprise Example

### Loan Approval Workflow

```text
Application Submitted
    ↓
Identity Verified
    ↓
Credit Evaluated
    ↓
Approved
```

Replay reveals:

```text
Every state transition
```

which helps explain approval decisions.

---

## Common Mistakes

### 1. Assuming only final state matters

In production:

```text
History is often more important than the final result.
```

---

### 2. Confusing replay with rerunning

Replay:

```text
Read historical checkpoints
```

Rerun:

```text
Execute workflow again
```

These are different operations.

---

### 3. Ignoring checkpoint granularity

More checkpoints provide:

```text
better observability
```

but also:

```text
more stored history
```

---

## Mental Model

Checkpoint inspection:

```text
Current Snapshot
```

Replay:

```text
Complete Timeline
```

Time Travel:

```text
Return To Any Snapshot
```

---

## Key Takeaways

- Replay allows you to inspect the full execution history of a workflow.
- `graph.get_state_history()` retrieves historical checkpoints for a thread.
- Each checkpoint represents a point-in-time state snapshot.
- Time travel means returning to an earlier checkpoint and resuming execution from there.
- Replay is essential for debugging, auditing, compliance, and AI observability.
- Checkpoint history transforms workflows from black boxes into fully traceable systems.