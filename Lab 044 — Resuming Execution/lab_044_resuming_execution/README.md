# Lab 044 — Resuming Execution

## Lab Intro

In the previous labs we learned how to:

- Pause execution using interrupts
- Wait for human review
- Modify workflow state during review

Now we learn how to:

```text
Resume Execution
```

after a workflow has been interrupted.

This is a core Human-in-the-Loop capability in LangGraph.

---

## Enterprise Analogy

Imagine a purchase approval process:

```text
Purchase Request
        ↓
Manager Review
        ↓
(waiting)
        ↓
Approved
        ↓
Process Purchase
```

The workflow pauses during review.

Once the manager responds, the workflow continues from the exact point where it stopped.

---

## Key Idea

An interrupt creates a pause:

```text
Workflow Running
       ↓
Interrupt
       ↓
Waiting
```

A resume command continues execution:

```text
Waiting
      ↓
Command(resume=...)
      ↓
Continue Execution
```

---

## Visual Model

```text
START
   ↓
review_request
   ↓
INTERRUPT
   ↓
(waiting)
   ↓
Command(resume=...)
   ↓
finalize
   ↓
END
```

---

## Lab Code

from pydantic import BaseModel

from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

# -------------------------
# State
# -------------------------

class State(BaseModel):
    request: str
    approval: str = ""
    result: str = ""

# -------------------------
# Human Review
# -------------------------

def review_request(state: State):

    decision = interrupt(
        "Approve or reject?"
    )

    return {
        "approval": decision
    }

# -------------------------
# Final Step
# -------------------------

def finalize(state: State):

    return {
        "result":
        f"Request was {state.approval}"
    }

# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "review_request",
    review_request
)

builder.add_node(
    "finalize",
    finalize
)

builder.add_edge(
    START,
    "review_request"
)

builder.add_edge(
    "review_request",
    "finalize"
)

builder.add_edge(
    "finalize",
    END
)

# -------------------------
# Checkpointer Required
# -------------------------

graph = builder.compile(
    checkpointer=InMemorySaver()
)

# -------------------------
# Thread Configuration
# -------------------------

config = {
    "configurable": {
        "thread_id": "approval-1"
    }
}

# -------------------------
# Initial Execution
# -------------------------

graph.invoke(
    {
        "request": "Purchase Laptop"
    },
    config=config
)

print("Workflow paused")

# -------------------------
# Resume Execution
# -------------------------

result = graph.invoke(
    Command(
        resume="approved"
    ),
    config=config
)

print(result)

---

## Expected Output

```python
Workflow paused

{
    'request': 'Purchase Laptop',
    'approval': 'approved',
    'result': 'Request was approved'
}
```

---

# Explanation

## Step 1 — Execute Workflow

The workflow starts:

```text
START
   ↓
review_request
```

Inside the node:

```python
interrupt(...)
```

is reached.

Execution pauses.

---

## Step 2 — State Is Saved

Because we compiled the graph with:

```python
InMemorySaver()
```

LangGraph stores:

```text
Current State
Current Node
Execution Position
```

This allows execution to continue later.

---

## Step 3 — Resume The Workflow

We resume using:

```python
Command(
    resume="approved"
)
```

The value:

```text
approved
```

becomes the return value of:

```python
interrupt(...)
```

Conceptually:

```python
decision = interrupt(...)

# decision becomes:
"approved"
```

---

## Step 4 — Continue Execution

The workflow proceeds to:

```text
finalize
```

which produces:

```python
{
    "result": "Request was approved"
}
```

---

## Why Command(resume=...) Matters

Without resume:

```text
Pause
      ↓
Workflow Stuck
```

With resume:

```text
Pause
      ↓
Human Decision
      ↓
Continue Execution
```

This enables long-running workflows that may wait:

```text
Minutes
Hours
Days
```

for human input.

---

## Interrupt + Resume Lifecycle

```text
Execute Workflow
        ↓
Interrupt
        ↓
Save State
        ↓
Wait
        ↓
Command(resume=...)
        ↓
Restore State
        ↓
Continue Execution
```

---

## Common Use Cases

### Approval Systems

```text
Request
   ↓
Interrupt
   ↓
Manager Approval
   ↓
Resume
```

---

### Legal Review

```text
Contract Draft
       ↓
Interrupt
       ↓
Legal Approval
       ↓
Resume
```

---

### AI Agent Oversight

```text
Agent Recommendation
          ↓
Interrupt
          ↓
Human Validation
          ↓
Resume
```

---

## Mental Model

Think of:

```python
interrupt(...)
```

as pressing:

```text
PAUSE
```

and:

```python
Command(resume=...)
```

as pressing:

```text
PLAY
```

The workflow continues from the exact location where it stopped.

---

## Key Takeaways

- Interrupts pause workflow execution.
- A checkpointer is required so execution can be resumed later.
- `Command(resume=value)` provides the value returned by `interrupt(...)`.
- The workflow resumes from the exact point where it paused.
- State and execution position are automatically restored.
- Interrupt + Resume is the foundation of Human-in-the-Loop workflows in LangGraph.