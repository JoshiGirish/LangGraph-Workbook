# Lab 050 — Tool Error Recovery

## Lab Intro

In Lab 049, we built a multi-tool agent capable of selecting and executing different tools.

The workflow looked like:

```text
User
  ↓
LLM
  ↓
Tool Selection
  ↓
Tool Execution
  ↓
Answer
```

However, production systems face a major challenge:

```text
Tools fail.
```

Examples include:

- API timeouts
- database connection errors
- invalid user inputs
- missing records
- authentication failures
- network outages

A robust agent must be able to:

```text
Detect errors
Handle failures
Continue gracefully
```

This process is known as:

> **Tool Error Recovery**

---

## Key Idea

Naive workflow:

```text
Tool Error
    ↓
Workflow Crashes ❌
```

Production workflow:

```text
Tool Error
    ↓
Capture Error
    ↓
Return Error Message
    ↓
LLM Responds Gracefully ✔
```

The goal is resilience rather than perfect execution.

---

## Enterprise Analogy

Imagine a customer support representative checking an order.

Customer asks:

```text
What is the status of order 9999?
```

The order system responds:

```text
Order Not Found
```

A good representative does not crash.

Instead:

```text
"I couldn't locate that order.
Could you verify the order number?"
```

AI agents should behave similarly.

---

## Lab Code

from typing import Annotated

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from langgraph.graph.message import (
    add_messages
)

from langgraph.prebuilt import ToolNode

from typing_extensions import TypedDict


# -------------------------
# Tool
# -------------------------

@tool
def divide(a: float, b: float) -> float:
    """
    Divide one number by another.
    """

    if b == 0:
        raise ValueError(
            "Division by zero is not allowed."
        )

    return a / b


# -------------------------
# State
# -------------------------

class State(TypedDict):
    messages: Annotated[list, add_messages]


# -------------------------
# LLM
# -------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

tools = [divide]

llm_with_tools = llm.bind_tools(
    tools
)


# -------------------------
# Chatbot Node
# -------------------------

def chatbot(state: State):

    response = llm_with_tools.invoke(
        state["messages"]
    )

    return {
        "messages": [response]
    }


# -------------------------
# Tool Node
# -------------------------

tool_node = ToolNode(tools)


# -------------------------
# Router
# -------------------------

def route_tools(state: State):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


# -------------------------
# Build Graph
# -------------------------

builder = StateGraph(State)

builder.add_node(
    "chatbot",
    chatbot
)

builder.add_node(
    "tools",
    tool_node
)

builder.add_edge(
    START,
    "chatbot"
)

builder.add_conditional_edges(
    "chatbot",
    route_tools
)

builder.add_edge(
    "tools",
    "chatbot"
)

graph = builder.compile()


# -------------------------
# Execute
# -------------------------

result = graph.invoke(
    {
        "messages": [
            (
                "user",
                "Divide 100 by 0"
            )
        ]
    }
)

for msg in result["messages"]:
    print(msg)

---

## Example Output

```python
HumanMessage(
    content='Divide 100 by 0'
)

AIMessage(
    content='',
    tool_calls=[
        {
            'name': 'divide',
            'args': {
                'a': 100,
                'b': 0
            }
        }
    ]
)

ToolMessage(
    content='Error: Division by zero is not allowed.'
)

AIMessage(
    content='The calculation cannot be completed because division by zero is undefined.'
)
```

---

## Explanation

## Why Tool Errors Matter

Tools interact with the real world.

Real-world systems are imperfect.

Common failures include:

```text
Missing data
Network failures
Invalid requests
Permission issues
Unexpected exceptions
```

Agents must be designed with failure in mind.

---

## Step 1 — Create a Tool That Can Fail

Our tool:

```python
@tool
def divide(a, b):
```

works normally:

```python
divide(100, 5)
```

Result:

```text
20
```

But:

```python
divide(100, 0)
```

raises:

```python
ValueError
```

---

## Step 2 — LLM Generates Tool Call

The user asks:

```text
Divide 100 by 0
```

The model produces:

```python
{
    "name": "divide",
    "args": {
        "a": 100,
        "b": 0
    }
}
```

Tool execution begins.

---

## Step 3 — Tool Execution Fails

