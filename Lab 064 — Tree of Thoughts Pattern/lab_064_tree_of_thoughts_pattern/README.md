# Lab 064 — Tree of Thoughts Pattern

## Lab Intro

In Lab 063, we explored the **Debate Pattern**:

```text
PRO Agent
CON Agent
   ↓
Synthesis
```

This introduced multiple perspectives and improved reasoning quality.

However, debate still has a limitation:

```text
It explores only a few fixed viewpoints.
```

Real problem solving is often not binary.

Instead, we naturally explore:

```text
multiple possible paths
branching ideas
alternative strategies
```

This leads us to one of the most powerful reasoning patterns in agentic AI:

> **Tree of Thoughts Pattern**

---

## Key Idea

Instead of generating a single chain of reasoning, the model explores:

```text
multiple branches of thought
```

then evaluates them and selects the best one.

---

## Traditional Reasoning

```text
Question
   ↓
Single Chain of Thought
   ↓
Answer
```

---

## Tree of Thoughts Reasoning

```text
Question
   ↓
Thought A ─┐
Thought B ─┼── Evaluation ──► Best Path ──► Answer
Thought C ─┘
```

The system explores multiple candidate reasoning paths before committing.

---

## Enterprise Analogy

Imagine a product team designing a new feature.

They brainstorm:

```text
Approach A: Simple UI redesign
Approach B: Add automation
Approach C: Introduce AI assistant
```

Instead of picking the first idea, they:

```text
Evaluate all options
Compare tradeoffs
Select the best strategy
```

This is exactly what Tree of Thoughts does.

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

    thought_a: str = ""

    thought_b: str = ""

    thought_c: str = ""

    evaluation: str = ""

    final_answer: str = ""


# -------------------------
# LLM
# -------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)


# -------------------------
# Thought A
# -------------------------

def generate_thought_a(state: State):

    response = llm.invoke(
        f"""
        Generate a solution approach (A)
        for the following question:

        {state.question}

        Focus on a practical and simple approach.
        """
    )

    return {
        "thought_a": response.content
    }


# -------------------------
# Thought B
# -------------------------

def generate_thought_b(state: State):

    response = llm.invoke(
        f"""
        Generate a solution approach (B)
        for the following question:

        {state.question}

        Focus on an innovative and scalable approach.
        """
    )

    return {
        "thought_b": response.content
    }


# -------------------------
# Thought C
# -------------------------

def generate_thought_c(state: State):

    response = llm.invoke(
        f"""
        Generate a solution approach (C)
        for the following question:

        {state.question}

        Focus on a cost-effective and minimal approach.
        """
    )

    return {
        "thought_c": response.content
    }


# -------------------------
# Evaluation Agent
# -------------------------

def evaluate_thoughts(state: State):

    response = llm.invoke(
        f"""
        Evaluate the following three approaches:

        Approach A:
        {state.thought_a}

        Approach B:
        {state.thought_b}

        Approach C:
        {state.thought_c}

        Choose the best approach and explain why.
        """
    )

    return {
        "evaluation": response.content
    }


# -------------------------
# Final Answer Agent
# -------------------------

def final_answer_agent(state: State):

    response = llm.invoke(
        f"""
        Using the selected best approach:

        {state.evaluation}

        Provide a final, well-structured answer to:

        {state.question}
        """
    )

    return {
        "final_answer": response.content
    }


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node("thought_a", generate_thought_a)
builder.add_node("thought_b", generate_thought_b)
builder.add_node("thought_c", generate_thought_c)

builder.add_node("evaluate", evaluate_thoughts)
builder.add_node("final_answer", final_answer_agent)

builder.add_edge(START, "thought_a")
builder.add_edge(START, "thought_b")
builder.add_edge(START, "thought_c")

builder.add_edge("thought_a", "evaluate")
builder.add_edge("thought_b", "evaluate")
builder.add_edge("thought_c", "evaluate")

builder.add_edge("evaluate", "final_answer")
builder.add_edge("final_answer", END)

graph = builder.compile()


# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "question":
        "How can a small business improve customer retention?"
    }
)

print(result["final_answer"])

---

## Example Output

```text
A small business can improve customer retention by focusing on personalized service,
consistent communication, and value-driven engagement.

One effective approach is to implement a simple customer feedback system to
understand pain points and preferences.

Additionally, businesses can use lightweight CRM tools to track interactions
and offer targeted promotions. Cost-effective loyalty programs and regular
follow-ups can significantly increase repeat customers.

Overall, combining simplicity with consistency is often the most practical
strategy for small businesses.
```

