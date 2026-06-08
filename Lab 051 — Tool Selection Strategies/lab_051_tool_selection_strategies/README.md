# Lab 051 — Tool Selection Strategies

## Lab Intro

In Lab 049, we built a multi-tool agent.

The workflow looked like:

```text
User
  ↓
LLM
  ↓
Choose Tool
  ↓
Execute Tool
  ↓
Answer
```

In Lab 050, we learned how to recover when tool execution fails.

Now we focus on another important question:

> How does the model decide which tool to use?

When an agent has only one tool:

```text
Tool selection is trivial.
```

But production agents often have:

```text
10+
20+
50+
100+ tools
```

Poor tool selection leads to:

- incorrect answers
- unnecessary tool calls
- higher latency
- increased cost
- unreliable behavior

Therefore, designing good tool selection strategies is a critical part of agent engineering.

---

## Key Idea

The model selects tools using:

```text
User Request
+
Tool Descriptions
+
Available Context
```

A well-designed tool ecosystem helps the model choose correctly.

A poorly-designed one creates confusion.

---

## Enterprise Analogy

Imagine a large company help desk.

Available departments:

```text
Billing
Technical Support
Sales
Shipping
Returns
```

Customer asks:

```text
Where is my order?
```

A good routing system sends them to:

```text
Shipping
```

not:

```text
Billing
```

Tool selection in agents works similarly.

The LLM acts as the dispatcher.

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
# Tool 1
# -------------------------

@tool
def weather_lookup(city: str) -> str:
    """
    Retrieve weather information
    for a specific city.
    """
    return f"Sunny in {city}"


# -------------------------
# Tool 2
# -------------------------

@tool
def stock_lookup(symbol: str) -> str:
    """
    Retrieve stock market information
    using a ticker symbol.
    """
    return f"{symbol}: $180"


# -------------------------
# Tool 3
# -------------------------

@tool
def currency_converter(
    amount: float,
    from_currency: str,
    to_currency: str
) -> str:
    """
    Convert money between currencies.
    """
    return "Converted amount"


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

tools = [
    weather_lookup,
    stock_lookup,
    currency_converter
]

llm_with_tools = llm.bind_tools(
    tools
)


# -------------------------
# Chatbot
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
# Graph
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
# Example Queries
# -------------------------

queries = [
    "What's the weather in London?",
    "Convert 100 USD to EUR",
    "What is the price of AAPL stock?"
]

for query in queries:

    result = graph.invoke(
        {
            "messages": [
                ("user", query)
            ]
        }
    )

    print(
        result["messages"][-1].content
    )

---

## Example Output

```python
Sunny in London

Converted amount

AAPL: $180
```

---

## Explanation

## What Is Tool Selection?

Tool selection is the process of deciding:

```text
Which tool should handle a request?
```

For example:

User asks:

```text
What's the weather in London?
```

The model evaluates:

```text
weather_lookup
stock_lookup
currency_converter
```

and chooses:

```text
weather_lookup
```

---

## How the LLM Selects Tools

Internally, the model performs reasoning similar to:

```text
User wants weather information.
```

↓

```text
Available tools:
- weather_lookup
- stock_lookup
- currency_converter
```

↓

```text
weather_lookup is the best match.
```

↓

```text
Generate tool call.
```

This happens automatically.

---

## Strategy 1 — Clear Tool Descriptions

The most important factor is:

```text
Tool description quality
```

Good:

```python
"""
Retrieve weather information
for a specific city.
"""
```

The purpose is obvious.

---

Bad:

```python
"""
Gets data.
"""
```

The model cannot infer intent.

---

## Strategy 2 — Distinct Responsibilities

Each tool should solve a specific problem.

Good:

```text
Weather
Stocks
Currency Conversion
```

Different domains.

---

Bad:

```text
Weather Tool A
Weather Tool B
Weather Tool C
```

The model may become confused.

---

## Strategy 3 — Specific Tool Names

Tool names should communicate purpose.

Good:

```python
weather_lookup
```

---

Bad:

```python
tool1
```

The model receives little information.

---

Good:

```python
currency_converter
```

---

Bad:

```python
utility_service
```

Specificity improves selection accuracy.

---

## Strategy 4 — Minimize Tool Overlap

Suppose we create:

```python
weather_lookup()
```

and

```python
city_weather_lookup()
```

