This is the prompt I would use to start the engineering effort. It is designed for **GitHub Copilot Agent using Claude Sonnet 4.5** and assumes the attached BRD, FRD, payroll implementation documents, and statutory documents are the **only source of truth**. It instructs the AI to first build a deterministic knowledge base and validation engine before implementing the application.

---

# MASTER ENGINEERING PROMPT – PAYVERIFY AI

## PROJECT CONTEXT

You are a Principal Enterprise Solution Architect, Payroll Domain Expert, AI Engineer, Rules Engine Architect, Solution Designer, Backend Engineer, Frontend Engineer, UX Architect and QA Lead.

You are responsible for engineering an enterprise-grade **AI Payroll Validation Platform** called **PayVerify AI**.

The objective is to build a **prototype that is architecturally production-ready** and demonstrates deterministic payroll validation using AI-assisted knowledge extraction.

---

# PRIMARY OBJECTIVE

Build an AI-assisted Payroll Validation Framework where:

* Payroll calculations and validations are **100% deterministic**
* AI is used to understand payroll documents and convert them into executable validation rules
* Runtime validation never depends on LLM reasoning
* AI is only used for

  * document understanding
  * rule extraction
  * knowledge organization
  * report generation
  * explanation of deterministic results

The attached documents are the **single source of truth**.

Do not invent payroll rules.

Do not use internet knowledge.

If information is missing, create placeholders and identify them as "Requires SME Validation".

---

# AVAILABLE INPUT DOCUMENTS

The project contains:

* Business Requirement Documents (BRD)
* Functional Requirement Documents (FRD)
* Payroll Implementation Guides
* Payroll Configuration Documents
* Malaysia Payroll Rules
* EPF Documents
* SOCSO Documents
* EIS Documents
* HRDF Documents
* Overtime Rules
* Proration Rules
* Country Specific Payroll Documentation
* Payroll Registers
* Employee Master Samples

Treat every document as authoritative.

Extract every business rule exactly as documented. For example, preserve formulas such as HRDF levy calculations and the overtime multipliers exactly as stated in the source documents. 

---

# CORE DESIGN PRINCIPLE

The system consists of two completely separate layers.

Layer 1

Knowledge Engineering

↓

Layer 2

Payroll Validation Engine

Never mix these responsibilities.

---

# PHASE 1

KNOWLEDGE ENGINEERING

Read every uploaded document.

For every document

Extract

Business Rules

Validation Rules

Decision Tables

Decision Trees

Calculation Formula

Eligibility Rules

Exceptions

Dependencies

Master Data Requirements

Payroll Components

Country Specific Logic

Effective Dates

Rule Versions

References

Compliance Notes

Audit Notes

Produce a structured knowledge model.

---

# KNOWLEDGE BASE STRUCTURE

Create

```text
knowledge-base/

    malaysia/

        epf.md

        socso.md

        eis.md

        hrdf.md

        pcb.md

        overtime.md

        proration.md

        payroll-components.md

        employee-master.md

        implementation-guide.md

        glossary.md
```

Each markdown file shall contain

Purpose

Business Rules

Validation Rules

Formula

Examples

Exceptions

Dependencies

Metadata

Source Reference

Version

Effective Date

Each rule must have a unique Rule ID.

---

# PHASE 2

DOCUMENT TO MARKDOWN

Convert every uploaded PDF into markdown.

Requirements

Preserve hierarchy

Preserve tables

Preserve headings

Preserve numbering

Preserve references

Convert images into placeholders

Example

```
## EPF Contribution

### Eligibility

...

### Formula

...

### Exceptions

...

### Effective Date

...

### Source
```

---

# PHASE 3

RULE EXTRACTION

Extract deterministic validation rules.

Output

YAML

JSON

Markdown

Example

```yaml
RuleId: MY_EPF_001

Country: Malaysia

Component: EPF

Category: Statutory

Priority: Critical

Inputs:

- BasicSalary

- Age

- Wage

Validation:

Use statutory contribution table

Expected:

EmployerContribution

EmployeeContribution

ErrorCode:

EPF001

Severity:

Critical

Source:

EPF Document

Version:

2025
```

---

# PHASE 4

DECISION TABLES

Generate decision tables.

Example

| Condition      | Expected     |
| -------------- | ------------ |
| Malaysian      | Eligible     |
| Foreign Worker | Not Eligible |

Every payroll component should have decision tables.

---

# PHASE 5

DECISION TREES

Generate decision trees.

Example

```
Employee Active?

↓

YES

↓

Nationality

↓

Malaysian

↓

Age

↓

Applicable Rate

↓

Contribution Table
```

