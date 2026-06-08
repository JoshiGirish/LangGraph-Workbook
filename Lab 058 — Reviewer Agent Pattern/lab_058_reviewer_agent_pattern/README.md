# Lab 058 — Reviewer Agent Pattern

## Lab Intro

In real organizations, content usually goes through review before publication.

Examples:

```text
Writer
  ↓
Editor
  ↓
Published Article
```

or

```text
Developer
  ↓
Code Reviewer
  ↓
Production
```

This introduces one of the most important multi-agent architectures:

> **Reviewer Agent Pattern**

A reviewer agent examines another agent's work and provides feedback before final delivery.

---

## Key Idea

Without review:

```text
Research
   ↓
Write
   ↓
Publish
```

With review:

```text
Research
   ↓
Write
   ↓
Review
   ↓
Publish
```

The reviewer acts as a quality-control layer.

---

## Enterprise Analogy

Consider a consulting firm creating a client report.

Workflow:

```text
Research Analyst
      ↓
Report Writer
      ↓
Senior Reviewer
      ↓
Client Delivery
```

The reviewer checks for:

- factual accuracy
- missing information
- weak arguments
- unclear writing

This reduces mistakes and improves quality.

Multi-agent systems use the same approach.

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

    topic: str

    research_notes: str = ""

    draft_article: str = ""

    review_feedback: str = ""

    final_article: str = ""


# -------------------------
# LLM
# -------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# -------------------------
# Research Agent
# -------------------------

def research_agent(state: State):

    response = llm.invoke(
        f"""
        Research:

        {state.topic}

        Provide key facts,
        benefits, and challenges.
        """
    )

    return {
        "research_notes": response.content
    }


# -------------------------
# Writer Agent
# -------------------------

def writer_agent(state: State):

    response = llm.invoke(
        f"""
        Write an article using:

        {state.research_notes}
        """
    )

    return {
        "draft_article": response.content
    }


# -------------------------
# Reviewer Agent
# -------------------------

def reviewer_agent(state: State):

    response = llm.invoke(
        f"""
        Review the article below.

        Identify:
        - weaknesses
        - missing information
        - clarity issues

        Article:

        {state.draft_article}
        """
    )

    return {
        "review_feedback": response.content
    }


# -------------------------
# Final Writer Agent
# -------------------------

def revision_agent(state: State):

    response = llm.invoke(
        f"""
        Improve the article using
        the review feedback.

        Draft:

        {state.draft_article}

        Feedback:

        {state.review_feedback}
        """
    )

    return {
        "final_article": response.content
    }


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "research_agent",
    research_agent
)

builder.add_node(
    "writer_agent",
    writer_agent
)

builder.add_node(
    "reviewer_agent",
    reviewer_agent
)

builder.add_node(
    "revision_agent",
    revision_agent
)

builder.add_edge(
    START,
    "research_agent"
)

builder.add_edge(
    "research_agent",
    "writer_agent"
)

builder.add_edge(
    "writer_agent",
    "reviewer_agent"
)

builder.add_edge(
    "reviewer_agent",
    "revision_agent"
)

builder.add_edge(
    "revision_agent",
    END
)

graph = builder.compile()


# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "topic":
        "Artificial Intelligence in Healthcare"
    }
)

print(
    result["final_article"]
)

---

## Example Output

```text
Artificial Intelligence is transforming healthcare through improved diagnostics,
predictive analytics, and personalized treatment planning.

AI systems help physicians analyze medical images, detect diseases earlier,
and optimize hospital operations. These capabilities can improve efficiency
and patient outcomes.

However, successful adoption requires careful attention to privacy,
regulatory compliance, model bias, and transparency. Human oversight
remains essential to ensure safe and responsible use.
```

---

## Explanation

## What Is the Reviewer Agent Pattern?

The Reviewer Agent Pattern introduces a dedicated quality-control step.

Instead of:

```text
Generate Output
      ↓
Return Output
```

we use:

```text
Generate Output
      ↓
Review Output
      ↓
Improve Output
```

This creates a feedback loop.

---

## Step 1 — Research Agent

The first agent gathers information.

Output:

```text
Research Notes
```

Stored in:

```python
research_notes
```

---

## Step 2 — Writer Agent

The writer creates an initial draft.

Output:

```text
Draft Article
```

Stored in:

```python
draft_article
```

At this point:

```text
The article may contain weaknesses.
```

---

## Step 3 — Reviewer Agent

The reviewer does not rewrite the article.

Its job is:

```text
Evaluate
Critique
Identify Gaps
```

Output:

```text
Review Feedback
```

Examples:

```text
Missing challenges section
```

or

```text
Benefits need supporting details
```

---

## Step 4 — Revision Agent

The revision agent receives:

```text
Draft
+
Feedback
```

and produces:

```text
Improved Version
```

This becomes the final output.

---

## Execution Flow

```text
START
   │
   ▼
Research Agent
   │
   ▼
Writer Agent
   │
   ▼
Reviewer Agent
   │
   ▼
Revision Agent
   │
   ▼
END
```

---

## Why This Pattern Works

A single LLM often performs better when asked to:

```text
Generate
```

and

```text
Critique
```

in separate steps.

Instead of:

```text
Write perfectly on first try
```

we allow:

```text
Draft
Review
Improve
```

This mirrors human workflows.

---

## Reviewer Responsibilities

A reviewer may check:

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

### Clarity

```text
Is it easy to understand?
```

---

### Consistency

```text
Are arguments coherent?
```

---

### Compliance

```text
Does it follow required rules?
```

---

## Common Enterprise Uses

### Content Creation

```text
Writer
  ↓
Reviewer
```

---

### Legal Review

```text
Draft Contract
      ↓
Compliance Reviewer
```

---

### Code Generation

```text
Coder Agent
      ↓
Code Reviewer
```

---

### Research Reports

```text
Analyst
      ↓
Senior Reviewer
```

---

## Reviewer vs Writer

### Writer

Goal:

```text
Create content
```

Focus:

```text
Generation
```

---

### Reviewer

Goal:

```text
Improve content
```

Focus:

```text
Evaluation
```

Keeping these roles separate often improves quality.

---

## Extending the Pattern

Many systems use multiple reviewers.

Example:

```text
Writer
   ↓
Technical Reviewer
   ↓
Compliance Reviewer
   ↓
Editor
```

Each reviewer checks a different dimension.

---

## Common Mistakes

### 1. Reviewer Rewrites Everything

Bad reviewer:

```text
Generates a new article
```

This duplicates the writer.

---

Better:

```text
Provides critique and feedback
```

---

### 2. Weak Review Instructions

Bad:

```text
Review this.
```

Too vague.

---

Better:

```text
Check accuracy,
clarity,
and missing information.
```

---

### 3. Skipping Revision

Bad:

```text
Writer
  ↓
Reviewer
  ↓
END
```

Feedback is generated but never used.

---

Better:

```text
Writer
  ↓
Reviewer
  ↓
Revision Agent
```

---

### 4. Overly Harsh Review Loops

Infinite critique cycles can occur.

Production systems usually limit:

```text
1–3 review rounds
```

to control cost and latency.

---

## Mental Model

Think of the reviewer agent as:

```text
An editor before publication
```

The reviewer's purpose is not to create.

The reviewer exists to improve.

---

## Architecture

```text
                Topic
                  │
                  ▼
         ┌────────────────┐
         │ Research Agent │
         └───────┬────────┘
                 │
                 ▼
         ┌────────────────┐
         │  Writer Agent  │
         └───────┬────────┘
                 │
                 ▼
         ┌────────────────┐
         │ Reviewer Agent │
         └───────┬────────┘
                 │
                 ▼
         ┌────────────────┐
         │ Revision Agent │
         └───────┬────────┘
                 │
                 ▼
            Final Output
```

---

## Why This Matters

Many production-grade AI systems are not:

```text
One-shot generation systems
```

They are:

```text
Generate
  ↓
Review
  ↓
Revise
```

systems.

This approach improves quality, reliability, and consistency while remaining relatively simple to implement.

---

## Key Takeaways

- The Reviewer Agent Pattern adds a quality-control step to multi-agent workflows.
- Reviewers critique and evaluate rather than generate primary content.
- Separating generation and review often improves output quality.
- Feedback becomes an explicit artifact that downstream agents can use.
- Revision agents transform reviewer feedback into improved outputs.
- The pattern mirrors real-world editorial, consulting, legal, and software review processes.
- Reviewer agents are foundational for building robust multi-agent systems.
- In the next lab, we will explore the Planner-Executor pattern, one of the most important architectures for complex agentic workflows.
