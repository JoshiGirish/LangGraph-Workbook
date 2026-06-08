# Lab 062 — Critic Pattern

## Lab Intro

In Lab 061, we explored the **Reflection Pattern**:

```text
Generate
   ↓
Reflect
   ↓
Improve
```

Reflection allows an agent to review its own work.

However, self-review has limitations.

Humans often miss their own mistakes because they are too close to the work.

This is why organizations use:

```text
Editors
Reviewers
Auditors
Code Reviewers
```

to provide an independent perspective.

Agent systems can do the same thing.

Instead of asking:

```text
How good is my answer?
```

we introduce a dedicated critic whose job is:

```text
Find weaknesses.
```

This architecture is known as the:

> **Critic Pattern**

---

## Key Idea

Without a critic:

```text
Question
   ↓
Answer
```

With a critic:

```text
Question
   ↓
Draft
   ↓
Critic
   ↓
Revision
   ↓
Final Answer
```

The critic acts as a quality-control mechanism.

---

## Enterprise Analogy

Think about software development.

Without code review:

```text
Developer
    ↓
Production
```

With code review:

```text
Developer
    ↓
Reviewer
    ↓
Production
```

The reviewer identifies:

- bugs
- risks
- missing requirements
- design issues

A critic agent performs the same role.

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

    draft_answer: str = ""

    critique: str = ""

    final_answer: str = ""


# -------------------------
# LLM
# -------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# -------------------------
# Writer
# -------------------------

def writer(state: State):

    response = llm.invoke(
        f"""
        Answer the following question.

        Question:

        {state.question}
        """
    )

    return {
        "draft_answer": response.content
    }


# -------------------------
# Critic
# -------------------------

def critic(state: State):

    response = llm.invoke(
        f"""
        Critically review the answer below.

        Identify:

        - factual weaknesses
        - missing information
        - unclear reasoning
        - possible improvements

        Answer:

        {state.draft_answer}
        """
    )

    return {
        "critique": response.content
    }


# -------------------------
# Revision
# -------------------------

