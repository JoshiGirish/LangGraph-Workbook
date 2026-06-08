# Lab 028 — Building a State Machine

## Lab Intro

As we combine everything from previous labs:

- static edges
- conditional edges
- multi-branch routing
- dynamic routing
- command-based routing
- loops
- termination conditions

we naturally arrive at a more powerful abstraction:

> **A State Machine**

A state machine is a system where:

- the application is always in a **defined state**
- transitions between states are **explicit**
- behavior depends on the **current state**

In LangGraph terms:

```text
Nodes = States / Actions
Edges = Transitions
State = Shared memory
```

---

## Enterprise Analogy

Think of an order processing system:

```text
NEW → VALIDATED → PAID → SHIPPED → COMPLETED
                 ↘ FAILED ↗
```

At any time, the order is in exactly one state.

Transitions are controlled and rule-based.

---

## Lab Code

from typing import Optional, Literal

from pydantic import BaseModel

from langgraph.graph import StateGraph
from langgraph.graph import START, END


# -------------------------
# State Model
# -------------------------

class State(BaseModel):
    order_id: str

    status: Optional[str] = None

    payment_verified: bool = False

    retry_count: int = 0


# -------------------------
# Node 1 — Validate Order
# -------------------------

def validate_order(state: State):

    return {
        "status": "VALIDATED"
    }


# -------------------------
# Node 2 — Process Payment
# -------------------------

def process_payment(state: State):

    # Simulated failure on first attempt
    if state.retry_count < 1:
        return {
            "status": "PAYMENT_FAILED",
            "payment_verified": False
        }

    return {
        "status": "PAID",
        "payment_verified": True
    }


# -------------------------
# Node 3 — Ship Order
# -------------------------

def ship_order(state: State):

    return {
        "status": "SHIPPED"
    }


# -------------------------
# Node 4 — Complete Order
# -------------------------

def complete_order(state: State):

    return {
        "status": "COMPLETED"
    }


# -------------------------
# Router — State Transition Logic
# -------------------------

def state_router(state: State) -> Literal[
    "process_payment",
    "ship_order",
    "complete_order",
    "process_payment"
]:

    if state.status == "VALIDATED":
        return "process_payment"

    if state.status == "PAYMENT_FAILED":
        return "process_payment"

    if state.status == "PAID":
        return "ship_order"

    if state.status == "SHIPPED":
        return "complete_order"

    return "complete_order"


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node("validate_order", validate_order)
builder.add_node("process_payment", process_payment)
builder.add_node("ship_order", ship_order)
builder.add_node("complete_order", complete_order)

builder.add_edge(START, "validate_order")

builder.add_conditional_edges(
    "validate_order",
    state_router,
    {
        "process_payment": "process_payment",
        "ship_order": "ship_order",
        "complete_order": "complete_order"
    }
)

builder.add_conditional_edges(
    "process_payment",
    state_router,
    {
        "process_payment": "process_payment",
        "ship_order": "ship_order",
        "complete_order": "complete_order"
    }
)

builder.add_conditional_edges(
    "ship_order",
    state_router,
    {
        "complete_order": "complete_order"
    }
)

builder.add_edge("complete_order", END)

graph = builder.compile()


# -------------------------
# Execute Graph
# -------------------------

result = graph.invoke(
    {
        "order_id": "ORD-1001"
    }
)

print(result)

---

## Expected Output (Example)

```python
{
    'order_id': 'ORD-1001',
    'status': 'COMPLETED',
    'payment_verified': True,
    'retry_count': 0
}
```

---

## Explanation

## What Is a State Machine?

A state machine is a system where:

> behavior depends on the current state of the system

Instead of thinking in terms of:

```text
steps
```

we think in terms of:

```text
states and transitions
```

---

## Step 1 — Define States

We define explicit states using:

```python
status
```

Possible values:

```text
VALIDATED
PAYMENT_FAILED
PAID
SHIPPED
COMPLETED
```

Each state represents a **system condition**.

---

## Step 2 — State Transitions

Transitions are handled by:

```python
state_router(state)
```

Example:

```python
VALIDATED → process_payment
PAID → ship_order
SHIPPED → complete_order
```

This is the **core of the state machine**.

---

## Step 3 — Nodes as State Updaters

Each node modifies state:

### validate_order

```python
VALIDATED
```

---

### process_payment

```python
PAID or PAYMENT_FAILED
```

---

### ship_order

```python
SHIPPED
```

---

### complete_order

```python
COMPLETED
```

Each node moves the system forward.

---

## Step 4 — Handling Failure States

Payment failure:

```text
PAYMENT_FAILED → retry process_payment
```

This introduces:

- resilience
- retry behavior
- recovery logic

---

## Step 5 — Execution Flow

### Step 1

```text
START → validate_order
```

---

### Step 2

```text
VALIDATED → process_payment
```

---

### Step 3 (Failure First Attempt)

```text
PAYMENT_FAILED → retry process_payment
```

---

### Step 4 (Success)

```text
PAID → ship_order
```

---

### Step 5

```text
SHIPPED → complete_order
```

---

### Step 6

```text
COMPLETED → END
```

---

## Why This Is a State Machine

Because:

- system has **finite states**
- transitions depend on current state
- nodes represent state changes
- routing is state-driven

---

## Enterprise Examples

### 1. Order Lifecycle

```text
Created → Paid → Shipped → Delivered
```

---

### 2. Ticket System

```text
Open → In Progress → Resolved → Closed
```

---

### 3. Loan Processing

```text
Applied → Verified → Approved → Funded
```

---

## State Machine vs Graph

### Graph (General)

```text
Flexible execution flow
```

---

### State Machine

```text
Strictly defined states + transitions
```

State machines are:

- more structured
- more predictable
- easier to reason about

---

## Common Mistakes

### 1. Missing explicit states

Bad:

```text
random string values
```

Good:

```text
clearly defined statuses
```

---

### 2. Mixing logic and state transitions

Keep:

```text
routing separate from node logic
```

---

### 3. No terminal state

Always ensure:

```text
COMPLETED → END
```

---

## Key Takeaways

- A state machine models systems using explicit states and transitions.
- Nodes represent state changes, not just computations.
- Routing depends on current state values.
- State machines provide structure and predictability.
- Many real-world enterprise systems are state machines.
- LangGraph naturally supports state machine design patterns.