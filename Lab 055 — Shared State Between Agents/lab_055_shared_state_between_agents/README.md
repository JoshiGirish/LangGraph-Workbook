# Lab 055 — Shared State Between Agents

## Lab Intro

In Lab 054, we built our first multi-agent graph.

Each agent:

```text
Reads state → Writes new field → Passes to next agent
```

This worked because the flow was strictly linear.

But real multi-agent systems are rarely that simple.

In production systems:

- multiple agents may read the same data
- multiple agents may update overlapping fields
- later agents depend on earlier updates
- state becomes the "shared memory" of the system

This introduces an important concept:

> **Shared State Between Agents**

---

## Key Idea

In LangGraph:

```text
State is the communication layer between agents
```

There is no direct agent-to-agent communication.

Instead:

```text
Agent A → updates state → Agent B reads state
```

So the state is:

- shared
- mutable (via updates)
- progressively enriched

---

## Enterprise Analogy

Think of a shared Google Doc:

```text
Researcher writes notes
Analyst adds insights
Editor refines structure
```

Everyone works on the same document.

No one passes files around.

That is exactly how LangGraph state works.

---

## Lab Code

We extend Lab 054 by making state usage more explicit and additive.

from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END


# -------------------------
# Shared State (Central Memory)
# -------------------------

class State(BaseModel):
    topic: str

    research_notes: str = ""
    key_insights: str = ""
    risks: str = ""
    final_summary: str = ""


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
        f"""
        Research the topic and produce structured notes:

        Topic: {state.topic}

        Output format:
        - Key facts
        - Important data
        - Context
        """
    )

    return {
        "research_notes": response.content
    }


# -------------------------
# Agent 2 — Insight Agent
# -------------------------

def insight_agent(state: State):
    response = llm.invoke(
        f"""
        Extract key insights from:

        {state.research_notes}
        """
    )

    return {
        "key_insights": response.content
    }


# -------------------------
# Agent 3 — Risk Analysis Agent
# -------------------------

def risk_agent(state: State):
    response = llm.invoke(
        f"""
        Identify risks based on:

        {state.research_notes}
        """
    )

    return {
        "risks": response.content
    }


# -------------------------
# Agent 4 — Final Writer Agent
# -------------------------

def writer_agent(state: State):
    response = llm.invoke(
        f"""
        Create a final summary report using:

        Insights:
        {state.key_insights}

        Risks:
        {state.risks}
        """
    )

    return {
        "final_summary": response.content
    }


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node("research_agent", research_agent)
builder.add_node("insight_agent", insight_agent)
builder.add_node("risk_agent", risk_agent)
builder.add_node("writer_agent", writer_agent)

builder.add_edge(START, "research_agent")
builder.add_edge("research_agent", "insight_agent")
builder.add_edge("research_agent", "risk_agent")
builder.add_edge("insight_agent", "writer_agent")
builder.add_edge("risk_agent", "writer_agent")
builder.add_edge("writer_agent", END)

graph = builder.compile()


# -------------------------
# Execute
# -------------------------

result = graph.invoke({
    "topic": "Artificial Intelligence in Finance"
})

print(result["final_summary"])

---

## Example Output

```text
Artificial Intelligence is rapidly transforming the financial sector
through fraud detection, algorithmic trading, and risk modeling.

Key insights include increased efficiency in decision-making and improved
predictive analytics capabilities.

However, risks include model bias, regulatory uncertainty, and over-reliance
on automated systems without human oversight.
```

---

## Explanation

## What Is Shared State?

Shared state is:

```text
A single evolving data structure used by all agents
```

Instead of passing messages directly:

```text
Agent A → Agent B
```

we use:

```text
Agent A → State → Agent B
```

---

## Step 1 — State as Central Memory

Our state contains multiple fields:

```python
research_notes
key_insights
risks
final_summary
```

Each field is:

```text
written by one agent
read by another agent
```

---

## Step 2 — Parallel State Writing

Unlike Lab 064, we now introduce branching:

```text
research_agent
     ↓
 ┌──────────────┐
 ▼              ▼
insight_agent   risk_agent
     └──────┬──────┘
            ▼
        writer_agent
```

Two agents write different parts of state in parallel.

This is a key multi-agent pattern.

---

## Step 3 — State Enrichment Pattern

Each agent adds information:

### Research Agent

```text
Adds raw knowledge
```

---

### Insight Agent

```text
Adds interpretation
```

---

### Risk Agent

```text
Adds evaluation
```

---

### Writer Agent

```text
Combines everything
```

This is called:

> **Progressive State Enrichment**

---

## Why Shared State Matters

### 1. Decoupling Agents

Agents do not directly depend on each other:

```text
Only depend on state
```

This makes systems modular.

---

### 2. Parallelism

Independent agents can run in parallel:

```text
insight_agent ↔ risk_agent
```

This improves efficiency.

---

### 3. Flexibility

We can easily add new agents:

```text
compliance_agent
sentiment_agent
cost_analysis_agent
```

without changing existing ones.

---

### 4. Traceability

State provides a full audit trail:

```text
What was known at each stage
```

---

## Important Concept: State is the Contract

In LangGraph:

```text
State = Contract between agents
```

Agents do not need to know:

- who created the data
- how it was generated

They only care about:

```text
what fields exist
```

---

## Common Mistakes

### 1. Overwriting State Incorrectly

Bad:

```python
return {
    "research_notes": "new only"
}
```

This may discard important previous context if not careful.

---

### 2. Unstructured State Growth

Bad:

```python
data1
data2
data3
data4
```

No clear meaning.

---

Better:

```python
research_notes
key_insights
risks
final_summary
```

Each field has a role.

---

### 3. Hidden Dependencies

Bad:

```text
Agent depends on something not in state
```

Always ensure:

```text
Everything needed is in State
```

---

## Mental Model

Think of shared state as:

```text
A living document that evolves over time
```

Each agent:

```text
reads the document
adds a section
moves on
```

---

## Architecture

```text
                Topic
                  │
                  ▼
          Research Agent
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
 Insight Agent        Risk Agent
        └─────────┬─────────┘
                  ▼
           Writer Agent
                  ▼
            Final Output
```

---

## Key Takeaways

- Shared state is the core communication mechanism in LangGraph multi-agent systems.
- Agents do not communicate directly; they read and write state.
- State acts as a contract between all agents.
- Multiple agents can enrich different parts of state in parallel.
- This enables modularity, scalability, and traceability.
- Shared state is the foundation for more advanced patterns like agent messaging, reviewer systems, and planner-executor architectures.
- In the next lab, we will extend this model to true agent-to-agent messaging where agents can explicitly communicate through structured messages rather than only state fields.
