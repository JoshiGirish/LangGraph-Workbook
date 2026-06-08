# Lab 067 — MCP Fundamentals

## Lab Intro

So far in this course, our agents have interacted with:

- LLMs
- tools
- memory
- vector stores
- external APIs

However, every integration has required custom code.

For example:

```text
Tool A → Custom Integration
Tool B → Custom Integration
Tool C → Custom Integration
```

As the number of tools grows, maintaining integrations becomes difficult.

This challenge led to the creation of:

> **Model Context Protocol (MCP)**

MCP is an open protocol that standardizes how AI systems connect to external tools, resources, and services.

Instead of building a custom integration for every system:

```text
One Protocol
      ↓
Many Tools
```

---

## Key Idea

Without MCP:

```text
Agent
  ├── Custom API #1
  ├── Custom API #2
  ├── Custom API #3
  └── Custom API #4
```

With MCP:

```text
Agent
   ↓
 MCP
   ↓
Multiple External Systems
```

MCP acts as a universal communication layer between AI applications and external resources.

---

## Enterprise Analogy

Imagine a company with dozens of internal systems:

```text
CRM
ERP
Ticketing
Analytics
Knowledge Base
HR Platform
```

Without a standard interface:

```text
Every application needs separate integrations.
```

With MCP:

```text
One protocol
     ↓
Access to all systems
```

This significantly reduces integration complexity.

---

## What is MCP?

MCP stands for:

```text
Model Context Protocol
```

It is a protocol designed to allow AI applications to:

- discover tools
- invoke tools
- access resources
- retrieve context
- interact with external systems

through a common interface.

---

## Why MCP Was Created

Before MCP:

```text
Every AI vendor built integrations differently.
```

This caused:

- duplicated work
- vendor lock-in
- inconsistent tool interfaces

MCP introduces a standard approach.

Think of it as:

```text
USB-C for AI tools
```

Just as USB-C standardized hardware connections:

```text
MCP standardizes AI integrations.
```

---

## Core MCP Architecture

At a high level:

```text
AI Application
      ↓
   MCP Client
      ↓
   MCP Server
      ↓
 External System
```

---

### MCP Client

The client is typically:

```text
Agent
Assistant
AI Application
```

Its responsibility is to:

- discover capabilities
- request resources
- invoke tools

---

### MCP Server

The server exposes:

```text
Tools
Resources
Prompts
```

to MCP-compatible clients.

The server acts as the bridge between AI systems and external services.

---

### External Systems

These can include:

```text
Databases
REST APIs
Internal Services
Knowledge Bases
Filesystems
Business Applications
```

---

## MCP Building Blocks

MCP revolves around several core concepts.

---

## 1. Tools

Tools represent actions.

Examples:

```text
search_customer()
create_ticket()
send_email()
query_database()
```

Agents invoke tools through MCP.

---

## 2. Resources

Resources represent information.

Examples:

```text
Documents
Files
Knowledge Articles
Configurations
Reports
```

Resources provide context.

---

## 3. Prompts

Servers may expose reusable prompts.

Example:

```text
Summarize customer issue
Generate compliance report
Analyze financial data
```

These become reusable AI workflows.

---

## MCP Conceptual Example

Imagine a CRM MCP server.

It may expose:

### Tools

```text
create_customer()
update_customer()
lookup_customer()
```

### Resources

```text
Customer Records
Sales Reports
Account History
```

### Prompts

```text
Generate Sales Summary
Analyze Customer Health
```

An MCP-enabled agent can automatically discover these capabilities.

---

## Traditional Integration vs MCP

### Traditional

```text
Agent
 ├── CRM API
 ├── ERP API
 ├── HR API
 └── Ticket API
```

Each integration is custom.

---

### MCP

```text
Agent
   ↓
 MCP
   ↓
CRM Server
ERP Server
HR Server
Ticket Server
```

Unified interaction model.

---

## Why MCP Matters for Agents

Modern agents increasingly need access to:

```text
Enterprise Data
Business Processes
Knowledge Sources
External Services
```

Without MCP:

```text
Integration effort grows rapidly.
```

With MCP:

```text
Discover → Connect → Use
```

becomes standardized.

---

## MCP and Agentic Systems

Many agent workflows require:

```text
Reason
 ↓
Retrieve Data
 ↓
Use Tool
 ↓
Generate Response
```

MCP provides a consistent way to perform:

```text
Retrieve
Use Tool
Access Resource
```

regardless of the underlying system.

---

## Typical MCP Workflow

```text
Agent Starts
      ↓
Discover Available Tools
      ↓
Select Appropriate Tool
      ↓
Invoke Tool
      ↓
Receive Result
      ↓
Continue Reasoning
```

This fits naturally into LangGraph workflows.

---

## Example MCP Interaction

Conceptually:

```text
Agent:
"What tools are available?"
```

Server:

```text
search_customers
create_ticket
lookup_order
```

Agent:

```text
Call lookup_order(order_id=123)
```

Server:

```text
Returns order information
```

Agent:

```text
Uses result to answer user
```

---

## MCP Benefits

### 1. Standardization

One protocol across many systems.

---

### 2. Tool Discovery

Agents can discover capabilities dynamically.

---

### 3. Reusability

Servers can be reused across applications.

---

### 4. Reduced Integration Cost

Less custom development.

---

### 5. Vendor Neutrality

Tools become portable across AI ecosystems.

---

## Common Enterprise MCP Use Cases

### Customer Support

```text
Agent
 ↓
CRM MCP Server
 ↓
Customer Data
```

---

### IT Operations

```text
Agent
 ↓
Infrastructure MCP Server
 ↓
System Information
```

---

### Analytics

```text
Agent
 ↓
Data Warehouse MCP Server
 ↓
Business Reports
```

---

### Knowledge Management

```text
Agent
 ↓
Knowledge MCP Server
 ↓
Documents and Policies
```

---

## How MCP Relates to LangGraph

LangGraph provides:

```text
Reasoning
State Management
Workflow Orchestration
```

MCP provides:

```text
External Connectivity
Tool Discovery
Resource Access
```

Together:

```text
LangGraph + MCP
```

enable powerful enterprise-grade agent systems.

---

## Mental Model

Think of MCP as:

```text
A universal adapter
```

between:

```text
AI Applications
```

and

```text
External Systems
```

Instead of learning every API individually:

```text
Learn MCP once
Use many systems
```

---

## Architecture

```text
                Agent
                  │
                  ▼
          ┌─────────────┐
          │ MCP Client  │
          └──────┬──────┘
                 │
                 ▼
          ┌─────────────┐
          │ MCP Server  │
          └──────┬──────┘
                 │
                 ▼
      ┌─────────────────────┐
      │ External Systems    │
      │ Databases           │
      │ APIs                │
      │ Files               │
      │ Business Apps       │
      └─────────────────────┘
```

---

## Important Note

In this lab we focused on:

```text
Concepts
Architecture
Terminology
```

We intentionally did not write code yet.

The goal is to understand:

```text
What MCP is
Why it exists
How it fits into agent systems
```

Before we begin implementing it.

---

## Key Takeaways

- MCP stands for Model Context Protocol.
- MCP standardizes communication between AI systems and external services.
- MCP introduces clients and servers.
- Servers expose tools, resources, and prompts.
- Agents can dynamically discover and use MCP capabilities.
- MCP reduces custom integration work.
- MCP is becoming a foundational standard for enterprise AI systems.
- LangGraph orchestrates workflows, while MCP provides standardized external connectivity.
