# Documentation-BC — Document Types Reference

This document catalogues every document type produced by the `documentation-bc-*` skill family (excluding the `documentation-bc-md-to-docx-converter`, which only converts these markdown artefacts to `.docx` and does not define a document type of its own).

Each entry lists: the artefact ID prefix, where it is stored, what it is for, and the key sections with the information each one holds.

---

## 1. User Story (US)

- **Skill**: `documentation-bc-user-story-generator`
- **ID format**: `US-NNN`
- **Output**: `openspec/user-stories/US-NNN-<kebab-title>.userstory.md` (+ sibling `.userstory.json`)
- **Purpose**: Captures a functional/business requirement for a BC feature in OpenSpec format, before any technical planning. Starting point of the documentation chain.
- **Frontmatter**: `id, title, version, status (draft), module, productOwner, prepared_by, created_date, approved_date`

### Key sections

| Section | Information it holds |
|---|---|
| **User Story** | The "As a / I want / so that" statement: persona (role), capability wanted, business value/outcome. |
| **Business Context** | Current situation, who is affected, concrete operational pain points (≥2), real-world usage scenarios. |
| **Current Situation (Standard Business Central)** | Verified facts (via Microsoft Learn) on how standard BC behaves today, naming relevant objects/actions, ending with a **Conclusion** stating what BC already supports and the gap the story closes. |
| **Acceptance Criteria** | Numbered `AC1…ACn` (minimum 3), each with a short title and bullet points describing expected, testable behavior (no vague/subjective language). |
| **Out of Scope** | Items explicitly excluded from the story. |
| **Open Questions** | Numbered list of unresolved questions to be answered by the Product Owner. |

---

## 2. Technical Specification (SPEC)

- **Skill**: `documentation-bc-technical-spec-generator`
- **ID format**: `SPEC-NNN`
- **Output**: `openspec/specs/<kebab-title>.spec.md` (+ sibling `.spec.json`); also triggers per-phase plan files
- **Purpose**: Decomposes an **approved** user story into a complete technical/AL design — describes **what** to build. Requires `status: approved` on the source US.
- **Frontmatter**: `id, title, version, type (features), status (draft), user_story, priority, complexity, estimated_effort, module, prefix, id_range, prepared_by, created_date, approved_date`

### Key sections

| Section | Information it holds |
|---|---|
| **User Story Reference** | Link to source US, quoted As/Want/So-that block, confirmation that all US ACs are addressed in §7. |
| **Technical Design Overview** | 2.1 Design Principles (table: principle + rationale); 2.2 Architecture (Mermaid `erDiagram`/`flowchart`); 2.3 Out-of-Scope Confirmation echoing the US. |
| **AL Object Inventory** | Tables, Enums, Pages, Page Extensions, Codeunits, Permission Sets, Number Series — each as `ID \| Object Name \| Purpose` (or type-specific columns); plus an ID Allocation Summary (range/type/status). |
| **Table Field Definitions** | One table per new AL table: `Field No. \| Field Name \| Data Type \| Length/Properties \| Notes`, plus `Keys` and `Triggers` bullet lists. |
| **Page Design Notes** | Per non-trivial page: layout (groups/repeater/FactBoxes), actions, visibility/promotion logic. |
| **Integration with Standard BC Objects** | Table of `Standard Object \| Interaction` — TableRelations, FlowFields, standard codeunits used. |
| **Technical Acceptance Criteria** | Table `ID \| Description \| Maps to US-AC` using IDs like `AC-TBL-001`, `AC-FLD-001`, `AC-PAGE-001`, `AC-CU-001`, `AC-PERM-001`, `AC-LANG-001` — every US AC must map to ≥1 technical AC. |
| **Phase Overview** | Table `Phase \| Slug \| Name \| Effort (dev days) \| Description`, plus total estimated effort. |
| **Testing Strategy** | Per-phase unit-test plan: test codeunit names and locations under `test/`. |
| **Dependencies** | Table `Dependency \| Source \| Resolution`. |
| **Open Questions Tracking** | Table `# \| From \| Status \| Resolution proposed in this spec` echoing every US Open Question with its status (Resolved/Not blocking/Functional question/Escalated). |
| **Phase Plans** | Numbered list of links to each generated per-phase plan file. |