---

## Explanation

## What Is the Tree of Thoughts Pattern?

The Tree of Thoughts Pattern extends reasoning by allowing:

```text
multiple simultaneous reasoning paths
```

Instead of committing to one idea early, the system explores several options.

---

## Step 1 — Generate Multiple Thoughts

We create three different reasoning branches:

### Thought A

```text
Simple and practical approach
```

### Thought B

```text
Innovative and scalable approach
```

### Thought C

```text
Cost-effective and minimal approach
```

Each represents a different strategy.

---

## Step 2 — Evaluate All Thoughts

The evaluation node compares:

```text
A vs B vs C
```

It decides:

```text
Which approach is best and why
```

This step introduces structured comparison.

---

## Step 3 — Generate Final Answer

The final node uses:

```text
Selected best approach
```

to produce a complete answer.

---

## Execution Flow

```text
            START
              │
   ┌──────────┼──────────┐
   ▼          ▼          ▼
Thought A  Thought B  Thought C
   └──────────┼──────────┘
              ▼
        Evaluation Node
              │
              ▼
        Final Answer
              │
              ▼
             END
```

This is a classic **branch-and-merge architecture**.

---

## Why Tree of Thoughts Works

Many problems have:

```text
multiple valid strategies
```

Instead of relying on a single path, this pattern:

- explores alternatives
- compares tradeoffs
- selects the best option

This improves robustness.

---

## Tree of Thoughts vs Debate

### Debate Pattern

```text
Two opposing views
↓
Synthesis
```

Focused on:

```text
argument vs counterargument
```

---

### Tree of Thoughts Pattern

```text
Multiple independent solutions
↓
Evaluation
↓
Selection
```

Focused on:

```text
best possible approach
```

---

## Tree of Thoughts vs Reflection

### Reflection

```text
Improve one answer
```

---

### Tree of Thoughts

```text
Generate multiple answers
then choose best
```

---

## Benefits of Tree of Thoughts

### 1. Better Exploration

Avoids early commitment to one idea.

---

### 2. Higher Quality Outputs

Multiple candidates increase solution quality.

---

### 3. Structured Decision-Making

Explicit evaluation step improves clarity.

---

### 4. Flexible Architecture

Easy to extend with more branches.

---

## Common Use Cases

### Product Design

```text
UI Approach A
UI Approach B
UI Approach C
```

---

### Strategy Planning

```text
Growth Strategy A
Growth Strategy B
Growth Strategy C
```

---

### Problem Solving

```text
Algorithm A
Algorithm B
Algorithm C
```

---

### Business Decisions

```text
Pricing Model A
Pricing Model B
Pricing Model C
```

---

## Extending the Pattern

You can expand Tree of Thoughts into:

```text
Tree → Subtrees → Multi-Level Reasoning
```

Example:

```text
Level 1: Ideas
Level 2: Expanded plans
Level 3: Evaluation
```

This becomes a deep reasoning structure.

---

## Common Mistakes

### 1. Weak Branch Diversity

Bad:

```text
Three similar approaches
```

Better:

```text
Distinct strategies per branch
```

---

### 2. Skipping Evaluation

Without evaluation:

```text
No comparison = no selection logic
```

---

### 3. Overcomplicating Small Tasks

Not every task needs multiple branches.

Simple questions may not benefit.

---

### 4. No Clear Selection Criteria

Evaluation should explain:

```text
WHY one option is better
```

---

## Mental Model

Think of Tree of Thoughts as:

```text
Brainstorm → Compare → Decide
```

instead of:

```text
Think → Answer
```

---

## Architecture

```text
                 Question
                     │
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
 Thought A       Thought B       Thought C
     └───────────────┼───────────────┘
                     ▼
              Evaluation Node
                     │
                     ▼
               Final Answer
```

---

## Why This Matters

Tree of Thoughts is a core reasoning strategy in advanced AI systems.

It enables models to:

```text
explore multiple hypotheses
compare alternatives
select optimal solutions
```

This is much closer to how humans solve complex problems.

---

## Key Takeaways

- Tree of Thoughts explores multiple reasoning paths in parallel.
- Each branch represents a different strategy or solution.
- An evaluation step selects the best option.
- The pattern improves exploration and decision quality.
- It differs from debate by focusing on solutions rather than arguments.
- It differs from reflection by generating multiple independent paths.
- It is widely used in planning, design, and strategic reasoning systems.
- In the next lab, we will explore the LLM-as-Judge Pattern, where a model evaluates outputs using structured scoring instead of free-form reasoning.
