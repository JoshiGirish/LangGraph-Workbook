# Lab 059 — Planner-Executor Pattern

## Lab Intro

In the previous labs, we built increasingly sophisticated multi-agent systems:

```text
Research Agent
Writer Agent
Reviewer Agent
```

Each agent had a specialized responsibility.

However, there is still a limitation:

```text
The workflow itself is predefined.
```

The graph already knows exactly what steps will happen.

But many real-world tasks are different.

For example:

```text
Create a market analysis
Build a business plan
Research a company
Develop a product strategy
```

The required steps may change depending on the task.

Instead of hardcoding the workflow, we can introduce a new role:

> **Planner Agent**

The planner decides:

```text
What should be done
```

while another agent executes the plan.

This architecture is called:

> **Planner-Executor Pattern**

---

## Key Idea

Traditional workflow:

```text
Task
 ↓
Execute
 ↓
Result
```

Planner-Executor workflow:

```text
Task
 ↓
Planner
 ↓
Plan
 ↓
Executor
 ↓
Result
```

The planner determines:

```text
What actions should happen
```

The executor determines:

```text
How to perform them
```

---

## Enterprise Analogy

Imagine a construction project.

The architect:

```text
Creates the blueprint
```

The construction team:

```text
Builds according to the blueprint
```

The architect does not pour concrete.

The builders do not design the building.

This separation improves efficiency and organization.

The Planner-Executor pattern follows the same principle.

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
# Planner Agent
# -------------------------

def planner_agent(state: State):

    response = llm.invoke(
        f"""
        Create a step-by-step plan
        for the following task.

        Task:

        {state.task}

        Produce a numbered plan.
        """
    )

    return {
        "plan": response.content
    }


# -------------------------
# Executor Agent
# -------------------------