---

## 3. Phase Plan (PLAN)

- **Skill**: `documentation-bc-phase-plan-generator`
- **ID format**: `PLAN-NNN-P<N>`
- **Output**: `openspec/plans/SPEC-NNN-phase-<N>-<kebab-phase-name>.plan.md`
- **Purpose**: Translates one phase of an **approved** spec's §8 Phase Overview into the AL Developer's working backlog — a checkbox task list bounded by exit criteria. One file per phase, all generated in a single pass.
- **Frontmatter**: `id, title, version, spec, user_story, ccn, phase, status (not-started), estimated_hours, branch, depends_on, assignee, created_date, approved_date, related_docs`

### Key sections

| Section | Information it holds |
|---|---|
| **References** | Links to the source US (with the AC numbers this phase satisfies), the SPEC sections this phase implements, and the CCN (if any). |
| **Goal** | 2–4 sentences describing the concrete, demoable outcome at the end of the phase. |
| **Branch** | Git branch instructions — cut a new feature branch (Phase 1) or continue on it (Phase >1). |
| **Tasks** | Checkbox list `- [ ] N.x <action + object + properties>`, each citing the AC it satisfies; includes manual smoke-test/verification steps. |
| **Exit criteria** | Conditions to consider the phase done: tasks checked, ACs demonstrably met, build/tests green, `app.json` version bumped. |
| **Out of scope for this phase** | Items explicitly deferred to later phases or excluded per the US. |
| **Dependencies** | Prerequisites (upstream phase and what it delivers) and Downstream consumers (what the next phase needs from this one). |
| **Testing notes** | Test codeunits added/extended, mocked-vs-live strategy, deferred live-tenant tests, manual smoke-test scripts. |
| **Notes for the AL Developer** | Caption/tooltip rules, lookup filters/defaults, translation guidance, performance caveats, Microsoft Learn verification gaps. |

---

## 4. Feasibility Analysis (ANALYSIS)

- **Skill**: `documentation-bc-analysis-generator`
- **ID format**: `ANALYSIS-NNN`
- **Output**: `openspec/analysis/ANALYSIS-NNN-<kebab-title>.analysis.md`
- **Purpose**: The AL Analyst's working artefact backing a CCN — answers "is it worth building, at what cost, and what is the risk?" (the spec says **what**, the architecture explains **why**, this says **whether to proceed**).
- **Frontmatter**: `id, title, version, status (draft), spec, user_story, ccn, prepared_by, date, recommendation (GO/CONDITIONAL-GO/NO-GO), related_docs`

### Key sections

| Section | Information it holds |
|---|---|
| **References** | Table linking to the source User Story, Spec, and CCN with their statuses. |
| **Change summary** | One-paragraph framing plus bullet counts of new tables, pages, codeunits, permission sets, modified objects, and a note on legacy objects untouched. |
| **Scope & impact** | Table of dimensions: new/modified AL object counts, BC modules touched, external dependencies, net new LoC estimate, object ID range usage; plus an open-questions resolution summary. |
| **Time estimate** | Phased table of Optimistic/Expected/Pessimistic hours with subtotal, 20% contingency, and total; plus a calendar-duration table (working days / wall-clock weeks) per scenario. |
| **Cost estimate** | EUR/hour rate and rationale; cost per scenario; cost breakdown by phase + contingency; assumptions (developer familiarity, testing strategy, exclusions, review cycles). |
| **SWOT analysis** | Strengths, Weaknesses, Opportunities, and Threats — each with evidence citations (ACs, objects, design decisions), plus the "cost of NOT implementing" baseline. |
| **Risk assessment** | Numbered risk register `R-NN \| Risk \| Likelihood \| Impact \| Mitigation`, plus an overall risk rating (LOW…HIGH) with justification. |
| **Feasibility recommendation** | Verdict (**GO / CONDITIONAL-GO / NO-GO**) with justification (complexity, additive-vs-invasive nature, scope-creep risk, cost vs. value); pre-conditions if CONDITIONAL-GO; non-blocking advisories at kick-off. |
| **Handoff back to the Architect** | States the next decision the Architect must make (approve spec & hand off to development, or revise spec and re-analyse). |

