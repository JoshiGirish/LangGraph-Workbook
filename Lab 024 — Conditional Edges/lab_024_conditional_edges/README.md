# Lab 024 — Conditional Edges

## Lab Intro

Static edges always follow a fixed path.

But real enterprise workflows are rarely that simple.

In production systems, execution often depends on:

- input data
- validation results
- business rules
- external system responses

This introduces a key concept:

> **Conditional Edges**

Conditional edges allow a LangGraph workflow to **choose the next node dynamically at runtime**.

Instead of:

```text
A → B → C
```

we now have:

```text
A → (B or C)
```

This is where graphs become truly powerful.

---

## Enterprise Analogy

Consider a loan application system:

```text
START
  ↓
check_credit_score
  ↓
approve_loan OR reject_loan
  ↓
END
```

Decision depends on credit score.

---

## Lab Code

```python
from typing import Optional, Literal

from pydantic import BaseModel

from langgraph.graph import StateGraph
from langgraph.graph import START, END


# -------------------------
# State Model
# -------------------------

class State(BaseModel):
    user_id: str

    credit_score: Optional[int] = None

    decision: Optional[str] = None


# -------------------------
# Node 1 — Evaluate Credit Score
# -------------------------

def check_credit_score(state: State):

    # Simulated scoring logic
    if state.user_id == "USER-GOOD":
        score = 750
    else:
        score = 550

    return {
        "credit_score": score
    }


# -------------------------
# Node 2A — Approve Loan
# -------------------------

def approve_loan(state: State):

    return {
        "decision": "approved"
    }


# -------------------------
# Node 2B — Reject Loan
# -------------------------

def reject_loan(state: State):

    return {
        "decision": "rejected"
    }


# -------------------------
# Router Function (Conditional Logic)
# -------------------------

def route_credit_decision(state: State) -> Literal["approve_loan", "reject_loan"]:

    if state.credit_score is None:
        return "reject_loan"

    if state.credit_score >= 700:
        return "approve_loan"

    return "reject_loan"


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node("check_credit_score", check_credit_score)
builder.add_node("approve_loan", approve_loan)
builder.add_node("reject_loan", reject_loan)

builder.add_edge(START, "check_credit_score")

# Conditional Edge
builder.add_conditional_edges(
    "check_credit_score",
    route_credit_decision,
    {
        "approve_loan": "approve_loan",
        "reject_loan": "reject_loan"
    }
)

builder.add_edge("approve_loan", END)
builder.add_edge("reject_loan", END)

graph = builder.compile()


# -------------------------
# Execute Graph
# -------------------------

print("GOOD USER")
result_1 = graph.invoke({"user_id": "USER-GOOD"})
print(result_1)

print("\nBAD USER")
result_2 = graph.invoke({"user_id": "USER-BAD"})
print(result_2)
```

---

## Expected Output

```python
GOOD USER

{
    'user_id': 'USER-GOOD',
    'credit_score': 750,
    'decision': 'approved'
}

BAD USER

{
    'user_id': 'USER-BAD',
    'credit_score': 550,
    'decision': 'rejected'
}
```

---

## Explanation

### What Are Conditional Edges?

A conditional edge allows a node to decide:

```text
Where should execution go next?
```

Instead of a fixed connection, we use logic:

```python
if credit_score >= 700:
    return "approve_loan"
else:
    return "reject_loan"
```

---

## Step 1 — Generate Data

We first compute a value:

```python
credit_score
```

This is done in:

```python
check_credit_score
```

---

## Step 2 — Routing Function

The router:

```python
route_credit_decision(state)
```

acts as a decision engine.

It returns one of:

```text
approve_loan
reject_loan
```

---

## Step 3 — Conditional Edge Mapping

We define:

```python
builder.add_conditional_edges(
    "check_credit_score",
    route_credit_decision,
    {
        "approve_loan": "approve_loan",
        "reject_loan": "reject_loan"
    }
)
```

This means:

```text
Output of router → Next node
```

---

## Step 4 — Execution Flow (Good User)

Input:

```python
{"user_id": "USER-GOOD"}
```

### Step 1

```text
check_credit_score → 750
```

### Step 2 (Routing)

```python
750 ≥ 700 → approve_loan
```

### Step 3

```text
decision = "approved"
```

---

## Step 5 — Execution Flow (Bad User)

Input:

```python
{"user_id": "USER-BAD"}
```

### Step 1

```text
check_credit_score → 550
```

### Step 2 (Routing)

```text
550 < 700 → reject_loan
```

### Step 3

```python
decision = "rejected"
```

---

## Key Concept: Router Function

The router is the heart of conditional edges.

It:

- reads state
- applies logic
- returns a label
- determines next node

Think of it as:

```text
Traffic Controller for your graph
```

---

## Static vs Conditional Edges

### Static

```text
A → B → C
```

Fixed path.

---

### Conditional

```text
A → (B or C)
```

Decision-based path.

---

## Why Conditional Edges Matter

Real systems are not linear.

Examples:

### Fraud Detection

```text
fraud_score > threshold → block transaction
else → approve transaction
```

---

### Content Moderation

```text
safe → publish
unsafe → reject
```

---

### Customer Support

```text
simple issue → chatbot
complex issue → human agent
```

---

## Enterprise Pattern

Most production graphs follow:

```text
Data Node
   ↓
Decision Node
   ↓
Branch A OR Branch B
   ↓
END
```

This is the foundation of intelligent workflows.

---

## Common Mistakes

### 1. Putting logic inside multiple nodes

Bad:

```python
if score > 700:
    approve()
```

Better:

```text
Central router decides path
```

---

### 2. Returning invalid routing keys

Router must return valid labels:

```text
approve_loan
reject_loan
```

Not:

```text
"approve"
"yes"
```

---

### 3. Overcomplicating routing logic

Keep routers:

- simple
- deterministic
- readable

---

## Key Takeaways

- Conditional edges allow dynamic routing in LangGraph.
- A router function decides the next node at runtime.
- Execution paths depend on state values.
- Conditional edges enable real-world decision-making workflows.
- Most enterprise systems rely heavily on conditional routing.
- This is a foundational concept for building intelligent graphs.