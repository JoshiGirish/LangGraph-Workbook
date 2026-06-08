# Lab 022 — Node Testing Strategies

## Lab Intro

As LangGraph applications grow, workflows become increasingly dependent on individual nodes.

A node may:

- validate data
- call APIs
- transform information
- make decisions
- update state

If a node contains a bug, the entire workflow may behave incorrectly.

For this reason, production teams do not only test complete workflows.

They also test nodes independently.

This practice is called:

> **Node Testing**

Instead of testing:

```text
Entire Graph
```

we test:

```text
Single Node
```

in isolation.

This makes debugging easier and helps identify problems early.

Workflow:

```text
START
   |
calculate_discount
   |
END
```

---

## Lab Code

```python
from typing import Optional

from pydantic import BaseModel


# -------------------------
# State Model
# -------------------------

class State(BaseModel):
    customer_type: str

    discount: Optional[int] = None


# -------------------------
# Node
# -------------------------

def calculate_discount(state: State):

    if state.customer_type == "premium":

        return {
            "discount": 20
        }

    return {
        "discount": 5
    }


# -------------------------
# Node Testing
# -------------------------

premium_state = State(
    customer_type="premium"
)

regular_state = State(
    customer_type="regular"
)

premium_result = calculate_discount(
    premium_state
)

regular_result = calculate_discount(
    regular_state
)

print("PREMIUM RESULT")
print(premium_result)

print()

print("REGULAR RESULT")
print(regular_result)
```

---

## Expected Output

```python
PREMIUM RESULT

{
    'discount': 20
}

REGULAR RESULT

{
    'discount': 5
}
```

Notice:

```text
No Graph
No START
No END
No invoke()
```

We are testing the node directly.

---

## Explanation

### What Is Node Testing?

Node testing means executing a node as a regular Python function.

Instead of:

```python
graph.invoke(...)
```

we directly call:

```python
calculate_discount(state)
```

This allows us to verify:

- inputs
- outputs
- business rules

without involving the rest of the workflow.

---

## Why Test Nodes Independently?

Imagine a workflow:

```text
Node A
   ↓
Node B
   ↓
Node C
```

A bug appears.

Without node testing:

```text
Investigate Entire Workflow
```

With node testing:

```text
Test A
Test B
Test C
```

and quickly isolate the problem.

---

## Step 1 — Define the State

```python
class State(BaseModel):
```

Contains:

```python
customer_type: str
discount: Optional[int]
```

This represents customer information.

---

## Step 2 — Create Business Logic

The node:

```python
def calculate_discount(state):
```

contains a simple rule.

Premium customer:

```python
20%
```

Regular customer:

```python
5%
```

---

## Step 3 — Create Test Inputs

Premium scenario:

```python
premium_state = State(
    customer_type="premium"
)
```

Regular scenario:

```python
regular_state = State(
    customer_type="regular"
)
```

These are controlled test cases.

---

## Step 4 — Execute the Node Directly

Instead of:

```python
graph.invoke(...)
```

we call:

```python
calculate_discount(
    premium_state
)
```

just like any normal Python function.

---

## Step 5 — Verify Results

Premium result:

```python
{
    "discount": 20
}
```

Regular result:

```python
{
    "discount": 5
}
```

The node behaves correctly.

---

## Why This Is Valuable

Suppose the business rule changes.

Someone accidentally writes:

```python
if state.customer_type == "premium":
    return {
        "discount": 2
    }
```

Node testing immediately reveals:

```text
Expected: 20
Actual: 2
```

before the workflow reaches production.

---

## Enterprise Example

Consider:

```text
Loan Approval Workflow

START
   ↓
validate_income
   ↓
calculate_risk
   ↓
approve_loan
   ↓
END
```

If:

```text
calculate_risk
```

produces incorrect values, the entire workflow becomes unreliable.

Teams therefore test:

```python
calculate_risk(...)
```

independently using many inputs.

This is faster than running the entire workflow repeatedly.

---

## Basic Assertion Testing

Instead of printing:

```python
result = calculate_discount(
    premium_state
)

assert result["discount"] == 20
```

If the node returns:

```python
{
    "discount": 10
}
```

Python raises:

```text
AssertionError
```

indicating a failed test.

---

## Example Using Assertions

```python
premium_result = calculate_discount(
    State(customer_type="premium")
)

assert premium_result["discount"] == 20

regular_result = calculate_discount(
    State(customer_type="regular")
)

assert regular_result["discount"] == 5

print("All tests passed.")
```

Output:

```text
All tests passed.
```

if everything works correctly.

---

## Testing Edge Cases

Good tests also cover unusual inputs.

Example:

```python
State(customer_type="")
```

or:

```python
State(customer_type="unknown")
```

Questions:

```text
What should happen?
Should a discount be assigned?
Should an error be raised?
```

Testing edge cases improves reliability.

---

## Common Node Testing Strategy

For each node test:

```text
Create State
      ↓
Execute Node
      ↓
Verify Output
```

This is the foundation of unit testing.

---

## Why Node Testing Matters in LangGraph

As workflows grow:

```text
10 Nodes
20 Nodes
50 Nodes
```

debugging entire graphs becomes harder.

Node testing provides:

- faster feedback
- easier debugging
- isolated validation
- confidence during refactoring

Production teams rely heavily on node-level testing.

---

## Node Testing vs Graph Testing

### Node Testing

Tests:

```text
One Node
```

Focus:

```text
Business Logic
```

Fast:

```text
Yes
```

---

### Graph Testing

Tests:

```text
Entire Workflow
```

Focus:

```text
Workflow Behavior
```

Fast:

```text
Usually No
```

Both are valuable and often used together.

---

## Key Takeaways

- Nodes can be tested independently of a LangGraph workflow.
- A node is just a Python function that receives state and returns updates.
- Node testing helps validate business logic quickly.
- Testing nodes directly simplifies debugging.
- Assertions provide a simple way to verify expected behavior.
- Edge cases should be tested alongside normal scenarios.
- Production LangGraph applications typically use both node tests and full workflow tests.