---

## 5. Architecture (ARCH)

- **Skill**: `documentation-bc-architecture-generator`
- **ID format**: `ARCH-NNN`
- **Output**: `openspec/architecture/ARCH-NNN-<kebab-title>.architecture.md`
- **Purpose**: The long-lived companion to an approved technical spec — explains **why** it is built the way it is (design rationale, ADRs, cross-cutting concerns), without modifying the spec.
- **Frontmatter**: `id, title, spec, user_story, ccn, status (draft), version, created_date, author, related_docs`

### Key sections

| Section | Information it holds |
|---|---|
| **Context** | 1.1 Business context (originating need, link to US); 1.2 Technical context (existing objects/codeunits/integration points and the gap); 1.3 Scope of this architecture (in-scope / out-of-scope-deferred items). |
| **Architectural drivers** | Table `# (D-N) \| Driver \| Source (US AC / SPEC § / CCN §) \| Implication`. |
| **Architectural style and key decisions** | Naming of the chosen architectural style, plus numbered **ADR-N** records each with Context / Decision / Consequence / Alternatives rejected. |
| **Logical component view** | ASCII or Mermaid diagram of the components and their relations, plus a Component responsibilities table (`Component \| Responsibility \| Does NOT do`). |
| **Key runtime flows** | Diagrams of the primary happy path, optimised/cached path, configuration/state-change path, and no-match/error path. |
| **Data architecture** | 6.1 Entity-relationship overview (ER diagram of new tables and relations to existing ones); 6.2 Storage and ownership (`Object \| Storage class \| Owner \| Lifecycle`); 6.3 Key derivation (PK composition and rationale per table). |
| **Cross-cutting concerns** | Security (permission sets, auth flows), Reliability/error handling, Performance (per-record cost, DB/HTTP call counts), Observability (telemetry), Localisation/translations, RapidStart/portability, Upgrade/migration. |
| **Coexistence with legacy `<area>`** | Which legacy objects remain unchanged vs. touched, and how (only when legacy code exists). |
| **Constraints and known limitations** | Table `# (C-N) \| Constraint/limitation \| Source (ADR/Driver) \| Mitigation`. |

---

## 6. Change Control Note (CCN)

- **Skill**: `documentation-bc-ccn-generator`
- **ID format**: `CCN-NNN`
- **Output**: `docs/ccn/CCN-NNN-<kebab-title>.md` (English) or `docs/<lang>-ccn/...` (translated variants)
- **Purpose**: The single **stakeholder-facing** artefact that consolidates the approved User Story, Spec, Architecture, and Analysis into one consistent document for sign-off; feeds into `md-to-docx-converter`. Section headings, frontmatter keys, and diagram markers stay in canonical English across all language variants so downstream tooling binds identically.
- **Frontmatter**: `id, title, version, status (Pending Approval), client, dsd_ticket, user_story, spec, architecture, analysis, prepared_by, date, recommendation, related_docs`

### Key sections

