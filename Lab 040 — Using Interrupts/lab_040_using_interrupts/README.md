# Lab 040 — Using Interrupts

## Lab Intro

So far our workflows have executed automatically:

```text
START
   ↓
Step 1
   ↓
Step 2
   ↓
END
```

However, many real-world processes require:

```text
Human Input
Human Approval
Human Validation
```

before execution can continue.

LangGraph supports this through:

```text
Interrupts
```

An interrupt pauses workflow execution and waits for an external action before resuming.

---

## Enterprise Analogy

Consider an expense approval workflow:

```text
Employee Submits Expense
          ↓
Manager Review
          ↓
Approval
          ↓
Payment
```

The workflow cannot continue until the manager makes a decision.

This pause is an interrupt.

---

## Key Idea

An interrupt allows a workflow to:

```text
Pause
Wait
Resume Later
```

without losing state.

---

## Visual Model

```text
START
   ↓
submit_request
   ↓
INTERRUPT
   ↓
(waiting for human)
   ↓
resume
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
    approval: Optional[str] = None

# -------------------------
# Human Approval Step
# -------------------------

def human_review(state: State):

    decision = interrupt(
        {
            "message": "Approve request?"
        }
    )

    return {
        "approval": decision
    }

# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "human_review",
    human_review
)

builder.add_edge(
    START,
    "human_review"
)

builder.add_edge(
    "human_review",
    END
)

graph = builder.compile()

# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "request": "Purchase Laptop"
    }
)

print(result)

---

## What Happens?

When execution reaches:

```python
interrupt(...)
```

the workflow:

```text
Pauses
```

and returns control to the caller.

The workflow state is preserved.

---

## Example Interrupt Event

```python
{
    "message": "Approve request?"
}
```

The application can now present this information to a human reviewer.

---

## Resume Later

After the human responds:

```text
approved
```

execution resumes from the interrupt point.

Conceptually:

```text
Paused Workflow
        ↓
Human Decision
        ↓
Resume Execution
```

---

## Why Interrupts Matter

Interrupts are the foundation for:

```text
Approval Workflows
Human Review
Escalations
Compliance Checks
Human-in-the-Loop Agents
```

Without interrupts:

```text
Agent Makes Every Decision
```

With interrupts:

```text
Humans Control Critical Decisions
```

---

## Common Use Cases

### Financial Approvals

```text
Expense Request
      ↓
Manager Approval
      ↓
Payment
```

---

### Legal Review

```text
Generate Contract
      ↓
Legal Review
      ↓
Send Contract
```

---

### AI Agent Oversight

```text
Agent Recommendation
        ↓
Human Validation
        ↓
Execute Action
```

---

## Mental Model

Think of an interrupt as:

```text
A Pause Button
```

for workflow execution.

The workflow stops, waits for input, and continues later from the same point.

---

## Key Takeaways

- Interrupts pause workflow execution and wait for external input.
- Workflow state is preserved while paused.
- Execution resumes from the interrupt point after input is provided.
- Interrupts enable human-in-the-loop workflows.
- Common use cases include approvals, reviews, compliance checks, and agent oversight.
- Interrupts are the foundation for building governed AI systems.