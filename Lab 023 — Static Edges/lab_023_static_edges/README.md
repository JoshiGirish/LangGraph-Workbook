# Lab 023 — Static Edges

## Lab Intro

In LangGraph, control flow defines **how execution moves between nodes**.

The simplest form of control flow is:

> **Static Edges**

Static edges mean the workflow path is **fixed at design time**.

There is:

- no branching
- no conditions
- no dynamic routing

Every execution follows the same path.

This is the foundation of all graph-based workflows.

---

## Enterprise Analogy

Think of a simple onboarding pipeline:

```text
START
  ↓
validate_user
  ↓
create_account
  ↓
send_welcome_email
  ↓
END
```

Every user goes through the same steps.

No decisions are made inside the graph structure.

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
    user_id: str

    is_valid: Optional[bool] = None

    account_created: Optional[bool] = None

    email_sent: Optional[bool] = None


# -------------------------
# Nodes
# -------------------------

def validate_user(state: State):
    return {
        "is_valid": True
    }


def create_account(state: State):
    return {
        "account_created": True
    }


def send_welcome_email(state: State):
    return {
        "email_sent": True
    }


# -------------------------
# Build Graph (Static Edges)
# -------------------------

builder = StateGraph(State)

builder.add_node("validate_user", validate_user)
builder.add_node("create_account", create_account)
builder.add_node("send_welcome_email", send_welcome_email)

# Static execution order
builder.add_edge(START, "validate_user")
builder.add_edge("validate_user", "create_account")
builder.add_edge("create_account", "send_welcome_email")
builder.add_edge("send_welcome_email", END)

graph = builder.compile()


# -------------------------
# Execute Graph
# -------------------------

result = graph.invoke(
    {
        "user_id": "USER-100"
    }
)

print(result)
```

---

## Expected Output

```python
{
    'user_id': 'USER-100',
    'is_valid': True,
    'account_created': True,
    'email_sent': True
}
```

---

## Explanation

### What Are Static Edges?

Static edges define a **fixed path** between nodes:

```text
A → B → C → D
```

Once defined, the path never changes.

---

## Step 1 — Define Nodes

We define three simple nodes:

### validate_user

```python
def validate_user(state):
    return {"is_valid": True}
```

---

### create_account

```python
def create_account(state):
    return {"account_created": True}
```

---

### send_welcome_email

```python
def send_welcome_email(state):
    return {"email_sent": True}
```

Each node performs one step in the pipeline.

---

## Step 2 — Build Fixed Flow

We connect nodes using edges:

```python
builder.add_edge(START, "validate_user")
builder.add_edge("validate_user", "create_account")
builder.add_edge("create_account", "send_welcome_email")
builder.add_edge("send_welcome_email", END)
```

This creates a strict sequence:

```text
START
  ↓
validate_user
  ↓
create_account
  ↓
send_welcome_email
  ↓
END
```

No branching logic exists.

---

## Step 3 — Execution Flow

Input:

```python
{
    "user_id": "USER-100"
}
```

Execution proceeds step-by-step:

### Step 1

```text
validate_user
```

Output:

```python
{"is_valid": True}
```

---

### Step 2

```text
create_account
```

Output:

```python
{"account_created": True}
```

---

### Step 3

```text
send_welcome_email
```

Output:

```python
{"email_sent": True}
```

---

## Key Property of Static Edges

Every run produces the same execution path:

```text
Run 1 → A → B → C
Run 2 → A → B → C
Run 3 → A → B → C
```

No variation.

---

## Why Static Edges Matter

Static graphs are useful when:

- the process is deterministic
- no decision-making is required
- order is strictly defined
- workflow is a pipeline

Examples:

```text
Data ETL pipelines
Document processing
Simple onboarding flows
Batch transformations
```

---

## Advantages

### 1. Predictability

Execution path is always known:

```text
No surprises
```

---

### 2. Easy Debugging

If something fails:

```text
Check each node in order
```

---

### 3. Simple Design

No conditional logic needed in graph structure.

---

### 4. Strong Observability

Logs always follow the same sequence.

---

## Limitations

Static edges are not suitable for:

### Conditional logic

```text
If user is premium → skip payment step
```

---

### Dynamic routing

```text
Choose model based on input size
```

---

### Error-based branching

```text
Retry if failure occurs
```

These require **dynamic edges**, which we will cover later.

---

## Enterprise Example

A real-world static pipeline:

```text
Raw Data
  ↓
Clean Data
  ↓
Transform Data
  ↓
Store in Database
  ↓
Generate Report
```

Each stage always runs in the same order.

---

## Static vs Dynamic Preview

### Static Edges

```text
Fixed path:
A → B → C
```

---

### Dynamic Edges (Next Lab Preview)

```text
Condition-based:
A → (B or C)
```

---

## Key Takeaways

- Static edges define a fixed execution path in a LangGraph workflow.
- Every run follows the same sequence of nodes.
- They are ideal for deterministic pipelines.
- Static graphs are simple, predictable, and easy to debug.
- They form the foundation before introducing conditional or dynamic routing.