# Lab 066 — Agentic RAG Pattern

## Lab Intro

In Lab 065, we explored the **LLM-as-Judge Pattern**:

```text
Generate multiple answers
   ↓
Judge evaluates
   ↓
Select best answer
```

This improved evaluation and selection quality using structured scoring.

However, all previous patterns share a limitation:

```text
The model relies only on its internal knowledge.
```

In real-world systems, we often need:

```text
Fresh information
Domain-specific knowledge
Verified external context
```

This leads us to one of the most important production patterns in modern AI systems:

> **Agentic RAG Pattern (Retrieval-Augmented Generation)**

In this pattern, the agent can:

```text
decide when to retrieve information
retrieve relevant context
use it to generate better answers
```

---

## Key Idea

Traditional RAG:

```text
Question
   ↓
Retrieve
   ↓
Answer
```

Agentic RAG:

```text
Question
   ↓
Decide if retrieval is needed
   ↓
Retrieve (if needed)
   ↓
Reason + Answer
```

The key difference is:

```text
Retrieval is not automatic — it is agent-driven.
```

---

## Enterprise Analogy

Imagine a consultant answering a client question.

A basic consultant:

```text
Answers from memory only
```

A strong consultant:

```text
Thinks first
   ↓
Checks documents if needed
   ↓
Then answers
```

The second approach is more reliable and grounded.

That is exactly what Agentic RAG does.

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

    needs_retrieval: str = ""

    retrieved_context: str = ""

    answer: str = ""


# -------------------------
# LLM
# -------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# -------------------------
# Retrieval Tool (Mock)
# -------------------------

def retrieve_information(query: str) -> str:

    """
    Simulated retrieval function.
    In real systems, this would call:
    - vector database
    - search API
    - knowledge base
    """

    return f"""
    Retrieved Knowledge for: {query}

    - Cloud computing provides on-demand resources.
    - It improves scalability and reduces infrastructure costs.
    - Major providers include AWS, Azure, and GCP.
    """


# -------------------------
# Decision Agent
# -------------------------

def decide_retrieval(state: State):

    response = llm.invoke(
        f"""
        Decide whether external knowledge is needed.

        Question:
        {state.question}

        Respond with:
        YES or NO and brief reasoning.
        """
    )

    return {
        "needs_retrieval": response.content
    }


# -------------------------
# Retrieval Agent
# -------------------------

def retrieval_agent(state: State):

    context = retrieve_information(state.question)

    return {
        "retrieved_context": context
    }


# -------------------------
# Answer Agent
# -------------------------

def answer_agent(state: State):

    response = llm.invoke(
        f"""
        Answer the question using context if available.

        Question:
        {state.question}

        Retrieved Context:
        {state.retrieved_context}
        """
    )

    return {
        "answer": response.content
    }


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node("decide_retrieval", decide_retrieval)
builder.add_node("retrieval_agent", retrieval_agent)
builder.add_node("answer_agent", answer_agent)

builder.add_edge(START, "decide_retrieval")
builder.add_edge("decide_retrieval", "retrieval_agent")
builder.add_edge("retrieval_agent", "answer_agent")
builder.add_edge("answer_agent", END)

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

print(result["answer"])

---

## Example Output

```text
Cloud computing offers several key benefits including scalability, cost efficiency,
and flexibility. It allows organizations to access computing resources on demand
without investing in physical infrastructure.

Major providers such as AWS, Microsoft Azure, and Google Cloud Platform offer
services that support storage, computation, and application deployment.

Overall, cloud computing enables faster innovation and reduces operational costs
for businesses of all sizes.
```

---

## Explanation

## What Is the Agentic RAG Pattern?

Agentic RAG introduces an intelligent retrieval step where the model:

```text
decides when to use external knowledge
```

instead of always retrieving or never retrieving.

---

## Step 1 — Decision Phase

The model evaluates:

```text
Is external knowledge needed?
```

Output:

```python
state.needs_retrieval
```

In real systems, this step may decide:

- search web
- query vector DB
- skip retrieval entirely

---