def revise(state: State):

    response = llm.invoke(
        f"""
        Improve the answer using
        the critique below.

        Original Answer:

        {state.draft_answer}

        Critique:

        {state.critique}
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
    "writer",
    writer
)

builder.add_node(
    "critic",
    critic
)

builder.add_node(
    "revise",
    revise
)

builder.add_edge(
    START,
    "writer"
)

builder.add_edge(
    "writer",
    "critic"
)

builder.add_edge(
    "critic",
    "revise"
)

builder.add_edge(
    "revise",
    END
)

graph = builder.compile()


# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "question":
        "What are the benefits and risks of artificial intelligence?"
    }
)

print(result["final_answer"])

---

## Example Output

```text
Artificial intelligence offers numerous benefits, including automation,
improved decision-making, increased productivity, and advancements in
fields such as healthcare and scientific research.

However, AI also presents risks such as job displacement, algorithmic bias,
privacy concerns, and potential misuse. Responsible governance, transparency,
and human oversight are essential to maximize benefits while reducing risks.
```

---

## Explanation

## What Is the Critic Pattern?

The Critic Pattern separates:

```text
Creation
```

from

```text
Evaluation
```

Instead of asking the same agent to both create and judge simultaneously, we create a dedicated critique stage.

---

## Step 1 — Generate a Draft

The writer produces:

```text
Draft Answer
```

Stored in:

```python
state.draft_answer
```

This is the initial solution.

---

## Step 2 — Critique the Draft

The critic receives:

```python
state.draft_answer
```

Its goal is not to rewrite.

Its goal is to identify:

```text
Problems
Weaknesses
Gaps
Risks
```

The critique is stored in:

```python
state.critique
```

---

## Step 3 — Revise the Draft

The revision step receives:

```text
Draft Answer
+
Critique
```

and generates:

```text
Improved Answer
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
   ▼
 Writer
   │
   ▼
 Critic
   │
   ▼
 Revision
   │
   ▼
 END
```

---

## Why Use a Critic?

When generating content, models tend to focus on:

```text
Producing an answer
```

When critiquing content, models focus on:

```text
Finding problems
```

These are different cognitive tasks.

Separating them often improves results.

---

## Critic vs Reflection

These patterns appear similar but serve different purposes.

### Reflection Pattern

```text
Agent reviews itself
```

Flow:

```text
Generate
 ↓
Reflect
 ↓
Improve
```

The same agent effectively performs both roles.

---

### Critic Pattern

```text
Separate evaluator
```

Flow:

```text
Writer
 ↓
Critic
 ↓
Revision
```

Responsibilities are clearly separated.

---

## Benefits of the Critic Pattern

### 1. Better Quality Control

The critic explicitly searches for weaknesses.

---

### 2. More Complete Outputs

Missing topics are often identified during critique.

---

### 3. Improved Reliability

The revision stage receives structured feedback.

---

### 4. Modular Design

You can replace:

```text
Writer
```

or

```text
Critic
```

independently.

---

## What Makes a Good Critic?

A good critic focuses on:

### Accuracy

```text
Are facts correct?
```

---

### Completeness

```text
Anything missing?
```

---

### Logic

```text
Does reasoning make sense?
```

---

### Clarity

```text
Can readers understand it?
```

---

### Risk

```text
Could this cause problems?
```

---

## Common Use Cases

### Content Generation

```text
Writer
 ↓
Critic
 ↓
Revision
```

---

### Research Reports

```text
Analyst
 ↓
Reviewer
 ↓
Final Report
```

---

### Code Generation

```text
Coder
 ↓
Code Reviewer
 ↓
Improved Code
```

---

### Business Recommendations

```text
Proposal
 ↓
Critic
 ↓
Refined Proposal
```

---

## Extending the Pattern

A system can use multiple critics.

Example:

```text
Writer
   ↓
Technical Critic
Compliance Critic
Risk Critic
   ↓
Revision
```

Each critic evaluates a different dimension.

---

## Common Mistakes

### 1. Critic Rewrites the Answer

Bad:

```text
Critic generates new content
```

This overlaps with the writer.

---

Better:

```text
Critic identifies issues
```

Only.

---

### 2. Vague Critique Instructions

Bad:

```text
Review this answer.
```

Produces weak feedback.

---

Better:

```text
Identify weaknesses,
missing information,
and reasoning errors.
```

---

### 3. Ignoring Critique

Bad:

```text
Writer
 ↓
Critic
 ↓
END
```

Feedback is generated but never used.

---

Better:

```text
Writer
 ↓
Critic
 ↓
Revision
```

---

### 4. Endless Critique Loops

Repeated cycles:

```text
Critic
Revision
Critic
Revision
```

can become expensive.

Most systems limit review rounds.

---

## Mental Model

Think of the Critic Pattern as:

```text
Author
  ↓
Editor
  ↓
Published Version
```

The editor's job is not to write.

The editor's job is to improve what was written.

---

## Architecture

```text
             Question
                 │
                 ▼
        ┌────────────────┐
        │     Writer     │
        └───────┬────────┘
                │
                ▼
        ┌────────────────┐
        │     Critic     │
        └───────┬────────┘
                │
                ▼
        ┌────────────────┐
        │    Revision    │
        └───────┬────────┘
                │
                ▼
           Final Answer
```

---

## Why This Matters

The Critic Pattern is one of the most common quality-improvement techniques in agentic systems.

Many production workflows rely on:

```text
Generate
 ↓
Critique
 ↓
Revise
```

rather than trusting a single draft.

This simple architectural change can significantly improve reliability and output quality.

---

## Key Takeaways

- The Critic Pattern introduces a dedicated evaluation stage.
- The critic identifies weaknesses, gaps, and opportunities for improvement.
- Creation and evaluation are separated into distinct responsibilities.
- Critique is used to guide revision and produce higher-quality outputs.
- The pattern is widely used in writing, coding, analysis, and research workflows.
- Critic agents improve reliability by acting as quality-control mechanisms.
- The pattern scales naturally to multiple specialized critics.
- In the next lab, we will explore the Self-Correction Pattern, where agents explicitly detect mistakes and regenerate improved solutions.
