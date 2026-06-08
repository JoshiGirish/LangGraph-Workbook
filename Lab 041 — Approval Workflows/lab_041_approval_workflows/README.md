# Lab 041 — Approval Workflows

## Lab Intro

In the previous lab we learned how to pause execution using:

```text
Interrupts
```

Now we build a complete pattern on top of that:

```text
Approval Workflows
```

Approval workflows ensure that certain actions only proceed after:

```text
Human Confirmation
```

---

## Enterprise Analogy

Consider a purchase system:

```text
User Requests Purchase
        ↓
System Validates Request
        ↓
Manager Approves / Rejects
        ↓
If Approved → Execute Payment
```

The key rule is:

```text
No approval → No execution
```

---

## Key Idea

An approval workflow introduces a gate:

```text
Automatic Step
      ↓
HUMAN GATE
      ↓
Conditional Execution
```

The system branches based on human decision.

---

## Visual Model

```text
START
   ↓
create_request
   ↓
REQUEST APPROVAL
   ↓
(Human Decision)
   ↓
 ┌───────────────┐
 │ Approved?      │
 └──────┬────────┘
        │Yes
        ↓
   execute_action
        ↓
       END
```

---

## Lab Code

from typing import Optional
from pydantic import BaseModel

from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langgraph.types import interrupt

# -------------------------
# State
# -------------------------

class State(BaseModel):
    request: str
    approved: Optional[bool] = None

# -------------------------
# Approval Step
# -------------------------

def request_approval(state: State):

    decision = interrupt(
        {
            "message": f"Approve request: {state.request}?"
        }
    )

    return {
        "approved": decision == "approved"
    }

# -------------------------
# Conditional Step
# -------------------------

def execute_action(state: State):

    return {
        "result": f"Executed: {state.request}"
        if state.approved
        else "Not executed"
    }

# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "request_approval",
    request_approval
)

builder.add_node(
    "execute_action",
    execute_action
)

builder.add_edge(
    START,
    "request_approval"
)

builder.add_edge(
    "request_approval",
    "execute_action"
)

builder.add_edge(
    "execute_action",
    END
)

graph = builder.compile()

# -------------------------
# Execute
# -------------------------
result = graph.invoke(
    {
        "request": "Buy GPU Cluster"
    }
)

print(result)


---

## What Happens?

### Step 1 — Request Created

```text
Buy GPU Cluster
```

---

### Step 2 — Workflow Pauses

At:

```python
interrupt(...)
```

Execution stops and waits for human input:

```text
Approve request?
```

---

### Step 3 — Human Decision

Possible inputs:

```text
approved
rejected
```

---

### Step 4 — Conditional Execution

If approved:

```text
Executed: Buy GPU Cluster
```

If rejected:

```text
Not executed
```

---

## Why Approval Workflows Matter

Approval workflows are critical in:

```text
Finance
Security
Healthcare
Enterprise Operations
AI Governance
```

They ensure:

```text
Controlled Execution
Risk Reduction
Auditability
Human Oversight
```

---

## Pattern Breakdown

### 1. Generate Request

```text
System prepares action
```

---

### 2. Pause Execution

```text
interrupt()
```

---

### 3. Human Decision

```text
approved / rejected
```

---

### 4. Conditional Logic

```text
if approved → execute
else → stop
```

---

## Mental Model

Think of this pattern as:

```text
AI Suggests
Human Decides
System Executes
```

---

## Common Mistakes

### 1. Skipping the Approval Gate

Bad:

```text
Execute immediately
```

Good:

```text
Wait for human decision
```

---

### 2. Not Handling Both Outcomes

Always handle:

```text
Approved path
Rejected path
```

---

### 3. Treating Interrupt as Optional

In approval workflows:

```text
Interrupt is mandatory
```

not optional.

---

## Key Takeaways

- Approval workflows enforce human decision-making before execution.
- Interrupts are used to pause and wait for approval input.
- Workflows branch based on approval or rejection.
- These patterns are essential for governance and risk control.
- Approval workflows are widely used in enterprise systems involving sensitive or irreversible actions.