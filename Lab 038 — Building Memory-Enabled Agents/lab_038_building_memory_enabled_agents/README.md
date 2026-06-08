# Lab 038 — Building Memory-Enabled Agents

## Lab Intro

In the previous labs we learned:

- How to store long-term memory
- How to search memory
- How semantic retrieval finds memories based on meaning

At this point we have all the foundational pieces needed to build:

```text
Memory-Enabled Agents
```

A memory-enabled agent is an agent that can:

```text
Learn
Remember
Retrieve
Personalize
```

instead of treating every interaction as completely new.

---

## Enterprise Analogy

Imagine a customer support representative.

Without memory:

```text
Customer: My preferred language is Spanish.

Next Day...

Customer: Hello

Agent: What language do you prefer?
```

The same information must be collected repeatedly.

---

With memory:

```text
Customer: Hello

Agent:
Welcome back.
I remember that you prefer Spanish.
How can I help today?
```

The interaction becomes:

```text
Personalized
Efficient
Context-Aware
```

This is the essence of a memory-enabled agent.

---

## The Evolution of Agents

### Stateless Agent

```text
User Message
      ↓
Agent Response
      ↓
Memory Lost
```

Every interaction starts from zero.

---

### Memory-Enabled Agent

```text
User Message
      ↓
Retrieve Memory
      ↓
Agent Response
      ↓
Store New Memory
```

The agent continuously learns over time.

---

## Key Idea

A memory-enabled agent performs two memory operations:

### Retrieve Before Acting

```text
What do I already know?
```

---

### Store After Learning

```text
What should I remember?
```

---

## Agent Memory Loop

```text
User Arrives
      ↓
Search Memory
      ↓
Retrieve Context
      ↓
Generate Response
      ↓
Learn New Information
      ↓
Store Memory
      ↓
Future Interactions Improve
```

---

## Example Scenario

First interaction:

```text
User:
My favorite color is blue.
```

Agent stores:

```text
favorite_color = blue
```

---

Second interaction:

```text
User:
What color do I like?
```

Agent retrieves memory:

```text
favorite_color = blue
```

Response:

```text
Your favorite color is blue.
```

The agent appears to remember.

---

## Workflow

```text
START
   ↓
retrieve_memory
   ↓
agent_response
   ↓
store_memory
   ↓
END
```

The workflow:

1. Retrieves existing memory
2. Uses memory to respond
3. Stores new information

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
    }
}

# -------------------------
# State
# -------------------------

class State(BaseModel):
    user_id: str
    message: str
    memory: Optional[dict] = None
    response: Optional[str] = None

# -------------------------
# Retrieve Memory
# -------------------------

def retrieve_memory(state: State):

    memory = memory_store.get(
        state.user_id,
        {}
    )

    return {
        "memory": memory
    }

# -------------------------
# Agent Response
# -------------------------

def agent_response(state: State):

    favorite_color = (
        state.memory.get("favorite_color")
        if state.memory
        else None
    )

    if favorite_color:
        response = (
            f"I remember your favorite color "
            f"is {favorite_color}."
        )
    else:
        response = (
            "I do not know your favorite color yet."
        )

    return {
        "response": response
    }

# -------------------------
# Store New Memory
# -------------------------

def store_memory(state: State):

    if "favorite color is" in state.message.lower():

        color = (
            state.message.lower()
            .split("favorite color is")[-1]
            .strip()
        )

        memory_store[state.user_id] = {
            "favorite_color": color
        }

    return {}

# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "retrieve_memory",
    retrieve_memory
)

builder.add_node(
    "agent_response",
    agent_response
)

builder.add_node(
    "store_memory",
    store_memory
)

builder.add_edge(
    START,
    "retrieve_memory"
)

builder.add_edge(
    "retrieve_memory",
    "agent_response"
)

builder.add_edge(
    "agent_response",
    "store_memory"
)

builder.add_edge(
    "store_memory",
    END
)

graph = builder.compile()

# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "user_id": "user-1",
        "message": "Hello"
    }
)

print(result["response"])

---

## Expected Output

```python
I remember your favorite color is blue.
```

---

# Explanation

## What Is a Memory-Enabled Agent?

