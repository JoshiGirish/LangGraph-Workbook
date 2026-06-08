# Lab 027 — Termination Conditions

## Lab Intro

Once you introduce loops in LangGraph, a new critical problem appears:

> How do we know when to stop?

Without a clear stopping rule, iterative graphs can:

- run forever
- waste compute
- produce unstable outputs
- exceed API limits

This introduces:

> **Termination Conditions**

A termination condition defines the rule that safely ends a loop.

---

## Enterprise Analogy

Think of an AI writing assistant:

```text
Draft → Review → Improve → Review → Improve → Finalize
```

But it must eventually stop:

```text
If quality ≥ threshold → STOP
If max iterations reached → STOP
If user approves → STOP
```

Without these rules:

```text
Infinite refinement loop ❌
```

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
    task: str

    draft: Optional[str] = None

    quality_score: Optional[int] = None

    iteration: int = 0

    status: Optional[str] = None


# -------------------------
# Node 1 — Generate Draft
# -------------------------

def generate_draft(state: State):

    state.iteration += 1

    return {
        "draft": f"Draft v{state.iteration} for task: {state.task}"
    }


# -------------------------
# Node 2 — Evaluate Quality
# -------------------------

def evaluate_quality(state: State):

    # Simulated improvement over time
    score = 30 + (state.iteration * 25)

    return {
        "quality_score": score
    }


# -------------------------
# Node 3 — Improve Draft
# -------------------------

def improve_draft(state: State):

    return {
        "draft": state.draft + " [improved]"
    }


# -------------------------
# Node 4 — Finalize
# -------------------------

def finalize(state: State):

    return {
        "status": "completed",
        "final_output": state.draft
    }


# -------------------------
# Router — Termination Logic
# -------------------------

MAX_ITERATIONS = 4
QUALITY_THRESHOLD = 85


def termination_router(state: State):

    # Hard stop: too many iterations
    if state.iteration >= MAX_ITERATIONS:
        return "finalize"

    # Success condition: good enough
    if state.quality_score is not None and state.quality_score >= QUALITY_THRESHOLD:
        return "finalize"

    # Otherwise continue loop
    return "improve_draft"


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node("generate_draft", generate_draft)
builder.add_node("evaluate_quality", evaluate_quality)
builder.add_node("improve_draft", improve_draft)
builder.add_node("finalize", finalize)

builder.add_edge(START, "generate_draft")
builder.add_edge("generate_draft", "evaluate_quality")

builder.add_conditional_edges(
    "evaluate_quality",
    termination_router,
    {
        "improve_draft": "improve_draft",
        "finalize": "finalize"
    }
)

builder.add_edge("improve_draft", "generate_draft")
builder.add_edge("finalize", END)

graph = builder.compile()


# -------------------------
# Execute Graph
# -------------------------

result = graph.invoke(
    {
        "task": "Write a short explanation of neural networks"
    }
)

print(result)

---

## Expected Output (Example)

```python
{
    'task': 'Write a short explanation of neural networks',
    'draft': 'Draft v3 for task: Write a short explanation of neural networks [improved] [improved]',
    'quality_score': 80,
    'iteration': 3,
    'status': 'completed',
    'final_output': 'Draft v3 for task: Write a short explanation of neural networks [improved] [improved]'
}
```

---

## Explanation

## What Are Termination Conditions?

A termination condition defines:

> when a loop should stop executing

In LangGraph loops, this is essential to prevent infinite execution.

---

## Step 1 — Two Types of Stopping Rules

We define two independent stopping conditions:

### 1. Success Condition

```python
if quality_score >= 85:
    stop
```

This means:

```text
Output is good enough → finish early
```

---

### 2. Safety Condition

```python
if iteration >= MAX_ITERATIONS:
    stop
```

This means:

```text
Prevent infinite loops → force stop
```

---

## Step 2 — Iterative Flow

Each cycle follows:

```text
generate_draft
    ↓
evaluate_quality
    ↓
decision (continue or stop)
```

---

## Step 3 — Loop Behavior

### Case A: Early Success

```text
iteration 2 → score 85+
```

Flow:

```text
STOP immediately → finalize
```

---

### Case B: Max Iterations Reached

```text
iteration 4 reached
```

Flow:

```text
STOP even if score is low
```

---

## Why Termination Conditions Matter

Without them:

```text
Loop runs forever ❌
API cost explodes ❌
System becomes unstable ❌
```

With them:

```text
Controlled execution ✔
Predictable cost ✔
Stable workflows ✔
```

---

## Step 4 — Common Patterns

### Pattern 1: Quality Threshold

```python
if score >= threshold:
    END
```

Used in:

- LLM generation
- content creation
- summarization systems

---

### Pattern 2: Max Iterations

```python
if iteration >= N:
    END
```

Used in:

- retry systems
- refinement loops
- planning agents

---

### Pattern 3: Hybrid (Best Practice)

We used both:

```text
STOP if good enough
OR
STOP if too many attempts
```

This is the most robust approach.

---

## Enterprise Example

### AI Writing System

```text
Draft article
   ↓
Review quality
   ↓
If good → publish
If bad → improve
If too many attempts → publish anyway
```

This ensures:

- productivity
- cost control
- safety limits

---

## Static vs Loop vs Terminated Loop

### Loop Without Termination

```text
A → B → A → B → A → ...
```

❌ Dangerous

---

### Loop With Termination

```text
A → B → A → B → END
```

✔ Safe

---

## Common Mistakes

### 1. Only using quality-based stopping

Bad:

```text
What if score never improves?
```

---

### 2. Only using iteration limit

Bad:

```text
Stops even when solution is already perfect
```

---

### 3. Forgetting to update state

If state never changes:

```text
Loop never progresses
```

---

## Key Takeaways

- Termination conditions define when loops stop executing.
- Every iterative LangGraph workflow must include stopping rules.
- Common strategies include quality thresholds and max iteration limits.
- Hybrid termination logic is the most reliable approach.
- Proper termination ensures safe, predictable, and cost-efficient workflows.
- Without termination conditions, loops become unsafe in production systems.