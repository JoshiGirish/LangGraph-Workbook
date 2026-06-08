# Lab 013 — Designing Large Shared State Models

## Lab Intro

As LangGraph applications grow from simple pipelines into full systems, the state stops being a small dictionary and becomes a **system-wide data model**.

At this stage, poor state design becomes one of the biggest causes of:

- tangled workflows
- hidden dependencies
- brittle nodes
- hard-to-debug systems

Large shared state models are about designing state like a **software architecture layer**, not just a container.

In this lab, we design a realistic multi-domain state for a customer support system and use it across multiple nodes.

Workflow:

```text
START
   |
ingest_ticket
   |
enrich_context
   |
analyze_issue
   |
generate_response
   |
END
```

---

## Lab Code

```python
from typing_extensions import TypedDict
from typing import Literal

from langgraph.graph import StateGraph
from langgraph.graph import START, END


# Large Shared State Model
class State(TypedDict, total=False):
    # Identity
    ticket_id: str
    customer_id: str
    customer_name: str

    # Ticket Data
    subject: str
    description: str
    priority: Literal["low", "medium", "high"]

    # Enriched Context
    sentiment: str
    category: str

    # Analysis
    issue_summary: str
    suggested_action: str

    # Output
    final_response: str


# Step 1 — Ingest Ticket
def ingest_ticket(state: State):
    return {
        "ticket_id": "T-1001",
        "customer_id": "C-501",
        "customer_name": "Alice",
        "subject": "Payment not processed",
        "description": "My payment failed but amount was deducted",
        "priority": "high"
    }


# Step 2 — Enrich Context
def enrich_context(state: State):
    return {
        "sentiment": "frustrated",
        "category": "payment_issue"
    }


# Step 3 — Analyze Issue
def analyze_issue(state: State):
    return {
        "issue_summary": (
            f"{state['customer_name']} is facing "
            f"{state['category']} with "
            f"{state['priority']} priority"
        ),
        "suggested_action": "Investigate transaction logs and initiate refund if needed"
    }


# Step 4 — Generate Response
def generate_response(state: State):
    return {
        "final_response": (
            f"Hello {state['customer_name']}, "
            f"we are looking into your issue regarding '{state['subject']}'. "
            f"Our team will resolve it shortly."
        )
    }


# Build Graph
builder = StateGraph(State)

builder.add_node("ingest_ticket", ingest_ticket)
builder.add_node("enrich_context", enrich_context)
builder.add_node("analyze_issue", analyze_issue)
builder.add_node("generate_response", generate_response)

builder.add_edge(START, "ingest_ticket")
builder.add_edge("ingest_ticket", "enrich_context")
builder.add_edge("enrich_context", "analyze_issue")
builder.add_edge("analyze_issue", "generate_response")
builder.add_edge("generate_response", END)

graph = builder.compile()


# Execute Graph
result = graph.invoke({})

print(result)
```

Expected Output (approx):

```python
{
    'ticket_id': 'T-1001',
    'customer_id': 'C-501',
    'customer_name': 'Alice',
    'subject': 'Payment not processed',
    'description': 'My payment failed but amount was deducted',
    'priority': 'high',
    'sentiment': 'frustrated',
    'category': 'payment_issue',
    'issue_summary': 'Alice is facing payment_issue with high priority',
    'suggested_action': 'Investigate transaction logs and initiate refund if needed',
    'final_response': "Hello Alice, we are looking into your issue regarding 'Payment not processed'. Our team will resolve it shortly."
}
```

---

## Explanation

### What Is a Large Shared State Model?

A large shared state model is a **single unified schema** that represents an entire workflow domain.

Instead of:

- passing small isolated variables
- or fragmented state objects

we define one **comprehensive state contract** that all nodes share.

---

## Step 1 — State Design

```python
class State(TypedDict, total=False):
```

This state is divided into logical sections:

### Identity

- ticket_id
- customer_id
- customer_name

### Ticket Data

- subject
- description
- priority

### Enriched Context

- sentiment
- category

### Analysis

- issue_summary
- suggested_action

### Output

- final_response

This structure mirrors real enterprise systems.

---

## Step 2 — Ingest Ticket Node

```python
def ingest_ticket(state: State):
```

This node simulates incoming data ingestion.

It populates the base ticket information.

Output:

- customer identity
- issue details
- priority level

This becomes the foundation for all downstream processing.

---

## Step 3 — Enrich Context Node

```python
def enrich_context(state: State):
```

This node adds semantic understanding:

- sentiment analysis
- issue classification

This step simulates an AI enrichment layer.

---

## Step 4 — Analyze Issue Node

```python
def analyze_issue(state: State):
```

This node combines multiple fields:

- customer data
- category
- priority

It produces:

- a structured issue summary
- a suggested action plan

This is where reasoning begins to appear in the workflow.

---

## Step 5 — Generate Response Node

```python
def generate_response(state: State):
```

This node generates a user-facing message using all prior context.

It demonstrates how downstream nodes depend on **accumulated state knowledge**.

---

## Step 6 — Graph Construction

Execution flow:

```text
START
   ↓
ingest_ticket
   ↓
enrich_context
   ↓
analyze_issue
   ↓
generate_response
   ↓
END
```

Each stage adds a new layer of meaning to the state.

---

## State Evolution

### Initial State

```python
{}
```

---

### After ingest_ticket

```python
{
    "ticket_id": "T-1001",
    "customer_id": "C-501",
    "customer_name": "Alice",
    "subject": "Payment not processed",
    "description": "My payment failed but amount was deducted",
    "priority": "high"
}
```

---

### After enrich_context

```python
{
    "sentiment": "frustrated",
    "category": "payment_issue"
}
```

---

### After analyze_issue

```python
{
    "issue_summary": "Alice is facing payment_issue with high priority",
    "suggested_action": "Investigate transaction logs and initiate refund if needed"
}
```

---

### After generate_response

```python
{
    "final_response": "Hello Alice, we are looking into your issue regarding 'Payment not processed'. Our team will resolve it shortly."
}
```

---

## Why Large State Models Matter

Large state models are essential for:

### 1. Enterprise Workflows
Customer support, finance, HR systems

### 2. Multi-Agent Systems
Shared memory between agents

### 3. AI Orchestration
Tool calling + reasoning + memory

### 4. Observability
Every decision is stored in state

---

## Key Takeaways

- Large shared state models define the full workflow domain.
- State should be designed like a system architecture, not a dictionary.
- Each node contributes a logical layer of transformation.
- Good state design reduces complexity in large LangGraph systems.
- Structured state is essential for enterprise-grade AI applications.
- Think in terms of domains: identity, input, enrichment, reasoning, output.