A memory-enabled agent is an agent that can:

```text
Store Knowledge
Retrieve Knowledge
Use Knowledge
Update Knowledge
```

across multiple interactions.

---

## Step 1 — Retrieve Existing Memory

The workflow begins by loading:

```python
memory_store.get(
    state.user_id,
    {}
)
```

Example result:

```python
{
    "favorite_color": "blue"
}
```

The agent now has context.

---

## Step 2 — Use Memory

The response node checks:

```python
favorite_color
```

and generates:

```text
I remember your favorite color is blue.
```

The memory influences behavior.

---

## Step 3 — Learn New Information

If the user says:

```text
My favorite color is green
```

the agent extracts:

```text
green
```

and stores it.

---

## Step 4 — Future Retrieval

Future interactions can retrieve:

```python
{
    "favorite_color": "green"
}
```

The agent's knowledge evolves over time.

---

## Why Memory Matters

Without memory:

```text
Conversation 1
      ↓
Knowledge Lost
      ↓
Conversation 2
```

The agent repeatedly asks the same questions.

---

With memory:

```text
Conversation 1
      ↓
Knowledge Stored
      ↓
Conversation 2
      ↓
Knowledge Retrieved
```

The agent becomes progressively more useful.

---

## Enterprise Example

### Customer Support Agent

Stored Memory:

```text
Preferred Language = Spanish
Subscription = Premium
```

When the customer returns:

```text
Use Spanish
Provide Premium Support
```

without asking again.

---

### Sales Agent

Stored Memory:

```text
Budget = $50,000
Interest = Analytics Platform
```

Future conversations become more targeted.

---

### IT Support Agent

Stored Memory:

```text
Operating System = Linux
```

Future troubleshooting recommendations are automatically tailored.

---

## Memory Lifecycle

```text
Observe
   ↓
Store
   ↓
Retrieve
   ↓
Use
   ↓
Update
```

This cycle continuously improves agent performance.

---

## Agent Architecture

```text
                 User
                   │
                   ▼

          Retrieve Memory
                   │
                   ▼

            Agent Logic
                   │
                   ▼

           Generate Reply
                   │
                   ▼

            Store Memory
                   │
                   ▼

            Long-Term Store
```

---

## Memory Retrieval + Reasoning

The most powerful agents combine:

```text
Memory
+
Reasoning
```

Memory provides:

```text
What the agent knows
```

Reasoning provides:

```text
What the agent should do
```

Together they create intelligent behavior.

---

## Why LangGraph Is Powerful

LangGraph naturally separates:

### Workflow State

```text
Current Execution
```

from

### Long-Term Memory

```text
Persistent Knowledge
```

This enables agents to:

```text
Resume Workflows
Remember Users
Personalize Responses
Maintain Context
```

at enterprise scale.

---

## Common Mistakes

### 1. Only Storing Memory

Incorrect:

```text
Store Everything
Retrieve Nothing
```

Memory is only useful when it influences behavior.

---

### 2. Only Retrieving Memory

Incorrect:

```text
Retrieve Existing Knowledge
Never Learn Anything New
```

The agent becomes static.

---

### 3. Mixing State and Memory

Workflow State:

```text
Current Task
```

Long-Term Memory:

```text
Persistent Knowledge
```

These should remain separate.

---

## Mental Model

Think of a memory-enabled agent as a person.

Each interaction:

```text
Learns Something
```

The information is remembered.

Future interactions:

```text
Recall What Was Learned
```

This creates continuity.

---

## Visual Summary

```text
User Interaction
        ↓
Retrieve Memories
        ↓
Apply Context
        ↓
Generate Response
        ↓
Learn New Facts
        ↓
Store Memories
        ↓
Future Interactions Improve
```

---

## Key Takeaways

- Memory-enabled agents retrieve and use knowledge from previous interactions.
- Effective agents both retrieve existing memories and store new memories.
- Memory retrieval enables personalization and contextual awareness.
- Long-term memory allows agents to improve across multiple sessions.
- Memory and reasoning work together to produce intelligent behavior.
- LangGraph provides a natural framework for combining workflows with persistent memory.
- Memory-enabled agents are the foundation for personalized AI assistants, support systems, and enterprise agents.