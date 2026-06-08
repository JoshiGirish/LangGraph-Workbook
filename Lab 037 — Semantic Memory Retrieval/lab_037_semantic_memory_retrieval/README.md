# Lab 037 — Semantic Memory Retrieval

## Lab Intro

In the previous lab we learned:

```text
Memory Search
```

We stored information and retrieved it using exact identifiers such as:

```text
user_id
customer_id
session_id
```

This works well when we know exactly what we are looking for.

However, real-world agents often need to answer questions like:

```text
What do we know about travel?
```

or

```text
Have we discussed cloud migration before?
```

or

```text
Find memories related to customer complaints.
```

In these situations, we may not know the exact memory identifier.

Instead, we want to retrieve memories based on:

```text
Meaning
```

rather than exact matches.

This is called:

```text
Semantic Memory Retrieval
```

---

## Enterprise Analogy

Imagine a customer success agent has stored the following memories:

```text
Customer is planning a vacation to Japan.
Customer likes international travel.
Customer recently booked airline tickets.
```

Later the customer asks:

```text
Can you remind me about my travel plans?
```

The word:

```text
travel
```

may not appear exactly in every stored memory.

Yet all three memories are clearly related.

A semantic retrieval system can recognize:

```text
vacation
airline tickets
international travel
```

are conceptually similar to:

```text
travel
```

and retrieve them.

---

## The Limitation of Exact Search

Suppose we store:

```text
Customer enjoys mountain hiking.
```

A search for:

```text
hiking
```

works.

But a search for:

```text
outdoor adventure
```

might fail with exact matching.

Why?

Because exact search looks for:

```text
Matching Words
```

Semantic search looks for:

```text
Matching Meaning
```

---

## Key Idea

Traditional Search:

```text
Same Words
```

Semantic Retrieval:

```text
Same Meaning
```

---

## Visual Comparison

### Exact Search

```text
Memory:
"I enjoy hiking"

Query:
"hiking"

Match:
YES
```

---

### Semantic Search

```text
Memory:
"I enjoy hiking"

Query:
"outdoor adventure"

Match:
YES
```

because the meanings are related.

---

## How Semantic Retrieval Works

Modern AI systems convert text into:

```text
Embeddings
```

An embedding is a numerical representation of meaning.

Conceptually:

```text
Sentence
      ↓
Embedding Model
      ↓
Vector
```

Example:

```text
"I love travel"

      ↓

[0.21, 0.87, 0.45, ...]
```

---

Another sentence:

```text
"I enjoy vacations"

      ↓

[0.19, 0.84, 0.43, ...]
```

The vectors are close together because the meanings are similar.

---

## Semantic Retrieval Flow

```text
Store Memory
      ↓
Create Embedding
      ↓
Store Vector
      ↓
User Query
      ↓
Create Query Embedding
      ↓
Similarity Search
      ↓
Return Relevant Memories
```

---

## Simplified Lab

To understand the concept, we'll simulate semantic retrieval using keyword similarity.

In production systems this would use:

```text
Embedding Models
Vector Databases
Cosine Similarity
```

but the learning objective is understanding the retrieval workflow.

---

## Workflow

```text
START
   ↓
retrieve_memory
   ↓
END
```

---

## Lab Code

from typing import List
from pydantic import BaseModel

from langgraph.graph import StateGraph
from langgraph.graph import START, END

# -------------------------
# Memory Store
# -------------------------

memory_store = [
    "Customer enjoys international travel",
    "Customer prefers dark mode",
    "Customer recently booked airline tickets",
    "Customer likes mountain hiking"
]

# -------------------------
# State
# -------------------------

class State(BaseModel):
    query: str
    memories: List[str] = []

# -------------------------
# Semantic Retrieval
# -------------------------

def retrieve_memory(state: State):

    query = state.query.lower()

    results = []

    for memory in memory_store:

        memory_lower = memory.lower()

        if (
            "travel" in query
            and (
                "travel" in memory_lower
                or "airline" in memory_lower
            )
        ):
            results.append(memory)

    return {
        "memories": results
    }

# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "retrieve_memory",
    retrieve_memory
)

builder.add_edge(
    START,
    "retrieve_memory"
)

builder.add_edge(
    "retrieve_memory",
    END
)

graph = builder.compile()

# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "query": "travel"
    }
)

print(result)

---

## Expected Output

```python
{
    'query': 'travel',
    'memories': [
        'Customer enjoys international travel',
        'Customer recently booked airline tickets'
    ]
}
```

---

# Explanation

## What Is Semantic Memory Retrieval?

Semantic memory retrieval finds memories based on:

```text
Meaning
```

instead of:

```text
Exact Matches
```

