# Lab 048 — ReAct Agent in LangGraph

## Lab Intro

In Lab 048, we learned how an LLM can generate tool calls.

The workflow looked like:

```text
User
  ↓
LLM
  ↓
Tool Request
```

However, the tool was never executed.

The model merely produced instructions such as:

```python
{
    "name": "calculator",
    "args": {
        "expression": "125 * 8"
    }
}
```

To build a real agent, we need the complete cycle:

```text
Reason
  ↓
Act
  ↓
Observe
  ↓
Reason Again
```

This pattern is called:

> **ReAct (Reason + Act)**

ReAct is one of the most important agent architectures in modern AI systems.

LangGraph provides built-in support for implementing ReAct workflows.

---

## Key Idea

Traditional chatbot:

```text
User → LLM → Answer
```

ReAct agent:

```text
User
  ↓
LLM Reasons
  ↓
Tool Call
  ↓
Tool Executes
  ↓
Observation Returned
  ↓
LLM Generates Final Answer
```

The agent can think, act, observe, and continue reasoning.

---

## Enterprise Analogy

Imagine a support agent receiving:

```text
What is the total value of 350 units at $24 each?
```

The agent does not perform large calculations mentally.

Instead:

```text
Customer Question
       ↓
Agent Thinks
       ↓
Calculator Used
       ↓
Result Returned
       ↓
Final Response
```

This mirrors the ReAct pattern:

```text
Reason → Action → Observation → Response
```

---

## Lab Code

from typing import Annotated

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from typing_extensions import TypedDict


# -------------------------
# Tool
# -------------------------

@tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    """
    return str(eval(expression))


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

tools = [calculator]

llm_with_tools = llm.bind_tools(tools)


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
# Routing Logic
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
                "What is 125 * 8?"
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
    content='What is 125 * 8?'
)

AIMessage(
    content='',
    tool_calls=[
        {
            'name': 'calculator',
            'args': {
                'expression': '125 * 8'
            }
        }
    ]
)

ToolMessage(
    content='1000'
)

AIMessage(
    content='125 multiplied by 8 equals 1000.'
)
```

---

## Explanation

## What Is ReAct?

ReAct stands for:

```text
Reason + Act
```

The model:

```text
Reasons about the problem
```

Then:

```text
Acts using tools
```

Then:

```text
Reasons again using tool results
```

The cycle continues until a final answer is produced.

---

## Step 1 — LLM Generates Tool Call

The user asks:

```text
What is 125 * 8?
```

The chatbot node executes:

```python
response = llm_with_tools.invoke(...)
```

The model decides:

```text
I should use the calculator.
```

Output:

```python
AIMessage(
    tool_calls=[...]
)
```

---

## Step 2 — Route to Tool Node

We inspect the last message:

```python
last_message = state["messages"][-1]
```

Check:

```python
if last_message.tool_calls:
```

If tool calls exist:

```python
return "tools"
```

Otherwise:

```python
return END
```

This creates dynamic graph behavior.

---

## Step 3 — Execute Tool

The built-in ToolNode handles execution:

```python
tool_node = ToolNode(tools)
```

It automatically:

```text
Reads tool request
Calls tool
Creates ToolMessage
Returns result
```

For example:

```python
ToolMessage(
    content="1000"
)
```

---

## Step 4 — Return to Chatbot

After execution:

```python
builder.add_edge(
    "tools",
    "chatbot"
)
```

The graph loops back.

Now the message history contains:

```text
User Message
AI Tool Request
Tool Result
```

The LLM receives the observation.

---

## Step 5 — Generate Final Answer

The model sees:

```text
Calculator Result = 1000
```

and responds:

```text
125 multiplied by 8 equals 1000.
```

No additional tool calls are needed.

The graph terminates.

---

## ReAct Execution Flow

```text
User
 │
 ▼
Chatbot
 │
 ▼
Tool Call?
 │
 ├─ No ─────────────► END
 │
 ▼
Tool Node
 │
 ▼
Tool Result
 │
 ▼
Chatbot
 │
 ▼
Final Answer
 │
 ▼
END
```

---

## Why ToolNode Matters

Without ToolNode:

```text
You manually parse tool calls
You manually execute tools
You manually create ToolMessages
```

With ToolNode:

```text
Tool execution is automatic
```

It handles:

- tool lookup
- argument passing
- execution
- ToolMessage creation

---

## Why ReAct Is Powerful

A ReAct agent can:

### Perform Calculations

```text
Calculator Tool
```

---

### Search Information

```text
Search Tool
```

---

### Query Databases

```text
Database Tool
```

---

### Access APIs

```text
Weather Tool
Stock Tool
CRM Tool
```

---

### Use Multiple Iterations

```text
Reason
→ Tool
→ Observation
→ Tool
→ Observation
→ Final Answer
```

The loop can repeat several times.

---

## Common Mistakes

### 1. Forgetting the Loop Back Edge

Bad:

```python
tools → END
```

The model never sees tool results.

---

Good:

```python
tools → chatbot
```

This enables observation and further reasoning.

---

### 2. Missing Conditional Routing

Bad:

```python
chatbot → tools
```

Tools execute even when unnecessary.

---

Good:

```python
route_tools()
```

Only execute tools when requested.

---

### 3. Executing Tools Manually

Bad:

```python
tool(...)
```

inside routing logic.

---

Better:

```python
ToolNode(tools)
```

Let LangGraph manage execution.

---

## Mental Model

Think of ReAct as:

```text
Think
 ↓
Act
 ↓
Observe
 ↓
Think Again
 ↓
Answer
```

The agent continuously alternates between:

```text
Reasoning
and
Tool Usage
```

until the task is complete.

---

## Architecture

```text
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   LLM       │
│ (Reason)    │
└──────┬──────┘
       │
 Tool Call
       │
       ▼
┌─────────────┐
│ Tool Node   │
│   (Act)     │
└──────┬──────┘
       │
 Observation
       │
       ▼
┌─────────────┐
│   LLM       │
│ (Reason)    │
└──────┬──────┘
       │
 Final Answer
       ▼
      END
```

---

## Key Takeaways

- ReAct stands for **Reason + Act**.
- A ReAct agent alternates between reasoning and tool execution.
- The LLM generates tool calls when needed.
- `ToolNode` automatically executes requested tools.
- Tool results are returned as `ToolMessage` objects.
- The graph loops back to the LLM so it can reason over observations.
- ReAct is the foundation of most modern tool-using AI agents.
- In the next lab, we will expand the architecture to support multiple tools and intelligent tool selection.