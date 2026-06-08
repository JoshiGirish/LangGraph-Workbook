# Lab 063 — Debate Pattern

## Lab Intro

In previous labs, we explored different patterns.

The agent planned and improved its own answer by identifying mistakes.

However, complex questions often involve:

```text
Multiple valid perspectives
```

For example:

```text
Should remote work become permanent?
Should governments regulate AI?
Are electric vehicles always better for the environment?
```

These questions rarely have a single obvious answer.

Instead of relying on one viewpoint, we can create multiple agents that argue different positions.

This architecture is known as the:

> **Debate Pattern**

The goal is not to determine a winner.

The goal is to:

```text
Explore competing viewpoints
```

before producing a final answer.

---

## Key Idea

Traditional reasoning:

```text
Question
   ↓
Answer
```

Debate reasoning:

```text
Question
   ↓
Agent A (Position 1)
Agent B (Position 2)
   ↓
Synthesis
   ↓
Final Answer
```

The debate exposes strengths and weaknesses in each argument.

---

## Enterprise Analogy

Imagine a leadership team discussing a major decision.

Before launching a new product:

```text
Product Team
```

argues:

```text
Launch immediately
```

while:

```text
Risk Team
```

argues:

```text
Delay until risks are addressed
```

Leadership listens to both sides before making a decision.

The Debate Pattern follows the same principle.

---

## Lab Code

from pydantic import BaseModel

from langchain_openai import ChatOpenAI

from langgraph.graph import (
    StateGraph,
    START,
    END
)


# -------------------------
# State
# -------------------------

class State(BaseModel):

    question: str

    pro_argument: str = ""

    con_argument: str = ""

    final_answer: str = ""


# -------------------------
# LLM
# -------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# -------------------------
# Pro Agent
# -------------------------

def pro_agent(state: State):

    response = llm.invoke(
        f"""
        Take the PRO position.

        Question:

        {state.question}

        Provide the strongest
        supporting arguments.
        """
    )

    return {
        "pro_argument": response.content
    }


# -------------------------
# Con Agent
# -------------------------

def con_agent(state: State):

    response = llm.invoke(
        f"""
        Take the CON position.

        Question:

        {state.question}

        Provide the strongest
        opposing arguments.
        """
    )

    return {
        "con_argument": response.content
    }


# -------------------------
# Synthesis Agent
# -------------------------

def synthesis_agent(state: State):

    response = llm.invoke(
        f"""
        Review both arguments.

        PRO Argument:

        {state.pro_argument}

        CON Argument:

        {state.con_argument}

        Produce a balanced conclusion.
        """
    )

    return {
        "final_answer": response.content
    }


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "pro_agent",
    pro_agent
)

builder.add_node(
    "con_agent",
    con_agent
)

builder.add_node(
    "synthesis_agent",
    synthesis_agent
)

builder.add_edge(
    START,
    "pro_agent"
)

builder.add_edge(
    START,
    "con_agent"
)

builder.add_edge(
    "pro_agent",
    "synthesis_agent"
)

builder.add_edge(
    "con_agent",
    "synthesis_agent"
)

builder.add_edge(
    "synthesis_agent",
    END
)

graph = builder.compile()


# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "question":
        "Should remote work become the default working model?"
    }
)

print(result["final_answer"])

---

## Example Output

```text
Remote work offers significant benefits including flexibility,
reduced commuting time, and access to global talent pools.

However, challenges such as reduced in-person collaboration,
organizational culture concerns, and communication difficulties
must also be considered.

A balanced approach may involve hybrid work models that combine
the advantages of flexibility with the benefits of face-to-face interaction.
```

---

## Explanation

## What Is the Debate Pattern?

The Debate Pattern introduces:

```text
Multiple reasoning agents
```

that intentionally explore different viewpoints.

Instead of:

```text
One answer
```

we generate:

```text
Competing arguments
```

and then reconcile them.

---

## Step 1 — Pro Agent

The first agent argues:

```text
In favor
```

of the proposition.

Output:

```python
state.pro_argument
```

The goal is to produce the strongest possible supporting case.

---

## Step 2 — Con Agent

The second agent argues:

```text
Against
```

the proposition.

Output:

```python
state.con_argument
```

The goal is to produce the strongest opposing case.

---

## Step 3 — Synthesis Agent

The synthesis agent reviews:

```text
Pro Argument
+
Con Argument
```

and produces:

```text
Balanced Conclusion
```

Stored in:

```python
state.final_answer
```

---

## Execution Flow

