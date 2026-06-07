# Lab 011 — State Validation Patterns

## Lab Intro

As LangGraph workflows become larger, ensuring that state contains valid and expected data becomes increasingly important.

Without validation, workflows may:

- Process incomplete data
- Generate incorrect results
- Fail unexpectedly
- Produce difficult-to-debug errors

State validation helps us verify that incoming data satisfies business requirements before the workflow continues.

In this lab, we'll build a simple customer registration workflow that validates state before processing it.

Workflow:

```text
START
  |
validate_customer
  |
create_profile
  |
END
```

---

## Lab Code

```python

from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph import START, END


# State Definition
class State(TypedDict, total=False):
    name: str
    email: str
    is_valid: bool
    profile: str


# Validation Node
def validate_customer(state: State):

    if not state.get("name"):
        raise ValueError(
            "Customer name is required"
        )

    if not state.get("email"):
        raise ValueError(
            "Customer email is required"
        )

    return {
        "is_valid": True
    }


# Profile Creation Node
def create_profile(state: State):
    return {
        "profile": (
            f"{state['name']} "
            f"({state['email']})"
        )
    }


# Build Graph
builder = StateGraph(State)

builder.add_node(
    "validate_customer",
    validate_customer
)

builder.add_node(
    "create_profile",
    create_profile
)

builder.add_edge(
    START,
    "validate_customer"
)

builder.add_edge(
    "validate_customer",
    "create_profile"
)

builder.add_edge(
    "create_profile",
    END
)


# Compile Graph
graph = builder.compile()


# Execute Graph
result = graph.invoke(
    {
        "name": "Alice",
        "email": "alice@example.com"
    }
)

print(result)
```

Expected Output:

```python
{
    'name': 'Alice',
    'email': 'alice@example.com',
    'is_valid': True,
    'profile': 'Alice (alice@example.com)'
}
```

---

## Explanation

### Why State Validation Matters

Consider the following input:

```python
{
    "name": "Alice"
}
```

The email field is missing.

If later nodes assume that email exists:

```python
state["email"]
```

the workflow will fail.

Validation helps catch these issues early and provides clear error messages.

---

### State Definition

```python
class State(TypedDict, total=False):
    name: str
    email: str
    is_valid: bool
    profile: str
```

The workflow expects:

- Customer name
- Customer email

Additional fields are added during execution.

---

### Validation Node

```python
def validate_customer(state):
```

This node verifies that required fields exist.

Validation rules:

```python
name must exist
email must exist
```

If validation fails:

```python
raise ValueError(...)
```

The workflow immediately stops and returns an error.

If validation succeeds:

```python
{
    "is_valid": True
}
```

is added to the state.

---

### Profile Creation Node

```python
def create_profile(state):
```

Since validation already ran, this node can safely assume:

```python
state["name"]
state["email"]
```

exist.

Output:

```python
{
    "profile": (
        "Alice "
        "(alice@example.com)"
    )
}
```

---

### Graph Construction

Execution flow:

```text
START
  ↓
validate_customer
  ↓
create_profile
  ↓
END
```

The validation node acts as a gatekeeper.

Only valid state proceeds further into the workflow.

---

### State Evolution

Initial State:

```python
{
    "name": "Alice",
    "email": "alice@example.com"
}
```

---

After `validate_customer`:

```python
{
    "name": "Alice",
    "email": "alice@example.com",
    "is_valid": True
}
```

---

After `create_profile`:

```python
{
    "name": "Alice",
    "email": "alice@example.com",
    "is_valid": True,
    "profile": (
        "Alice "
        "(alice@example.com)"
    )
}
```

---

Final State:

```python
{
    "name": "Alice",
    "email": "alice@example.com",
    "is_valid": True,
    "profile": (
        "Alice "
        "(alice@example.com)"
    )
}
```

---

### Validation Failure Example

Input:

```python
{
    "name": "Alice"
}
```

Execution:

```python
graph.invoke(
    {
        "name": "Alice"
    }
)
```

Result:

```python
ValueError:
Customer email is required
```

The workflow stops before reaching downstream nodes.

This prevents invalid data from propagating through the system.

---

### Pattern 1: Required Fields

The most common validation pattern checks for required fields.

Example:

```python
if not state.get("customer_id"):
    raise ValueError(
        "customer_id is required"
    )
```

---

### Pattern 2: Numeric Validation

Example:

```python
if state["amount"] <= 0:
    raise ValueError(
        "Amount must be positive"
    )
```

Useful for:

- Orders
- Payments
- Loan applications

---

### Pattern 3: Allowed Values

Example:

```python
allowed_statuses = [
    "open",
    "closed",
    "pending"
]

if state["status"] not in allowed_statuses:
    raise ValueError(
        "Invalid status"
    )
```

Useful for:

- Workflow states
- Approval processes
- Ticketing systems

---

### Pattern 4: Business Rule Validation

Example:

```python
if state["age"] < 18:
    raise ValueError(
        "Applicant must be 18+"
    )
```

Validation can enforce real business rules before processing continues.

---

### Pydantic-Based Validation

As workflows become more complex, Pydantic can handle validation automatically.

Example:

```python
from pydantic import BaseModel


class CustomerState(BaseModel):
    name: str
    email: str
```

Pydantic automatically validates:

- Required fields
- Types
- Constraints

This is often preferred in production systems.

---

### Where Validation Is Commonly Used

Validation is common in:

#### Customer Onboarding

```python
{
    "name": "Alice",
    "email": "alice@example.com"
}
```

#### Order Processing

```python
{
    "order_id": "123",
    "amount": 500
}
```

#### Loan Applications

```python
{
    "applicant": "John",
    "income": 100000
}
```

#### Agent Workflows

```python
{
    "task": "Research AI trends"
}
```

Validating state early helps ensure reliable workflow execution.

---

## Key Takeaways

- State validation prevents invalid data from entering workflows.
- Validation nodes act as gatekeepers for downstream processing.
- Required fields should be validated as early as possible.
- Business rules can be enforced through validation logic.
- Validation failures should stop workflow execution immediately.
- Pydantic provides powerful validation capabilities for larger systems.
- Reliable workflows begin with reliable state.