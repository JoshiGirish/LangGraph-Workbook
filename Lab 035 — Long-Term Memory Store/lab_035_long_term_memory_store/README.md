# Lab 035 — Long-Term Memory Store

## Lab Intro

In the previous labs we learned:

- Checkpointing stores workflow execution state
- Threads isolate independent executions
- Replay lets us inspect historical state transitions
- Time travel allows returning to previous checkpoints

All of these capabilities focus on:

```text
Workflow State Persistence
```

But there is another kind of memory that agents often need:

```text
Knowledge Persistence
```

A workflow may finish today and run again tomorrow.

The agent may need to remember:

```text
User preferences
Customer information
Past conversations
Learned facts
Business context
```

This is where LangGraph's **Long-Term Memory Store** becomes important.

---

## Enterprise Analogy

Imagine a customer support agent.

Today the customer says:

```text
My preferred language is Spanish.
```

Tomorrow the customer starts a completely new conversation.

The workflow state from yesterday may be gone.

But the agent should still remember:

```text
Preferred Language = Spanish
```

This information belongs in:

```text
Long-Term Memory
```

not in workflow state.

---

## Two Types of Memory

### Workflow State

Stored by checkpointing:

```text
Current Task
Current Execution
Current Thread
```

Example:

```text
Order being processed
Current approval step
Current agent action
```

---

### Long-Term Memory

Stored separately:

```text
User Preferences
Business Facts
Learned Information
Persistent Context
```

Example:

```text
Preferred language
Favorite products
Customer tier
```

---

## Key Idea

Checkpointing remembers:

```text
What happened during this run
```

Long-term memory remembers:

```text
What should be remembered across runs
```

---

## Visual Model

```text
                 ┌─────────────────┐
                 │ Workflow State  │
                 └────────┬────────┘
                          │
                    Checkpointer
                          │
               Thread-Specific Memory

                 ┌─────────────────┐
                 │ Long-Term Store │
                 └────────┬────────┘
                          │
                 Cross-Thread Memory
```

---

## Example Scenario

Run 1:

```text
User: I like dark mode.
```

Store memory:

```text
theme = dark
```

---

Run 2 (new thread):

```text
User returns later.
```

Agent retrieves memory:

```text
theme = dark
```

The workflow starts with existing knowledge.

---

## Workflow

```text
START
   ↓
remember_preference
   ↓
END
```

The node stores user information in long-term memory.

---

## Lab Code

from typing import Optional
from pydantic import BaseModel

from langgraph.graph import StateGraph
from langgraph.graph import START, END

# -------------------------
# Simple In-Memory Store
# -------------------------

memory_store = {}

# -------------------------
# State
# -------------------------

class State(BaseModel):
    user_id: str
    preference: str
    stored: bool = False

# -------------------------
# Node
# -------------------------

def remember_preference(state: State):

    memory_store[state.user_id] = {
        "preference": state.preference
    }

    return {
        "stored": True
    }

# -------------------------
# Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "remember_preference",
    remember_preference
)

builder.add_edge(
    START,
    "remember_preference"
)

builder.add_edge(
    "remember_preference",
    END
)

graph = builder.compile()

# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "user_id": "user-1",
        "preference": "dark-mode"
    }
)

print(result)

print("\nLONG TERM MEMORY")
print(memory_store)

---

## Expected Output

```python
{
    'user_id': 'user-1',
    'preference': 'dark-mode',
    'stored': True
}

LONG TERM MEMORY

{
    'user-1': {
        'preference': 'dark-mode'
    }
}
```

---

## Explanation

## What Is a Long-Term Memory Store?

A long-term memory store is a storage system that survives beyond a single workflow execution.

Instead of storing:

```text
Current workflow progress
```

it stores:

```text
Persistent knowledge
```

Examples:

```text
User preferences
Customer information
Past conversations
Learned facts
Business context
```

---

## Step 1 — User Provides Information

Input:

```python
{
    "user_id": "user-1",
    "preference": "dark-mode"
}
```

The workflow receives information worth remembering.