| Section | Information it holds |
|---|---|
| **Header** | Bold-labelled metadata table: CCN ID, Title, Client, DSD ticket, BC environment, BC version baseline, extension affected (publisher/prefix/ID range), source US/SPEC (with approval dates), Architecture & Analysis refs, prepared by, date, status, recommendation. |
| **Business context** | Drawn from the US: Who (persona), What they want, Why, Objective, Functional scope (numbered list), Acceptance criteria summary table (`AC0x \| Topic`), Out of scope (Phase 1), Future enhancements. |
| **Proposed solution** | Drawn from the SPEC: Design principles, AL object inventory table with totals, Number series, API surface, Localisation approach, Open-question resolutions, Delivery phases table, plus a status-lifecycle state diagram. |
| **Architecture solution** | Drawn from ARCH (or a placeholder note if absent): ADR summary table, logical component view diagram, cross-cutting concerns table, coexistence-with-legacy note, known constraints table, ER diagram, and runtime-flow sequence diagram(s). |
| **Feasibility analysis** | Drawn from ANALYSIS (or placeholder if absent): change-summary bullets, SWOT prose (Strengths/Weaknesses/Opportunities/Threats), risk register table with overall rating, open-question status wrap-up. |
| **Time estimate** | Conditionally rendered per interview answers (`include_hours`, `include_costs`, chosen scenarios): effort-per-phase table, calendar-duration table, cost table (EUR rate and totals — only if costs included), assumptions. |
| **Testing setup (planned)** | Table `Phase \| Test coverage`, plus the phase exit policy (test codeunit green + smoke-checklist sign-off). |
| **Testing steps (acceptance, executed by `<Client>`)** | Numbered manual acceptance steps derived from the US Acceptance Criteria. |
| **Recommendation** | Verdict (**GO / CONDITIONAL-GO / NO-GO**) with justification; pre-conditions (if CONDITIONAL-GO); non-blocking advisories at kick-off. |
| **Approvals** | Sign-off table `Role \| Name \| Decision \| Date \| Signature` for Client Product Owner, Vendor Technical Lead, and Vendor Project Manager. |

---

## 7. Release Note (RN)

- **Skill**: `documentation-bc-release-note-generator`
- **ID format**: `RN-NNN`
- **Output**: `docs/releasenotesmd/<...>.releasenote.md` (+ sibling `.releasenote.json` field map)
- **Purpose**: The single stakeholder-facing artefact handed to the client at deployment time — summarises **what** changed, **why**, **how it was tested**, and **who approved it**. No company/client/publisher values are hardcoded; identity fields come from `app.json` or the user.
- **Frontmatter**: `id, template, language, title, version, status (draft), clientName, ccnNumber, issueNumber, releaseDate, releasedBy, module, createdDate, approvedDate`

### Key sections

| Section | Information it holds |
|---|---|
| **Release Summary** | High-level narrative of the release — what shipped and the headline value. |
| **Scope of Change** | Grouped lists of changed AL objects: Tables, Table Extensions, Pages, Page Extensions, Codeunits, Permission Sets — each entry naming the object, ID, and a Caption/XML-doc-based functional description (groups with no entries are omitted). |
| **Change Request Details** | Narrative of the underlying change request / CCN / issue driving the release. |
| **Testing Setup** | Prerequisites table (BC runtime, application version, extension + version, dependencies, permission sets), Environment notes (sandbox type, integration prerequisites), Functional setup (master-data preconditions). |
| **Testing Steps** | Numbered, subsectioned manual test scripts: verify permissions; test each new/changed page (with field captions and tooltips to check); test page-extension functionality; test codeunit integrations (scenarios from XML docs). |
| **Known Limitations** | Bullet list of known issues/limitations, or the literal word "None". |
| **Approvals** | Sign-off table `Role \| Name \| Decision \| Date \| Signature` for Product Owner, AL Architect, Client representative. |

---

## Document chain at a glance

```
US (User Story)
  └─► SPEC (Technical Spec) ──► PLAN (Phase Plans, one per phase)
         ├─► ANALYSIS (Feasibility Analysis)
         └─► ARCH (Architecture)
                      │
                      ▼
              CCN (Change Control Note)  ── consolidates US + SPEC + ARCH + ANALYSIS for stakeholder sign-off
                      │
                      ▼
              RN (Release Note)  ── deployment-time summary of what shipped, derived from spec/CCN/merged changes
```

> Note: The `documentation-bc-md-to-docx-converter` skill is a downstream rendering pipeline (markdown → `.docx` via Word templates) and does not define a document type of its own — it is intentionally excluded from this catalogue.
