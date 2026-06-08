# Lab 061 — Reflection Pattern

## Lab Intro

In Lab 060, we introduced the **Planner Pattern**:

```text
Task
 ↓
Plan
 ↓
Execute
```

Planning helps an agent think before acting.

However, even a good plan can produce an imperfect answer.

Humans often improve their work by asking:

```text
Did I miss anything?
Could this be better?
```

This process is called:

> **Reflection**

Instead of immediately returning an answer, the agent pauses and reviews its own work.

This creates the:

> **Reflection Pattern**

---

## Key Idea

Without reflection:

```text
Question
   ↓
Answer
```

With reflection:

```text
Question
   ↓
Answer Draft
   ↓
Reflection
   ↓
Improved Answer
```

The reflection step acts like an internal review.

---

## Enterprise Analogy

Imagine an analyst preparing a report.

A rushed workflow:

```text
Write Report
     ↓
Submit
```

A better workflow:

```text
Write Report
     ↓
Review Report
     ↓
Improve Report
     ↓
Submit
```

The analyst becomes their own reviewer.

Reflection allows AI systems to do the same thing.

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

    reflection: str = ""

    final_answer: str = ""


# -------------------------
# LLM
# -------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# -------------------------
# Step 1 — Generate Draft
# -------------------------

def generate_answer(state: State):

    response = llm.invoke(
        f"""
        Answer the following question:

        {state.question}
        """
    )

    return {
        "draft_answer": response.content
    }


# -------------------------
# Step 2 — Reflect
# -------------------------

def reflect(state: State):

    response = llm.invoke(
        f"""
        Review the answer below.

        Identify:
        - missing information
        - weaknesses
        - possible improvements

        Answer:

        {state.draft_answer}
        """
    )

    return {
        "reflection": response.content
    }


# -------------------------
# Step 3 — Improve
# -------------------------

def improve_answer(state: State):

    response = llm.invoke(
        f"""
        Improve the answer using
        the reflection notes.

        Original Answer:

        {state.draft_answer}

        Reflection:

        {state.reflection}
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
    "generate_answer",
    generate_answer
)

builder.add_node(
    "reflect",
    reflect
)

builder.add_node(
    "improve_answer",
    improve_answer
)

builder.add_edge(
    START,
    "generate_answer"
)

builder.add_edge(
    "generate_answer",
    "reflect"
)

builder.add_edge(
    "reflect",
    "improve_answer"
)

builder.add_edge(
    "improve_answer",
    END
)

graph = builder.compile()


# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "question":
        "What are the advantages and disadvantages of remote work?"
    }
)

print(result["final_answer"])

---

## Example Output

```text
Remote work offers several advantages, including increased flexibility,
reduced commuting time, and access to a broader talent pool for employers.

Employees often benefit from improved work-life balance and greater autonomy.

However, remote work can also create challenges such as communication barriers,
feelings of isolation, and difficulties maintaining team culture.

Organizations must balance flexibility with effective collaboration practices
to maximize the benefits of remote work.
```

---

## Explanation

## What Is the Reflection Pattern?

The Reflection Pattern introduces a self-review step.

Instead of:

```text
Generate
 ↓
Return
```

the agent performs:

```text
Generate
 ↓
Review
 ↓
Improve
```

before returning the final answer.

---

## Step 1 — Generate an Initial Answer

The first node creates:

```text
Draft Answer
```

Stored in:

```python
state.draft_answer
```

This is the agent's first attempt.

---

## Step 2 — Reflect on the Draft

The reflection step reviews:

```python
state.draft_answer
```

and identifies:

- weaknesses
- missing details
- improvement opportunities

The result is stored in:

```python
state.reflection
```

---

## Step 3 — Improve the Answer

The final node receives:

```text
Draft Answer
+
Reflection Notes
```

and produces a better version.

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
Generate Draft
   │
   ▼
Reflect
   │
   ▼
Improve
   │
   ▼
END
```

---

## Why Reflection Helps

Large language models often generate reasonable first drafts.

However:

```text
First draft ≠ Best draft
```

Reflection creates an opportunity to:

- catch omissions
- improve clarity
- strengthen reasoning
- add missing perspectives

---

## Reflection vs Planning

### Planner Pattern

Question:

```text
What should I do?
```

Focus:

```text
Before generation
```

---

### Reflection Pattern

Question:

```text
How good is my answer?
```

Focus:

```text
After generation
```

---

## Reflection Prompting

A good reflection prompt asks:

```text
What is missing?
What is unclear?
What could be improved?
```

Poor reflection prompts often produce:

```text
Looks good.
```

without meaningful critique.

---

## Common Use Cases

### Content Writing

```text
Draft
 ↓
Reflect
 ↓
Improve
```

---

### Report Generation

```text
Analysis
 ↓
Reflection
 ↓
Revision
```

---

### Educational Systems

```text
Solution
 ↓
Reflection
 ↓
Better Explanation
```

---

### Customer Communications

```text
Response Draft
 ↓
Reflection
 ↓
Refined Response
```

---

## Reflection vs Reviewer Agent

At first glance, reflection looks similar to the reviewer pattern.

However:

### Reflection Pattern

```text
One agent reviews itself
```

---

### Reviewer Pattern

```text
Separate reviewing agent
```

Reflection is:

```text
Self-review
```

Reviewer pattern is:

```text
External review
```

---

## Benefits of Reflection

### 1. Better Quality

The model gets a second chance to improve.

---

### 2. More Complete Answers

Reflection often identifies missing topics.

---

### 3. Improved Reasoning

Weak logic can be strengthened before delivery.

---

### 4. Easy to Add

The pattern only requires one additional reasoning step.

---

## Common Mistakes

### 1. Weak Reflection Prompts

Bad:

```text
Review this answer.
```

Too vague.

---

Better:

```text
Identify weaknesses,
missing information,
and opportunities for improvement.
```

---

### 2. Skipping Improvement

Bad:

```text
Generate
 ↓
Reflect
 ↓
END
```

---

Better:

```text
Generate
 ↓
Reflect
 ↓
Improve
```

---

### 3. Infinite Reflection Loops

It is tempting to repeat:

```text
Reflect
Improve
Reflect
Improve
```

indefinitely.

In production systems:

```text
Reflection rounds are usually limited.
```

---

### 4. Reflecting on Trivial Tasks

Not every question needs reflection.

Simple requests may not justify the additional cost.

---

## Mental Model

Think of the Reflection Pattern as:

```text
Write Draft
      ↓
Proofread Yourself
      ↓
Submit Final Version
```

The model becomes its own editor.

---

## Architecture

```text
             Question
                 │
                 ▼
      ┌──────────────────┐
      │ Generate Answer  │
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │     Reflect      │
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │ Improve Answer   │
      └────────┬─────────┘
               │
               ▼
          Final Answer
```

---

## Why This Matters

Reflection is one of the foundational reasoning patterns in agentic AI.

Many advanced systems improve performance not by using larger models, but by allowing models to:

```text
Think
Review
Improve
```

before producing a final answer.

This often leads to better results than one-shot generation.

---

## Key Takeaways

- The Reflection Pattern adds a self-review step after generation.
- Reflection identifies weaknesses and improvement opportunities.
- The final answer is produced using both the draft and the reflection.
- Reflection improves completeness, clarity, and reasoning quality.
- It differs from the Reviewer Pattern because the model reviews its own work.
- The pattern is simple yet highly effective.
- Reflection is commonly used in advanced agentic workflows.
- In the next lab, we will explore the Self-Correction Pattern, where agents explicitly identify mistakes and regenerate improved outputs.