---

## Step 2 — Store the Memory

Inside the node:

```python
memory_store[state.user_id] = {
    "preference": state.preference
}
```

Result:

```python
{
    "user-1": {
        "preference": "dark-mode"
    }
}
```

The memory is now stored independently from workflow execution.

---

## Step 3 — Workflow Completes

The graph finishes:

```text
START
   ↓
remember_preference
   ↓
END
```

Even though execution ends, the stored knowledge remains available.

---

## Why This Is Different From Checkpointing

Checkpoint:

```text
Thread-specific
Execution-specific
Temporary workflow state
```

Example:

```text
Current order status = shipped
```

---

Long-Term Memory:

```text
Cross-thread
Cross-session
Persistent knowledge
```

Example:

```text
User prefers dark mode
```

---

## Real LangGraph Memory Architecture

In production systems, memory is often stored in:

```text
Database
Redis
PostgreSQL
Vector Database
Cloud Storage
Knowledge Store
```

rather than a Python dictionary.

Example:

```text
Workflow State
    ↓
Checkpoint Store

Long-Term Knowledge
    ↓
Memory Store
```

The two systems serve different purposes.

---

## Enterprise Example

### Customer Success Agent

Customer says:

```text
I work in healthcare.
```

Store:

```text
industry = healthcare
```

Future conversations can automatically adapt responses based on that information.

---

### Sales Agent

Store:

```text
budget = $50,000
product_interest = analytics
```

Future workflows can personalize recommendations.

---

### IT Support Agent

Store:

```text
preferred_os = Linux
```

Future troubleshooting workflows immediately know the user's environment.

---

## Long-Term Memory Lifecycle

```text
Store Memory
      ↓
Persist
      ↓
Retrieve Later
      ↓
Use In Future Workflows
```

This creates continuity across interactions.

---

## Checkpoints vs Long-Term Memory

### Checkpoints

Purpose:

```text
Resume execution
```

Scope:

```text
Single thread
```

Lifetime:

```text
Execution history
```

Example:

```text
Order currently validated
```

---

### Long-Term Memory

Purpose:

```text
Retain knowledge
```

Scope:

```text
Multiple threads
Multiple sessions
```

Lifetime:

```text
Potentially permanent
```

Example:

```text
User prefers dark mode
```

---

## Common Mistakes

### 1. Treating Checkpoints as Long-Term Memory

Incorrect assumption:

```text
Checkpoint history = persistent knowledge
```

Checkpoint history tracks execution, not user knowledge.

---

### 2. Storing Everything in Memory

Not all information should be remembered.

Good candidates:

```text
Preferences
Profiles
Facts
Learned context
```

Poor candidates:

```text
Temporary calculations
Intermediate workflow variables
```

---

### 3. Mixing Execution State and Knowledge

Execution state:

```text
Current approval stage
```

Knowledge:

```text
Customer risk profile
```

Keep these concepts separate.

---

## Mental Model

Checkpointing is:

```text
Short-Term Memory
```

Long-Term Memory Store is:

```text
Persistent Knowledge
```

Another way to think about it:

```text
Checkpoint
    =
Working Memory

Long-Term Store
    =
Knowledge Base
```

---

## Visual Summary

```text
Conversation Starts
        ↓
Agent Learns Something
        ↓
Store In Long-Term Memory
        ↓
Workflow Ends
        ↓
New Workflow Starts
        ↓
Retrieve Memory
        ↓
Agent Appears To Remember
```

---

## Key Takeaways

- Long-term memory stores persistent knowledge beyond a single workflow execution.
- Checkpoints capture workflow state, while memory stores capture reusable knowledge.
- Long-term memory can be shared across multiple threads and sessions.
- Typical memories include preferences, profiles, learned facts, and business context.
- Memory storage is often backed by databases, Redis, vector stores, or cloud storage in production systems.
- Long-term memory enables agents to maintain continuity across interactions.
- Checkpointing answers **"What happened during execution?"**, while long-term memory answers **"What should be remembered for the future?"**.