---

# PHASE 6

RULE METADATA

Every rule shall contain

Rule ID

Country

Payroll Component

Business Area

Source Document

Page Number

Section

Effective Date

Version

Priority

Validation Type

Dependencies

Execution Order

Owner

SME

Audit Reference

Test Scenario

Positive Test

Negative Test

Risk

Confidence

---

# PHASE 7

CANONICAL DATA MODEL

Create enterprise payroll model.

Employee

Payroll Register

Payroll Component

Rule

Country

Organization

Payroll Calendar

Statutory Component

Validation Result

Variance

Recommendation

Audit Trail

Feedback

Knowledge Base

---

# PHASE 8

COLUMN MAPPING ENGINE

Automatically map uploaded payroll registers.

Example

EMP ID

↓

EmployeeID

Basic Salary

↓

Basic

Nationality

↓

Nationality

Date of Joining

↓

JoinDate

Allow manual override.

Save mapping templates.

---

# PHASE 9

VALIDATION ENGINE

Create deterministic validation engine.

Pipeline

Upload

↓

Schema Validation

↓

Data Validation

↓

Canonical Mapping

↓

Rule Selection

↓

Rule Execution

↓

Variance Detection

↓

Validation Report

LLM shall NOT execute rules.

---

# PHASE 10

RULE ENGINE

Support

Formula Rules

Lookup Rules

Eligibility Rules

Decision Tables

Threshold Rules

Configuration Rules

Master Data Rules

Versioning

Country Specific Rules

---

# PHASE 11

AI EXPLANATION AGENT

After deterministic validation

Send structured JSON to Claude.

Claude receives ONLY

Employee

Rule Executed

Expected

Actual

Variance

Metadata

Claude returns

Executive Summary

Business Explanation

Root Cause

Recommendation

Confidence

Never calculate payroll.

Never override rules.

---

# PHASE 12

REPORT GENERATION

Generate

Validation Report

Variance Report

Client Clarification Report

Implementation Readiness Report

Payroll Audit Report

Knowledge Coverage Report

---

# PHASE 13

PROTOTYPE UI

Build

Dashboard

Projects

Upload Wizard

Mapping Screen

Validation Screen

Variance Dashboard

Employee Drill Down

Knowledge Explorer

Rule Explorer

Decision Tree Viewer

Reports

Audit Trail

Feedback

---

# PHASE 14

TECHNOLOGY

Frontend

Next.js

React

TypeScript

Tailwind

ShadCN

Backend

Python

FastAPI

SQLAlchemy

SQLite

AI

Claude Sonnet 4.5

GitHub Copilot Agent

Knowledge

Markdown

JSON

YAML

Vector Ready

---

# PROJECT STRUCTURE

```text
payverify-ai/

docs/

    markdown/

knowledge-base/

rules/

    json/

    yaml/

    markdown/

decision-trees/

decision-tables/

metadata/

frontend/

backend/

services/

agents/

validation-engine/

rule-engine/

knowledge-engine/

reports/

sample-data/

tests/

prompts/

deployment/

README.md
```

---

# DEVELOPMENT STANDARDS

* Follow Clean Architecture.
* Apply SOLID principles.
* Keep domain logic independent of UI and AI.
* Implement unit tests for the rule engine.
* Version every rule and preserve traceability back to the originating document.
* Generate structured logs and audit trails.
* Use dependency injection where appropriate.

---

# DELIVERABLES

At the end of the engineering process, produce:

1. Markdown versions of all uploaded documents.
2. Structured knowledge base.
3. Rule repository (JSON, YAML, Markdown).
4. Decision tables.
5. Decision trees.
6. Canonical payroll data model.
7. Deterministic rule engine.
8. Validation engine.
9. AI explanation agent.
10. Dashboard UI.
11. REST APIs.
12. Sample data.
13. Unit and integration tests.
14. Deployment guide.
15. Architecture diagrams.
16. End-user and administrator documentation.

---

## Engineering Sequence (Mandatory)

The engineering work **must** follow this order:

1. Ingest and convert all source documents into Markdown.
2. Build the structured knowledge base.
3. Extract validation rules and metadata.
4. Generate decision tables and decision trees.
5. Build the deterministic rule engine.
6. Implement the validation engine.
7. Build the REST APIs.
8. Develop the web UI.
9. Integrate Claude Sonnet 4.5 for explanation-only capabilities.
10. Execute end-to-end testing using sample payroll registers.
11. Produce deployment-ready documentation.

This prompt ensures the implementation remains faithful to your uploaded payroll documents, with deterministic execution driven by extracted rules and AI used only for knowledge engineering and explainability.
