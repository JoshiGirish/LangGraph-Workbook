# Lab 020 — Idempotent Node Design

## Lab Intro

As LangGraph workflows become more sophisticated, nodes may be:

- retried after failures
- resumed from checkpoints
- replayed during debugging
- executed multiple times in distributed systems

This introduces an important concept:

> **Idempotency**

A node is **idempotent** if running it multiple times produces the same result as running it once.

For example:

```python
send_email()
```

is usually **not idempotent** because running it twice sends two emails.

Whereas:

```python
set_status("approved")
```

is typically idempotent because the status remains "approved" no matter how many times it is executed.

Designing idempotent nodes is critical for building reliable and fault-tolerant LangGraph applications.

Workflow:

```text
START
   |
process_order
   |
END
```

---

## Lab Code

```python
from typing import Optional

from pydantic import BaseModel

from langgraph.graph import StateGraph
from langgraph.graph import START, END


# -------------------------
# State Model
# -------------------------
class State(BaseModel):
    order_id: str
    status: Optional[str] = None
    processed: bool = False


# -------------------------
# Idempotent Node
# -------------------------
def process_order(state: State):

    # If already processed,
    # do nothing.
    if state.processed:
        return {}

    return {
        "status": "processed",
        "processed": True
    }


# -------------------------
# Build Graph
# -------------------------
builder = StateGraph(State)

builder.add_node(
    "process_order",
    process_order
)

builder.add_edge(
    START,
    "process_order"
)

builder.add_edge(
    "process_order",
    END
)

graph = builder.compile()


# -------------------------
# Execute Graph
# -------------------------
result_1 = graph.invoke(
    {
        "order_id": "ORD-1001"
    }
)

print("FIRST RUN")
print(result_1)

result_2 = graph.invoke(result_1)

print("\nSECOND RUN")
print(result_2)
```

Expected Output:

```python
FIRST RUN

{
    'order_id': 'ORD-1001',
    'status': 'processed',
    'processed': True
}

SECOND RUN

{
    'order_id': 'ORD-1001',
    'status': 'processed',
    'processed': True
}
```

Notice that the second execution does not change the state.

---

## Explanation

### What Is Idempotency?

A function is idempotent if:

```text
f(x) = f(f(x))
```

In simple terms:

```text
Run Once  → Result A
Run Twice → Result A
Run Ten Times → Result A
```

The final state remains unchanged.

---

## Why Idempotency Matters

LangGraph supports:

- checkpointing
- retries
- replay
- recovery

During these operations, nodes may execute again.

If nodes are not idempotent, unexpected side effects can occur.

Examples:

```text
Duplicate emails
Duplicate payments
Duplicate database inserts
Duplicate notifications
```

---

## Step 1 — Define the State

```python
class State(BaseModel):
    order_id: str
    status: Optional[str] = None
    processed: bool = False
```

The state contains:

- order identifier
- order status
- processing flag

The flag helps prevent duplicate work.

---

## Step 2 — Create an Idempotent Node

```python
def process_order(state: State):
```

Before processing:

```python
if state.processed:
    return {}
```

This means:

```text
Already Processed
      ↓
Skip Work
```

No changes are applied.

---

## Step 3 — First Execution

Initial State:

```python
{
    "order_id": "ORD-1001"
}
```

Node executes:

```python
{
    "status": "processed",
    "processed": True
}
```

Result:

```python
{
    "order_id": "ORD-1001",
    "status": "processed",
    "processed": True
}
```

---

## Step 4 — Second Execution

Input:

```python
{
    "order_id": "ORD-1001",
    "status": "processed",
    "processed": True
}
```

Node sees:

```python
state.processed == True
```

Therefore:

```python
return {}
```

No updates occur.

Final state remains unchanged.

---

## State Evolution

### Initial State

```python
{
    "order_id": "ORD-1001"
}
```

---

### After First Run

```python
{
    "order_id": "ORD-1001",
    "status": "processed",
    "processed": True
}
```

---

### After Second Run

```python
{
    "order_id": "ORD-1001",
    "status": "processed",
    "processed": True
}
```

No change.

---

## Non-Idempotent Example

Consider:

```python
def increment_counter(state):
    return {
        "counter": state.counter + 1
    }
```

Execution:

```text
Run 1 → 1
Run 2 → 2
Run 3 → 3
```

Every execution changes the result.

This is not idempotent.

---

## Another Non-Idempotent Example

```python
def send_email(state):
    send_email_to_user()
```

Running twice:

```text
Email #1 Sent
Email #2 Sent
```

This creates duplicate side effects.

---

## Common Idempotent Patterns

### Status Updates

```python
status = "approved"
```

Running again has no effect.

---

### Flag Assignment

```python
processed = True
```

Running again has no effect.

---

### Upsert Operations

```python
update_or_create(...)
```

Instead of:

```python
insert(...)
```

---

### Conditional Execution

```python
if already_done:
    return {}
```

A very common pattern in production systems.

---

## Why Idempotency Is Critical in LangGraph

As you move into:

- checkpointing
- persistence
- replay
- retries
- human-in-the-loop workflows
- multi-agent systems

nodes may execute more than once.

Idempotent nodes ensure that:

```text
Repeated Execution
       ↓
Consistent Results
```

without introducing unwanted side effects.

---

## Key Takeaways

- Idempotent nodes produce the same result even when executed multiple times.
- Idempotency is essential for retries, checkpoint recovery, and replay.
- State flags are a common way to implement idempotent behavior.
- Avoid duplicate side effects such as repeated emails or inserts.
- Reliable production workflows are built from idempotent components.
- As LangGraph systems grow, idempotent node design becomes increasingly important.