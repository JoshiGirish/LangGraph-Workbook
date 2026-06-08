# Lab 017 — Runtime Context

## Lab Intro

In previous labs, nodes received only the workflow state.

However, real-world workflows often need access to information that should **not live inside the state itself**, such as:

- User information
- Environment settings
- API configuration
- Tenant metadata
- Request-specific parameters

This information is called **Runtime Context**.

A runtime context allows us to provide additional information during graph execution without polluting the shared state.

Think of it this way:

```text
State
=
Workflow Data

Context
=
Execution Environment
```

In this lab, we'll pass runtime context into a LangGraph workflow and use it inside our nodes.

Workflow:

```text
START
   |
create_greeting
   |
END
```

---

## Lab Code

```python
from typing import Optional

from pydantic import BaseModel
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langgraph.runtime import Runtime


# -------------------------
# State Model
# -------------------------
class State(BaseModel):
    name: str
    greeting: Optional[str] = None


# -------------------------
# Runtime Context Model
# -------------------------
class Context(BaseModel):
    company_name: str
    environment: str


# -------------------------
# Node
# -------------------------
def create_greeting(
    state: State,
    runtime: Runtime[Context]
):
    company = runtime.context.company_name
    environment = runtime.context.environment

    return {
        "greeting": (
            f"Hello {state.name}! "
            f"Welcome to {company} "
            f"({environment})."
        )
    }


# -------------------------
# Build Graph
# -------------------------
builder = StateGraph(
    State,
    context_schema=Context
)

builder.add_node(
    "create_greeting",
    create_greeting
)

builder.add_edge(
    START,
    "create_greeting"
)

builder.add_edge(
    "create_greeting",
    END
)

graph = builder.compile()


# -------------------------
# Execute Graph
# -------------------------
result = graph.invoke(
    {
        "name": "Alice"
    },
    context={
        "company_name": "LangGraph Academy",
        "environment": "development"
    }
)

print(result)
```

Expected Output:

```python
{
    'name': 'Alice',
    'greeting': (
        'Hello Alice! '
        'Welcome to LangGraph Academy '
        '(development).'
    )
}
```

---

## Explanation

### What Is Runtime Context?

Runtime context is execution-specific information that is available to nodes but is not stored in workflow state.

Example:

```text
State:
    Customer Name
    Order ID
    Status

Context:
    Environment
    API Keys
    Tenant Information
```

State evolves during execution.

Context remains available throughout execution.

---

## State vs Context

### State

```python
class State(BaseModel):
    name: str
    greeting: str | None = None
```

Represents workflow data.

Example:

```python
{
    "name": "Alice"
}
```

State is updated by nodes.

---

### Context

```python
class Context(BaseModel):
    company_name: str
    environment: str
```

Represents execution metadata.

Example:

```python
{
    "company_name": "LangGraph Academy",
    "environment": "development"
}
```

Context is not modified by nodes.

---

## Step 1 — Define Context Schema

```python
class Context(BaseModel):
    company_name: str
    environment: str
```

This creates a strongly-typed context model.

Benefits:

- Validation
- Autocomplete
- Type safety
- Better documentation

---

## Step 2 — Access Runtime Context

```python
def create_greeting(
    state: State,
    runtime: Runtime[Context]
):
```

LangGraph automatically injects:

```python
runtime
```

into the node.

Access values:

```python
runtime.context.company_name
```

and

```python
runtime.context.environment
```

just like a normal Pydantic model.

---

## Step 3 — Build Graph with Context Schema

```python
builder = StateGraph(
    State,
    context_schema=Context
)
```

This tells LangGraph:

```text
This graph expects a Context model.
```

Now every node can safely access:

```python
runtime.context
```

---

## Step 4 — Execute Graph

State:

```python
{
    "name": "Alice"
}
```

Context:

```python
{
    "company_name": "LangGraph Academy",
    "environment": "development"
}
```

Execution:

```python
graph.invoke(
    state,
    context=context
)
```

Both become available during runtime.

---

## State Evolution

### Initial State

```python
{
    "name": "Alice"
}
```

---

### Context

```python
{
    "company_name": "LangGraph Academy",
    "environment": "development"
}
```

---

### After create_greeting

```python
{
    "name": "Alice",
    "greeting": (
        "Hello Alice! "
        "Welcome to LangGraph Academy "
        "(development)."
    )
}
```

---

### Final State

```python
{
    "name": "Alice",
    "greeting": (
        "Hello Alice! "
        "Welcome to LangGraph Academy "
        "(development)."
    )
}
```

---

## Common Runtime Context Use Cases

### Multi-Tenant Applications

```python
runtime.context.tenant_id
```

---

### Environment-Aware Workflows

```python
runtime.context.environment
```

Examples:

- development
- staging
- production

---

### User Information

```python
runtime.context.user_id
```

---

### API Configuration

```python
runtime.context.api_version
```

---

### Feature Flags

```python
runtime.context.feature_enabled
```

---

## Why Context Should Not Be State

Bad:

```python
{
    "customer_name": "Alice",
    "environment": "production"
}
```

Environment is not workflow data.

---

Better:

```python
State:
{
    "customer_name": "Alice"
}

Context:
{
    "environment": "production"
}
```

This keeps responsibilities clean.

---

## Key Takeaways

- Runtime context provides execution-specific information to nodes.
- Context is separate from workflow state.
- Context does not evolve during execution.
- Use `Runtime[Context]` to access strongly-typed runtime data.
- Context is ideal for environment settings, user metadata, and configuration.
- Separating state from context leads to cleaner workflow design.