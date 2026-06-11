# Lab 072 — A2A Fundamentals

## Lab Intro

In the previous section we explored how agents can interact with external systems through standardized protocols.

One emerging protocol for agent-to-agent communication is:

    Agent-to-Agent (A2A)

A2A enables independent AI agents to:

- discover other agents
- exchange messages
- delegate tasks
- collaborate on work

using a common protocol.

Just as MCP standardizes communication between:

    Agent ↔ Tool

A2A standardizes communication between:

    Agent ↔ Agent

In this lab we will build our first A2A-enabled agent and understand the fundamental concepts behind the protocol.

This lab focuses on:

    Agent Cards
    Messages
    Tasks
    Responses

without introducing LangGraph yet.

The goal is to understand the protocol before building more advanced multi-agent systems.

---

# Key Idea

A2A interactions typically follow a simple workflow:

Discover
    ↓
Understand Capabilities
    ↓
Send Task
    ↓
Receive Result

Before one agent can delegate work to another agent, it must understand:

- who the agent is
- what capabilities it provides
- how to communicate with it

This information is typically exposed through an Agent Card.

---

# Enterprise Analogy

Imagine working in a large organization.

You need help with legal advice.

Instead of emailing everyone in the company, you first discover:

    Who handles legal matters?

You then:

- learn their responsibilities
- contact them
- assign a task
- receive a response

A2A works in a very similar way.

Agents advertise their capabilities and other agents can delegate work to them.

---

# A2A Architecture

```text
Consumer Agent
       │
       │ Task
       ▼
┌──────────────────┐
│ Research Agent   │
└────────┬─────────┘
         │
         │ Execute
         ▼
      Result
```

In this lab we will manually play the role of the consumer agent.

---

# Core A2A Concepts

## Agent

An autonomous software component capable of performing work.

Example:

```text
Research Agent
Weather Agent
Travel Agent
Finance Agent
```

---

## Agent Card

An Agent Card describes an agent.

Example:

```json
{
  "name": "Research Agent",
  "description": "Provides information about cities, history and culture.",
  "version": "1.0.0"
}
```

Think of it as:

```text
Business Card for an Agent
```

---

## Task

A task represents work delegated to an agent.

Example:

```text
Tell me about Pune
```

---

## Message

Messages are used to exchange information between agents.

Example:

```json
{
  "message": {
    "role": "user",
    "parts": [
      {
        "type": "text",
        "text": "Tell me about Pune"
      }
    ]
  }
}
```

---

## Response

The receiving agent executes the task and returns a result.

Example:

```json
{
  "result": "Pune is a major city in Maharashtra."
}
```

---

# Lab Code

## Install Dependencies

```bash
pip install fastapi uvicorn requests
```

---

## Create the Agent

Create:

```text
research_agent.py
```

```python
from fastapi import FastAPI

app = FastAPI()

AGENT_CARD = {
    "name": "Research Agent",
    "description":
        "Provides information about cities, history and culture.",
    "version": "1.0.0"
}


@app.get("/.well-known/agent.json")
def agent_card():
    return AGENT_CARD


@app.post("/tasks/send")
def send_task(payload: dict):

    text = payload["message"]["parts"][0]["text"]

    return {
        "result":
            f"You asked: {text}"
    }
```

---

## Run the Agent

```bash
uvicorn research_agent:app --port 8001
```

Expected output:

```text
INFO:     Uvicorn running on http://127.0.0.1:8001
```

---

# Discover the Agent Card

Open a browser and navigate to:

```text
http://localhost:8001/.well-known/agent.json
```

Expected output:

```json
{
  "name": "Research Agent",
  "description": "Provides information about cities, history and culture.",
  "version": "1.0.0"
}
```

---

# Send an A2A Task

Create:

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
                    "text": "Tell me about Pune"
                }
            ]
        }
    }
)

print(response.json())
```

Run:

```bash
python client.py
```

Expected output:

```python
{
    'result': 'You asked: Tell me about Pune'
}
```

---

# Explanation

## What Just Happened?

The client sent an A2A-style message:

```text
Tell me about Pune
```

to the agent.

The agent:

1. Received the task
2. Processed the message
3. Returned a response

This is the fundamental A2A interaction pattern.

---

# Agent Card Architecture

```text
Agent
  │
  ▼
Agent Card

Name
Description
Version
Capabilities
```

Before an agent can be used, other agents need a way to understand:

- what it does
- what tasks it can perform

Agent Cards provide that metadata.

---

# Task Flow

The complete flow becomes:

```text
Client
   │
   ▼
Agent Card Discovery
   │
   ▼
Task Submission
   │
   ▼
Agent Execution
   │
   ▼
Response
```

This pattern appears in nearly every A2A system.

---

# Why Agent Cards Matter

Without Agent Cards:

```text
Unknown Agent
      ↓
Unknown Capabilities
      ↓
Cannot Delegate Work
```

With Agent Cards:

```text
Known Agent
      ↓
Known Capabilities
      ↓
Task Delegation
```

Agent Cards are therefore the foundation of agent discovery.

---

# Common Errors

## 1. Missing Agent Card Endpoint

Incorrect:

```text
/.well-known/agent.json
```

does not exist.

Result:

```text
404 Not Found
```

Ensure the Agent Card endpoint is exposed.

---

## 2. Invalid Message Structure

Incorrect:

```json
{
  "question": "Tell me about Pune"
}
```

The agent expects:

```json
{
  "message": {
    "role": "user",
    "parts": [...]
  }
}
```

---

## 3. Agent Not Running

Attempting to send tasks before starting:

```bash
uvicorn research_agent:app --port 8001
```

will result in connection errors.

---

# Mental Model

Think of A2A as:

```text
Professional Delegation
```

Before assigning work:

1. Discover the expert
2. Understand capabilities
3. Send a task
4. Receive results

Agent Cards are the equivalent of professional profiles.

Tasks are work requests.

Responses are completed work.

---

# Architecture

```text
            Client
               │
               │ Discover
               ▼
     ┌─────────────────────┐
     │     Agent Card      │
     └──────────┬──────────┘
                │
                │ Task
                ▼
     ┌─────────────────────┐
     │   Research Agent    │
     └──────────┬──────────┘
                │
                ▼
             Result
```

---

# Why This Matters

Every multi-agent system starts with:

    Agent Discovery

Before agents can collaborate they must first understand:

- who exists
- what capabilities are available
- how to communicate

Agent Cards provide that foundation.

In future labs we will:

- build A2A agents with LangGraph
- introduce agent registries
- implement semantic discovery
- orchestrate multiple agents dynamically

---

# Key Takeaways

- A2A enables communication between independent agents.
- Agent Cards describe an agent and its capabilities.
- Tasks represent delegated work.
- Messages provide a standard communication structure.
- Agents receive tasks and return results.
- Agent discovery is the first step in any A2A workflow.
- Agent Cards are the foundation of multi-agent systems.
- Understanding A2A fundamentals is essential before introducing orchestration and discovery.