## Step 2 — Retrieval Phase

If retrieval is needed, the system fetches:

```text
Relevant context
```

from an external source.

In this lab, we simulate it with:

```python
retrieve_information()
```

In production, this could be:

- vector database (FAISS, Pinecone)
- document store
- API search engine

---

## Step 3 — Answer Generation

The final agent combines:

```text
Question + Retrieved Context
```

to produce a grounded response.

This improves factual reliability.

---

## Execution Flow

```text
              START
                │
                ▼
      Decide Retrieval Needed
                │
                ▼
         Retrieve Context
                │
                ▼
          Generate Answer
                │
                ▼
               END
```

---

## Why Agentic RAG Matters

Traditional LLMs:

```text
Answer from memory only
```

This can lead to:

- hallucinations
- outdated information
- missing domain knowledge

Agentic RAG improves this by:

```text
Grounding responses in external data
```

---

## Key Advantage: Selective Retrieval

Not every question needs retrieval.

Example:

### No retrieval needed

```text
What is 2 + 2?
```

---

### Retrieval needed

```text
What are the latest AWS pricing changes?
```

Agentic systems learn to distinguish between the two.

---

## Agentic RAG vs Traditional RAG

### Traditional RAG

```text
Always retrieve → Then answer
```

Problems:

- unnecessary retrieval
- higher latency
- increased cost

---

### Agentic RAG

```text
Decide → Retrieve (if needed) → Answer
```

Benefits:

- efficient
- adaptive
- context-aware

---

## Real-World Applications

### Enterprise Search

```text
Employee question → Decide → Search docs → Answer
```

---

### Customer Support

```text
User query → Check KB → Respond accurately
```

---

### Research Assistants

```text
Question → Retrieve papers → Summarize findings
```

---

### Legal / Compliance Systems

```text
Query → Retrieve regulations → Provide answer
```

---

## Extending the Pattern

Advanced systems include:

### 1. Multi-Step Retrieval

```text
Decide → Retrieve → Refine Query → Retrieve Again
```

---

### 2. Tool-Enhanced RAG

```text
Search Engine + Vector DB + APIs
```

---

### 3. Memory-Augmented RAG

```text
Short-term + Long-term memory retrieval
```

---

### 4. Multi-Agent RAG

```text
Retriever Agent
Reasoner Agent
Verifier Agent
```

---

## Common Mistakes

### 1. Always Retrieving

This defeats the purpose of agentic control.

---

### 2. Poor Retrieval Queries

Weak query generation leads to irrelevant context.

---

### 3. Ignoring Retrieved Context

Bad systems:

```text
retrieve → ignore → hallucinate
```

---

### 4. No Decision Logic

Skipping the "should we retrieve?" step reduces efficiency.

---

## Mental Model

Think of Agentic RAG as:

```text
Smart Research Assistant
```

who:

```text
thinks first
checks sources if needed
then answers
```

instead of:

```text
guessing from memory
```

---

## Architecture

```text
                 Question
                     │
                     ▼
      ┌────────────────────────┐
      │ Decide Retrieval Needed│
      └──────────┬─────────────┘
                 │
                 ▼
      ┌────────────────────────┐
      │   Retrieve Context     │
      └──────────┬─────────────┘
                 │
                 ▼
      ┌────────────────────────┐
      │   Generate Answer      │
      └──────────┬─────────────┘
                 │
                 ▼
                END
```

---

## Why This Matters

Agentic RAG is one of the most important production patterns in modern AI systems.

It enables:

```text
factual accuracy
scalable knowledge integration
adaptive reasoning
```

It is widely used in:

- enterprise AI assistants
- knowledge management systems
- AI copilots
- research tools

---

## Key Takeaways

- Agentic RAG introduces intelligent, decision-based retrieval.
- The model decides whether retrieval is needed.
- Retrieval is performed only when beneficial.
- External context improves factual accuracy and grounding.
- The pattern reduces hallucinations and improves reliability.
- It is more efficient than traditional always-on RAG.
- It is a core production pattern in modern AI systems.