with nearly identical descriptions.

The model now faces ambiguity.

Whenever possible:

```text
One responsibility
One tool
```

---

## Strategy 5 — Limit Tool Count

More tools create more complexity.

Small toolset:

```text
3 tools
```

Selection is easy.

---

Large toolset:

```text
100 tools
```

Selection becomes harder.

Many production systems use:

```text
Hierarchical routing
```

to reduce the active tool set.

---

## Hierarchical Tool Selection

Instead of exposing:

```text
100 tools
```

to the model at once:

```text
Step 1:
Choose category

Weather
Finance
Support
Search

Step 2:
Choose tool inside category
```

Example:

```text
User asks:
What's the weather in Paris?
```

↓

```text
Select category:
Weather
```

↓

```text
Select tool:
weather_lookup
```

This improves accuracy at scale.

---

## Strategy 6 — Use Examples

Descriptions can include examples.

Example:

```python
"""
Convert money between currencies.

Examples:
- USD to EUR
- GBP to INR
"""
```

Examples help the model understand intended usage.

---

## Strategy 7 — Force Tool Usage

Sometimes you want:

```text
Always use a tool
```

even when the model believes it knows the answer.

For example:

```text
Current stock prices
```

should always come from a live system.

Many providers support:

```python
tool_choice="required"
```

or equivalent configurations.

This improves reliability for real-time data.

---

## Strategy 8 — Let the Model Answer Directly

Not every question requires a tool.

Example:

```text
What is 2 + 2?
```

Some models may answer directly.

Others may call a calculator.

Both can be valid depending on system design.

Avoid forcing tools unnecessarily.

---

## Tool Selection Flow

```text
User Question
       │
       ▼
Understand Intent
       │
       ▼
Review Available Tools
       │
       ▼
Find Best Match
       │
       ▼
Generate Tool Call
       │
       ▼
Execute Tool
```

---

## Real-World Agent Toolkits

Enterprise agents commonly include:

```text
CRM Tool
Search Tool
Database Tool
Calculator
Email Service
Calendar Service
Weather API
Inventory System
Analytics Platform
```

Tool selection quality often determines:

```text
Agent quality
```

more than model quality alone.

---

## Common Mistakes

### 1. Generic Tool Descriptions

Bad:

```python
"""
Does operations.
"""
```

Provides little guidance.

---

Good:

```python
"""
Retrieve current weather
for a city.
"""
```

Specific and clear.

---

### 2. Too Many Similar Tools

Bad:

```text
search_v1
search_v2
search_v3
search_v4
```

The model struggles to distinguish them.

---

Better:

```text
Web Search
Document Search
Database Search
```

Distinct purposes.

---

### 3. Exposing Every Tool

Some systems expose:

```text
50+ tools simultaneously
```

This often reduces selection accuracy.

Consider:

```text
Tool filtering
Category routing
Hierarchical selection
```

---

### 4. Ignoring Tool Names

The model uses:

```text
Tool Name
+
Description
```

for reasoning.

Meaningful names matter.

---

## Mental Model

Think of tool selection as:

```text
Intent Matching
```

The model asks:

```text
What does the user need?
```

Then:

```text
Which tool best satisfies that need?
```

The better the tools are designed:

```text
The easier this decision becomes.
```

---

## Architecture

```text
                    User Request
                          │
                          ▼
                  Intent Analysis
                          │
                          ▼
               Available Tool Set
                          │
      ┌───────────────────┼───────────────────┐
      │                   │                   │
      ▼                   ▼                   ▼
 Weather Tool       Stock Tool       Currency Tool
      │                   │                   │
      └───────────────────┼───────────────────┘
                          │
                          ▼
                   Best Tool Chosen
                          │
                          ▼
                    Tool Execution
                          │
                          ▼
                     Final Answer
```

---

## Key Takeaways

- Tool selection determines which tool an agent chooses for a task.
- The LLM relies heavily on tool names and descriptions.
- Clear, specific tool descriptions improve selection accuracy.
- Tool overlap should be minimized whenever possible.
- Large tool collections often benefit from hierarchical routing.
- Examples inside tool descriptions can improve tool usage.
- Some systems force tool usage for critical real-time operations.
- Good tool selection is a foundational skill in building reliable AI agents.
- In the next lab, we will learn how to stream agent responses and observe tool execution in real time.
