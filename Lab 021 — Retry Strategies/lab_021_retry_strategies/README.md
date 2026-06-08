# Lab 021 — Retry Strategies

## Lab Intro

In production workflows, failures are not always permanent.

Many failures are **temporary** and can often succeed if retried.

Examples:

```text
Network timeout
Temporary API outage
Database connection issue
Rate limiting
```

In these situations:

```text
Fail Once
   ↓
Retry
   ↓
Success
```

is often preferable to immediately failing the workflow.

A retry strategy allows a node to:

- attempt an operation
- detect failure
- retry a limited number of times
- eventually succeed or fail gracefully

This is a common reliability pattern in enterprise systems.

Workflow:

```text
START
   |
fetch_customer_profile
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
# Simulated External Service
# -------------------------

attempt_counter = {
    "count": 0
}


def external_customer_service():

    attempt_counter["count"] += 1

    # Simulate temporary failure
    # on first two attempts

    if attempt_counter["count"] < 3:
        raise ConnectionError(
            "Customer service unavailable"
        )

    return {
        "name": "Alice"
    }


# -------------------------
# State Model
# -------------------------

class State(BaseModel):
    customer_id: str

    customer_name: Optional[str] = None

    status: Optional[str] = None

    retries: int = 0

    error: Optional[str] = None


# -------------------------
# Retry Node
# -------------------------

MAX_RETRIES = 3


def fetch_customer_profile(state: State):

    retries = 0

    while retries < MAX_RETRIES:

        try:

            customer = external_customer_service()

            return {
                "customer_name": customer["name"],
                "status": "success",
                "retries": retries
            }

        except ConnectionError as e:

            retries += 1

    return {
        "status": "failed",
        "retries": retries,
        "error": "Customer service unavailable"
    }


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "fetch_customer_profile",
    fetch_customer_profile
)

builder.add_edge(
    START,
    "fetch_customer_profile"
)

builder.add_edge(
    "fetch_customer_profile",
    END
)

graph = builder.compile()


# -------------------------
# Execute Graph
# -------------------------

result = graph.invoke(
    {
        "customer_id": "CUST-100"
    }
)

print(result)
```

---

## Expected Output

```python
{
    'customer_id': 'CUST-100',
    'customer_name': 'Alice',
    'status': 'success',
    'retries': 2,
    'error': None
}
```

Notice:

```text
Attempt 1 → Failure
Attempt 2 → Failure
Attempt 3 → Success
```

The workflow succeeds even though the external service failed twice.

---

## Explanation

### What Is a Retry Strategy?

A retry strategy means:

```text
Try Operation
      ↓
Failed?
      ↓
Retry
      ↓
Success or Give Up
```

Instead of failing immediately.

---

## Why Retries Matter

Many production failures are temporary.

Examples:

```text
Network interruption
API timeout
Database overload
Cloud service hiccup
```

Failing immediately can make workflows unnecessarily fragile.

Retries improve resilience.

---

## Step 1 — Simulate an External Service

```python
def external_customer_service():
```

We simulate a service that fails twice:

```python
if attempt_counter["count"] < 3:
    raise ConnectionError(...)
```

and succeeds on the third attempt.

This mimics a transient outage.

---

## Step 2 — Define Retry Limits

```python
MAX_RETRIES = 3
```

This prevents:

```text
Infinite Retry Loop
```

which could consume resources forever.

Production systems always use retry limits.

---

## Step 3 — Attempt the Operation

```python
while retries < MAX_RETRIES:
```

Inside the loop:

```python
customer = external_customer_service()
```

If successful:

```python
return {
    "customer_name": customer["name"],
    "status": "success"
}
```

Execution ends immediately.

---

## Step 4 — Handle Failure

If the service fails:

```python
except ConnectionError:
```

increment:

```python
retries += 1
```

and try again.

---

## Step 5 — Exhaust Retries

If all attempts fail:

```python
return {
    "status": "failed",
    "error": "Customer service unavailable"
}
```

The node exits gracefully.

---

## Execution Timeline

### Attempt 1

```text
Call Service
      ↓
ConnectionError
      ↓
Retry
```

---

### Attempt 2

```text
Call Service
      ↓
ConnectionError
      ↓
Retry
```

---

### Attempt 3

```text
Call Service
      ↓
Success
```

Node returns:

```python
{
    "customer_name": "Alice",
    "status": "success",
    "retries": 2
}
```

---

## State Evolution

### Initial State

```python
{
    "customer_id": "CUST-100"
}
```

---

### After Successful Retry

```python
{
    "customer_id": "CUST-100",
    "customer_name": "Alice",
    "status": "success",
    "retries": 2
}
```

---

## What Happens If Retries Are Exhausted?

Imagine the service never recovers.

All attempts fail:

```text
Attempt 1 → Fail
Attempt 2 → Fail
Attempt 3 → Fail
```

Result:

```python
{
    "customer_id": "CUST-100",
    "status": "failed",
    "retries": 3,
    "error": "Customer service unavailable"
}
```

The workflow records the failure instead of crashing.

---

## Enterprise Example

A common enterprise workflow:

```text
Order Processing
      ↓
Payment Gateway
      ↓
Temporary Timeout
      ↓
Retry
      ↓
Payment Approved
```

Without retries:

```text
Customer Payment Fails
```

With retries:

```text
Temporary Issue
      ↓
Recovered Automatically
```

leading to a better customer experience.

---

## Retry vs Error Handling

Error handling:

```text
Failure
   ↓
Record Error
```

Retry strategy:

```text
Failure
   ↓
Retry
   ↓
Maybe Recover
```

Retries are often built on top of error handling.

---

## Common Production Retry Patterns

### Fixed Retry

```text
Retry Every 1 Second
```

Simple and predictable.

---

### Exponential Backoff

```text
Retry 1 → 1 sec
Retry 2 → 2 sec
Retry 3 → 4 sec
Retry 4 → 8 sec
```

Reduces pressure on struggling services.

---

### Retry with Jitter

```text
Randomized Delay
```

Prevents thousands of clients from retrying simultaneously.

---

## Why Retry Strategies Matter in LangGraph

Many LangGraph nodes interact with:

- APIs
- databases
- vector stores
- LLM providers
- third-party services

These dependencies occasionally fail.

Retries help workflows:

```text
Recover Automatically
      ↓
Continue Processing
```

instead of failing due to temporary issues.

---

## Key Takeaways

- Many failures are temporary rather than permanent.
- Retry strategies improve workflow reliability.
- Retries should always have a maximum limit.
- A retry loop attempts recovery before declaring failure.
- Retry strategies are commonly used around APIs, databases, and external services.
- Enterprise workflows frequently combine retries with error handling.
- Reliable LangGraph applications often use retries to tolerate transient failures.