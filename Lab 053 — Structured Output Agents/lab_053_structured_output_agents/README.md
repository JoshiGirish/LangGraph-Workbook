# Lab 053 — Structured Output Agents

## Lab Intro

In previous labs, our agents primarily produced:

```text
Natural language responses
```

Example:

```text
The laptop is currently in stock.
```

or

```text
Order 1001 has been shipped.
```

While human-readable text is useful, production systems often require:

```text
Structured data
```

Examples:

- API responses
- database updates
- workflow triggers
- dashboards
- business applications

Instead of free-form text, we may want outputs like:

```json
{
  "order_id": "1001",
  "status": "shipped"
}
```

or

```json
{
  "product": "laptop",
  "available": true
}
```

This is where:

> **Structured Output Agents**

become important.

---

## Key Idea

Traditional agent:

```text
Question
   ↓
LLM
   ↓
Text Response
```

Structured output agent:

```text
Question
   ↓
LLM
   ↓
Validated Schema
   ↓
Structured Data
```

The output becomes predictable and machine-readable.

---

## Enterprise Analogy

Imagine a shipping system.

A human support agent may write:

```text
The package was delivered yesterday.
```

A workflow engine cannot reliably process that sentence.

Instead it prefers:

```json
{
  "status": "delivered",
  "delivery_date": "2025-02-10"
}
```

Structured outputs allow AI agents to integrate cleanly with software systems.

---

## Lab Code

from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI


# -------------------------
# Structured Schema
# -------------------------

class ProductAvailability(BaseModel):

    product_name: str = Field(
        description="Product name"
    )

    available: bool = Field(
        description="Whether the product is available"
    )

    quantity: int = Field(
        description="Available inventory quantity"
    )


# -------------------------
# LLM
# -------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

structured_llm = llm.with_structured_output(
    ProductAvailability
)


# -------------------------
# Invoke
# -------------------------

result = structured_llm.invoke(
    """
    Product: Laptop

    Inventory:
    25 units available
    """
)

print(result)

---

## Example Output

```python
ProductAvailability(
    product_name='Laptop',
    available=True,
    quantity=25
)
```

---

## Explanation

## What Is Structured Output?

Structured output means the model produces data that conforms to a predefined schema.

Instead of:

```text
Laptop is available and there are 25 units.
```

we get:

```python
ProductAvailability(
    product_name="Laptop",
    available=True,
    quantity=25
)
```

This output can be used directly by applications.

---

## Step 1 — Define a Schema

We create a Pydantic model:

```python
class ProductAvailability(BaseModel):
```

Fields:

```python
product_name: str
available: bool
quantity: int
```

This schema defines exactly what the model must produce.

---

## Step 2 — Add Field Descriptions

```python
Field(
    description="Product name"
)
```

Descriptions help the LLM understand:

```text
What data belongs in each field.
```

Well-described schemas generally produce better results.

---

## Step 3 — Enable Structured Output

Convert the model:

```python
structured_llm =
    llm.with_structured_output(
        ProductAvailability
    )
```

Now the LLM is constrained to generate data matching the schema.

---

## Step 4 — Invoke the Model

Input:

```text
Product: Laptop

Inventory:
25 units available
```

The model extracts:

```text
Product Name
Availability
Quantity
```

and maps them into the schema.

---

## Step 5 — Receive Validated Data

Output:

```python
ProductAvailability(
    product_name='Laptop',
    available=True,
    quantity=25
)
```

Rather than raw text, we receive a validated object.

---

## Why Structured Outputs Matter

Natural language is designed for humans.

Software systems prefer:

```text
Predictable fields
```

Structured outputs make AI systems easier to integrate.

---

## Common Use Cases

### Information Extraction

Convert documents into:

```json
{
  "customer": "...",
  "invoice_total": ...
}
```

---

### Workflow Automation

Generate:

```json
{
  "action": "approve"
}
```

for downstream systems.

---

### CRM Updates

Extract:

