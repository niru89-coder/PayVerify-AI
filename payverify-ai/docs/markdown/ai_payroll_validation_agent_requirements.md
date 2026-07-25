# AI_Payroll_Validation_Agent_Requirements

> Source: `AI_Payroll_Validation_Agent_Requirements.docx` (converted verbatim, Phase 0 digitization)

Business & Functional Requirements Document

AI Agent for Payroll Implementation Validation

(Statutory Compliance & Parallel-Run Variance Assistant for SaaS Payroll Platforms)

| Field | Details |
| --- | --- |
| Document Type | Business & Functional Requirements Document (BRD/FRD) |
| Project Name | Statutory Payroll Validation AI Agent ("PayVerify AI") |
| Prepared For | Product / Engineering / Implementation Teams |
| Version | 1.0 (Draft) |
| Date | 25 July 2026 |
| Status | Draft — for review |

## Table of Contents

- Purpose & Objective

- Background & Problem Statement

- Scope

- Stakeholders & Users

- Definitions & Abbreviations

- Solution Overview

- Functional Requirements

- Detailed Logic Examples (Reference Patterns)

- Data Requirements

- System Architecture

- AI / ML Approach

- Non-Functional Requirements

- Integration Requirements

- Compliance, Security & Data Privacy

- Reporting & Dashboard Requirements

- Success Metrics / KPIs

- Assumptions & Constraints

- Risks & Mitigations

- Implementation Roadmap

- Team & Roles Required

- Appendix

## 1. Purpose & Objective

This document defines the business and functional requirements for building an AI-based agent ("PayVerify AI") that reduces manual effort in payroll implementation and parallel-run validation projects for SaaS payroll platforms (e.g., Darwinbox implementations). The agent's core function is to compare a client's payroll register against the payroll platform's calculated register, identify variances at employee and pay-component level, and generate an explainable root-cause suggestion together with a recommended next action — replicating the diagnostic reasoning currently performed manually by payroll implementation consultants.

#### 1.1 Objectives

- Reduce manual effort and turnaround time (TAT) for parallel-run / UAT reconciliation cycles.

- Encode country-specific statutory rules (contribution ceilings, age bands, nationality/residency conditions, exemptions) into a maintainable, versioned knowledge base.

- Automatically detect and explain variances between the client register and the platform (Darwinbox) register at employee → pay component → statutory contribution level.

- Provide a graded, human-readable recommendation for every variance: whether the platform calculation is statutorily correct, whether the client input/configuration is likely wrong, or whether clarification is required.

- Continuously learn from consultant feedback and legislative updates, improving suggestion accuracy over time.

- Provide an audit trail so every AI suggestion can be traced back to the statutory rule, rate, and employee data point that produced it.

## 2. Background & Problem Statement

Payroll implementation projects require validating that a new payroll system computes statutory and business pay components correctly against a client's existing (source/legacy) payroll register, across every country the client operates in. Today this is a manual, consultant-driven process: for every variance found between the client register and the platform register, a consultant must manually check pay component mapping, employee master data (nationality, age, date of joining, wage type), applicable statutory rule/rate for that country, and then judge whether the client or the platform is correct.

This is slow, inconsistent across consultants, dependent on tribal knowledge of statutory rules, and difficult to scale across the many countries and frequent legislative changes a multi-country SaaS payroll product must support. An AI agent that encodes this reasoning — combining a deterministic statutory rule engine with an LLM-based explanation layer — can significantly compress this effort while improving consistency and auditability.

## 3. Scope

#### 3.1 In Scope

- Upload and comparison of Client Register and Darwinbox (platform) Register at employee and pay-component level.

- Country-specific statutory rule knowledge base — starting with Malaysia (EPF, SOCSO, EIS, HRDF, PCB/MTD) as the reference country, architected to extend to other countries (India, Philippines, Indonesia, UAE/GCC, Singapore, etc.).

- Variance detection, classification, root-cause suggestion, and recommended next action per variance.

- Employee-level statutory eligibility logic (e.g., age-based EPF rate, nationality-based HRDF applicability, wage ceiling caps).

- Dashboard/report of all variances with drill-down to employee and rule level.

- Feedback capture loop for consultants to confirm/reject/correct AI suggestions, feeding back into the rule base and model.