def executor_agent(state: State):

    response = llm.invoke(
        f"""
        Execute the following plan.

        Plan:

        {state.plan}

        Complete the task and
        provide the final result.
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
    "planner_agent",
    planner_agent
)

builder.add_node(
    "executor_agent",
    executor_agent
)

builder.add_edge(
    START,
    "planner_agent"
)

builder.add_edge(
    "planner_agent",
    "executor_agent"
)

builder.add_edge(
    "executor_agent",
    END
)

graph = builder.compile()


# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "task":
        "Create a market analysis for electric vehicles"
    }
)

print(result["plan"])

print("\n" + "=" * 50 + "\n")

print(result["result"])

---

## Example Output

### Generated Plan

```text
1. Define the electric vehicle market.
2. Identify major industry trends.
3. Analyze key competitors.
4. Evaluate growth drivers.
5. Examine risks and challenges.
6. Produce final market assessment.
```

### Final Result

```text
The electric vehicle market continues to experience significant growth driven by
government incentives, advances in battery technology, and increasing consumer demand.

Major competitors include Tesla, BYD, Volkswagen, and other global manufacturers.

Key growth drivers include sustainability initiatives and infrastructure expansion,
while challenges include supply chain constraints and charging network availability.
```

---

## Explanation

## What Is the Planner-Executor Pattern?

The Planner-Executor pattern separates:

```text
Thinking
```

from

```text
Doing
```

The planner:

```text
Decides the steps
```

The executor:

```text
Carries out the steps
```

This creates more structured problem solving.

---

## Step 1 — Planner Agent

The planner receives:

```text
Task
```

Example:

```text
Create a market analysis
```

The planner produces:

```text
Step-by-step plan
```

Stored in:

```python
state.plan
```

---

## Step 2 — Executor Agent

The executor receives:

```text
Plan
```

instead of the original task alone.

This reduces ambiguity.

The executor follows the plan and generates:

```text
Final result
```

Stored in:

```python
state.result
```

---

## Execution Flow

```text
START
   │
   ▼
Planner Agent
   │
   ▼
Executor Agent
   │
   ▼
END
```

---

## Why Planning Improves Results

When an LLM tackles a large task directly:

```text
Task
 ↓
Answer
```

important steps may be skipped.

Planning forces decomposition:

```text
Task
 ↓
Plan
 ↓
Execution
```

This generally improves:

- completeness
- consistency
- reasoning quality

---

## Planner Responsibilities

A planner should:

### Break Down Tasks

Example:

```text
Research competitors
Analyze trends
Assess risks
```

---

### Create Order

Determine:

```text
What happens first?
What happens next?
```

---

### Identify Missing Work

Reveal hidden requirements.

Example:

```text
Need competitor analysis
Need risk assessment
Need recommendations
```

---

## Executor Responsibilities

The executor should:

### Follow the Plan

Use the planner's output as guidance.

---

### Produce Deliverables

Generate:

- reports
- analyses
- summaries
- recommendations

---

### Avoid Replanning

The executor focuses on execution.

Planning already happened upstream.

---

## Real-World Applications

### Business Analysis

```text
Planner
   ↓
Analyst
```

---

### Research Systems

```text
Planner
   ↓
Research Agent
```

---

### Software Development

```text
Planner
   ↓
Coder Agent
```

---

### Content Creation

```text
Planner
   ↓
Writer Agent
```

---

## Extending the Pattern

Many production systems introduce additional stages:

```text
Planner
   ↓
Executor
   ↓
Reviewer
```

or

```text
Planner
   ↓
Multiple Executors
   ↓
Aggregator
```

Example:

```text
Planner
   ↓
Research Agent
Finance Agent
Legal Agent
   ↓
Final Report
```

This becomes the foundation of advanced agent orchestration.

---

## Planner vs Executor

### Planner

Focus:

```text
Strategy
```

Produces:

```text
Plan
```

---

### Executor

Focus:

```text
Action
```

Produces:

```text
Result
```

---

## Why Not Use One Agent?

You could ask:

```text
Create a plan and execute it.
```

in a single prompt.

However, separating the roles provides:

```text
Better visibility
Better debugging
Better control
```

You can inspect:

```python
state.plan
```

before execution begins.

---

## Common Mistakes

### 1. Planner Creates Vague Plans

Bad:

```text
Research topic
Write report
```

Too generic.

---

Better:

```text
Identify competitors
Analyze trends
Assess risks
```

Specific and actionable.

---

### 2. Executor Ignores the Plan

Bad:

```text
Uses its own approach
```

This defeats the purpose of planning.

---

### 3. Overplanning Small Tasks

Not every task needs:

```text
Planner → Executor
```

Simple tasks may not benefit from planning.

---

### 4. Excessively Detailed Plans

Plans should guide execution.

They should not become:

```text
Hundreds of steps
```

unless necessary.

---

## Mental Model

Think of the Planner-Executor pattern as:

```text
Architect
    ↓
Builder
```

or

```text
Project Manager
    ↓
Implementation Team
```

One decides what should happen.

The other makes it happen.

---

## Architecture

```text
                Task
                  │
                  ▼
         ┌────────────────┐
         │ Planner Agent  │
         └───────┬────────┘
                 │
                 ▼
               Plan
                 │
                 ▼
         ┌────────────────┐
         │ Executor Agent │
         └───────┬────────┘
                 │
                 ▼
            Final Result
```

---

## Why This Matters

The Planner-Executor pattern is one of the most important architectures in agentic AI.

Many advanced systems use planning to:

- improve reasoning
- coordinate complex tasks
- manage multiple workers
- reduce execution errors

It is often the first step toward autonomous multi-agent systems.

---

## Key Takeaways

- The Planner-Executor pattern separates planning from execution.
- Planner agents decide what work should be done.
- Executor agents carry out the planned work.
- Planning improves task decomposition and reasoning quality.
- The pattern provides transparency and easier debugging.
- It is widely used in business analysis, research, software development, and content generation.
- Planner-Executor systems serve as the foundation for more advanced orchestration architectures.
- In future labs, planners will coordinate multiple worker agents rather than a single executor, enabling large-scale agent collaboration.