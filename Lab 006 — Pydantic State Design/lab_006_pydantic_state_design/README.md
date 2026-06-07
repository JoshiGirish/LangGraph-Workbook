# Lab 006 — Pydantic State Design

## Learning Objectives

By the end of this lab, you will:

- Understand how to define state using Pydantic models
- Compare `Pydantic` and `TypedDict` state schemas
- Create a graph that uses a Pydantic state model
- Validate state data using type-safe models

---

## Concept Overview

In previous labs, we defined state using `TypedDict`.

```python
class State(TypedDict):
    message: str
```

For simple workflows, this approach works well.

As workflows become larger and more complex, you may want:

- Validation
- Default values
- Better documentation
- Stronger type safety

Pydantic models provide these capabilities.

```python
from pydantic import BaseModel

class State(BaseModel):
    message: str
```

---

## TypedDict vs Pydantic

### TypedDict

```python
class State(TypedDict):
    message: str
```

Advantages:

- Lightweight
- Simple
- Fast

---

### Pydantic

```python
from pydantic import BaseModel

class State(BaseModel):
    message: str
```

Advantages:

- Validation
- Default values
- Rich model behavior
- Better support for complex applications

---

## Workflow Diagram

```text
START
   |
greet
   |
 END
```

---

## Step 1 — Imports

```python
from pydantic import BaseModel

from langgraph.graph import StateGraph
from langgraph.graph import START, END
```

---

## Step 2 — Define State

```python
class State(BaseModel):
    message: str
```

This model represents the state shared across the workflow.

---

## Step 3 — Create a Node

```python
def greet(state: State):
    return {
        "message": f"Hello {state.message}"
    }
```

Notice that fields can be accessed using dot notation.

```python
state.message
```

instead of:

```python
state["message"]
```

---

## Step 4 — Build the Graph

```python
builder = StateGraph(State)

builder.add_node("greet", greet)

builder.add_edge(START, "greet")
builder.add_edge("greet", END)
```

---

## Step 5 — Compile the Graph

```python
graph = builder.compile()
```

---

## Step 6 — Execute the Graph

Expected output:

```python
{
    "message": "Hello LangGraph"
}
```

```python
result = graph.invoke(
    {
        "message": "LangGraph"
    }
)
```

---

## Understanding the State Flow

### Initial State

```python
{
    "message": "LangGraph"
}
```

---

### Input to greet

```python
State(
    message="LangGraph"
)
```

---

### Output from greet

```python
{
    "message": "Hello LangGraph"
}
```

---

### Final State

```python
{
    "message": "Hello LangGraph"
}
```

---

## Using Default Values

Pydantic models support defaults.

```python
class State(BaseModel):
    message: str
    status: str = "pending"
```

Example:

```python
state = State(message="Hello")
```

Result:

```python
State(
    message="Hello",
    status="pending"
)
```

---

## Using Multiple Fields

```python
class State(BaseModel):
    first_name: str
    last_name: str
    age: int
```

Node:

```python
def profile(state: State):
    return {
        "summary": (
            f"{state.first_name} "
            f"{state.last_name} "
            f"is {state.age} years old"
        )
    }
```

---

## Key Takeaways

- Pydantic models can be used as LangGraph state schemas.
- Pydantic provides validation and default values.
- Fields can be accessed using dot notation.
- Pydantic is useful for larger and more complex workflows.
- Both `TypedDict` and `Pydantic` are valid state design choices.