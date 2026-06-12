# Lab 073 — Building Your First A2A Agent with LangGraph

# Lab Intro

In the previous lab we introduced the core concepts of:

    Agent-to-Agent (A2A)

and learned about:

- Agent Cards
- Tasks
- Messages
- Responses

However, our agent was extremely simple.

When a task arrived, the agent returned a hardcoded response.

Real-world agents need a way to:

- maintain state
- execute workflows
- perform reasoning
- orchestrate actions

In this lab we will replace our hardcoded A2A agent with a LangGraph-powered agent.

---

# Key Idea

A2A defines:

```text
How Agents Communicate
```

LangGraph defines:

```text
How Agents Think
```

Together they form a powerful combination:

```text
A2A
  +
LangGraph
```

A2A handles communication.

LangGraph handles execution.

---

# Enterprise Analogy

Imagine a customer support department.

The company receives a support request.

The request then passes through a workflow:

```text
Receive Ticket
      ↓
Classify Issue
      ↓
Resolve Issue
      ↓
Send Response
```

The communication channel is not the workflow.

The workflow is the internal process used to complete the work.

A2A is the communication layer.

LangGraph is the workflow layer.

---

# Architecture

```text
Consumer Agent
       │
       │ Task
       ▼
┌─────────────────────┐
│     A2A Endpoint    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      LangGraph      │
└──────────┬──────────┘
           │
           ▼
        Result
```

The A2A endpoint receives tasks.

LangGraph performs the actual work.

---

# Why LangGraph?

Without LangGraph:

```python
if task:
    return response
```

With LangGraph:

```text
START
   │
   ▼
Research
   │
   ▼
Summarize
   │
   ▼
 END
```

As agents become more complex, graph-based execution becomes easier to manage than large collections of functions.

---

# Lab Code

## Install Dependencies

```bash
pip install fastapi uvicorn requests
pip install langgraph
```

---

# Create the Agent

Create:

```text
research_agent.py
```

```python
from typing import TypedDict

from fastapi import FastAPI

from langgraph.graph import (
    StateGraph,
    END
)

app = FastAPI()


# ----------------------------------
# Agent Card
# ----------------------------------

AGENT_CARD = {
    "name": "Research Agent",
    "description":
        "Provides information about cities, history and culture.",
    "version": "1.0.0"
}


# ----------------------------------
# LangGraph State
# ----------------------------------

class AgentState(TypedDict):
    question: str
    answer: str


# ----------------------------------
# LangGraph Node
# ----------------------------------

def research_node(state):

    question = state["question"]

    answer = f"""
Research Results

Question:
{question}

Pune is a major city in Maharashtra and
is often called the Oxford of the East.
"""

    return {
        "answer": answer
    }


# ----------------------------------
# Build Graph
# ----------------------------------

builder = StateGraph(AgentState)

builder.add_node(
    "research",
    research_node
)

builder.set_entry_point(
    "research"
)

builder.add_edge(
    "research",
    END
)

graph = builder.compile()


# ----------------------------------
# Agent Card Endpoint
# ----------------------------------

@app.get("/.well-known/agent.json")
def agent_card():
    return AGENT_CARD


# ----------------------------------
# A2A Task Endpoint
# ----------------------------------

@app.post("/tasks/send")
def send_task(payload: dict):

    question = (
        payload["message"]["parts"][0]["text"]
    )

    result = graph.invoke(
        {
            "question": question
        }
    )

    return {
        "result":
            result["answer"]
    }
```

---

# Run the Agent

```bash
uvicorn research_agent:app --port 8001
```

Expected Output:

```text
INFO:     Uvicorn running on http://127.0.0.1:8001
```

---

# Create the Client

Create:

```text
client.py
```

```python
import requests

response = requests.post(
    "http://localhost:8001/tasks/send",
    json={
        "message": {
            "role": "user",
            "parts": [
                {
                    "type": "text",
                    "text":
                        "Tell me about Pune"
                }
            ]
        }
    }
)

print(
    response.json()["result"]
)
```