#### 3.2 Out of Scope (Phase 1)

- Automatic correction/write-back of client source data or Darwinbox configuration (Phase 1 is advisory-only; auto-remediation is a later phase — see Section 19).

- Real-time legislative monitoring/auto-ingestion of new laws without human legal review (Phase 1 knowledge base is curated and versioned by a compliance team; automated legislative scraping is a future enhancement).

- Statutory filing/submission functionality (the agent validates calculations; it does not file returns).

## 4. Stakeholders & Users

| Stakeholder | Role | Interest in the System |
| --- | --- | --- |
| Payroll Implementation Consultants | Primary users | Use the agent daily during parallel-run/UAT to triage variances faster |
| Implementation Project Managers | Secondary users | Track project-level variance closure status & TAT |
| Compliance / Statutory SMEs | Knowledge base owners | Author, review, and version statutory rules per country |
| Client Payroll POC | Indirect user / recipient | Receives clarification requests generated by the agent |
| Product & Engineering | Builders | Design, build, and maintain the agent and rule engine |
| Data Privacy / InfoSec | Governance | Ensure PII handling meets regulatory and contractual obligations |

## 5. Definitions & Abbreviations

| Term | Definition |
| --- | --- |
| Client Register | The payroll output/report from the client's existing (source/legacy) payroll system, treated as the input to be validated. |
| Darwinbox Register / Platform Register | The payroll output computed by the target SaaS payroll platform (Darwinbox), being validated against the client register during parallel run. |
| Pay Component | An individual payroll line item (e.g., Basic, HRA, HRDF, EPF Employee, EPF Employer, SOCSO, EIS, PCB/MTD). |
| Variance | A discrepancy between client register and platform register for a given employee and pay component, in either amount or applicability (calculated vs. not calculated). |
| Statutory Rule Engine | The deterministic, versioned repository of country-specific legal formulas, thresholds, ceilings, and eligibility conditions. |
| EPF | Employees Provident Fund (Malaysia) — retirement contribution scheme with age-banded contribution rates. |
| HRDF | Human Resources Development Fund (Malaysia) — statutory levy, applicability tied to employer registration and (in practice) commonly reviewed against employee nationality/registration category. |
| SOCSO / EIS | Social Security Organisation / Employment Insurance System (Malaysia) statutory contributions. |
| Confidence Score | AI-generated likelihood that a given suggestion (client-side error vs. platform-side error vs. needs clarification) is correct, based on rule match strength and historical feedback. |

## 6. Solution Overview

PayVerify AI is a hybrid system combining a deterministic statutory rule engine (for legally precise calculations, since payroll law cannot tolerate probabilistic error) with an LLM-based reasoning/explanation layer (for natural-language root-cause narration, ambiguous-case handling, and consultant-facing communication). The system ingests two registers, normalizes and maps their fields to a canonical employee/pay-component schema, runs each employee's applicable statutory calculation independently through the rule engine, compares all three data points (client value, platform value, rule-engine expected value) per component, classifies the variance, and produces a suggestion with a recommended next action and confidence score.

#### 6.1 High-Level Process Flow

- Consultant uploads Client Register and Darwinbox Register for a project/country/pay period.

- System maps both files to a canonical schema (employee ID, DOB, nationality, DOJ, wage components, statutory fields).

- System resolves employee master attributes required for statutory logic (age as of calculation date, nationality/residency status, wage ceiling category, exemption flags).

- Statutory Rule Engine independently computes the expected value for every applicable pay component per employee, per the country's current statutory rules and the client's configured pay component mapping.

- Reconciliation engine compares Client value vs. Darwinbox value vs. Rule-Engine expected value.

- Where Client ≠ Darwinbox, the system classifies the variance and applies decision-tree + LLM reasoning to generate a suggestion (see Section 8 for worked examples).

- Findings are presented on a dashboard with drill-down, exportable to Excel/Word, with a feedback capture mechanism.

- Consultant confirms, overrides, or requests clarification from the client; feedback is logged to improve future accuracy.

## 7. Functional Requirements

Each requirement below is tagged with a unique ID, priority (Must/Should/Could — MoSCoW), and description, for direct use in a product backlog.

