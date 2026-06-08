# Lab 065 — LLM-as-Judge Pattern

## Lab Intro

In Lab 064, we explored the **Tree of Thoughts Pattern**:

```text
Multiple solutions
   ↓
Evaluation
   ↓
Best choice
```

This introduced structured comparison between different candidate outputs.

However, the evaluation step was still somewhat informal:

```text
"Choose the best approach"
```

In real systems, we often need something more precise:

```text
Scoring
Ranking
Consistent evaluation criteria
```

This leads us to a powerful evaluation technique:

> **LLM-as-Judge Pattern**

In this pattern, an LLM is used not to generate content, but to:

```text
Evaluate outputs systematically
```

---

## Key Idea

Instead of:

```text
Generate Answer
```

we do:

```text
Generate Multiple Answers
        ↓
Judge Evaluates Them
        ↓
Scores / Ranking / Selection
```

The LLM becomes a **scoring system**, not a generator.

---

## Enterprise Analogy

Imagine hiring candidates for a job.

You do not rely on a single interview.

Instead:

```text
Candidate A
Candidate B
Candidate C
```

are evaluated using:

- structured criteria
- scoring rubrics
- comparison frameworks

Then a hiring decision is made.

The LLM-as-Judge acts like an evaluator panel.

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

    answer_a: str = ""

    answer_b: str = ""

    answer_c: str = ""

    judgment: str = ""

    final_answer: str = ""


# -------------------------
# LLM
# -------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# -------------------------
# Answer A
# -------------------------

def generate_a(state: State):

    response = llm.invoke(
        f"""
        Provide Answer A for the question:

        {state.question}

        Focus on a practical explanation.
        """
    )

    return {"answer_a": response.content}


# -------------------------
# Answer B
# -------------------------

def generate_b(state: State):

    response = llm.invoke(
        f"""
        Provide Answer B for the question:

        {state.question}

        Focus on a technical explanation.
        """
    )

    return {"answer_b": response.content}


# -------------------------
# Answer C
# -------------------------

def generate_c(state: State):

    response = llm.invoke(
        f"""
        Provide Answer C for the question:

        {state.question}

        Focus on a simple beginner-friendly explanation.
        """
    )

    return {"answer_c": response.content}


# -------------------------
# Judge Agent
# -------------------------

def judge(state: State):

    response = llm.invoke(
        f"""
        You are an expert evaluator.

        Evaluate the following answers
        based on:

        - accuracy
        - clarity
        - completeness
        - usefulness

        Question:
        {state.question}

        Answer A:
        {state.answer_a}

        Answer B:
        {state.answer_b}

        Answer C:
        {state.answer_c}

        Provide:
        1. Ranking of best to worst
        2. Brief justification
        """
    )

    return {"judgment": response.content}


# -------------------------
# Final Selection Agent
# -------------------------

def select_best(state: State):

    response = llm.invoke(
        f"""
        Based on the following judgment:

        {state.judgment}

        Select the best answer (A, B, or C)
        and provide the final refined version.
        """
    )

    return {"final_answer": response.content}


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node("generate_a", generate_a)
builder.add_node("generate_b", generate_b)
builder.add_node("generate_c", generate_c)

builder.add_node("judge", judge)
builder.add_node("select_best", select_best)

builder.add_edge(START, "generate_a")
builder.add_edge(START, "generate_b")
builder.add_edge(START, "generate_c")

builder.add_edge("generate_a", "judge")
builder.add_edge("generate_b", "judge")
builder.add_edge("generate_c", "judge")

builder.add_edge("judge", "select_best")
builder.add_edge("select_best", END)

graph = builder.compile()


# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "question":
        "What are the benefits of cloud computing?"
    }
)

print(result["final_answer"])

---

## Example Output

```text
Answer B is the most accurate and comprehensive explanation of cloud computing benefits.

Cloud computing provides scalability, cost efficiency, and flexibility by allowing organizations to access computing resources on demand. It reduces the need for physical infrastructure and enables faster deployment of applications.

Additionally, cloud platforms support global accessibility and improved collaboration.

Overall, cloud computing helps businesses reduce operational costs while improving performance and scalability.
```

---

## Explanation

## What Is the LLM-as-Judge Pattern?

The LLM-as-Judge Pattern uses a language model to:

```text
Evaluate, score, or rank outputs
```

instead of generating them.

It acts as a:

```text
neutral evaluator
```

between multiple candidate responses.

---

## Step 1 — Generate Multiple Answers

We create three different responses:

### Answer A

```text
Practical explanation
```

### Answer B

```text
Technical explanation
```

### Answer C

```text
Beginner-friendly explanation
```

Each answer has a different style and perspective.

---

## Step 2 — Judge Evaluation

The judge receives:

```text
All candidate answers
```

and evaluates them using criteria:

- accuracy
- clarity
- completeness
- usefulness

The output includes:

```text
Ranking + reasoning
```

---

## Step 3 — Final Selection

The final agent:

```text
Reads the judgment
Selects best answer
Refines output
```

This ensures structured decision-making.

---

## Execution Flow

```text
            START
              │
   ┌──────────┼──────────┐
   ▼          ▼          ▼
Answer A   Answer B   Answer C
   └──────────┼──────────┘
              ▼
          Judge Agent
              │
              ▼
      Selection Agent
              │
              ▼
             END
```

---

## Why LLM-as-Judge Works

Language models are not only good at generating text.

They are also good at:

```text
Comparing
Ranking
Evaluating quality
```

This makes them useful as:

```text
automated evaluators
```

---

## LLM-as-Judge vs Tree of Thoughts

### Tree of Thoughts

```text
Generate → Evaluate → Select
```

Focus:

```text
Reasoning paths
```

---

### LLM-as-Judge

```text
Generate → Score → Rank → Select
```

Focus:

```text
Output quality assessment
```

---

## LLM-as-Judge vs Debate

### Debate Pattern

```text
Arguments → Synthesis
```

Focus:

```text
Perspectives and reasoning
```

---

### LLM-as-Judge Pattern

```text
Answers → Evaluation → Ranking
```

Focus:

```text
Quality measurement
```

---

## Benefits of LLM-as-Judge

### 1. Structured Evaluation

Outputs are judged using explicit criteria.

---

### 2. Scalable Comparison

Works well for:

```text
many candidate outputs
```

---

### 3. Consistent Scoring

Same rubric can be reused across tasks.

---

### 4. Useful for Automation

Can power:

- ranking systems
- recommendation engines
- A/B testing

---

## Common Use Cases

### Model Selection

```text
Compare multiple LLM outputs
```

---

### Content Quality Ranking

```text
Rank articles or responses
```

---

### Search Result Ranking

```text
Evaluate relevance
```

---

### Code Evaluation

```text
Compare solutions for correctness and efficiency
```

---

## Extending the Pattern

Advanced systems often use:

```text
Multiple Judges
```

Example:

```text
Accuracy Judge
Clarity Judge
Safety Judge
```

Then aggregate scores:

```text
Final Ranking
```

---

## Common Mistakes

### 1. Vague Evaluation Criteria

Bad:

```text
Evaluate these answers.
```

---

Better:

```text
Evaluate based on accuracy, clarity, and completeness.
```

---

### 2. No Clear Output Format

Judges should produce:

```text
Ranking or scoring
```

not just free-form commentary.

---

### 3. Over-reliance on One Judge

Single judge models can be biased.

---

### 4. Ignoring Context

Judges must always consider:

```text
Original question
```

---

## Mental Model

Think of LLM-as-Judge as:

```text
Exam grading system
```

where:

- students = generated answers
- teacher = judge model
- rubric = evaluation criteria

---

## Architecture

```text
                 Question
                     │
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
 Answer A       Answer B       Answer C
     └───────────────┼───────────────┘
                     ▼
               Judge Agent
                     │
                     ▼
              Selection Agent
                     │
                     ▼
               Final Answer
```

---

## Why This Matters

LLM-as-Judge is widely used in modern AI systems for:

```text
evaluation, ranking, benchmarking, and alignment
```

It is a core building block in:

- AI evaluation pipelines
- automated testing systems
- reinforcement learning setups
- agent benchmarking frameworks

---

## Key Takeaways

- LLM-as-Judge uses a model to evaluate other model outputs.
- It introduces structured scoring and ranking mechanisms.
- It is highly useful for comparing multiple candidate responses.
- It separates generation from evaluation.
- It scales well for automation and benchmarking tasks.
- It is often combined with other patterns like Tree of Thoughts and Debate.
- In the next lab, we will explore the Agentic RAG Pattern, where agents dynamically decide when and how to retrieve external knowledge before answering.