Run:

```bash
python client.py
```

Expected Output:

```text
Research Results

Question:
Tell me about Pune

Pune is a major city in Maharashtra and
is often called the Oxford of the East.
```

---

# Understanding the Graph

Our graph contains a single node:

```text
START
   │
   ▼
Research
   │
   ▼
 END
```

The node receives:

```python
{
    "question":
        "Tell me about Pune"
}
```

and returns:

```python
{
    "answer":
        "..."
}
```

The resulting state becomes:

```python
{
    "question":
        "Tell me about Pune",

    "answer":
        "Research Results..."
}
```

---

# Step 1 — Define State

LangGraph workflows operate on shared state.

```python
class AgentState(TypedDict):
    question: str
    answer: str
```

Think of state as:

```text
Working Memory
```

for the graph.

---

# Step 2 — Create a Node

```python
def research_node(state):
```

Nodes receive state.

Nodes return state updates.

Example:

```text
Input State
      ↓
 Process
      ↓
Output State
```

---

# Step 3 — Build the Workflow

```python
builder.add_node(
    "research",
    research_node
)
```

This registers the node.

---

# Step 4 — Define Execution Flow

```python
START
  ↓
research
  ↓
 END
```

This tells LangGraph:

```text
Execute Research
Then Stop
```

---

# Step 5 — Invoke the Graph

```python
graph.invoke(...)
```

When the A2A task arrives:

```text
Tell me about Pune
```

the graph executes and produces the final answer.

---

# A2A + LangGraph Architecture

The complete flow now becomes:

```text
Client
   │
   ▼
A2A Task
   │
   ▼
A2A Endpoint
   │
   ▼
LangGraph
   │
   ▼
Research Node
   │
   ▼
Response
```

This architecture appears frequently in modern agent systems.

---

# Why This Matters

A2A gives us:

```text
Communication
```

LangGraph gives us:

```text
Execution
```

Separating these concerns makes agents:

- easier to maintain
- easier to scale
- easier to extend

---

# Common Errors

## 1. Missing State Field

Incorrect:

```python
{
    "query": question
}
```

Expected:

```python
{
    "question": question
}
```

State keys must match the schema.

---

## 2. Returning Wrong Fields

Incorrect:

```python
return {
    "result": answer
}
```

Expected:

```python
return {
    "answer": answer
}
```

LangGraph updates state using matching keys.

---

## 3. Forgetting END

Incorrect:

```python
builder.add_node(...)
```

without:

```python
builder.add_edge(
    "research",
    END
)
```

The graph must have a valid termination path.

---

## 4. Not Compiling the Graph

Incorrect:

```python
builder = StateGraph(...)
```

Expected:

```python
graph = builder.compile()
```

Only compiled graphs can execute.

---

# Mental Model

Think of A2A and LangGraph as two separate layers.

```text
Layer 1

Communication

Agent
  ↔
Agent
```

```text
Layer 2

Execution

START
  ↓
Node
  ↓
Node
  ↓
END
```

A2A handles communication.

LangGraph handles execution.

---

# Architecture

```text
             Client
                │
                ▼
      ┌──────────────────┐
      │  A2A Endpoint    │
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │    LangGraph     │
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │ Research Node    │
      └────────┬─────────┘
               │
               ▼
            Result
```

---

# Why This Matters

Most production agents are not:

```text
Request
   ↓
Response
```

Instead they execute workflows.

LangGraph provides a structured way to build those workflows while A2A provides a structured way to communicate between agents.

Together they form the foundation of modern multi-agent systems.

In the next lab we will introduce:

    Agent Registries

which allow agents to discover other agents dynamically.

---

# Key Takeaways

- A2A handles communication between agents.
- LangGraph handles internal agent execution.
- State stores information shared across nodes.
- Nodes receive state and return state updates.
- Graphs define execution flow.
- A2A endpoints can invoke LangGraph workflows.
- Separating communication and execution improves agent design.
- LangGraph-powered A2A agents provide the foundation for multi-agent systems.