### 7.1 Data Ingestion

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-01 | System shall allow upload of Client Register and Darwinbox Register in Excel/CSV format, per project, per country, per pay cycle. | Must |
| FR-02 | System shall support configurable column-to-field mapping (mapping wizard) since client register formats vary by client/country. | Must |
| FR-03 | System shall validate uploaded files for structural integrity (required columns present, employee ID uniqueness, numeric fields, date formats) before processing. | Must |
| FR-04 | System shall support bulk upload of employee master data separately if not embedded in the register (DOB, nationality, DOJ, employment type, work location/state). | Must |
| FR-05 | System shall support re-upload/versioning of registers as client submits corrected data across parallel-run cycles. | Should |

### 7.2 Field & Pay Component Mapping

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-06 | System shall maintain a configurable Pay Component Mapping table per client, linking client-side component names to canonical statutory components (e.g., client's "HRDF Levy" → canonical "HRDF"). | Must |
| FR-07 | System shall detect and flag pay components present in one register but absent/unmapped in the other. | Must |
| FR-08 | System shall allow the compliance/implementation team to maintain mapping templates reusable across similar clients within a country. | Should |

### 7.3 Statutory Knowledge Base (Rule Repository)

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-09 | System shall maintain a country-wise, versioned, effective-dated repository of statutory rules: contribution rates, wage ceilings, age bands, nationality/residency eligibility, minimum wage thresholds, rounding rules, and exemption conditions. | Must |
| FR-10 | Each rule shall store: legal reference/citation, effective start/end date, applicable jurisdiction (country/state), and last-reviewed-by (compliance SME) metadata for auditability. | Must |
| FR-11 | System shall support rule versioning so historical pay periods are validated against the statutory rule that was in force at that time, not the current rule. | Must |
| FR-12 | System shall provide an admin interface for compliance SMEs to add/update rules without requiring engineering changes (low-code rule authoring). | Should |
| FR-13 | System shall flag pay periods calculated using a rule version that has since been superseded, prompting re-validation. | Could |

### 7.4 Variance Detection Engine

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-14 | System shall compare Client Register vs. Darwinbox Register at employee + pay component granularity for every employee in both files. | Must |
| FR-15 | System shall independently compute an expected value per employee per applicable statutory component using the rule engine, to serve as a neutral third reference point. | Must |
| FR-16 | System shall classify each variance into types: (a) Component not calculated in one system, (b) Amount mismatch within tolerance, (c) Amount mismatch beyond tolerance, (d) Rate/slab mismatch, (e) Eligibility/applicability mismatch. | Must |
| FR-17 | System shall support a configurable rounding/tolerance threshold per country/component to avoid flagging immaterial rounding differences as variances. | Must |
| FR-18 | System shall detect missing or inconsistent employee master fields (e.g., blank DOB, blank nationality) that block statutory computation, and flag as a data-quality issue rather than a calculation variance. | Must |

### 7.5 Root-Cause Suggestion & Recommendation Engine

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-19 | For every variance, system shall generate a plain-language root-cause hypothesis referencing the specific employee attribute or configuration that drove the rule engine's expected outcome. | Must |
| FR-20 | System shall classify each suggestion outcome as one of: 'Platform (Darwinbox) calculation appears statutorily correct — client data likely needs review', 'Client register appears correct — platform configuration/mapping likely needs review', or 'Inconclusive — clarification required from client'. | Must |
| FR-21 | System shall generate a recommended next action per variance (e.g., 'Validate employee nationality field with client', 'Check HRDF component mapping in platform configuration', 'Confirm date of birth for age-band recalculation'). | Must |
| FR-22 | System shall attach a confidence score to each suggestion, derived from rule-match strength and historical consultant feedback on similar cases. | Should |
| FR-23 | System shall chain multi-step diagnostic logic (decision trees) per statutory component, mirroring expert consultant reasoning (see Section 8 for worked examples). | Must |
| FR-24 | Where a rule cannot fully explain a variance (e.g., ambiguous or conflicting data), the system shall use an LLM-based reasoning layer to draft a candidate explanation, clearly marked as 'AI-suggested / unverified' pending SME confirmation. | Should |

### 7.6 Feedback & Continuous Learning Loop

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-25 | Consultants shall be able to mark each AI suggestion as Confirmed / Rejected / Needs Correction, with free-text notes. | Must |
| FR-26 | Rejected/corrected suggestions shall be routed to compliance SMEs to assess whether the underlying rule needs updating. | Should |
| FR-27 | System shall track suggestion-acceptance accuracy over time, per country and per rule, to identify rules needing SME review. | Should |

### 7.7 Reporting & Case Management

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-28 | System shall provide a variance dashboard summarizing total variances by country, project, component, severity, and resolution status. | Must |
| FR-29 | System shall support drill-down from summary to individual employee-level variance detail with full reasoning trail. | Must |
| FR-30 | System shall auto-generate a client-ready clarification list/query log (exportable to Excel/Word) for items requiring client input. | Must |
| FR-31 | System shall track variance resolution status (Open / Pending Client / Pending Internal / Resolved) through to project sign-off. | Should |

## 8. Detailed Logic Examples (Reference Patterns)

These worked examples define the decision-tree pattern the rule engine and suggestion layer must replicate. Each new statutory component follows the same structural pattern: (1) check mapping/configuration, (2) check the employee attribute(s) that govern eligibility or rate, (3) compute the expected value via the rule engine, (4) compare all three values, (5) generate suggestion and next action.

### 8.1 Example — Malaysia HRDF Not Calculated in Darwinbox

Scenario: Client register shows an HRDF levy for an employee; Darwinbox register shows no HRDF calculated for the same employee.

- Check pay component mapping: Is HRDF mapped to an active pay component in the Darwinbox configuration for this client/entity? If unmapped → suggestion: "Platform configuration issue — HRDF component is not mapped; recommend engaging implementation team to configure mapping."

- If mapped, check employee nationality/eligibility category: Is the employee Malaysian or a category to which the client's HRDF registration applies?

- If nationality is non-Malaysian (and the applicable HRDF category excludes non-citizens per the client's registration/statute), the rule engine's expected value is zero HRDF → suggestion: "Darwinbox calculation appears statutorily correct. Client-side HRDF figure may be an error. Recommended action: validate the employee's nationality field and confirm with client whether HRDF was intentionally applied."

- If nationality is Malaysian and mapping is active but the value is still zero in Darwinbox, escalate as a genuine calculation defect → suggestion: "Employee is eligible and component is mapped, but not computed. Recommended action: raise as a system/configuration defect for engineering review."

### 8.2 Example — Malaysia EPF Age-Band Rate Mismatch

Scenario: EPF employee contribution rate applied differs between client register and Darwinbox register.

- Compute employee age as of the statutory reference date, from date of birth (age = reference date − DOB).

- Determine the applicable EPF contribution rate band from the current statutory rule set for that age (e.g., standard rate under 60; reduced/age-60-and-above rate for employees aged 60 and above, per the Malaysia EPF Third Schedule in force for that pay period).

- Identify EPF-applicable wage components per the client's configured wage definition (Basic, fixed allowances, etc. — only components statutorily subject to EPF), and sum them to determine EPF wages.

- Compute expected EPF employee & employer contribution using the correct age-band rate and EPF wage base; compare to both client and Darwinbox figures.

- If Darwinbox used the below-60 rate for an employee who is 60 or above → suggestion: "Employee's age (computed from DOB) qualifies for the 60-and-above EPF rate band; Darwinbox appears to have applied the incorrect rate band. Recommended action: verify employee DOB accuracy, then raise as a system rate-configuration defect if DOB is confirmed correct."

- If DOB itself differs between client and Darwinbox master data → suggestion: "Underlying DOB values differ between systems, which is the likely root cause of the rate mismatch. Recommended action: confirm correct DOB with client/HR master and update before re-validating."

### 8.3 Generalized Decision Pattern

This two-example pattern generalizes to every statutory component the knowledge base will encode. The reusable pattern is:

- Step 1 — Configuration check: is the component mapped/enabled correctly on the platform?

- Step 2 — Eligibility check: does the employee meet the statutory eligibility conditions (nationality, residency, age, wage threshold, employment type, state/region)?

- Step 3 — Base/rate determination: what wage base and rate/slab applies per current statutory rule for this employee?

- Step 4 — Independent computation: rule engine computes the expected value.

- Step 5 — Three-way comparison: client value vs. platform value vs. rule-engine expected value.

- Step 6 — Classification & suggestion: which side (if any) deviates from the statutorily-expected value, and what is the most likely underlying data/configuration cause.

- Step 7 — Recommended action: a specific, actionable next step (validate a specific field, check a specific configuration, escalate as defect, or request client clarification).

Additional components to encode using this same pattern (illustrative, not exhaustive): SOCSO/EIS category and wage ceiling; PCB/MTD tax computation basis; India PF wage ceiling and pension split; India ESI eligibility wage threshold; gratuity eligibility by tenure; overtime eligibility by exempt/non-exempt classification; minimum wage compliance checks by state/region.

## 9. Data Requirements

#### 9.1 Employee Master Fields Required

| Field | Purpose |
| --- | --- |
| Employee ID | Primary key for matching across registers |
| Date of Birth | Age-band statutory calculations (e.g., EPF) |
| Nationality / Citizenship | Nationality-dependent statutory applicability (e.g., HRDF, EPF for foreign workers) |
| Residency Status | Tax residency-dependent calculations (e.g., PCB/MTD) |
| Date of Joining / Date of Exit | Pro-ration, eligibility tenure checks (e.g., gratuity, probation-linked components) |
| Work Location / State | State/region-specific statutory rules (e.g., minimum wage, professional tax in India) |
| Employment Type / Category | Eligibility for components (e.g., contract vs. permanent, exempt vs. non-exempt) |
| Wage Components (Basic, Allowances, etc.) | Statutory wage base computation per component |

#### 9.2 Pay Component Data (per register)

- Component name/code (as per client register and as per Darwinbox).

- Component amount for the pay period.

- Component category (statutory / non-statutory, earning / deduction / employer contribution).

#### 9.3 Statutory Rule Data (Knowledge Base)

- Country, and where applicable, state/region.

- Component code and legal name.

- Rate/slab table, wage ceiling, age bands, or other conditional logic.

- Eligibility conditions (nationality, residency, wage threshold, employment type).

- Effective date range and legal citation/source reference.

## 10. System Architecture

Recommended high-level layered architecture:

- Ingestion Layer — file upload, parsing (Excel/CSV), field-mapping wizard, data validation.

- Canonical Data Layer — normalized employee master + pay component schema, common across countries.

- Statutory Rule Engine (deterministic) — versioned, country-wise rule repository and calculation logic, implemented as explicit, testable business rules (not left to the LLM) since statutory math must be exact and auditable.

- Reconciliation & Classification Engine — three-way comparison logic, variance classification, tolerance handling.

- AI Reasoning Layer (LLM, e.g., via Claude API) — converts rule-engine + comparison output into natural-language root-cause narrative and recommended action; handles ambiguous/edge cases via retrieval-augmented generation (RAG) over the statutory knowledge base and prior resolved cases.

- Feedback & Learning Layer — captures consultant confirm/reject actions, feeds a review queue to compliance SMEs, and (optionally) fine-tunes suggestion ranking over time.

- Application/Presentation Layer — dashboard, drill-down UI, exportable reports, client query-log generator.

- Audit & Logging Layer — immutable log of every rule version, computed value, and suggestion generated, for compliance traceability.

Design principle: keep statutory calculation deterministic and rule-based (auditable, testable, legally defensible), and use the LLM strictly for natural-language explanation, ambiguous-case triage, and consultant-facing communication — never as the source of the numeric statutory computation itself.

## 11. AI / ML Approach

#### 11.1 Hybrid Architecture Rationale

Payroll statutory calculations are deterministic and legally exact — an LLM should not be relied upon to compute contribution amounts directly, since even small hallucinated errors carry compliance and financial risk. The recommended approach separates concerns:

- Deterministic Rule Engine: computes exact expected statutory values from versioned, SME-authored rules (source of numeric truth).

- LLM Reasoning Layer: consumes structured output from the rule engine and reconciliation logic (client value, platform value, expected value, matched rule, employee attributes) and generates the human-readable explanation, root-cause hypothesis, and recommended action — grounded strictly in that structured data (retrieval-augmented, not free generation).

- Retrieval-Augmented Generation (RAG): for edge cases not fully covered by the decision tree, the LLM retrieves relevant statutory clauses and previously resolved similar cases from the knowledge base to draft a candidate explanation, clearly labeled as unverified pending SME sign-off.

#### 11.2 Guardrails

- Every AI-generated suggestion must cite the specific rule/version and employee data field it is based on (explainability requirement).

- Any suggestion generated purely via LLM reasoning (not backed by a deterministic rule match) must be visually flagged as lower-confidence / requiring SME review.

- No AI-generated suggestion should auto-modify client or platform data in Phase 1 — output is advisory only.

- Model outputs should be periodically benchmarked against consultant-confirmed ground truth to track accuracy drift.

## 12. Non-Functional Requirements

| Category | Requirement |
| --- | --- |
| Accuracy | Statutory calculations must match legal formulas with 100% accuracy for supported rule versions; suggestion accuracy should be tracked and continuously improved via feedback loop. |
| Auditability | Every suggestion must be traceable to the exact rule version, source data, and computation used — required for compliance defensibility. |
| Explainability | All AI outputs must be human-readable, with clear reasoning steps, not black-box scores alone. |
| Performance | System should process a standard client register (up to ~10,000 employees) and generate full variance analysis within a defined SLA (e.g., under 15 minutes for batch processing). |
| Scalability | Architecture should support addition of new countries/statutory rules without core re-engineering. |
| Data Privacy | All employee PII must be encrypted at rest and in transit; access restricted on a need-to-know basis; compliant with applicable data protection regulations (e.g., PDPA Malaysia, India DPDP Act, GDPR where applicable) and client contractual data handling terms. |
| Availability | Target uptime per standard SaaS SLA (e.g., 99.5%) for the validation platform. |
| Maintainability | Statutory rules must be updatable by compliance SMEs via a low-code interface without requiring a full engineering release cycle. |
| Auditor/Regulator Readiness | System should be able to produce an audit export showing rule basis for any historical calculation on demand. |

## 13. Integration Requirements

- Darwinbox API/export integration to pull the platform-calculated payroll register directly (reducing manual upload where feasible).

- Support for manual file upload (Excel/CSV) as the baseline integration method for the client register and for platforms without API access.

- Optional integration with project management tooling (e.g., for auto-creating tickets/tasks for unresolved variances).

- Optional integration with an LLM API (e.g., Claude API) for the reasoning/explanation layer, with configurable data redaction/anonymization before any data leaves the secure environment, per client contractual requirements.

## 14. Compliance, Security & Data Privacy

- PII minimization: only fields required for statutory computation should be ingested; avoid unnecessary sensitive data collection.

- Role-based access control: consultants see only projects/clients they are assigned to; compliance SMEs have rule-authoring access; audit logs restricted to compliance/security roles.

- Data residency: ensure storage/processing location complies with country-specific data residency requirements where applicable.

- Anonymization/pseudonymization option before any data is sent to an external LLM API, if required by client data processing agreements.

- Retention policy: define retention and secure deletion timelines for uploaded client registers post-project closure.

- Legal/compliance sign-off required before publishing any new or updated statutory rule to production.

## 15. Reporting & Dashboard Requirements

- Project-level summary dashboard: total employees, total variances, variance rate by component, resolution status.

- Employee-level detail view: side-by-side client value, platform value, rule-engine expected value, classification, suggestion, recommended action, confidence score.

- Exportable client query log: auto-formatted list of items requiring client clarification, ready to send.

- Trend view: variance patterns across pay cycles for the same client (to catch recurring configuration issues).

- SME review queue: items where AI suggestion was rejected/corrected, awaiting rule review.

## 16. Success Metrics / KPIs

| Metric | Target / Purpose |
| --- | --- |
| Reduction in manual reconciliation effort (hours per project) | Primary efficiency KPI |
| Variance detection coverage | % of true variances correctly identified by the system vs. manual audit |
| Suggestion acceptance rate | % of AI suggestions confirmed as correct by consultants, tracked per country/component |
| Time-to-resolution | Average time from variance detection to closure, pre- vs. post-AI-agent adoption |
| Statutory calculation accuracy | 100% match to legally correct values for all supported, versioned rules |
| Knowledge base coverage | Number of countries / statutory components fully encoded vs. roadmap target |

## 17. Assumptions & Constraints

- Client registers will be provided in a reasonably structured tabular format (Excel/CSV); free-text or scanned/image payslips are out of scope for Phase 1.

- Statutory rules will be authored and reviewed by qualified compliance/legal SMEs before being published to the rule engine; the AI does not independently determine legal correctness.

- Darwinbox register can be obtained either via export/upload or API access, depending on client/project setup.

- Employee master data required for eligibility logic (DOB, nationality, etc.) will be available from at least one of the two source registers or a separate master file.

- Phase 1 will focus on one reference country (Malaysia) to prove the pattern before scaling to additional countries.

## 18. Risks & Mitigations

| Risk | Mitigation |
| --- | --- |
| Statutory rules change frequently and knowledge base becomes outdated | Establish a defined SME review cadence and rule-versioning process; flag pay periods using superseded rules for re-validation |
| Incomplete/incorrect employee master data blocks accurate eligibility checks | Data-quality validation step before variance analysis; explicit data-quality flags separate from calculation variances |
| Over-reliance on AI suggestions without human validation | Keep Phase 1 strictly advisory; require consultant confirmation before any client-facing communication; track suggestion accuracy transparently |
| LLM hallucination in ambiguous/edge cases | Restrict LLM to explanation generation grounded in structured rule-engine output; flag ungrounded suggestions as low-confidence |
| Data privacy/security exposure of client PII, especially if using external LLM APIs | Data minimization, encryption, anonymization before external API calls, contractual and regulatory compliance review |
| Inconsistent pay component naming across clients complicates mapping | Configurable mapping templates, reusable per client/country, with mapping validation before analysis runs |

## 19. Implementation Roadmap

| Phase | Focus | Key Deliverables |
| --- | --- | --- |
| Phase 1
(MVP) | Single country proof of concept — Malaysia | Register upload & mapping, EPF/SOCSO/EIS/HRDF rule engine, variance detection, suggestion engine for the worked examples in Section 8, basic dashboard |
| Phase 2 | Multi-country expansion | Add 2–3 additional priority countries (e.g., India, Philippines, Indonesia), generalized rule-authoring interface for compliance SMEs, confidence scoring |
| Phase 3 | Intelligence & scale | LLM-based RAG reasoning layer for edge cases, feedback-driven suggestion accuracy tuning, Darwinbox API integration, trend analytics |
| Phase 4 | Advanced automation | Optional guided/assisted remediation workflows (human-approved auto-corrections), predictive variance flagging before parallel run based on configuration audit |

## 20. Team & Roles Required

- Product Manager — owns requirements, prioritization, and stakeholder alignment.

- Payroll Compliance SME(s) — per country, to author and validate statutory rules and review AI suggestions.

- Backend Engineers — build ingestion, rule engine, reconciliation logic.

- AI/ML Engineer — build and integrate the LLM reasoning/RAG layer and feedback-driven tuning.

- Frontend Engineer — dashboard, mapping wizard, review/feedback UI.

- QA Engineer — validate statutory calculation accuracy against known test cases per country.

- Data Privacy/Security Lead — ensure PII handling and access control meet regulatory and contractual requirements.

- Payroll Implementation Consultants (pilot users) — provide UAT feedback and validate suggestion usefulness in real projects.

## 21. Appendix

#### 21.1 Sample Variance Classification Reference (Malaysia)

| Component | Common Variance Trigger | Typical Root Cause Checked |
| --- | --- | --- |
| HRDF | Calculated in client, not in Darwinbox | Mapping configuration → employee nationality/eligibility category |
| EPF | Rate mismatch | Employee age band (60 and above) → DOB accuracy → EPF wage base composition |
| SOCSO/EIS | Not calculated / wrong category | Employee category (new hire, foreign worker exemption) → wage ceiling |
| PCB/MTD | Tax amount mismatch | Residency status → cumulative YTD income basis → relief/exemption configuration |

#### 21.2 Glossary Source Note

Statutory definitions and rates referenced in this document (EPF age-band rates, HRDF applicability, SOCSO/EIS categories) must be sourced from and periodically re-verified against official government publications (e.g., KWSP/EPF, HRD Corp, PERKESO, LHDN) by a qualified compliance SME before being encoded into the production rule engine. This document defines the system's requirements and logic pattern; it does not itself constitute a verified statutory rate table.
