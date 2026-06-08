# Lab 054 — Your First Multi-Agent Graph

## Lab Intro

In earlier parts, we built single-agent systems with tools, memory, and structured outputs.

Now we shift to a new architecture:

> **Multi-Agent Systems**

Instead of one agent doing everything, we split responsibility across multiple specialized agents.

In LangGraph, a multi-agent system is simply:

```text
A graph where each node behaves like an agent
```

There is no special "multi-agent mode".

Just:

```text
Nodes + Shared State + Control Flow
```

---

## Key Idea

Single-agent system:

```text
User → LLM → Tools → Answer
```

Multi-agent system:

```text
User → Agent A → Agent B → Agent C → Answer
```

Each agent:

- reads state
- performs a focused task
- writes back to state

---

## Enterprise Analogy

Think of a real product team:

```text
Research Analyst → Data Scientist → Report Writer
```

Each person:

- does one job well
- passes output to the next person

No one does everything.

That is exactly how multi-agent graphs work.

---

## Lab Code

from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END


# -------------------------
# Shared State
# -------------------------

class State(BaseModel):
    topic: str
    research: str = ""
    analysis: str = ""
    report: str = ""


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
        f"Research the topic: {state.topic}"
    )

    return {
        "research": response.content
    }


# -------------------------
# Agent 2 — Analysis Agent
# -------------------------

def analysis_agent(state: State):
    response = llm.invoke(
        f"Analyze the following research:\n{state.research}"
    )

    return {
        "analysis": response.content
    }


# -------------------------
# Agent 3 — Writer Agent
# -------------------------

def writer_agent(state: State):
    response = llm.invoke(
        f"Write a final report based on:\n{state.analysis}"
    )

    return {
        "report": response.content
    }


# -------------------------
# Build Multi-Agent Graph
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
    "topic": "Artificial Intelligence in Healthcare"
})

print(result["report"])

---

## Example Output

```text
Artificial Intelligence is transforming healthcare through improved diagnostics,
predictive modeling, and personalized treatment planning.

AI systems assist doctors by analyzing medical images, predicting disease risks,
and optimizing hospital operations.

However, challenges such as data privacy, bias, and regulatory compliance remain
critical considerations.
```

---

## Explanation

## What Makes This a Multi-Agent System?

Even though there is only one LLM:

```text
We simulate multiple roles
```

Each node behaves like an independent agent:

### Research Agent
```text
Collects raw information
```

### Analysis Agent
```text
Interprets and structures insights
```

### Writer Agent
```text
Produces final output
```

---

## Step 1 — Shared State

All agents communicate through:

```python
State
```

Each field represents a stage:

```text
topic → research → analysis → report
```

This is the backbone of multi-agent systems.

---

## Step 2 — Sequential Agent Flow

The graph enforces strict ordering:

```text
START → Research → Analysis → Writer → END
```

This ensures:

- predictable execution
- clean separation of responsibility
- structured progression of information

---

## Step 3 — Why This Works

Instead of one large prompt:

```text
Do everything at once
```

we break reasoning into stages:

```text
Understand → Analyze → Write
```

This improves:

- clarity
- consistency
- quality of output

---

## Why Multi-Agent Design Matters

### 1. Separation of Concerns

Each agent has one job:

```text
No overloaded prompts
```

---

### 2. Better Reasoning

Breaking tasks improves:

```text
depth of thinking
```

---

### 3. Debugging Simplicity

If output is bad:

```text
Check which agent failed
```

---

### 4. Reusability

Each agent can be reused in other workflows:

- research agent → multiple domains
- writer agent → reports, emails, summaries

---

## Mental Model

Think of this system as:

```text
An assembly line for thinking
```

Each stage refines the output further.

---

## Architecture

```text
User Input
    │
    ▼
Research Agent
    │
    ▼
Analysis Agent
    │
    ▼
Writer Agent
    │
    ▼
Final Output
```

---

## Key Takeaways

- Multi-agent systems divide a task into specialized roles.
- In LangGraph, agents are just nodes operating on shared state.
- Each agent reads previous outputs and writes new fields.
- Sequential graphs create structured reasoning pipelines.
- This pattern improves modularity, clarity, and maintainability.
- This is the foundation for advanced patterns like:
  - agent communication
  - reviewer systems
  - planner-executor architectures
