# Lab 057 — Specialized Worker Agents

## Lab Intro

In Lab 056, we introduced **agent-to-agent messaging**, where agents collaborate through shared conversation history.

Now we take the next step in multi-agent design:

> **Specialized Worker Agents**

Instead of having agents that all behave similarly, we design agents with **strict roles and narrow expertise**.

Each agent becomes a "worker" optimized for a single type of task.

---

## Key Idea

Instead of:

```text
General-purpose agents doing everything
```

We build:

```text
Specialized agents with clear responsibilities
```

Example:

```text
Research Agent → gathers facts
Math Agent     → solves calculations
Critic Agent   → finds issues
Writer Agent   → produces final output
```

Each agent is:

```text
Focused, predictable, reusable
```

---

## Enterprise Analogy

Think of a software company:

```text
Frontend Engineer
Backend Engineer
QA Engineer
DevOps Engineer
```

Each engineer:

- has a specific skillset
- performs a specific role
- contributes to a larger system

You don't ask a DevOps engineer to design UI.

Same principle applies to AI agents.

---

## Lab Code

We design a **router-based worker system** using LangGraph.

from typing import TypedDict, Annotated

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


# -------------------------
# State
# -------------------------

class State(TypedDict):
    messages: Annotated[list, add_messages]
    task_type: str


# -------------------------
# LLM
# -------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# -------------------------
# Worker 1 — Research Agent
# -------------------------

def research_worker(state: State):

    response = llm.invoke(
        state["messages"] +
        [
            HumanMessage(content="You are a Research Specialist. Provide facts and context only.")
        ]
    )

    return {
        "messages": [AIMessage(content=response.content)]
    }


# -------------------------
# Worker 2 — Math Agent
# -------------------------

def math_worker(state: State):

    response = llm.invoke(
        state["messages"] +
        [
            HumanMessage(content="You are a Math Specialist. Solve calculations step by step.")
        ]
    )

    return {
        "messages": [AIMessage(content=response.content)]
    }


# -------------------------
# Worker 3 — Critic Agent
# -------------------------

def critic_worker(state: State):

    response = llm.invoke(
        state["messages"] +
        [
            HumanMessage(content="You are a Critic. Find errors, risks, or missing logic.")
        ]
    )

    return {
        "messages": [AIMessage(content=response.content)]
    }


# -------------------------
# Worker 4 — Writer Agent
# -------------------------

def writer_worker(state: State):

    response = llm.invoke(
        state["messages"] +
        [
            HumanMessage(content="You are a Technical Writer. Produce a final polished answer.")
        ]
    )

    return {
        "messages": [AIMessage(content=response.content)]
    }


# -------------------------
# Router
# -------------------------

def router(state: State):

    task = state["task_type"]

    if task == "research":
        return "research_worker"

    if task == "math":
        return "math_worker"

    if task == "critique":
        return "critic_worker"

    return "writer_worker"


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node("research_worker", research_worker)
builder.add_node("math_worker", math_worker)
builder.add_node("critic_worker", critic_worker)
builder.add_node("writer_worker", writer_worker)

builder.add_conditional_edges(START, router)

builder.add_edge("research_worker", END)
builder.add_edge("math_worker", END)
builder.add_edge("critic_worker", END)
builder.add_edge("writer_worker", END)

graph = builder.compile()


# -------------------------
# Execute
# -------------------------

result = graph.invoke({
    "task_type": "critique",
    "messages": [
        HumanMessage(content="AI will replace all jobs in the future.")
    ]
})

print(result["messages"][-1].content)

---

## Example Output

```text
The statement is overly broad and lacks nuance.

While AI will automate many tasks, it is unlikely to replace all jobs entirely.
Historical technological shifts show job transformation rather than full replacement.

Additional considerations such as regulation, human creativity, and economic structure
also limit full automation.
```

---

## Explanation

## What Are Specialized Worker Agents?

Specialized worker agents are:

```text
Agents designed for a single, narrow function
```

Instead of general intelligence:

```text
One agent doing everything
```

we decompose work into roles.

---

## Step 1 — Define Worker Roles

We created four workers:

### Research Worker

```text
Focus: facts and context
```

---

### Math Worker

```text
Focus: calculations and reasoning
```

---

### Critic Worker

```text
Focus: identifying flaws
```

---

### Writer Worker

```text
Focus: final polished output
```

Each worker has a strict identity.

---

## Step 2 — Task Routing

We introduce a router:

```python
def router(state: State):
```

It selects the correct worker based on:

```python
task_type
```

Example:

```text
"math" → math_worker
"critique" → critic_worker
```

This is a form of:

> **Policy-based agent routing**

---

## Step 3 — Single Responsibility Principle

Each worker follows:

```text
One job only
```

This improves:

- accuracy
- consistency
- predictability

---

## Step 4 — Why Specialization Works

LLMs perform better when:

```text
Role is clearly defined
```

Example:

Bad prompt:

```text
Solve this problem.
```

Good prompt:

```text
You are a Math Specialist. Solve step by step.
```

Specialization improves reasoning quality.

---

## Step 5 — Execution Flow

Depending on task:

```text
User Input
   ↓
Router
   ↓
Selected Worker
   ↓
Final Output
```

No unnecessary steps.

---

## Why Use Worker Agents?

### 1. Better Accuracy

Each agent is optimized for its domain.

---

### 2. Easier Maintenance

You can modify one worker without affecting others.

---

### 3. Scalability

You can add new workers easily:

```text
Legal Worker
Finance Worker
Coding Worker
```

---

### 4. Clear System Design

Each agent has:

```text
Single responsibility
```

This mirrors real software architecture.

---

## Shared Pattern: Router + Workers

This architecture is very common:

```text
          Router
            │
 ┌──────────┼──────────┐
 ▼          ▼          ▼
Agent A   Agent B   Agent C
```

Used in:

- customer support systems
- enterprise automation
- AI assistants
- document processing pipelines

---

## Common Mistakes

### 1. Too Many Worker Types

Bad:

```text
10+ overlapping workers
```

This creates confusion.

---

### 2. Weak Task Routing

Bad:

```text
Ambiguous task_type values
```

Better:

```text
Strict categories
```

---

### 3. Overlapping Responsibilities

Bad:

```text
Research + Critic doing same job
```

Workers must be distinct.

---

### 4. Ignoring Router Logic

The router is the brain of this system.

If routing is weak:

```text
Whole system breaks
```

---

## Mental Model

Think of specialized worker agents as:

```text
A factory assembly line with expert stations
```

Each station performs a precise transformation.

---

## Architecture

```text
User Input
    │
    ▼
   Router
    │
 ┌──┼───────────────┐
 ▼  ▼               ▼
Research  Math   Critic   Writer
 Worker   Worker  Worker   Worker
    │      │       │        │
    └──────┴───────┴────────┘
             ▼
        Final Output
```

---

## Key Takeaways

- Specialized worker agents are single-purpose agents with narrow expertise.
- A router selects which worker handles a request.
- This improves accuracy, modularity, and scalability.
- Each worker follows a strict role definition.
- This pattern is widely used in production AI systems.
- It is the foundation for more advanced orchestration patterns like reviewer loops and planner-executor systems.
- In the next lab, we will combine Research + Writer agents into a structured pipeline that demonstrates real-world content generation workflows.
