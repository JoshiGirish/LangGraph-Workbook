# Lab 034 — State Recovery After Failure

## Lab Intro

One of the primary reasons checkpointing exists is:

> **Recovery after failure**

In real-world systems, failures happen all the time:

- API outages
- network issues
- database timeouts
- service crashes
- unexpected exceptions

Without checkpointing:

```text
Failure
   ↓
Restart Entire Workflow
```

With checkpointing:

```text
Failure
   ↓
Recover Last Checkpoint
   ↓
Resume Execution
```

This dramatically improves:

- reliability
- fault tolerance
- user experience
- operational efficiency

---

## Enterprise Analogy

Imagine an order fulfillment workflow:

```text
Validate Order
   ↓
Charge Payment
   ↓
Reserve Inventory
   ↓
Ship Order
```

Suppose:

```text
Reserve Inventory
```

fails because the inventory service is temporarily unavailable.

Without checkpointing:

```text
Restart from Validate Order ❌
```

With checkpointing:

```text
Resume from Reserve Inventory ✔
```

The work already completed is preserved.

---

## Key Idea

Checkpointing allows us to recover:

```text
State
+
Progress
+
Execution Context
```

instead of starting from scratch.

---

## Workflow

```text
START
   ↓
validate_order
   ↓
charge_payment
   ↓
reserve_inventory
   ↓
ship_order
   ↓
END
```

Failure occurs here:

```text
reserve_inventory
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

    inventory_reserved: bool = False

    shipped: bool = False

    recovery_attempt: int = 0


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

def reserve_inventory(state: State):

    # Simulate failure on first attempt
    if state.recovery_attempt == 0:
        raise RuntimeError(
            "Inventory service unavailable"
        )

    return {
        "status": "inventory_reserved",
        "inventory_reserved": True
    }


# -------------------------
# Node 4
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
    "reserve_inventory",
    reserve_inventory
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
    "reserve_inventory"
)

builder.add_edge(
    "reserve_inventory",
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
# First Execution
# -------------------------

try:

    graph.invoke(
        {
            "order_id": "ORD-1001"
        },
        config=config
    )

except Exception as e:

    print("WORKFLOW FAILED")
    print(e)


# -------------------------
# Inspect Recovery State
# -------------------------

snapshot = graph.get_state(config)

print("\nLAST CHECKPOINT")

print(snapshot.values)


# -------------------------
# Resume Workflow
# -------------------------

print("\nRECOVERING...")

recovered_state = {
    **snapshot.values,
    "recovery_attempt": 1
}

result = graph.invoke(
    recovered_state,
    config=config
)

print("\nFINAL RESULT")

print(result)

---

## Expected Output (Example)

```python
WORKFLOW FAILED

Inventory service unavailable

LAST CHECKPOINT

{
    'order_id': 'ORD-1001',
    'status': 'charged',
    'validated': True,
    'charged': True
}

RECOVERING...

FINAL RESULT

{
    'order_id': 'ORD-1001',
    'status': 'shipped',
    'validated': True,
    'charged': True,
    'inventory_reserved': True,
    'shipped': True,
    'recovery_attempt': 1
}
```

---

## Explanation

## What Is State Recovery?

State recovery means:

> Resuming execution from the most recent successful checkpoint after a failure.

Instead of:

```text
Restart Workflow
```

we:

```text
Restore State
Resume Processing
```

---

## Step 1 — Successful Execution

The workflow begins:

```text
validate_order
   ↓
charge_payment
```

State becomes:

```python
{
    "validated": True,
    "charged": True
}
```

These checkpoints are safely stored.

---

## Step 2 — Failure Occurs

The inventory node throws:

```python
raise RuntimeError(...)
```

Execution stops.

Current workflow state:

```text
Failed
```

but prior checkpoints still exist.

---

## Step 3 — Inspect Last Checkpoint

We retrieve:

```python
snapshot = graph.get_state(config)
```

Result:

```python
{
    "status": "charged",
    "validated": True,
    "charged": True
}
```

This is the most recent successful state.

---

## Step 4 — Recover State

We use:

```python
snapshot.values
```

as the recovery point.

Conceptually:

```text
Restore Workflow
```

to:

```text
Before Failure
```

---

## Step 5 — Resume Execution

We invoke the graph again using:

```python
recovered_state
```

The workflow continues from the restored state.

No need to repeat:

```text
validate_order
charge_payment
```

because those steps were already completed.

---

## Why Recovery Matters

### Reliability

Systems survive transient failures.

---

### Cost Savings

Avoid recomputing expensive work.

---

### Better User Experience

Users do not lose progress.

---

### Long-Running Workflows

Recovery becomes essential when workflows run for:

- minutes
- hours
- days

---

## Enterprise Example

### Insurance Claims

```text
Submit Claim
   ↓
Verify Documents
   ↓
Fraud Check
   ↓
Approval
```

If Fraud Check fails:

```text
Resume from Fraud Check
```

instead of:

```text
Restart entire claim process
```

---

## Recovery vs Retry

### Retry

```text
Run failed step again
```

Usually immediate.

---

### Recovery

```text
Restore saved state
Resume workflow later
```

Can occur:

- minutes later
- hours later
- after a process restart

---

## Recovery Lifecycle

```text
Execute
   ↓
Checkpoint
   ↓
Failure
   ↓
Load Checkpoint
   ↓
Resume
```

This is the foundation of fault-tolerant systems.

---

## Common Mistakes

### 1. No Checkpointing

Without checkpoints:

```text
Recovery impossible
```

---

### 2. Non-Idempotent Nodes

Recovery may re-run nodes.

Nodes should be:

```text
safe to execute multiple times
```

---

### 3. Assuming Failure Loses State

Checkpointing exists specifically to preserve state across failures.

---

## Mental Model

Without checkpointing:

```text
Failure = Start Over
```

With checkpointing:

```text
Failure = Resume From Last Save Point
```

---

## Key Takeaways

- State recovery restores execution from the latest checkpoint after a failure.
- Checkpointing enables fault-tolerant workflows.
- Recovery prevents expensive recomputation.
- `graph.get_state()` provides access to the latest recoverable state.
- Recovery and idempotency work together to build resilient systems.
- State recovery is one of the most important production benefits of LangGraph checkpointing.