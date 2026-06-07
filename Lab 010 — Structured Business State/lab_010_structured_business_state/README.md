# Lab 010 — Structured Business State

## Lab Intro

So far, our state has contained simple fields such as strings, booleans, and message lists.

In real-world applications, workflows often operate on business data that contains multiple related fields.

Examples include:

- Customer records
- Orders
- Support tickets
- Loan applications
- Insurance claims
- Employee onboarding requests

Instead of storing isolated values, we can design a state schema that represents an entire business process.

In this lab, we'll build a simple order-processing workflow that updates a structured business state as it moves through the graph.

Workflow:

```text
START
  |
validate_order
  |
calculate_discount
  |
generate_summary
  |
END
```

---

## Lab Code

```python
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph import START, END


# Structured Business State
class State(TypedDict, total=False):
    customer_name: str
    order_amount: float
    order_valid: bool
    discount_percent: int
    final_amount: float
    summary: str


# Validate order
def validate_order(state: State):
    return {
        "order_valid": state["order_amount"] > 0
    }


# Calculate discount
def calculate_discount(state: State):
    discount = 10 if state["order_amount"] >= 1000 else 0

    final_amount = (
        state["order_amount"]
        * (1 - discount / 100)
    )

    return {
        "discount_percent": discount,
        "final_amount": final_amount
    }


# Generate summary
def generate_summary(state: State):
    return {
        "summary": (
            f"Customer: {state['customer_name']} | "
            f"Amount: {state['order_amount']} | "
            f"Discount: {state['discount_percent']}% | "
            f"Final Amount: {state['final_amount']}"
        )
    }


# Build graph
builder = StateGraph(State)

builder.add_node(
    "validate_order",
    validate_order
)

builder.add_node(
    "calculate_discount",
    calculate_discount
)

builder.add_node(
    "generate_summary",
    generate_summary
)

builder.add_edge(
    START,
    "validate_order"
)

builder.add_edge(
    "validate_order",
    "calculate_discount"
)

builder.add_edge(
    "calculate_discount",
    "generate_summary"
)

builder.add_edge(
    "generate_summary",
    END
)


# Compile graph
graph = builder.compile()


# Execute graph
result = graph.invoke(
    {
        "customer_name": "Alice",
        "order_amount": 1500
    }
)

print(result)
```

Expected Output:

```python
{
    'customer_name': 'Alice',
    'order_amount': 1500,
    'order_valid': True,
    'discount_percent': 10,
    'final_amount': 1350.0,
    'summary': (
        'Customer: Alice | '
        'Amount: 1500 | '
        'Discount: 10% | '
        'Final Amount: 1350.0'
    )
}
```

---

## Explanation

### What Is Structured Business State?

A structured business state models an entire business process instead of a single value.

For example:

```python
{
    "customer_name": "Alice",
    "order_amount": 1500,
    "discount_percent": 10,
    "final_amount": 1350
}
```

All information related to the workflow lives inside a single shared state object.

This makes workflows easier to understand, debug, and extend.

---

### State Definition

```python
class State(TypedDict, total=False):
    customer_name: str
    order_amount: float
    order_valid: bool
    discount_percent: int
    final_amount: float
    summary: str
```

This state represents an order-processing workflow.

Fields are added progressively as nodes execute.

Initial state:

```python
{
    "customer_name": "Alice",
    "order_amount": 1500
}
```

Later nodes enrich the state with additional business information.

---

### Validate Order Node

```python
def validate_order(state):
    return {
        "order_valid": state["order_amount"] > 0
    }
```

This node performs a simple validation.

Input:

```python
{
    "order_amount": 1500
}
```

Output:

```python
{
    "order_valid": True
}
```

The workflow now knows whether the order is valid.

---

### Calculate Discount Node

```python
def calculate_discount(state):
```

Business rule:

```python
Order Amount >= 1000
```

receives:

```python
10% discount
```

For an order amount of:

```python
1500
```

Discount:

```python
150
```

Final amount:

```python
1350
```

Node output:

```python
{
    "discount_percent": 10,
    "final_amount": 1350
}
```

---

### Generate Summary Node

```python
def generate_summary(state):
```

This node creates a human-readable summary using all information accumulated so far.

Output:

```python
{
    "summary": (
        "Customer: Alice | "
        "Amount: 1500 | "
        "Discount: 10% | "
        "Final Amount: 1350"
    )
}
```

---

### Graph Construction

Execution flow:

```text
START
  ↓
validate_order
  ↓
calculate_discount
  ↓
generate_summary
  ↓
END
```

Each node adds new business information to the state.

The state becomes richer as the workflow progresses.

---

### State Evolution

Initial State:

```python
{
    "customer_name": "Alice",
    "order_amount": 1500
}
```

---

After `validate_order`:

```python
{
    "customer_name": "Alice",
    "order_amount": 1500,
    "order_valid": True
}
```

---

After `calculate_discount`:

```python
{
    "customer_name": "Alice",
    "order_amount": 1500,
    "order_valid": True,
    "discount_percent": 10,
    "final_amount": 1350.0
}
```

---

After `generate_summary`:

```python
{
    "customer_name": "Alice",
    "order_amount": 1500,
    "order_valid": True,
    "discount_percent": 10,
    "final_amount": 1350.0,
    "summary": (
        "Customer: Alice | "
        "Amount: 1500 | "
        "Discount: 10% | "
        "Final Amount: 1350.0"
    )
}
```

---

Final State:

```python
{
    "customer_name": "Alice",
    "order_amount": 1500,
    "order_valid": True,
    "discount_percent": 10,
    "final_amount": 1350.0,
    "summary": (
        "Customer: Alice | "
        "Amount: 1500 | "
        "Discount: 10% | "
        "Final Amount: 1350.0"
    )
}
```

---

### Why Structured Business State Matters

Most production LangGraph systems are built around structured state models.

Examples include:

#### Customer Support

```python
{
    "ticket_id": "T123",
    "customer": "Alice",
    "priority": "High",
    "status": "Open"
}
```

#### Loan Processing

```python
{
    "applicant": "John",
    "credit_score": 750,
    "income": 100000,
    "decision": "Approved"
}
```

#### Insurance Claims

```python
{
    "claim_id": "C456",
    "amount": 5000,
    "fraud_check": True,
    "status": "Approved"
}
```

Designing a good state schema is one of the most important skills when building LangGraph applications.

---

## Key Takeaways

- Structured business state models an entire business process.
- Multiple related fields can be stored in a single shared state object.
- Nodes progressively enrich the state as the workflow executes.
- Business workflows become easier to understand when state is well organized.
- Most production LangGraph systems rely on structured state models.
- Good state design is a foundational skill for building scalable workflows.