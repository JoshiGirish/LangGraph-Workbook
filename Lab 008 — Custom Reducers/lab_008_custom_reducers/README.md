# Lab 008 — Custom Reducers

## Lab Intro

In the previous lab, we learned that LangGraph automatically merges state updates returned by nodes.

By default, when multiple nodes update the same field, the latest value replaces the previous value.

Sometimes, however, we want to accumulate values instead of overwriting them.

Examples include:

- Building message histories
- Collecting logs
- Tracking events
- Aggregating results from multiple nodes

LangGraph allows us to customize how state updates are merged using **Reducers**.

In this lab, we'll use a reducer to accumulate items into a list as the workflow executes.

Workflow:

```text
START
   |
add_first_item
   |
add_second_item
   |
END
```

---

## Lab Code

```python
from typing import Annotated
from typing_extensions import TypedDict

from operator import add

from langgraph.graph import StateGraph
from langgraph.graph import START, END


# State with a reducer
class State(TypedDict):
    items: Annotated[list[str], add]


# Node 1
def add_first_item(state: State):
    return {
        "items": ["Apple"]
    }


# Node 2
def add_second_item(state: State):
    return {
        "items": ["Banana"]
    }


# Build graph
builder = StateGraph(State)

builder.add_node(
    "add_first_item",
    add_first_item
)

builder.add_node(
    "add_second_item",
    add_second_item
)

builder.add_edge(
    START,
    "add_first_item"
)

builder.add_edge(
    "add_first_item",
    "add_second_item"
)

builder.add_edge(
    "add_second_item",
    END
)


# Compile graph
graph = builder.compile()


# Execute graph
result = graph.invoke(
    {
        "items": []
    }
)

print(result)
```

---

## Expected Output

```python
{
    'items': [
        'Apple',
        'Banana'
    ]
}
```

---

## Explanation

### What Is a Reducer?

A reducer tells LangGraph how to merge updates for a specific field.

Without a reducer:

```python
Current Value:
["Apple"]

New Update:
["Banana"]
```

Result:

```python
["Banana"]
```

The previous value is replaced.

With a reducer:

```python
Current Value:
["Apple"]

New Update:
["Banana"]
```

Result:

```python
["Apple", "Banana"]
```

The values are combined.

---

### The Reducer Used in This Lab

The state is defined as:

```python
class State(TypedDict):
    items: Annotated[list[str], add]
```

The reducer is:

```python
add
```

which comes from Python's `operator` module.

For lists:

```python
add(
    ["Apple"],
    ["Banana"]
)
```

produces:

```python
["Apple", "Banana"]
```

LangGraph automatically calls this reducer whenever the `items` field receives an update.

---

### Node 1

```python
def add_first_item(state):
    return {
        "items": ["Apple"]
    }
```

This node contributes the first item.

Output:

```python
{
    "items": ["Apple"]
}
```

---

### Node 2

```python
def add_second_item(state):
    return {
        "items": ["Banana"]
    }
```

This node contributes the second item.

Output:

```python
{
    "items": ["Banana"]
}
```

Instead of replacing the previous list, LangGraph applies the reducer.

---

### Graph Construction

The graph executes sequentially:

```text
START
   ↓
add_first_item
   ↓
add_second_item
   ↓
END
```

Each node updates the same state field:

```python
items
```

The reducer determines how those updates are combined.

---

### State Evolution

Initial State:

```python
{
    "items": []
}
```

---

After `add_first_item`:

Node returns:

```python
{
    "items": ["Apple"]
}
```

State becomes:

```python
{
    "items": ["Apple"]
}
```

---

After `add_second_item`:

Node returns:

```python
{
    "items": ["Banana"]
}
```

Reducer executes:

```python
["Apple"] + ["Banana"]
```

State becomes:

```python
{
    "items": [
        "Apple",
        "Banana"
    ]
}
```

---

Final State:

```python
{
    "items": [
        "Apple",
        "Banana"
    ]
}
```

---

### Why Reducers Matter

Reducers become extremely important when building:

- Message histories
- Multi-agent systems
- Parallel workflows
- Event streams
- Aggregation pipelines
- Map-Reduce architectures

Without reducers, later updates overwrite earlier values.

With reducers, state can accumulate information throughout the workflow.

---

### Custom Reducers

Reducers are simply Python functions.

Example:

```python
def combine_strings(
    current,
    new
):
    return current + " | " + new
```

State:

```python
class State(TypedDict):
    log: Annotated[str, combine_strings]
```

LangGraph will use this function whenever the `log` field receives updates.

This allows you to define custom merge logic for any type of state.

---

## Key Takeaways

- Reducers control how LangGraph merges state updates.
- By default, updates overwrite existing values.
- Reducers allow values to be accumulated instead of replaced.
- `Annotated` is used to attach reducers to state fields.
- The built-in `add` reducer is commonly used for lists.
- Reducers become essential in message histories, parallel execution, and multi-agent systems.
- Custom reducers can implement any merge behavior required by your workflow.