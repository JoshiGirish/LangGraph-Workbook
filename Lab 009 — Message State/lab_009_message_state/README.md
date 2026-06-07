# Lab 009 — Message State

## Lab Intro

Most LangGraph applications involve conversations between users, agents, tools, and other systems.

A common requirement is maintaining a history of messages throughout workflow execution.

Instead of storing a single string, we often store a list of messages that grows over time.

LangGraph provides specialized support for message-based state management, making it easier to build:

- Chatbots
- AI Agents
- Multi-Agent Systems
- Tool Calling Workflows
- Conversational Applications

In this lab, we'll create a simple message history that accumulates messages as the graph executes.

Workflow:

```text
START
   |
user_message
   |
assistant_message
   |
END
```

---

## Lab Code

```python
from typing import Annotated
from operator import add

from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph import START, END


# Message State
class State(TypedDict):
    messages: Annotated[list[str], add]


# User message node
def user_message(state: State):
    return {
        "messages": [
            "User: Hello LangGraph!"
        ]
    }


# Assistant response node
def assistant_message(state: State):
    return {
        "messages": [
            "Assistant: Hello! How can I help you today?"
        ]
    }


# Build graph
builder = StateGraph(State)

builder.add_node(
    "user_message",
    user_message
)

builder.add_node(
    "assistant_message",
    assistant_message
)

builder.add_edge(
    START,
    "user_message"
)

builder.add_edge(
    "user_message",
    "assistant_message"
)

builder.add_edge(
    "assistant_message",
    END
)


# Compile graph
graph = builder.compile()


# Execute graph
result = graph.invoke(
    {
        "messages": []
    }
)

print(result)
```

---

Expected Output:

```python
{
    'messages': [
        'User: Hello LangGraph!',
        'Assistant: Hello! How can I help you today?'
    ]
}

---

## Explanation

### What Is Message State?

Message state is a shared state structure that stores conversation history.

Instead of storing a single value:

```python
{
    "message": "Hello"
}
```

we store a growing collection of messages:

```python
{
    "messages": [
        "User: Hello",
        "Assistant: Hi!"
    ]
}
```

This allows later nodes to access the entire conversation history.

---

### State Definition

```python
class State(TypedDict):
    messages: Annotated[list[str], add]
```

The state contains a single field:

```python
messages
```

which stores a list of strings.

The reducer:

```python
add
```

ensures that new messages are appended rather than replacing previous messages.

Without the reducer, every update would overwrite the conversation history.

---

### User Message Node

```python
def user_message(state):
    return {
        "messages": [
            "User: Hello LangGraph!"
        ]
    }
```

This node simulates a user sending a message.

Output:

```python
{
    "messages": [
        "User: Hello LangGraph!"
    ]
}
```

---

### Assistant Message Node

```python
def assistant_message(state):
    return {
        "messages": [
            "Assistant: Hello! How can I help you today?"
        ]
    }
```

This node simulates an assistant response.

Output:

```python
{
    "messages": [
        "Assistant: Hello! How can I help you today?"
    ]
}
```

Because of the reducer, this message is added to the existing message history.

---

### Graph Construction

The workflow executes sequentially:

```text
START
   ↓
user_message
   ↓
assistant_message
   ↓
END
```

Each node contributes additional messages to the conversation.

---

### State Evolution

Initial State:

```python
{
    "messages": []
}
```

---

After `user_message`:

Node returns:

```python
{
    "messages": [
        "User: Hello LangGraph!"
    ]
}
```

State becomes:

```python
{
    "messages": [
        "User: Hello LangGraph!"
    ]
}
```

---

After `assistant_message`:

Node returns:

```python
{
    "messages": [
        "Assistant: Hello! How can I help you today?"
    ]
}
```

Reducer executes:

```python
[
    "User: Hello LangGraph!"
]
+
[
    "Assistant: Hello! How can I help you today?"
]
```

State becomes:

```python
{
    "messages": [
        "User: Hello LangGraph!",
        "Assistant: Hello! How can I help you today?"
    ]
}
```

---

Final State:

```python
{
    "messages": [
        "User: Hello LangGraph!",
        "Assistant: Hello! How can I help you today?"
    ]
}
```

---

### Why Message State Is Important

Message state is one of the most commonly used patterns in LangGraph.

Almost every agent workflow needs access to previous messages.

Examples:

#### Chatbots

```python
[
    "User: Hello",
    "Assistant: Hi!"
]
```

#### Tool Calling Agents

```python
[
    "User: What's the weather?",
    "Assistant: Calling weather tool...",
    "Tool: 28°C",
    "Assistant: It's 28°C today."
]
```

#### Multi-Agent Systems

```python
[
    "Planner: Create a plan",
    "Researcher: Gathering information",
    "Writer: Drafting report"
]
```

By storing messages in state, every node can access the full conversation history.

---

### Real LangGraph Message Objects

In production applications, LangGraph commonly uses message classes instead of plain strings.

Examples include:

```python
HumanMessage
```

```python
AIMessage
```

```python
ToolMessage
```

These message objects contain structured information such as:

- Message content
- Sender role
- Tool metadata
- Additional attributes

We'll explore those message types in later labs when building LLM-powered agents.

---

## Key Takeaways

- Message state stores conversation history inside the graph state.
- Message histories typically use reducers to accumulate messages.
- The `add` reducer appends new messages to existing messages.
- Every node can access previous messages stored in state.
- Message state forms the foundation of chatbots and agent workflows.
- Later LangGraph agents commonly use `HumanMessage`, `AIMessage`, and `ToolMessage` objects instead of plain strings.