```json
{
  "customer_name": "...",
  "email": "...",
  "priority": "high"
}
```

from conversations.

---

### API Responses

Produce consistent payloads:

```json
{
  "status": "...",
  "result": ...
}
```

for applications.

---

## Structured Outputs Inside Agents

Structured outputs are especially useful when an agent must:

```text
Think
↓
Use Tools
↓
Return Machine-Readable Result
```

Example:

```text
User Request
      ↓
Agent
      ↓
Inventory Tool
      ↓
Structured Response
```

Output:

```json
{
  "product": "Laptop",
  "available": true,
  "quantity": 25
}
```

instead of:

```text
The laptop appears to be available.
```

---

## Benefits

### Reliability

The format is predictable.

---

### Validation

Pydantic validates:

```text
Types
Required fields
Constraints
```

before returning data.

---

### Easier Integration

Applications consume:

```python
result.product_name
```

rather than parsing text.

---

### Reduced Prompt Fragility

Without structured output:

```text
Prompt carefully
Hope format remains consistent
```

With structured output:

```text
Schema enforces consistency
```

---

## Example: Customer Ticket Extraction

Schema:

```python
class Ticket(BaseModel):
    customer: str
    priority: str
    issue: str
```

Input:

```text
John reports a payment failure.
Urgency is high.
```

Output:

```python
Ticket(
    customer="John",
    priority="high",
    issue="payment failure"
)
```

Perfect for workflow systems.

---

## Structured Output vs Text Output

### Text Output

```python
"The laptop is available."
```

Pros:

```text
Human-friendly
```

Cons:

```text
Harder to parse
```

---

### Structured Output

```python
{
    "available": True
}
```

Pros:

```text
Machine-friendly
Predictable
Validated
```

Cons:

```text
Less conversational
```

---

## Common Mistakes

### 1. Overly Large Schemas

Bad:

```python
50+ fields
```

Large schemas increase complexity and error rates.

Start simple.

---

### 2. Missing Descriptions

Bad:

```python
status: str
```

The model has less context.

---

Better:

```python
status: str = Field(
    description="Current order status"
)
```

Descriptions improve accuracy.

---

### 3. Expecting Free-Form Responses

Once structured output is enabled:

```text
Schema becomes the contract.
```

The model focuses on filling fields rather than writing long explanations.

---

### 4. Using Text Parsing Instead

Bad:

```python
result = llm.invoke(...)
```

↓

```python
Regex parsing
```

↓

```python
Manual extraction
```

Fragile and error-prone.

---

Better:

```python
with_structured_output(...)
```

and let the model produce structured data directly.

---

## Mental Model

Think of structured output as:

```text
LLM
  ↓
Data Extraction Layer
  ↓
Validated Object
```

The model becomes a reliable data producer rather than a text generator.

---

## Architecture

```text
               User Input
                    │
                    ▼
                  Agent
                    │
                    ▼
               LLM Reasoning
                    │
                    ▼
            Structured Schema
                    │
                    ▼
            Validated Object
                    │
                    ▼
            Application Logic
```

The schema acts as the contract between the LLM and the application.

---

## Real-World Examples

Structured outputs power:

- invoice extraction
- document processing
- customer support automation
- CRM updates
- workflow orchestration
- agent handoffs
- API integrations
- business intelligence pipelines

Most production AI systems eventually require structured outputs.

---

## Key Takeaways

- Structured output agents return validated, machine-readable data instead of free-form text.
- Pydantic models define the schema the LLM must follow.
- `with_structured_output()` enables schema-constrained generation.
- Structured outputs improve reliability, validation, and application integration.
- They eliminate much of the fragile text-parsing logic used in traditional LLM workflows.
- Structured outputs are essential for production-grade automation systems.
- They work especially well when combined with tools, workflows, and LangGraph agents.
- This concludes Part 7, where we explored tool-calling agents, ReAct workflows, multi-tool systems, error handling, streaming, and structured outputs.
