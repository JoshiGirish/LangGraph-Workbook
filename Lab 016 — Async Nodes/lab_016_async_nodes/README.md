# Lab 016 — Async Nodes

## Lab Intro

In real-world LangGraph systems, not every operation is instantaneous.

Many tasks involve waiting on external systems such as:

- APIs
- Databases
- LLM calls
- Microservices
- Tool executions

To handle this efficiently, LangGraph supports **async nodes**.

Async nodes allow workflows to:

- run non-blocking operations
- improve throughput
- integrate cleanly with async APIs
- scale better in production systems

In this lab, we build a simple async workflow using **Pydantic state models**.

Workflow:

```text
START
   |
fetch_user_async
   |
generate_greeting_async
   |
END
```

---

## Lab Code

```python
import asyncio
from typing import Optional
from pydantic import BaseModel

from langgraph.graph import StateGraph
from langgraph.graph import START, END


# -------------------------
# Pydantic State Model
# -------------------------
class State(BaseModel):
    user_id: int
    user_name: Optional[str] = None
    greeting: Optional[str] = None


# -------------------------
# Async Node 1
# Simulates API call / DB fetch
# -------------------------
async def fetch_user_async(state: State):
    await asyncio.sleep(1)  # simulate IO delay

    # pretend we fetched this from DB
    return {
        "user_name": f"User_{state.user_id}"
    }


# -------------------------
# Async Node 2
# Simulates LLM / service call
# -------------------------
async def generate_greeting_async(state: State):
    await asyncio.sleep(1)  # simulate LLM delay

    return {
        "greeting": f"Hello {state.user_name}, welcome to LangGraph!"
    }


# -------------------------
# Build Graph
# -------------------------
builder = StateGraph(State)

builder.add_node("fetch_user_async", fetch_user_async)
builder.add_node("generate_greeting_async", generate_greeting_async)

builder.add_edge(START, "fetch_user_async")
builder.add_edge("fetch_user_async", "generate_greeting_async")
builder.add_edge("generate_greeting_async", END)

graph = builder.compile()

# -------------------------
# Execute Graph (async)
# -------------------------
async def run():
    result = await graph.ainvoke(
        {
            "user_id": 42
        }
    )
    print(result)


await run()
```

Expected Output:

```python
{
    "user_id": 42,
    "user_name": "User_42",
    "greeting": "Hello User_42, welcome to LangGraph!"
}
```

---

## Explanation

### Why Async Nodes Matter

Synchronous nodes block execution:

```text
Node 1 → wait → Node 2 → wait → Node 3
```

Async nodes allow LangGraph to:

- wait efficiently for I/O
- integrate with async LLM APIs
- improve system scalability

---

## Step 1 — Pydantic State Model

```python
class State(BaseModel):
    user_id: int
    user_name: Optional[str] = None
    greeting: Optional[str] = None
```

We define:

- required field: `user_id`
- computed fields:
  - `user_name`
  - `greeting`

This represents a typical **progressively enriched state model**.

---

## Step 2 — Async Node: fetch_user_async

```python
async def fetch_user_async(state: State):
```

### Behavior

- simulates DB/API call using `asyncio.sleep`
- derives user name from user_id

Input:

```python
state.user_id = 42
```

Output:

```python
{
    "user_name": "User_42"
}
```

---

## Step 3 — Async Node: generate_greeting_async

```python
async def generate_greeting_async(state: State):
```

### Behavior

- simulates LLM or external service call
- uses previously fetched `user_name`

Input:

```python
state.user_name = "User_42"
```

Output:

```python
{
    "greeting": "Hello User_42, welcome to LangGraph!"
}
```

---

## Step 4 — Graph Construction

```python
builder = StateGraph(State)

builder.add_node("fetch_user_async", fetch_user_async)
builder.add_node("generate_greeting_async", generate_greeting_async)

builder.add_edge(START, "fetch_user_async")
builder.add_edge("fetch_user_async", "generate_greeting_async")
builder.add_edge("generate_greeting_async", END)
```

Execution flow:

```text
START
  ↓
fetch_user_async
  ↓
generate_greeting_async
  ↓
END
```

---

## Step 5 — Async Execution

```python
result = await graph.ainvoke({"user_id": 42})
```

Key difference from sync execution:

| Sync | Async |
|------|-------|
| `invoke()` | `ainvoke()` |
| blocking | non-blocking |
| sequential waiting | efficient I/O handling |

---

## State Evolution

### Initial State

```python
{
    "user_id": 42
}
```

---

### After fetch_user_async

```python
{
    "user_id": 42,
    "user_name": "User_42"
}
```

---

### After generate_greeting_async

```python
{
    "user_id": 42,
    "user_name": "User_42",
    "greeting": "Hello User_42, welcome to LangGraph!"
}
```

---

## Why Async Nodes Are Important in LangGraph

Async nodes become critical when working with:

### 1. LLM APIs
- OpenAI
- Anthropic
- Azure OpenAI

### 2. External Tools
- search APIs
- databases
- vector stores

### 3. Multi-agent systems
- parallel execution
- concurrent tool usage

---

## Key Takeaways

- LangGraph supports async nodes natively.
- Async nodes use `async def` and `await`.
- Execution uses `ainvoke()` instead of `invoke()`.
- Async is essential for I/O-heavy workflows.
- Pydantic models work seamlessly with async graphs.
- Real-world agent systems are almost always async.