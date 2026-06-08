# Lab 045 — Escalation Patterns

## Lab Intro

In the previous labs we learned:

- Interrupts
- Approval workflows
- Human review queues
- State editing
- Resuming execution
- Human-governed agent systems

Sometimes an agent cannot confidently make a decision.

Instead of continuing automatically, it should:

```text
Escalate
```

the task to a higher authority.

This pattern is known as:

```text
Escalation
```

---

## Enterprise Analogy

Consider a customer support workflow:

```text
Customer Request
        ↓
AI Agent
        ↓
Can Resolve?
    ┌────┴────┐
   Yes       No
    ↓         ↓
 Resolve   Escalate
              ↓
       Human Specialist
```

The agent handles routine requests.

Complex cases are escalated.

---

## Key Idea

Escalation occurs when:

```text
Agent Confidence Is Low
Policy Requires Human Review
Risk Is High
Exception Occurs
```

Rather than making a potentially incorrect decision, the workflow transfers responsibility.

---

## Visual Model

```text
START
   ↓
analyze_request
   ↓
Needs Escalation?
   ↓
 ┌─────────────┐
 │    Yes      │
 └──────┬──────┘
        ↓
   human_review
        ↓
       END

      OR

        ↓ No
   auto_resolve
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
    request: str
    confidence: float
    outcome: str = ""

# -------------------------
# Analyze Request
# -------------------------

def analyze_request(state: State):

    if state.confidence < 0.8:
        return {
            "outcome": "escalate"
        }

    return {
        "outcome": "auto_resolve"
    }

# -------------------------
# Router
# -------------------------

def route(state: State):

    return state.outcome

# -------------------------
# Human Escalation
# -------------------------

def human_review(state: State):

    decision = interrupt(
        {
            "message":
            f"Review request: {state.request}"
        }
    )

    return {
        "outcome": f"human_{decision}"
    }

# -------------------------
# Automatic Resolution
# -------------------------

def auto_resolve(state: State):

    return {
        "outcome": "resolved_by_agent"
    }

# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "analyze_request",
    analyze_request
)

builder.add_node(
    "human_review",
    human_review
)

builder.add_node(
    "auto_resolve",
    auto_resolve
)

builder.add_edge(
    START,
    "analyze_request"
)

builder.add_conditional_edges(
    "analyze_request",
    route,
    {
        "escalate": "human_review",
        "auto_resolve": "auto_resolve"
    }
)

builder.add_edge(
    "human_review",
    END
)

builder.add_edge(
    "auto_resolve",
    END
)

graph = builder.compile()


---

## Example 1 — Auto Resolution

Input:

```python
{
    "request": "Reset Password",
    "confidence": 0.95
}
```

Flow:

```text
Analyze
    ↓
High Confidence
    ↓
Auto Resolve
```

Output:

```python
{
    "outcome": "resolved_by_agent"
}
```

---

## Example 2 — Escalation

Input:

```python
{
    "request": "Disputed Fraud Claim",
    "confidence": 0.45
}
```

Flow:

```text
Analyze
    ↓
Low Confidence
    ↓
Escalate
    ↓
Human Review
```

Execution pauses and waits for human input.

---

## Why Escalation Matters

Not every problem should be solved automatically.

Some situations require:

```text
Expert Judgment
Human Accountability
Risk Assessment
Policy Decisions
```

Escalation ensures difficult cases receive appropriate attention.

---

## Common Escalation Triggers

### Low Confidence

```text
Agent Unsure
```

Example:

```text
Confidence = 0.42
```

---

### High Risk

```text
Large Financial Transaction
```

---

### Compliance Requirements

```text
Human Approval Required
```

---

### Unexpected Situations

```text
Unknown Input
Policy Exception
```

---

## Enterprise Examples

### Customer Support

```text
Simple Password Reset
        ↓
Agent Resolves

Fraud Investigation
        ↓
Human Specialist
```

---

### Banking

```text
Small Transfer
       ↓
Automatic

Large Transfer
       ↓
Escalation
```

---

### Healthcare

```text
Routine Question
        ↓
Agent Response

Complex Diagnosis
        ↓
Doctor Review
```

---

### Enterprise AI Agents

```text
Low-Risk Actions
        ↓
Agent Executes

High-Risk Actions
        ↓
Manager Approval
```

---

## Escalation Hierarchy

Many organizations use multiple escalation levels:

```text
Agent
  ↓
Tier 1 Human
  ↓
Tier 2 Specialist
  ↓
Manager
```

Each level handles increasingly complex cases.

---

## Escalation vs Approval

### Approval

```text
Agent Knows What To Do
Needs Permission
```

Example:

```text
Purchase Request
```

---

### Escalation

```text
Agent Does Not Know What To Do
Needs Help
```

Example:

```text
Complex Fraud Investigation
```

---

## Mental Model

Think of escalation as:

```text
Raising Your Hand
```

The agent recognizes:

```text
This Is Beyond My Authority
```

and asks a human for assistance.

---

## Common Mistakes

### 1. Escalating Everything

Bad:

```text
Every Request
      ↓
Human
```

This removes the benefits of automation.

---

### 2. Never Escalating

Bad:

```text
Agent Handles Everything
```

This increases risk.

---

### 3. Using Poor Escalation Criteria

Escalation should be based on:

```text
Confidence
Risk
Policy
Business Rules
```

not random thresholds.

---

## Key Takeaways

- Escalation transfers responsibility from an agent to a human reviewer.
- Common triggers include low confidence, high risk, compliance requirements, and exceptions.
- Escalation helps balance automation with safety and accountability.
- Not all tasks should be automated and not all tasks should be escalated.
- Human-in-the-loop systems often rely on escalation patterns for complex or sensitive decisions.
- Escalation is a critical governance mechanism in enterprise AI systems.