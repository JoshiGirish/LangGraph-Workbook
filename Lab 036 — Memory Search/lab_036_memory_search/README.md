# Lab 036 — Memory Search

## Lab Intro

In the previous lab we introduced:

```text
Long-Term Memory Store
```

We learned that agents can save information that survives beyond a single workflow execution.

However, storing memory is only half of the problem.

The second half is:

```text
Finding the right memory later
```

This is where **Memory Search** becomes important.

A memory system is only useful if the agent can retrieve relevant information when it needs it.

---

## Enterprise Analogy

Imagine a customer support system that has stored:

```text
Customer Name
Preferred Language
Subscription Plan
Previous Issues
Product Preferences
```

After thousands of customers interact with the system, the memory store may contain:

```text
Millions of records
```

When a customer returns, the agent must quickly answer:

```text
What do we know about this customer?
```

The agent searches memory and retrieves only the relevant information.

---

## The Problem

Suppose our memory store contains:

```python
{
    "user-1": {
        "favorite_color": "blue"
    },
    "user-2": {
        "favorite_color": "green"
    },
    "user-3": {
        "favorite_color": "red"
    }
}
```

A user returns:

```text
user-2
```

The agent should retrieve:

```python
{
    "favorite_color": "green"
}
```

instead of scanning every piece of stored information manually.

---

## Key Idea

Long-term memory has two operations:

### Store

```text
Save Information
```

---

### Search

```text
Retrieve Information
```

Together they create a usable memory system.

---

## Visual Model

```text
User Interaction
        ↓
Store Memory
        ↓
Memory Database
        ↓
Search Request
        ↓
Retrieve Memory
        ↓
Agent Response
```

---

## Workflow

```text
START
   ↓
search_memory
   ↓
END
```

The workflow receives a user ID and searches the memory store.

---

## Lab Code

from typing import Optional
from pydantic import BaseModel

from langgraph.graph import StateGraph
from langgraph.graph import START, END

# -------------------------
# Long-Term Memory Store
# -------------------------

memory_store = {
    "user-1": {
        "favorite_color": "blue"
    },
    "user-2": {
        "favorite_color": "green"
    },
    "user-3": {
        "favorite_color": "red"
    }
}

# -------------------------
# State
# -------------------------

class State(BaseModel):
    user_id: str
    memory: Optional[dict] = None

# -------------------------
# Node
# -------------------------

def search_memory(state: State):

    memory = memory_store.get(
        state.user_id,
        {}
    )

    return {
        "memory": memory
    }

# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "search_memory",
    search_memory
)

builder.add_edge(
    START,
    "search_memory"
)

builder.add_edge(
    "search_memory",
    END
)

graph = builder.compile()

# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "user_id": "user-2"
    }
)

print(result)

---

## Expected Output

```python
{
    'user_id': 'user-2',
    'memory': {
        'favorite_color': 'green'
    }
}
```

---

## Explanation

## What Is Memory Search?

Memory search is the process of retrieving previously stored information from a memory system.

Conceptually:

```text
Store → Search → Retrieve
```

Without retrieval, stored memories provide no value.

---

## Step 1 — Receive Search Request

Input:

```python
{
    "user_id": "user-2"
}
```

The workflow receives an identifier for the memory being requested.

---

## Step 2 — Search the Memory Store

Inside the node:

```python
memory_store.get(
    state.user_id,
    {}
)
```

This performs a lookup using the user ID.

---

## Step 3 — Retrieve Memory

The search returns:

```python
{
    "favorite_color": "green"
}
```

The retrieved memory is added to workflow state.

---

## Step 4 — Continue Workflow

The workflow can now use the retrieved memory.

Example:

```text
User returns
      ↓
Retrieve Preferences
      ↓
Personalize Response
```

This is one of the foundations of memory-enabled agents.

---

## Why Memory Search Matters

Imagine an agent that remembers:

```text
Favorite Product
Preferred Language
Previous Purchases
Subscription Tier
```

When the user returns, the agent needs immediate access to that information.

Without search:

```text
Memory Exists
But Cannot Be Found
```

With search:

```text
Memory Exists
And Is Usable
```

---

## Enterprise Example

### Customer Support Agent

Stored Memory:

```text
Language = Spanish
Plan = Premium
```

Search Result:

```text
Spanish
Premium
```

Agent immediately personalizes the conversation.

---

### Sales Assistant

Stored Memory:

```text
Budget = $25,000
Interest = Analytics Platform
```

Search retrieves those values and helps guide future recommendations.

---

### IT Support Agent

Stored Memory:

```text
Operating System = Linux
```

The next troubleshooting workflow automatically uses Linux-specific instructions.

---

## Memory Search vs Checkpoint Search

These concepts are often confused.

### Checkpoint Search

Retrieves:

```text
Past Workflow State
```

Example:

```text
What happened during execution?
```

---

### Memory Search

Retrieves:

```text
Stored Knowledge
```

Example:

```text
What do we know about this user?
```

---

## Visual Comparison

```text
Checkpoint History

CP1 → CP2 → CP3 → CP4

Question:
What happened?

--------------------------------

Memory Store

User A
User B
User C

Question:
What do we know?
```

---

## Real Production Systems

Simple examples use:

```python
memory_store = {}
```

Production systems often use:

```text
PostgreSQL
Redis
MongoDB
Vector Databases
Cloud Databases
Knowledge Stores
```

The search operation remains conceptually the same:

```text
Find Relevant Memory
Return It
Use It
```

---

## Search by Key

Our example performs:

```text
Exact Lookup
```

Using:

```python
memory_store.get(user_id)
```

This is the simplest form of memory retrieval.

---

## Future Evolution

As memory systems grow, agents often need:

```text
Keyword Search
Similarity Search
Semantic Search
Vector Search
```

Instead of searching by exact user ID.

For example:

```text
Find memories related to travel
```

or

```text
Find memories about previous purchases
```

These advanced retrieval methods will be explored in upcoming labs.

---

## Common Mistakes

### 1. Assuming Stored Memory Is Automatically Used

Incorrect:

```text
Store Memory
Done
```

Correct:

```text
Store Memory
Search Memory
Use Memory
```

Retrieval is essential.

---

### 2. Confusing Memory Search with Workflow History

Memory search retrieves:

```text
Knowledge
```

Checkpoint history retrieves:

```text
Execution Records
```

These serve different purposes.

---

### 3. Returning All Memories

Bad:

```text
Load Entire Database
```

Good:

```text
Retrieve Relevant Information Only
```

Efficient search becomes critical as memory grows.

---

## Mental Model

Think of long-term memory as a library.

Storing memory:

```text
Adding a Book
```

Searching memory:

```text
Finding the Right Book
```

Without search:

```text
Library Exists
But Cannot Be Used
```

---

## Visual Summary

```text
Store Memory
      ↓
Memory Database
      ↓
Search Request
      ↓
Locate Matching Memory
      ↓
Retrieve Memory
      ↓
Use Memory
```

---

## Key Takeaways

- Memory search retrieves information from long-term memory stores.
- Storing memory is only useful if the information can later be found.
- Search typically begins with exact lookups using identifiers such as user IDs.
- Retrieved memories can be injected into workflow state and used by agents.
- Memory search is different from checkpoint history retrieval.
- Production systems use databases, caches, and memory stores for retrieval.
- Memory search is the foundation for more advanced retrieval techniques such as semantic search and vector search.