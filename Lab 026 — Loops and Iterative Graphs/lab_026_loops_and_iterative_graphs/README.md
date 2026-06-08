# Lab 026 — Loops and Iterative Graphs

## Lab Intro

So far, all workflows in LangGraph have been **acyclic**:

```text
START → A → B → C → END
```

or branching:

```text
START → A → (B or C) → END
```

But many real enterprise processes are not single-pass.

They require:

- repeated attempts
- refinement cycles
- convergence loops
- iterative decision-making

This introduces:

> **Loops and Iterative Graphs**

A loop allows a graph to **revisit a node multiple times** until a condition is met.

---

## Enterprise Analogy

Think of a customer support chatbot:

```text
User Query
   ↓
draft_response
   ↓
review_quality
   ↓
GOOD? → END
   ↓ NO
improve_response → back to draft_response
```

The system iterates until the response is acceptable.

---

## Lab Code

from typing import Optional

from pydantic import BaseModel

from langgraph.graph import StateGraph
from langgraph.graph import START, END


# -------------------------
# State Model
# -------------------------

class State(BaseModel):
    question: str

    draft: Optional[str] = None

    score: Optional[int] = None

    iterations: int = 0

    final_answer: Optional[str] = None


# -------------------------
# Node 1 — Draft Answer
# -------------------------

def draft_answer(state: State):

    state.iterations += 1

    return {
        "draft": f"Draft attempt {state.iterations} for: {state.question}"
    }


# -------------------------
# Node 2 — Evaluate Answer
# -------------------------

def evaluate_answer(state: State):

    # Simulated scoring logic
    # Improves over iterations

    score = 40 + (state.iterations * 20)

    if score > 80:
        quality = "good"
    else:
        quality = "bad"

    return {
        "score": score,
        "quality": quality
    }


# -------------------------
# Node 3 — Improve Answer
# -------------------------

def improve_answer(state: State):

    return {
        "draft": state.draft + " [improved]"
    }


# -------------------------
# Node 4 — Finalize
# -------------------------

def finalize(state: State):

    return {
        "final_answer": state.draft
    }


# -------------------------
# Router — Loop Control
# -------------------------

def loop_router(state: State):

    if state.score is None:
        return "draft_answer"

    if state.score > 80:
        return "finalize"

    return "improve_answer"


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node("draft_answer", draft_answer)
builder.add_node("evaluate_answer", evaluate_answer)
builder.add_node("improve_answer", improve_answer)
builder.add_node("finalize", finalize)

builder.add_edge(START, "draft_answer")
builder.add_edge("draft_answer", "evaluate_answer")

builder.add_conditional_edges(
    "evaluate_answer",
    loop_router,
    {
        "draft_answer": "draft_answer",
        "improve_answer": "improve_answer",
        "finalize": "finalize"
    }
)

builder.add_edge("improve_answer", "draft_answer")
builder.add_edge("finalize", END)

graph = builder.compile()


# -------------------------
# Execute Graph
# -------------------------

result = graph.invoke(
    {
        "question": "Explain quantum entanglement simply"
    }
)

print(result)

---

## Expected Output (Example)

```python
{
    'question': 'Explain quantum entanglement simply',
    'draft': 'Draft attempt 3 for: Explain quantum entanglement simply [improved] [improved]',
    'score': 80,
    'final_answer': 'Draft attempt 3 for: Explain quantum entanglement simply [improved] [improved]',
    'iterations': 3
}
```

---

## Explanation

### What Are Loops in LangGraph?

Loops allow a graph to:

> revisit nodes until a condition is satisfied

Instead of:

```text
Single pass execution
```

we get:

```text
Iterative refinement
```

---

## Step 1 — Initial Draft

```python
draft_answer()
```

Creates first version:

```text
Draft attempt 1
```

---

## Step 2 — Evaluation

```python
evaluate_answer()
```

Computes a score:

```text
40 → 60 → 80
```

Score increases per iteration.

---

## Step 3 — Loop Decision

Router logic:

```python
if score > 80:
    finalize
else:
    improve_answer
```

---

## Step 4 — Improvement Loop

If score is low:

```text
improve_answer → draft_answer → evaluate → repeat
```

This forms a cycle.

---

## Step 5 — Termination

When:

```text
score > 80
```

graph exits:

```text
finalize → END
```

---

## Execution Flow Example

### Iteration 1

```text
draft → evaluate (score 60)
→ improve
```

---

### Iteration 2

```text
draft → evaluate (score 80)
→ improve or finalize decision
```

---

### Iteration 3

```text
finalize → END
```

---

## Why Loops Matter

Real systems are not single-shot.

They require refinement:

### 1. LLM response improvement

```text
draft → critique → improve → repeat
```

---

### 2. Data processing pipelines

```text
clean → validate → fix → re-validate
```

---

### 3. Agent reasoning loops

```text
plan → act → observe → refine
```

---

## Key Concept: Convergence

Loops must eventually terminate.

Otherwise:

```text
Infinite loop → system crash
```

So we always need:

```text
Stopping condition
```

Example:

```python
if score > threshold:
    END
```

---

## Static vs Conditional vs Loop Graphs

### Static

```text
A → B → C
```

---

### Conditional

```text
A → (B or C)
```

---

### Loop

```text
A → B → C → B → C → END
```

---

## Common Mistakes

### 1. Missing termination condition

Bad:

```text
Always loop
```

Result:

```text
Infinite execution
```

---

### 2. No state progression

If score never changes:

```text
loop never ends
```

---

### 3. Overly aggressive looping

Too many iterations:

```text
expensive + slow system
```

---

## Enterprise Example

### AI Content Generation System

```text
Generate draft
   ↓
Quality check
   ↓
If poor → regenerate
   ↓
If good → publish
```

Used in:

- marketing content
- code generation
- report writing

---

## Key Takeaways

- Loops allow LangGraph workflows to revisit nodes repeatedly.
- They enable iterative refinement and convergence.
- A loop must always have a termination condition.
- Common use cases include LLM refinement, validation pipelines, and agent reasoning.
- Loops transform graphs from linear flows into adaptive systems.