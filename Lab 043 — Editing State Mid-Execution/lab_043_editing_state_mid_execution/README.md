# Lab 043 — Editing State Mid-Execution

## Lab Intro

In the previous labs we learned:

- Interrupts pause execution
- Approval workflows collect human decisions
- Review queues allow asynchronous review

Sometimes a human reviewer needs to do more than simply:

```text
Approve
Reject
```

They may need to:

```text
Correct Data
Modify Inputs
Update Workflow State
```

before execution continues.

This capability is called:

```text
Editing State Mid-Execution
```

---

## Enterprise Analogy

Consider a loan application workflow:

```text
Application Submitted
          ↓
Human Review
          ↓
Fix Incorrect Income
          ↓
Resume Processing
```

Instead of rejecting the application, the reviewer corrects the data and continues the workflow.

---

## Key Idea

A workflow can pause:

```text
Interrupt
```

A human can modify the state:

```text
Edit State
```

Then execution resumes using the updated values.

---

## Visual Model

```text
START
   ↓
collect_data
   ↓
INTERRUPT
   ↓
Human Edits State
   ↓
Resume
   ↓
END
```

---

## Lab Code

from pydantic import BaseModel

from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langgraph.types import interrupt

# -------------------------
# State
# -------------------------

class State(BaseModel):
    customer_name: str
    income: int

# -------------------------
# Review Step
# -------------------------

def review_application(state: State):

    updated_state = interrupt(
        {
            "customer_name": state.customer_name,
            "income": state.income
        }
    )

    return updated_state

# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "review_application",
    review_application
)

builder.add_edge(
    START,
    "review_application"
)

builder.add_edge(
    "review_application",
    END
)

graph = builder.compile()

# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "customer_name": "John Smith",
        "income": 50000
    }
)

print(result)

---

## What Happens?

### Step 1 — Workflow Starts

Input:

```python
{
    "customer_name": "John Smith",
    "income": 50000
}
```

---

### Step 2 — Interrupt Occurs

The workflow pauses and presents the current state:

```python
{
    "customer_name": "John Smith",
    "income": 50000
}
```

to a human reviewer.

---

### Step 3 — Human Edits State

Example update:

```python
{
    "customer_name": "John Smith",
    "income": 75000
}
```

The reviewer corrected the income value.

---

### Step 4 — Resume Execution

The workflow resumes using:

```python
income = 75000
```

instead of the original value.

---

## Why State Editing Matters

Many business processes require:

```text
Correction
Validation
Enrichment
```

rather than simple approval.

Examples:

```text
Fix Missing Data
Correct Customer Information
Update Risk Scores
Adjust Pricing
```

---

## Common Use Cases

### Loan Processing

```text
Application
      ↓
Human Corrects Income
      ↓
Continue Approval
```

---

### Insurance Claims

```text
Claim Submitted
      ↓
Adjust Claim Details
      ↓
Continue Processing
```

---

### AI Agents

```text
Agent Draft
      ↓
Human Edits Output
      ↓
Continue Workflow
```

---

## State Before vs After

### Before Review

```python
{
    "income": 50000
}
```

---

### After Review

```python
{
    "income": 75000
}
```

The workflow continues with the updated state.

---

## Why Not Restart?

Without state editing:

```text
Reject
Fix Data
Restart Workflow
```

With state editing:

```text
Pause
Fix Data
Resume Workflow
```

This is faster and more efficient.

---

## Mental Model

Think of workflow state as:

```text
A Form Being Processed
```

During review, a human can:

```text
Open Form
Edit Fields
Save Changes
Continue Processing
```

without starting over.

---

## Common Mistakes

### 1. Only Allowing Approvals

Human reviewers often need to:

```text
Modify Information
```

not just approve it.

---

### 2. Restarting Workflows Unnecessarily

Editing state is often simpler than:

```text
Terminate
Recreate
Rerun
```

---

### 3. Losing Context

The updated state should preserve all relevant workflow information.

Only modify what needs changing.

---

## Key Takeaways

- Human reviewers can modify workflow state while execution is paused.
- Interrupts allow workflows to stop and wait for state updates.
- Updated state is used when execution resumes.
- State editing is useful for corrections, validation, and enrichment.
- Editing state is often more efficient than restarting a workflow.
- Human-in-the-loop systems frequently combine approvals with state modification.