The tool detects:

```python
b == 0
```

and raises:

```python
ValueError(
    "Division by zero is not allowed."
)
```

Instead of producing a result:

```text
Execution fails
```

---

## Step 4 — ToolNode Captures the Error

LangGraph's ToolNode automatically captures tool exceptions.

Rather than crashing the workflow:

```text
Exception
      ↓
ToolMessage
```

The error becomes part of the conversation history.

Example:

```python
ToolMessage(
    content=
    "Error: Division by zero is not allowed."
)
```

---

## Step 5 — LLM Sees the Error

The next chatbot iteration receives:

```text
User Message
AI Tool Request
Tool Error Message
```

The model now understands:

```text
The tool failed.
```

and can generate a helpful response.

Example:

```text
Division by zero is undefined.
```

The workflow completes successfully.

---

## Execution Flow

```text
User
 │
 ▼
LLM
 │
 ▼
Tool Call
 │
 ▼
Tool Executes
 │
 ▼
Error Occurs
 │
 ▼
ToolMessage(Error)
 │
 ▼
LLM
 │
 ▼
Graceful Response
 │
 ▼
END
```

---

## Error Recovery Pattern

A common production pattern is:

```text
Try Tool
   │
   ▼
Success?
   │
 ┌─┴─────────┐
 │           │
Yes          No
 │           │
 ▼           ▼
Result    Error Message
 │           │
 └─────┬─────┘
       ▼
     LLM
       ▼
 Final Response
```

The conversation continues regardless of outcome.

---

## Why This Is Important

Without recovery:

```text
Single failure
      ↓
Entire workflow fails
```

With recovery:

```text
Failure
      ↓
Error captured
      ↓
Agent explains problem
```

This dramatically improves user experience.

---

## Production Examples

### Database Query

```text
Record not found
```

Agent response:

```text
I couldn't locate that record.
```

---

### Weather API

```text
API unavailable
```

Agent response:

```text
The weather service is temporarily unavailable.
```

---

### CRM System

```text
Customer ID invalid
```

Agent response:

```text
Please verify the customer ID.
```

---

### Payment Service

```text
Transaction failed
```

Agent response:

```text
The payment could not be processed.
```

---

## Beyond Basic Error Handling

Production systems often add:

### Retries

```text
Try again automatically
```

---

### Fallback Tools

```text
Primary search fails
      ↓
Use backup search
```

---

### Human Escalation

```text
Agent cannot recover
      ↓
Transfer to human
```

---

### Logging

```text
Capture failure details
for monitoring
```

These patterns build highly reliable agents.

---

## Common Mistakes

### 1. Assuming Tools Never Fail

Bad assumption:

```text
Tool execution always succeeds
```

Reality:

```text
Failures are inevitable
```

Design accordingly.

---

### 2. Hiding Errors From the LLM

Bad:

```text
Discard exception
```

The model loses context.

---

Better:

```text
Convert exception into a ToolMessage
```

so the model can react intelligently.

---

### 3. Returning Cryptic Error Messages

Bad:

```text
Error #58291
```

Not useful.

---

Better:

```text
Division by zero is not allowed.
```

Clear and actionable.

---

## Mental Model

Think of tool errors as:

```text
Observations
```

rather than:

```text
Catastrophes
```

The agent observes:

```text
Tool succeeded
```

or:

```text
Tool failed
```

and continues reasoning in either case.

---

## Architecture

```text
                 User
                   │
                   ▼
                LLM
                   │
                   ▼
              Tool Call
                   │
                   ▼
               ToolNode
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
      Success             Error
          │                 │
          ▼                 ▼
   Tool Result      Error Message
          │                 │
          └────────┬────────┘
                   ▼
                  LLM
                   ▼
             Final Answer
```

---

## Key Takeaways

- Production tools can fail for many reasons.
- Tool errors should be treated as part of the agent workflow.
- `ToolNode` can capture tool exceptions and return them as messages.
- Error information becomes available to the LLM for reasoning.
- Robust agents recover gracefully instead of crashing.
- Error recovery is a critical requirement for real-world AI systems.
- In the next lab, we will explore tool selection strategies and learn how to improve an agent's ability to choose the right tool at the right time.