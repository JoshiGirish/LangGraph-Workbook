# Lab 056 — Agent-to-Agent Messaging

## Lab Intro

In Lab 055, we improved multi-agent systems using **shared state**.

Agents communicated indirectly:

```text
Agent → State → Agent
```

This works well for structured pipelines, but it has a limitation:

```text
Agents cannot directly "talk" to each other
```

They only read and write fields in a shared object.

In more advanced systems, we often need:

- direct handoffs
- contextual explanations between agents
- dynamic coordination
- conversational collaboration

This introduces a new pattern:

> **Agent-to-Agent Messaging**

---

## Key Idea

Instead of only using shared state fields:

```text
state.research_notes
state.analysis
```

agents can exchange **messages as structured communication units**.

So the flow becomes:

```text
Agent A → Message → Agent B → Message → Agent C
```

Each agent receives a message history and responds with new messages.

---

## Enterprise Analogy

Think of a real team in a company:

### Shared state approach:

```text
Everyone edits the same document
```

### Messaging approach:

```text
People send emails or Slack messages
```

Example:

```text
Researcher → "Here are findings..."
Analyst → "I see issues in point 3..."
Writer → "I will summarize this..."
```

This is more natural for coordination-heavy workflows.

---

## Lab Code

We now switch from field-based state to **message-based state**.

from typing import Annotated

from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


# -------------------------
# State (Message-Based)
# -------------------------

class State(TypedDict):
    messages: Annotated[list, add_messages]


# -------------------------
# LLM
# -------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# -------------------------
# Agent 1 — Research Agent
# -------------------------

def research_agent(state: State):

    response = llm.invoke(
        state["messages"] +
        [
            HumanMessage(
                content="Generate structured research notes."
            )
        ]
    )

    return {
        "messages": [AIMessage(content=response.content)]
    }


# -------------------------
# Agent 2 — Analysis Agent
# -------------------------

def analysis_agent(state: State):

    response = llm.invoke(
        state["messages"] +
        [
            HumanMessage(
                content="Analyze the research and extract insights."
            )
        ]
    )

    return {
        "messages": [AIMessage(content=response.content)]
    }


# -------------------------
# Agent 3 — Writer Agent
# -------------------------

def writer_agent(state: State):

    response = llm.invoke(
        state["messages"] +
        [
            HumanMessage(
                content="Write a final report based on the conversation."
            )
        ]
    )

    return {
        "messages": [AIMessage(content=response.content)]
    }


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node("research_agent", research_agent)
builder.add_node("analysis_agent", analysis_agent)
builder.add_node("writer_agent", writer_agent)

builder.add_edge(START, "research_agent")
builder.add_edge("research_agent", "analysis_agent")
builder.add_edge("analysis_agent", "writer_agent")
builder.add_edge("writer_agent", END)

graph = builder.compile()


# -------------------------
# Execute
# -------------------------

result = graph.invoke({
    "messages": [
        HumanMessage(
            content="Topic: Artificial Intelligence in Education"
        )
    ]
})

print(result["messages"][-1].content)

---

## Example Output

```text
Artificial Intelligence is transforming education by enabling personalized learning,
automated grading, and intelligent tutoring systems.

Research shows improvements in student engagement and learning outcomes when AI
tools are integrated into classrooms.

However, concerns remain regarding data privacy, bias in educational models,
and over-reliance on automated systems.
```

---

## Explanation

## What Is Agent-to-Agent Messaging?

Agent-to-agent messaging means:

```text
Agents communicate using messages instead of shared fields
```

Each agent:

- receives a message history
- adds new messages
- passes them forward

---

## Step 1 — Message-Based State

Instead of structured fields:

```python
research_notes
analysis
report
```

we use:

```python
messages
```

This is more flexible and closer to real conversational systems.

---

## Step 2 — Message Flow

Each agent receives:

```python
state["messages"]
```

and appends new reasoning.

Example:

```text
Human → Research Agent → Analysis Agent → Writer Agent
```

Each step builds on the previous conversation.

---

## Step 3 — Agent Communication Pattern

### Research Agent

Receives:

```text
User prompt
```

Adds:

```text
Research output message
```

---

### Analysis Agent

Receives full conversation:

```text
User + Research output
```

Adds:

```text
Insights message
```

---

### Writer Agent

Receives full context:

```text
Full conversation history
```

Produces final report.

---

## Step 4 — Why Messages Instead of Fields?

### Field-based state:

```text
Structured but rigid
```

Good for pipelines.

---

### Message-based state:

```text
Flexible and conversational
```

Good for:

- collaborative agents
- dynamic reasoning
- LLM-driven workflows

---

## Key Insight

In message-based systems:

```text
State = Conversation
```

Not:

```text
State = Data structure
```

This shifts the system closer to how humans communicate.

---

## When to Use Agent-to-Agent Messaging

Use this pattern when:

### 1. Agents need context awareness

Each agent sees full history.

---

### 2. Tasks are open-ended

Not strictly structured pipelines.

---

### 3. Agents may adapt reasoning dynamically

Later agents can reinterpret earlier messages.

---

### 4. You want conversational workflows

Example:

```text
Debates
Collaborations
Iterative refinement
```

---

## Comparison: Shared State vs Messaging

### Shared State (Lab 065)

```text
Structured
Deterministic
Pipeline-based
```

---

### Messaging (Lab 066)

```text
Flexible
Conversational
Context-rich
```

---

## Common Mistakes

### 1. Losing Context Control

Message history grows quickly.

Bad:

```text
No filtering of messages
```

Better:

```text
Careful prompt design or pruning
```

---

### 2. Overusing Messages for Simple Pipelines

If task is linear:

```text
Use shared state instead
```

Messaging is more expensive and verbose.

---

### 3. Not Controlling Prompt Injection

Since all agents see messages:

```text
One bad message can influence others
```

Always design prompts carefully.

---

## Mental Model

Think of agent-to-agent messaging as:

```text
A group chat between AI agents
```

Each agent:

- reads the conversation
- adds a response
- passes it forward

---

## Architecture

```text
User
  │
  ▼
Research Agent
  │   (adds message)
  ▼
Analysis Agent
  │   (adds message)
  ▼
Writer Agent
  │   (final message)
  ▼
Final Output
```

---

## Why This Matters

Agent-to-agent messaging is the foundation of:

- collaborative AI systems
- debate agents
- critique loops
- iterative refinement systems
- autonomous multi-agent coordination

It is the closest model to **human teamwork communication**.

---

## Key Takeaways

- Agent-to-agent messaging uses message history instead of structured fields.
- Each agent reads full conversation context.
- Agents communicate by appending messages, not by writing to shared variables.
- This enables flexible, conversational, and adaptive multi-agent systems.
- It is ideal for dynamic reasoning and collaborative workflows.
- It trades structure for flexibility.
- In the next lab, we will build specialized worker agents that focus on narrow skills and are orchestrated as a coordinated system.
