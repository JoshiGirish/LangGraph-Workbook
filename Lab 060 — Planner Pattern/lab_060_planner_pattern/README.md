# Lab 060 — Planner Pattern

## Lab Intro

In previous labs, we built multi-agent systems and introduced the:

```text
Planner Agent
      ↓
Executor Agent
```

architecture.

That pattern used two separate agents.

However, planning is useful even when there is only a single agent.

Before attempting a task, the agent can first decide:

```text
What should I do?
```

and only then:

```text
Execute the work
```

This idea is known as the:

> **Planner Pattern**

The Planner Pattern is one of the most important reasoning techniques in agentic systems because it encourages deliberate thinking before action.

---

## Key Idea

Without planning:

```text
Question
   ↓
Answer
```

With planning:

```text
Question
   ↓
Plan
   ↓
Execute
   ↓
Answer
```

The extra planning step often leads to:

- better reasoning
- more complete answers
- fewer missed steps

---

## Enterprise Analogy

Imagine a project manager receives a request:

```text
Launch a new product
```

A poor approach would be:

```text
Start working immediately
```

A better approach is:

```text
Create a plan
      ↓
Assign tasks
      ↓
Execute
```

The Planner Pattern follows the same principle.

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

    task: str

    plan: str = ""

    result: str = ""


# -------------------------
# LLM
# -------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# -------------------------
# Planning Step
# -------------------------

def planner(state: State):

    response = llm.invoke(
        f"""
        Create a step-by-step plan
        for the following task.

        Task:

        {state.task}

        Produce a concise plan.
        """
    )

    return {
        "plan": response.content
    }


# -------------------------
# Execution Step
# -------------------------

def execute(state: State):

    response = llm.invoke(
        f"""
        Execute the following plan.

        Plan:

        {state.plan}

        Original Task:

        {state.task}
        """
    )

    return {
        "result": response.content
    }


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "planner",
    planner
)

builder.add_node(
    "execute",
    execute
)

builder.add_edge(
    START,
    "planner"
)

builder.add_edge(
    "planner",
    "execute"
)

builder.add_edge(
    "execute",
    END
)

graph = builder.compile()


# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "task":
        "Explain how electric vehicles impact the environment."
    }
)

print("PLAN:")
print(result["plan"])

print("\n" + "=" * 50 + "\n")

print("RESULT:")
print(result["result"])

---

## Example Output

### Generated Plan

```text
1. Explain what electric vehicles are.
2. Describe environmental benefits.
3. Discuss battery production impacts.
4. Compare emissions with gasoline vehicles.
5. Provide a balanced conclusion.
```

### Final Result

```text
Electric vehicles (EVs) can reduce greenhouse gas emissions by replacing
internal combustion engines with electric motors.

Their environmental benefits include lower tailpipe emissions and improved
energy efficiency. However, battery production requires significant raw
materials and energy.

Overall, EVs generally offer environmental advantages over traditional
vehicles, especially when powered by renewable energy sources.
```

---

## Explanation

## What Is the Planner Pattern?

The Planner Pattern introduces an explicit reasoning phase before execution.

Instead of:

```text
Input
 ↓
Output
```

we use:

```text
Input
 ↓
Plan
 ↓
Output
```

The plan acts as a roadmap.

---

## Step 1 — Receive a Task

Input:

```text
Explain how electric vehicles impact the environment.
```

The task is stored in:

```python
state.task
```

---

## Step 2 — Generate a Plan

The planner creates:

```text
A sequence of steps
```

Example:

```text
Define EVs
Discuss benefits
Discuss drawbacks
Provide conclusion
```

The plan is stored in:

```python
state.plan
```

---

## Step 3 — Execute the Plan

The execution step receives:

```python
state.plan
```

and uses it to guide reasoning.

Instead of improvising, the model follows a structured path.

The result is stored in:

```python
state.result
```

---

## Execution Flow

```text
START
   │
   ▼
 Planner
   │
   ▼
 Execute
   │
   ▼
 END
```

Simple but powerful.

---

## Why Planning Helps

Large tasks often contain hidden subtasks.

Example:

```text
Analyze a company
```

may require:

```text
Company Overview
Financial Analysis
Competitive Analysis
Risks
Conclusion
```

Without planning:

```text
Some steps may be skipped.
```

With planning:

```text
Work becomes structured.
```

---

## Benefits of the Planner Pattern

### 1. Better Completeness

Planning encourages the model to consider:

```text
All required steps
```

before generating an answer.

---

### 2. Better Reasoning

Breaking a task into smaller pieces improves:

```text
Problem solving
```

and

```text
Logical consistency
```

---

### 3. Greater Transparency

You can inspect:

```python
state.plan
```

to understand how the model intends to solve the task.

---

### 4. Easier Debugging

If the final answer is poor:

Check:

```text
The plan
```

first.

Often the problem starts there.

---

## Planner Pattern vs Direct Generation

### Direct Generation

```text
Task
 ↓
Answer
```

Pros:

```text
Fast
Simple
```

Cons:

```text
May skip important steps
```

---

### Planner Pattern

```text
Task
 ↓
Plan
 ↓
Answer
```

Pros:

```text
Structured
More reliable
```

Cons:

```text
Additional LLM call
```

---

## Common Use Cases

### Research

```text
Research Question
      ↓
Plan Research Areas
      ↓
Generate Findings
```

---

### Writing

```text
Article Topic
      ↓
Create Outline
      ↓
Write Article
```

---

### Business Analysis

```text
Business Problem
      ↓
Analysis Plan
      ↓
Recommendations
```

---

### Software Development

```text
Feature Request
      ↓
Implementation Plan
      ↓
Code Generation
```

---

## Common Mistakes

### 1. Creating Vague Plans

Bad:

```text
Think about topic
Write answer
```

Not useful.

---

Better:

```text
Define topic
Identify benefits
Identify drawbacks
Summarize findings
```

---

### 2. Ignoring the Plan

Bad:

```text
Generate plan
Never use it
```

The execution step should explicitly reference the plan.

---

### 3. Overplanning Simple Tasks

Not every task needs:

```text
Detailed planning
```

For very small questions:

```text
Direct generation may be sufficient.
```

---

### 4. Excessive Detail

Plans should guide execution.

They should not become:

```text
Hundreds of steps
```

for simple tasks.

---

## Mental Model

Think of the Planner Pattern as:

```text
Think
 ↓
Act
```

instead of:

```text
Act Immediately
```

The planning phase provides direction before execution begins.

---

## Architecture

```text
             Task
               │
               ▼
      ┌────────────────┐
      │    Planner     │
      └───────┬────────┘
              │
              ▼
             Plan
              │
              ▼
      ┌────────────────┐
      │   Execution    │
      └───────┬────────┘
              │
              ▼
         Final Result
```

---

## Why This Matters

Many advanced agent architectures rely on planning.

Examples include:

```text
Planner-Executor Systems
Tree of Thoughts
Autonomous Agents
Agentic RAG
```

The Planner Pattern is often the first step toward more deliberate and reliable AI reasoning.

---

## Key Takeaways

- The Planner Pattern introduces a planning step before execution.
- Planning encourages structured reasoning.
- The plan acts as a roadmap for solving a task.
- Explicit plans improve completeness and transparency.
- The pattern separates thinking from execution.
- Planning is widely used in advanced agent architectures.
- Inspecting plans makes debugging much easier.
- In the next lab, we will explore the Reflection Pattern, where an agent reviews its own reasoning and attempts to improve it.