The goal is to retrieve information that is conceptually relevant.

---

## Step 1 — User Submits a Query

Input:

```python
{
    "query": "travel"
}
```

The query represents an idea rather than a specific memory ID.

---

## Step 2 — Compare Against Stored Memories

Stored memories:

```text
International travel
Dark mode preference
Airline tickets
Mountain hiking
```

The retrieval process evaluates which memories are related to:

```text
travel
```

---

## Step 3 — Identify Similar Memories

Relevant memories:

```text
International travel
Airline tickets
```

These are returned because they relate to the same concept.

---

## Step 4 — Inject Results Into State

The retrieved memories become part of workflow state:

```python
{
    "memories": [...]
}
```

The workflow can now use them to personalize future actions.

---

## Why Semantic Retrieval Matters

Imagine a user asks:

```text
What vacation plans have we discussed?
```

The stored memory might contain:

```text
Trip to Japan
Flight booking
Hotel reservation
```

None of those memories contain the exact word:

```text
vacation
```

Yet they are highly relevant.

Semantic retrieval makes this possible.

---

## Real AI Memory Systems

Production implementations typically use:

```text
Text Embeddings
```

generated by embedding models.

Example:

```text
Memory
      ↓
Embedding
      ↓
Vector Store
```

Common vector databases include:

```text
Pinecone
Weaviate
Milvus
Chroma
FAISS
```

---

## Similarity Search

When a query arrives:

```text
Query
      ↓
Embedding
      ↓
Vector Search
```

The system computes similarity scores.

Example:

```text
Travel Query

Memory A: Travel Plans       Score 0.95
Memory B: Airline Tickets    Score 0.91
Memory C: Dark Mode          Score 0.12
```

The highest-scoring memories are returned.

---

## Enterprise Example

### Customer Success Agent

Stored Memory:

```text
Interested in expanding to Europe
```

User Query:

```text
International growth
```

Semantic retrieval recognizes that both relate to:

```text
Global expansion
```

---

### Sales Assistant

Stored Memory:

```text
Looking for analytics software
```

User Query:

```text
Business intelligence tools
```

A semantic system understands the connection.

---

### IT Support Agent

Stored Memory:

```text
Migrating workloads to AWS
```

User Query:

```text
Cloud migration
```

Relevant memories are retrieved even though the wording differs.

---

## Semantic Retrieval vs Exact Search

### Exact Search

Looks for:

```text
Identical Terms
```

Example:

```text
travel = travel
```

---

### Semantic Retrieval

Looks for:

```text
Related Meaning
```

Example:

```text
travel ≈ vacation
travel ≈ flights
travel ≈ tourism
```

---

## Visual Comparison

```text
Exact Search

Query:
travel

Matches:
travel

--------------------------------

Semantic Search

Query:
travel

Matches:
vacation
flights
tourism
airline tickets
```

---

## Why This Is Important For Agents

Agents become far more useful when they can remember concepts instead of exact phrases.

Without semantic retrieval:

```text
Memory Exists
But Is Hard To Find
```

With semantic retrieval:

```text
Memory Exists
And Is Discoverable
```

This dramatically improves personalization and contextual awareness.

---

## Common Mistakes

### 1. Assuming Semantic Search Uses Keywords

Keywords are only a simplified approximation.

Real semantic retrieval uses:

```text
Embeddings
Vector Similarity
```

---

### 2. Expecting Perfect Results

Semantic retrieval finds:

```text
Most Relevant Memories
```

not necessarily:

```text
Exact Matches
```

---

### 3. Confusing Search With Storage

Storage:

```text
Save Memory
```

Retrieval:

```text
Find Relevant Memory
```

Both are necessary components of a memory system.

---

## Mental Model

Traditional search is like looking up a word in a dictionary.

```text
Find Exact Word
```

Semantic retrieval is like asking a knowledgeable librarian:

```text
Find Information Related To This Idea
```

The librarian understands meaning rather than exact wording.

---

## Visual Summary

```text
Store Memory
      ↓
Generate Embeddings
      ↓
Store Vectors
      ↓
User Query
      ↓
Generate Query Embedding
      ↓
Similarity Search
      ↓
Retrieve Relevant Memories
      ↓
Use Retrieved Context
```

---

## Key Takeaways

- Semantic memory retrieval searches by meaning rather than exact matches.
- It enables agents to find relevant memories even when wording differs.
- Modern systems use embeddings to represent semantic meaning.
- Retrieval is typically performed using vector similarity search.
- Semantic retrieval is a core capability of memory-enabled AI agents.
- It significantly improves personalization, context awareness, and knowledge reuse.
- Semantic retrieval transforms memory systems from keyword lookup tools into meaning-aware knowledge systems.