```text
                 START
                   │
          ┌────────┴────────┐
          ▼                 ▼
      Pro Agent       Con Agent
          │                 │
          └────────┬────────┘
                   ▼
           Synthesis Agent
                   │
                   ▼
                  END
```

This is one of the first examples of:

```text
Parallel Agent Execution
```

in LangGraph.

---

## Why Debate Works

Complex questions often involve tradeoffs.

Example:

```text
Remote Work
```

Benefits:

```text
Flexibility
Lower Costs
```

Risks:

```text
Isolation
Communication Challenges
```

A debate forces the system to consider both.

---

## Debate vs Reflection

### Reflection Pattern

```text
Generate
 ↓
Review
 ↓
Improve
```

One perspective.

---

### Debate Pattern

```text
Perspective A
Perspective B
 ↓
Synthesize
```

Multiple perspectives.

---

## Debate vs Critic Pattern

### Critic Pattern

```text
Answer
 ↓
Critique
 ↓
Revision
```

Focus:

```text
Finding weaknesses
```

---

### Debate Pattern

```text
Argument A
Argument B
 ↓
Synthesis
```

Focus:

```text
Exploring alternatives
```

---

## Benefits of the Debate Pattern

### 1. Broader Reasoning

Multiple viewpoints improve coverage.

---

### 2. Reduced Bias

The system becomes less dependent on a single perspective.

---

### 3. Better Decision-Making

Tradeoffs become visible.

---

### 4. Improved Transparency

Users can inspect:

```python
pro_argument
```

and:

```python
con_argument
```

independently.

---

## Common Use Cases

### Policy Analysis

```text
Support Policy
Oppose Policy
 ↓
Recommendation
```

---

### Business Decisions

```text
Launch Product
Delay Product
 ↓
Decision
```

---

### Investment Analysis

```text
Bull Case
Bear Case
 ↓
Assessment
```

---

### Risk Evaluation

```text
Opportunity
Threat
 ↓
Final Analysis
```

---

## Extending the Pattern

Many advanced systems use:

```text
3 Agents
5 Agents
10 Agents
```

instead of just two.

Example:

```text
Technical Expert
Financial Expert
Legal Expert
Operations Expert
```

All contribute unique perspectives.

---

## Multi-Round Debates

A more advanced debate may allow agents to respond to each other.

Example:

```text
Round 1
Pro vs Con

Round 2
Counterarguments

Round 3
Final Statements

Synthesis
```

This creates richer reasoning but increases cost.

---

## Common Mistakes

### 1. Weak Role Definitions

Bad:

```text
Agent A
Agent B
```

No distinction.

---

Better:

```text
Pro Agent
Con Agent
```

Clear positions.

---

### 2. Premature Synthesis

The synthesis agent should review both sides carefully.

Avoid:

```text
Ignoring one argument
```

---

### 3. Forcing a Winner

The goal is often:

```text
Balanced reasoning
```

not:

```text
Declare a winner
```

---

### 4. Debate Without Diversity

If both agents produce nearly identical answers:

```text
No real debate occurs.
```

Prompts should encourage contrasting viewpoints.

---

## Mental Model

Think of the Debate Pattern as:

```text
A panel discussion
```

where multiple experts present competing viewpoints before a final recommendation is made.

---

## Architecture

```text
                 Question
                     │
         ┌───────────┴──────────┐
         ▼                       ▼
    ┌────────┐             ┌────────┐
    │  PRO   │             │  CON   │
    └────┬───┘             └───┬────┘
         │                     │
         └──────────┬──────────┘
                    ▼
          ┌─────────────────┐
          │   Synthesis     │
          └────────┬────────┘
                   │
                   ▼
             Final Answer
```

---

## Why This Matters

The Debate Pattern is widely used in advanced agentic systems because it encourages:

```text
Diverse viewpoints
Critical thinking
Balanced conclusions
```

Rather than relying on a single chain of reasoning, the system explores competing arguments before deciding what to believe.

This often produces more robust and trustworthy outputs.

---

## Key Takeaways

- The Debate Pattern uses multiple agents with competing viewpoints.
- Each agent argues a different position.
- A synthesis step combines the arguments into a balanced conclusion.
- Debate improves reasoning by exposing tradeoffs and alternative perspectives.
- The pattern naturally supports parallel execution in LangGraph.
- Debate is useful for policy analysis, business decisions, investment research, and risk evaluation.
- The pattern reduces dependence on a single perspective.
- In the next lab, we will explore the Tree of Thoughts Pattern, where agents explore multiple reasoning paths before selecting the best solution.
