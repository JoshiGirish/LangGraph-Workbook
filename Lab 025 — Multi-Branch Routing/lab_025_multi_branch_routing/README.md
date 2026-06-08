# Lab 025 — Multi-Branch Routing

## Lab Intro
Conditional edges allow a graph to choose between two paths.
But real enterprise systems often require **more than two outcomes**.
Examples:
- risk levels: low / medium / high
- customer tiers: basic / premium / enterprise
- ticket routing: billing / technical / fraud / general
- content classification: safe / review / blocked / escalate
This introduces:
> **Multi-Branch Routing**
Instead of:
```text
A → (B or C)
```
we now support:
```text
A → (B or C or D or E)
```
A single decision node can route to many possible branches.
---
## Enterprise Analogy
Think of a support ticket system:
```text
START
↓
classify_ticket
↓
billing OR technical OR fraud OR general
↓
END
```
Each ticket is routed based on its category.
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
ticket_id: str
category: Optional[str] = None
priority: Optional[str] = None
# -------------------------
# Node 1 — Classify Ticket
# -------------------------
def classify_ticket(state: State):
# Simulated classification logic
if state.ticket_id.startswith("BILL"):
category = "billing"
elif state.ticket_id.startswith("TECH"):
category = "technical"
elif state.ticket_id.startswith("FRAUD"):
category = "fraud"
else:
category = "general"
return {
"category": category
}
# -------------------------
# Node 2A — Billing Handler
# -------------------------
def handle_billing(state: State):
return {"priority": "medium"}
# -------------------------
# Node 2B — Technical Handler
# -------------------------
def handle_technical(state: State):
return {"priority": "high"}
# -------------------------
# Node 2C — Fraud Handler
# -------------------------
def handle_fraud(state: State):
return {"priority": "critical"}
# -------------------------
# Node 2D — General Handler
# -------------------------
def handle_general(state: State):
return {"priority": "low"}
# -------------------------
# Router Function
# -------------------------
def route_ticket(state: State) -> Literal[
"handle_billing",
"handle_technical",
"handle_fraud",
"handle_general"
]:
return state.category
# -------------------------
# Build Graph
# -------------------------
builder = StateGraph(State)
builder.add_node("classify_ticket", classify_ticket)
builder.add_node("handle_billing", handle_billing)
builder.add_node("handle_technical", handle_technical)
builder.add_node("handle_fraud", handle_fraud)
builder.add_node("handle_general", handle_general)
builder.add_edge(START, "classify_ticket")
builder.add_conditional_edges(
"classify_ticket",
route_ticket,
{
"billing": "handle_billing",
"technical": "handle_technical",
"fraud": "handle_fraud",
"general": "handle_general"
}
)
builder.add_edge("handle_billing", END)
builder.add_edge("handle_technical", END)
builder.add_edge("handle_fraud", END)
builder.add_edge("handle_general", END)
graph = builder.compile()
# -------------------------
# Execute Graph
# -------------------------
tests = [
{"ticket_id": "BILL-1001"},
{"ticket_id": "TECH-2001"},
{"ticket_id": "FRAUD-9001"},
{"ticket_id": "GEN-0001"}
]
for t in tests:
print("\nINPUT:", t)
print(graph.invoke(t))
---
## Expected Output
```python
INPUT: {'ticket_id': 'BILL-1001'}
{'ticket_id': 'BILL-1001', 'category': 'billing', 'priority': 'medium'}
INPUT: {'ticket_id': 'TECH-2001'}
{'ticket_id': 'TECH-2001', 'category': 'technical', 'priority': 'high'}
INPUT: {'ticket_id': 'FRAUD-9001'}
{'ticket_id': 'FRAUD-9001', 'category': 'fraud', 'priority': 'critical'}
INPUT: {'ticket_id': 'GEN-0001'}
{'ticket_id': 'GEN-0001', 'category': 'general', 'priority': 'low'}
```
---
## Explanation
### What Is Multi-Branch Routing?
Multi-branch routing extends conditional edges:
```text
Single decision → Multiple possible paths
```
Instead of binary logic:
```python
if condition:
A
else:
B
```
we support:
```python
A → B / C / D / E
```
---
## Step 1 — Classification Node
The node:
```python
def classify_ticket(state):
```
assigns a category based on prefix:
```text
BILL → billing
TECH → technical
FRAUD → fraud
else → general
```
This simulates a real classifier (rule-based or ML-based).
---
## Step 2 — Router Function
```python
def route_ticket(state) -> Literal[...]:
return state.category
```
This function:
- reads classification result
- returns routing key
- determines next node
---
## Step 3 — Conditional Mapping
```python
builder.add_conditional_edges(
"classify_ticket",
route_ticket,
{
"billing": "handle_billing",
"technical": "handle_technical",
"fraud": "handle_fraud",
"general": "handle_general"
}
)
```
This creates a routing table:
```text
billing   → handle_billing
technical → handle_technical
fraud     → handle_fraud
general   → handle_general
```
---
## Step 4 — Execution Flow
### Example 1: Billing Ticket
```text
BILL-1001
↓
classify → billing
↓
handle_billing → priority = medium
```
---
### Example 2: Fraud Ticket
```text
FRAUD-9001
↓
classify → fraud
↓
handle_fraud → priority = critical
```
---
## Why Multi-Branch Routing Matters
Real enterprise workflows are rarely binary.
Examples:
### Customer Support Routing
```text
billing / technical / legal / abuse / general
```
---
### Risk Scoring Systems
```text
low / medium / high / critical
```
---
### Content Moderation
```text
allow / review / block / escalate
```
---
## Static vs Conditional vs Multi-Branch
### Static Edges
```text
A → B → C
```
Fixed sequence.
---
### Conditional Edges (Binary)
```text
A → (B or C)
```
Two outcomes.
---
### Multi-Branch Routing
```text
A → (B or C or D or E)
```
Many outcomes.
---
## Common Design Pattern
Multi-branch systems usually follow:
```text
1. Classify
2. Route
3. Handle branch
```
This pattern is widely used in production systems.
---
## Common Mistakes
### 1. Missing routing key
If `state.category` is None:
```text
Router fails or misroutes
```
Always ensure classification step runs first.
---
### 2. Inconsistent labels
Bad:
```text
"Billing" vs "billing"
```
Must match exactly.
---
### 3. Overloading router logic
Avoid putting heavy logic in router.
Keep it:
```text
Simple and deterministic
```
---
## Key Takeaways
- Multi-branch routing extends conditional edges to multiple outcomes.
- A classification node usually determines the routing key.
- Router functions map state values to specific nodes.
- This pattern is common in enterprise systems like support, fraud detection, and moderation.
- It provides structured decision-making at scale.
- Multi-branch routing is a core building block for complex LangGraph workflows.