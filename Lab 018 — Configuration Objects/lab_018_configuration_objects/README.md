# Lab 018 — Configuration Objects

## Lab Intro

In the previous lab, we learned about Runtime Context, which provides execution-specific information to nodes.

Another important concept in LangGraph is the **Configuration Object**.

Configuration objects allow us to control graph execution without modifying the workflow state itself.

Typical examples include:

- User IDs
- Thread IDs
- Request IDs
- Execution settings
- Debug flags
- Model selection parameters

Unlike state, configuration values are:

- not part of business data
- not modified by nodes
- supplied at execution time

In this lab, we'll use a configuration object to customize node behavior.

Workflow:

```text
START
   |
generate_greeting
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
from langchain_core.runnables import RunnableConfig


# -------------------------
# State Model
# -------------------------
class State(BaseModel):
    name: str
    greeting: Optional[str] = None


# -------------------------
# Node
# -------------------------
def generate_greeting(
    state: State,
    config: RunnableConfig
):
    user_role = config["configurable"].get(
        "user_role",
        "guest"
    )

    return {
        "greeting": (
            f"Hello {state.name}! "
            f"Your role is '{user_role}'."
        )
    }


# -------------------------
# Build Graph
# -------------------------
builder = StateGraph(State)

builder.add_node(
    "generate_greeting",
    generate_greeting
)

builder.add_edge(
    START,
    "generate_greeting"
)

builder.add_edge(
    "generate_greeting",
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
    config={
        "configurable": {
            "user_role": "admin"
        }
    }
)

print(result)
```

Expected Output:

```python
{
    'name': 'Alice',
    'greeting': "Hello Alice! Your role is 'admin'."
}
```

---

## Explanation

### What Is a Configuration Object?

A configuration object contains execution-time settings.

Example:

```python
{
    "configurable": {
        "user_role": "admin"
    }
}
```

This information:

- influences execution
- is available to nodes
- does not become part of workflow state

---

## State vs Configuration

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

State evolves during execution.

---

### Configuration

```python
{
    "configurable": {
        "user_role": "admin"
    }
}
```

Represents execution settings.

Configuration does not evolve.

---

## Step 1 — Access RunnableConfig

```python
from langchain_core.runnables import RunnableConfig
```

LangGraph automatically injects:

```python
config
```

when the node declares it as a parameter.

Example:

```python
def node(
    state: State,
    config: RunnableConfig
):
```

---

## Step 2 — Read Configuration Values

```python
user_role = config["configurable"].get(
    "user_role",
    "guest"
)
```

The `configurable` section is commonly used for custom execution parameters.

If no value exists:

```python
"guest"
```

is used as the default.

---

## Step 3 — Generate Dynamic Output

Using configuration values:

```python
return {
    "greeting": (
        f"Hello {state.name}! "
        f"Your role is '{user_role}'."
    )
}
```

The node behavior changes depending on the supplied configuration.

---

## Step 4 — Execute with Configuration

```python
result = graph.invoke(
    {
        "name": "Alice"
    },
    config={
        "configurable": {
            "user_role": "admin"
        }
    }
)
```

State:

```python
{
    "name": "Alice"
}
```

Configuration:

```python
{
    "configurable": {
        "user_role": "admin"
    }
}
```

---

## State Evolution

### Initial State

```python
{
    "name": "Alice"
}
```

---

### Configuration

```python
{
    "configurable": {
        "user_role": "admin"
    }
}
```

---

### After generate_greeting

```python
{
    "name": "Alice",
    "greeting": (
        "Hello Alice! "
        "Your role is 'admin'."
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
        "Your role is 'admin'."
    )
}
```

---

## Common Configuration Use Cases

### Thread Management

```python
config = {
    "configurable": {
        "thread_id": "123"
    }
}
```

Used heavily with checkpointing.

---

### User Identity

```python
config = {
    "configurable": {
        "user_id": "user_001"
    }
}
```

---

### Debug Mode

```python
config = {
    "configurable": {
        "debug": True
    }
}
```

---

### Model Selection

```python
config = {
    "configurable": {
        "model": "gpt-5"
    }
}
```

---

### Request Tracking

```python
config = {
    "configurable": {
        "request_id": "req_789"
    }
}
```

Useful for observability and logging.

---

## Configuration vs Runtime Context

A useful rule of thumb:

### Runtime Context

Used for:

- environment metadata
- tenant information
- application context

Example:

```python
runtime.context.environment
```

---

### Configuration

Used for:

- execution settings
- thread IDs
- user IDs
- debugging flags

Example:

```python
config["configurable"]["thread_id"]
```

Both are available at runtime but serve different purposes.

---

## Key Takeaways

- Configuration objects provide execution-time settings.
- Configuration is separate from workflow state.
- Nodes can access configuration using `RunnableConfig`.
- The `configurable` section is commonly used for custom parameters.
- Configuration is ideal for thread IDs, user IDs, debug flags, and execution settings.
- State stores business data; configuration controls execution behavior.