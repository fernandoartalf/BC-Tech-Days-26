---
id: CCN-001
title: Employee Skill Catalog and Skill Profile Management
customer: BC Tech Days 26 (Demo)
version: "1.0"
status: Pending Approval
dsd_ticket: TBD
user_story: US-001
spec: SPEC-001
architecture: ARCH-001
analysis: ANALYSIS-001
prepared_by: Fernando Artigas Alfonso
date: 2026-06-10
recommendation: GO
label_date: "Date"
label_prepared_by: "Prepared by"
label_dsd_ticket: "DSD ticket"
---

# CCN-001 — Employee Skill Catalog and Skill Profile Management

## Header
<!-- section-key: Header -->

| Field | Value |
|---|---|
| CCN ID | CCN-001 |
| Title | Employee Skill Catalog and Skill Profile Management |
| Customer | BC Tech Days 26 (Demo) |
| DSD Ticket | TBD |
| BC Environment | BC Tech Days 2026 sandbox |
| BC Version Baseline | application 22.0.0.0 / runtime 15.2 |
| Extension Affected | Employee Skill Management (ESM) |
| Source User Story | US-001 |
| Source Spec | SPEC-001 |
| Architecture | ARCH-001 |
| Analysis | ANALYSIS-001 |
| Prepared By | Fernando Artigas Alfonso |
| Date | 2026-06-10 |
| Status | Pending Approval |
| Recommendation | GO |

---

## Business Context
<!-- section-key: BusinessContext -->

**Who:** HR administrators, line managers, and employees of BC Tech Days 2026.

**What:** Introduce a central, auditable skill catalog and an effective-dated employee skill assessment ledger inside Business Central.

**Why:** Skills are currently tracked informally in spreadsheets outside BC — with no shared catalog, no agreed proficiency scale, and no history preservation. When a skill assessment changes, the previous value is overwritten and lost. This blocks consistent competency reporting and auditability.

**Objective:** Deliver a greenfield Business Central extension (Employee Skill Management — ESM) that replaces spreadsheet-based skill tracking with an auditable, effective-dated ledger embedded in the standard Employee Card.

**Functional scope summary:**

| AC | Title | Key behaviour |
|---|---|---|
| AC1 | Skill catalog maintenance | Create/edit/block skills with unique code; deletion blocked when in use |
| AC2 | Employee skill profile maintenance | Add catalog-only skills per employee; current = latest confirmed effective assessment |
| AC3 | Effective-dated skill assessment | Mandatory effective date; "current" = latest Confirmed row on or before work date |
| AC4 | Immutable skill history and auditability | No overwrite/delete of prior entries; read-only history for non-admins |

**Out of scope (this CCN):** Development goals (US-002), performance reviews (US-003), training plans (US-004), reward eligibility (US-005), LMS integration, configurable proficiency scale, assessment correction mechanism, API pages, telemetry.

---

## Proposed Solution
<!-- section-key: ProposedSolution -->

The change introduces a greenfield AL extension with 14 objects across 2 delivery phases. No existing BC standard objects are modified — all touches to Employee Card (Page 5200) are via PageExtension.

### AL Object Inventory

| Category | Count | Object IDs |
|---|---|---|
| Enums | 2 | 51100–51101 |
| Tables (new) | 3 | 51100–51102 |
| Pages (new) | 5 | 51100–51104 |
| Codeunit (new) | 1 | 51100 (5 procedures) |
| Page Extensions (new) | 1 | 51100 |
| Permission Sets (new) | 2 | 51100–51101 |
| **Total** | **14** | ID range consumed: 51100–51104 |

### Key design decisions

| Decision | Choice |
|---|---|
| Proficiency scale | Fixed enum: Beginner / Intermediate / Advanced / Expert (Enum 51100) |
| Who may enter assessments | HR/manager (→ Confirmed) and employee self-service (→ Pending Confirmation) |
| Confirmation workflow | ESM FULL users confirm Pending rows via Confirm action on Employee Skill Profile ListPart |
| Assessment mutability | Append-only ledger — `OnBeforeModify` and `OnBeforeDelete` raise unconditional errors |
| Profile page UX | Inline editable ListPart (no dialog page); Pending rows rendered in Ambiguous (orange) style |
| Current proficiency | On-demand via `GetCurrentProficiency`; filters to Confirmed rows only |

### Delivery phases

| Phase | Scope | Effort |
|---|---|---|
| Phase 1 — Catalog Foundation | Enums 51100/51101; Tables 51100/51101; Pages 51100/51101/51102; Permission Sets 51100/51101 | 5–7 h |
| Phase 2 — Employee Assessments | Table 51102; Codeunit 51100; Pages 51103/51104; PageExtension 51100; permission set updates | 9–13 h |

### Open Questions resolution

| OQ | Status | Resolution |
|---|---|---|
| OQ1 — Proficiency scale | Resolved | Fixed 4-level enum |
| OQ2 — Self-service & confirmation | Resolved | Employee entries start as Pending; ESM FULL users confirm |
| OQ3 — Correction mechanism | Resolved (deferred) | No correction in v1; counter-entry pattern planned for future story |
| OQ4 — Profile page UX | Resolved | Inline editable ListPart |

---

## Architecture Solution
<!-- section-key: Architecture -->

Architecture document: ARCH-001 — see [openspec/architecture/ARCH-001-employee-skill-catalog-and-profile.architecture.md](../../openspec/architecture/ARCH-001-employee-skill-catalog-and-profile.architecture.md)

**Architectural style:** Master-data / append-only ledger (analogous to G/L Entry, Item Ledger Entry). Business logic concentrated in Codeunit 51100 "Skill Mgt." (codeunit-as-service pattern). Pages are thin and delegate all writes to the codeunit.

**ADR summary:**

| ADR | Decision |
|---|---|
| ADR-1 | Table 51102 append-only: unconditional errors in `OnBeforeModify` and `OnBeforeDelete` |
| ADR-2 | Current proficiency computed on demand via `GetCurrentProficiency`; no FlowField or denormalised store |
| ADR-3 | `ConfirmAssessment` uses `ModifyAll` on PK to bypass `OnBeforeModify`; procedure is `internal` to Codeunit 51100 |
| ADR-4 | Inline editable ListPart with `OnBeforeInsert` permission-driven `InitialStatus`; Pending rows styled Ambiguous |
| ADR-5 | Two standard permission sets (ESM BASIC / ESM FULL) — no custom user setup table |

**Standard BC objects touched:**

| Object | Touched by | Nature |
|---|---|---|
| Employee Card (Page 5200) | PageExtension 51100 | One FactBox + one navigation action added; no fields or triggers modified |
| Employee (Table 5200) | Table 51102 FK | `TableRelation: Employee.No.` on Field 2; no triggers or fields on Table 5200 modified |

**Key constraints:** C-5 — runtime permission guard absent from `ConfirmAssessment` (mandatory review item); C-7 — concurrent confirmation race condition (acceptable for v1).

---

## Feasibility Analysis
<!-- section-key: FeasibilityAnalysis -->

Analysis document: ANALYSIS-001 — see [openspec/analysis/ANALYSIS-001-employee-skill-catalog-and-profile.analysis.md](../../openspec/analysis/ANALYSIS-001-employee-skill-catalog-and-profile.analysis.md)

**Overall risk rating: LOW–MEDIUM**

### SWOT

**Strengths**
- Greenfield extension — zero conflict with existing objects; full ID range available
- All 4 Open Questions resolved before implementation; no unresolved functional unknowns
- Master-data / ledger pattern is standard in BC; familiar to any BC developer
- Phase 1 independently deployable; unblocks US-002 through US-005 immediately

**Weaknesses**
- `ConfirmAssessment` uses a non-standard `ModifyAll` bypass (ARCH-001 ADR-3) — requires explicit developer awareness
- No correction mechanism in v1 — incorrectly confirmed entries are permanent
- Runtime permission guard absent from `ConfirmAssessment` at codeunit level (flagged as mandatory review item)
- No automated test codeunits in scope

**Opportunities**
- Foundation for 4 downstream stories (US-002 to US-005)
- RapidStart-ready catalog tables for fast customer onboarding
- Natural telemetry target for Application Insights in a follow-on story

**Threats**
- Cost of not implementing: skills remain in spreadsheets; US-002 to US-005 blocked entirely
- Scope creep post-go-live from HR stakeholders; controlled by CCN process
- BC runtime version mismatch could invalidate ADR-3 assumptions (R-01, mitigated by sandbox verification)

### Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | `ConfirmAssessment` `ModifyAll` bypass behaves unexpectedly on target BC runtime | Low | High | Verify on target sandbox before Phase 2 merge |
| R-02 | HR users demand correction mechanism post-go-live | Medium | Medium | Brief HR users pre-go-live; correction-entry pattern logged as future story |
| R-03 | Missing runtime permission guard in `ConfirmAssessment` allows privilege escalation | Low | Medium | Blocking AL Reviewer comment; add `UserHasESMFullPermission()` guard in procedure |
| R-04 | `GetCurrentProficiency` performance at scale (>200 entries per employee+skill) | Low | Low | `SetLoadFields` + secondary key; bulk-import out of scope for v1 |
| R-05 | Phase 1 delay blocks US-002 spec work | Low | Medium | Phase 1 is 5–7 h; merge independently before US-002 development |
| R-06 | Concurrent confirmation audit stamp discrepancy | Low | Low | Acceptable for v1; `LockTable` guard deferred |

---

## Time Estimate
<!-- section-key: TimeEstimate -->

**Rate: 100 EUR/h · 1 developer · 8 h/day.** 20% contingency applied to Expected total.

### Hours by phase

| Phase | Optimistic | Expected | Pessimistic |
|---|---|---|---|
| Phase 1 — Catalog Foundation | 4.5 h | 6 h | 7 h |
| Phase 2 — Employee Assessments | 8.5 h | 11 h | 13 h |
| Code review (1 round) | 1 h | 1.5 h | 2 h |
| Integration testing on sandbox | 1 h | 1.5 h | 2 h |
| Subtotal | 15 h | 20 h | 24 h |
| Contingency (20% on Expected) | — | 4 h | — |
| **Total** | **15 h** | **24 h** | **24 h** |

### Calendar duration

| Scenario | Hours | Working days |
|---|---|---|
| Optimistic | 15 h | 2 days |
| Expected (with contingency) | 24 h | 3 days |
| Pessimistic | 24 h | 3 days |

### Cost estimate

| Scenario | Hours | Total (EUR) |
|---|---|---|
| Optimistic | 15 h | 1,500 EUR |
| Expected | 24 h | 2,400 EUR |
| Pessimistic | 24 h | 2,400 EUR |

*Excludes VAT, project management, deployment coordination, and user training. Assisted go-live: +1–2 h (100–200 EUR) not included above.*

---

## Testing Setup
<!-- section-key: TestingSetup -->

| Phase | Test scope | Exit gate |
|---|---|---|
| Phase 1 | Skill/Category CRUD; delete guards (blocked skill, skill with assessments, category with skills); permission set read-only verification | All Phase 1 AC1 tests green on sandbox |
| Phase 2 | `AddSkillAssessment` inserts (Confirmed + Pending paths); `GetCurrentProficiency` effective-date logic; immutability errors on modify/delete; `ConfirmAssessment` status transition; Employee Card FactBox and Skill History page; ESM BASIC / FULL role verification | All Phase 2 AC2–AC4 tests green; ESM FULL permission guard present in codeunit |

---

## Testing Steps
<!-- section-key: TestingSteps -->

The following acceptance steps are to be executed by the Customer on a BC sandbox with representative employee and skill catalog data.

1. **AC1 — Skill catalog:** Create a Skill Category and 3 Skills referencing it. Edit a Skill description. Block a Skill. Attempt to delete the blocked Skill — verify it can be deleted (Blocked ≠ In Use). Attempt to delete a Skill with an employee assessment — verify deletion is blocked with an error message.
2. **AC2 — Employee profile (HR path):** Open an Employee Card as an ESM FULL user. In the Skill Profile FactBox, enter a new row (Skill Code, Proficiency Level, Effective Date). Verify the row appears without orange styling (Status = Confirmed).
3. **AC2 — Employee profile (self-service path):** Open an Employee Card as an ESM BASIC user. Enter a new row. Verify the row appears in orange (Status = Pending Confirmation). Verify the Confirm action is not visible.
4. **AC2 — Confirmation:** Log in as an ESM FULL user. Select the orange Pending row. Invoke the Confirm action. Verify the row is no longer orange and Status shows Confirmed.
5. **AC3 — Effective date:** Add two assessments for the same employee + skill with different effective dates (one past, one future). Call the Skill History page and verify both rows are present. Verify the current proficiency in the FactBox matches the most recent Confirmed row on or before today.
6. **AC4 — Immutability:** Attempt to edit any field of an existing assessment row in the Skill History page — verify the page is read-only. Verify no Delete action is available on the history page.

---

## Recommendation
<!-- section-key: Recommendation -->

### GO — unconditional

SPEC-001 is technically sound, all 4 Open Questions are resolved, and the design is 100% additive (no existing BC objects modified). At an expected 24 h / 2,400 EUR it is a well-scoped, low-risk delivery that directly unblocks four subsequent user stories.

**Non-blocking advisories before developer handoff:**

1. Add a runtime `UserHasESMFullPermission()` guard as the first statement of `ConfirmAssessment` (ARCH-001 C-5) — mandatory AL Reviewer check.
2. Confirm target sandbox matches `application 22.0.0.0 / runtime 15.2` declared in `app.json`.
3. Define at least one test codeunit per phase as a merge pre-condition.
4. Reserve initial skill catalog data population as a separate go-live activity (not in the estimate).

---

## Approvals
<!-- section-key: Approvals -->

| Role | Name | Decision | Date |
|---|---|---|---|
| Project Sponsor | | Pending | |
| Technical Lead | | Pending | |
| AL Analyst | Fernando Artigas Alfonso | GO | 2026-06-10 |


| Field | Value |
|---|---|
| **CCN Nr.** | CCN-001 |
| **Spec Reference** | [SPEC-001](../../openspec/specs/employee-skill-catalog-and-profile.spec.md) |
| **Architecture Reference** | [ARCH-001](../../openspec/architecture/ARCH-001-employee-skill-catalog-and-profile.architecture.md) |
| **User Story** | [US-001](../../openspec/user-stories/US-001-employee-skill-catalog-and-profile.userstory.md) |
| **Module** | Human Resources |
| **Priority** | High |
| **Date** | 2026-06-10 |
| **Prepared By** | AL Analyst |
| **Rate Assumption** | 100 EUR/h · 1 developer · 8 h/day |
| **Status** | Pending Approval |

---

## Change Request Summary

This change request introduces a new **Employee Skill Management (ESM)** extension for Business Central (app "Employee Skill Management", publisher "BC Tech Days 2026"). It replaces the current spreadsheet-based competency tracking with an auditable, effective-dated skill ledger embedded in the standard Employee Card.

The extension delivers:

1. A **central skill catalog** (Skill + Skill Category tables) with a four-level proficiency scale (Beginner → Expert).
2. An **immutable employee skill assessment ledger** that preserves every assessment entry as an append-only record.
3. A **confirmation workflow** allowing employees to propose their own assessments, which only become authoritative after an HR/manager confirms them.
4. An **inline skill profile FactBox** on the Employee Card and a read-only assessment history page.
5. Two **permission sets** (ESM BASIC — view; ESM FULL — view + add + confirm).

The change is a greenfield extension. No existing BC standard tables, pages, or codeunits are modified; the Employee Card (Page 5200) is extended only via a PageExtension.

---

## Scope & Impact Analysis

### AL Object Inventory

| Category | Count | Object IDs |
|---|---|---|
| Enums | 2 | 51100–51101 |
| Tables (new) | 3 | 51100–51102 |
| Pages (new) | 5 | 51100–51104 |
| Codeunit (new) | 1 | 51100 (5 procedures) |
| Page Extensions (new) | 1 | 51100 |
| Permission Sets (new) | 2 | 51100–51101 |
| **Total AL objects** | **14** | ID range consumed: 51100–51104 (5 IDs), 51150 remaining unused |

### Modules Impacted

| Module | Impact | Nature |
|---|---|---|
| Human Resources | Primary | Employee Card extended; new skill objects alongside HR tables |
| Security / Role Center | Minor | Two new permission sets; must be assigned during deployment |
| US-002 (Development Goals) | Downstream dependency | Phase 1 enums and Skill table become a public contract that US-002 depends on |

### Integration Points

- **Standard Employee table (5200)**: referenced as FK only; no trigger or field changes.
- **Standard Employee Card page (5200)**: extended via PageExtension 51100; one FactBox and one action added.
- **No external API, no OData page, no Dataverse connector** in this scope.

### Estimated Lines of AL Code

| Component | Estimated LoC |
|---|---|
| Enums 51100–51101 | ~20 |
| Tables 51100–51102 | ~120 |
| Pages 51100–51104 | ~200 |
| Codeunit 51100 | ~150 |
| PageExtension 51100 | ~30 |
| Permission Sets 51100–51101 | ~30 |
| **Total** | **~550 LoC** |

---

## Time Estimation

### Phase-level breakdown

| Phase | Tasks | Optimistic | Expected | Pessimistic |
|---|---|---|---|---|
| **Phase 1** — Catalog Foundation | Enum 51100/51101; Tables 51100/51101 with delete guards; Pages 51100/51101/51102; Permission Sets 51100/51101 | 4.5 h | 6 h | 7 h |
| **Phase 2** — Employee Assessments | Table 51102 (10 fields, 3 triggers, secondary key); Codeunit 51100 (AddSkillAssessment, GetCurrentProficiency, ConfirmAssessment bypass, BlockSkill, CanDeleteSkill); Pages 51103/51104 (inline editable + StyleExpr + Confirm action); PageExtension 51100; Permission set updates | 8.5 h | 11 h | 13 h |
| **Code review** | AL Reviewer pass (1 round) | 1 h | 1.5 h | 2 h |
| **Integration test on sandbox** | HR user + employee self-service flows; ESM BASIC / FULL permission checks | 1 h | 1.5 h | 2 h |
| **Total** | | **15 h** | **20 h** | **24 h** |

### Contingency rationale

- **Pessimistic +20%** over expected accounts for: the non-trivial `ConfirmAssessment` `ModifyAll`-bypass pattern (ARCH-001 ADR-3) — no standard pattern in existing codebase; inline-editable ListPart with `StyleExpr` and permission-driven `InitialStatus` requiring edge-case testing; first implementation of ESM permission sets requiring sandbox deployment to verify.
- No allowance for requirements change — scope is frozen at SPEC-001 draft.

### Calendar duration (1 developer · 8 h/day)

| Scenario | Hours | Calendar days |
|---|---|---|
| Optimistic | 15 h | 2 days |
| Expected | 20 h | 2.5 days |
| Pessimistic | 24 h | 3 days |

---

## Cost Estimation

**Assumption**: 100 EUR/h · 1 developer. All figures exclude VAT, project management overhead, and deployment coordination unless stated.

| Cost component | Optimistic | Expected | Pessimistic |
|---|---|---|---|
| Development (Phase 1 + Phase 2) | 1,300 EUR | 1,700 EUR | 2,000 EUR |
| Code review | 100 EUR | 150 EUR | 200 EUR |
| Integration testing on sandbox | 100 EUR | 150 EUR | 200 EUR |
| **Total implementation cost** | **1,500 EUR** | **2,000 EUR** | **2,400 EUR** |

*Note: deployment to production environment (app package upload, permission set assignment, initial skill catalog data entry) is not included in the above. Estimate an additional 1–2 h (100–200 EUR) for assisted go-live.*

---

## SWOT Analysis

### Strengths

- **Aligns with BC standard patterns**: the master-data / append-only ledger approach mirrors how standard BC modules (G/L Entry, Item Ledger Entry) handle transactional history — familiar to any BC developer and to standard BC upgrade tooling.
- **Greenfield extension**: no existing objects to conflict with; the implementation is unconstrained by legacy choices. ID range 51100–51149 is fully available.
- **Scope is tightly controlled**: all four Open Questions have been resolved before implementation begins. There are no unresolved functional unknowns.
- **Confirmation workflow adds immediate business value**: the two-tier insert model (employee proposes → HR/manager confirms) meets real-world HR governance requirements without requiring a bespoke workflow engine.
- **Stable contract for downstream stories**: Phase 1 delivers the Skill catalog (enums + tables) as a public contract. US-002 through US-005 can begin their spec work immediately after Phase 1 merges.

### Weaknesses

- **ConfirmAssessment bypass is non-standard**: using `ModifyAll` on the primary key to circumvent `OnBeforeModify` is a deliberate workaround (ARCH-001 ADR-3). It is correct and documented, but it requires a developer who understands AL trigger execution order and must be explicitly called out in code review.
- **No correction mechanism in v1**: an incorrectly entered and confirmed assessment is permanent. This is an accepted constraint (SPEC §2.2 OQ3) but may generate pushback from HR users after go-live when they encounter their first data entry error.
- **Permission check for ConfirmAssessment is UI-only at page level** (ARCH-001 C-5): a developer bypassing the page can call the codeunit without an ESM FULL check. A runtime guard inside the procedure is flagged as a mandatory review item but is not yet in the spec.
- **~550 LoC is non-trivial for a medium-complexity extension**: the codeunit alone has 5 distinct procedures including one with a non-obvious bypass pattern. Test coverage is outlined but not yet formalized in test codeunits.

### Opportunities

- **Foundation for four subsequent user stories** (US-002 goals, US-003 performance review, US-004 training, US-005 reward eligibility): a well-built Phase 1 multiplies in value across the full backlog.
- **Reusable `UserHasESMFullPermission` helper**: generalises to any future ESM feature requiring role distinction without adding a new setup table.
- **RapidStart-ready catalog tables**: the Skill and Skill Category tables can be exported as configuration packages, enabling fast customer onboarding with pre-populated skill catalogs.
- **Natural telemetry candidate**: the `AddSkillAssessment` and `ConfirmAssessment` call paths are high-value business events for Application Insights instrumentation in a follow-on story using the `bc-telemetry-generator` skill.

### Threats

- **BC runtime version dependencies**: the extension targets runtime 15.2 (BC 22). If the BC Tech Days 2026 environment is on a different minor version, `NoImplicitWith` behavior or `ModifyAll` trigger semantics might differ from documented behavior. **Mitigation**: verify BC version on target sandbox before Phase 2 development.
- **Scope creep from HR stakeholders**: once employees can see the inline skill profile FactBox, stakeholders frequently request additions (bulk import, skill gap report, email notifications) before the core story is signed off. **Mitigation**: CCN approval process limits scope to SPEC-001; any new request requires a separate CCN.
- **Concurrent confirmation race condition** (ARCH-001 C-7): two managers confirming the same Pending row simultaneously will both succeed; only the audit stamp of the second write survives. Acceptable for v1 but a potential audit compliance issue in regulated environments. **Mitigation**: documented as a known limitation; a `LockTable` guard is a low-cost future fix.
- **Employee "orphan" rows on Employee deletion** (ARCH-001 C-6): no `OnBeforeDelete` subscriber exists on Employee (5200) for this extension. If an employee record is deleted, their skill assessments become orphaned. **Mitigation**: documented as a known limitation; future story can add a subscriber.

---

## Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | `ConfirmAssessment` bypass (`ModifyAll`) behaves differently on target BC runtime version — triggers fire unexpectedly or not at all | Low | High | Verify BC platform trigger behavior on target sandbox before merging Phase 2; reference Microsoft Learn documentation in ARCH-001 ADR-3 |
| R-02 | HR users encounter first data entry error post-go-live (wrong proficiency, wrong skill) and demand a correction path — escalates to scope change | Medium | Medium | Brief HR users on the no-correction policy before go-live; document C-3 in user training material; keep the correction-entry pattern design note in ARCH-001 to accelerate future delivery |
| R-03 | ESM FULL permission check absent at codeunit runtime level allows privilege escalation by a peer extension | Low | Medium | AL Reviewer must verify a runtime `UserHasESMFullPermission()` guard is added to `ConfirmAssessment` procedure (ARCH-001 C-5); treat as a blocking review comment |
| R-04 | `GetCurrentProficiency` performance degrades if a single employee accumulates >200 confirmed assessments for the same skill (e.g. from a legacy data import) | Low | Low | `SetLoadFields` + secondary key limits the query; bulk-import is out of scope for v1; document threshold in ARCH-001 C-4 |
| R-05 | Phase 1 delayed — US-002 spec work blocked because Skill catalog contract is not yet stable | Low | Medium | Phase 1 is 5–7 h; complete it first and merge as a standalone deployable unit; do not wait for Phase 2 to begin US-002 design |
| R-06 | Concurrent manager confirmation (ARCH-001 C-7) causes audit record discrepancy in a regulated environment | Low | Low (v1 context) | Accepted for BC Tech Days demo context; `LockTable` guard can be added in < 1 h if compliance requirement surfaces |

---

## Feasibility Recommendation

**GO**

SPEC-001 is technically sound, functionally complete (all 4 Open Questions resolved), and consistent with BC SaaS extension best practices. The implementation scope is bounded and well-understood — 14 AL objects across a 2-phase delivery of 15–24 hours (expected: 20 h, 2,000 EUR at the stated rate).

The most material risk is the `ConfirmAssessment` bypass pattern (R-01, R-03), which is documented and mitigated by the architectural ADRs and a mandatory AL Reviewer check. No risk in the register rises to a level that justifies delaying or descoping this change.

**Non-blocking advisories for the Architect to address before handoff to the Developer:**

1. Add a runtime `UserHasESMFullPermission()` guard as the first statement in `ConfirmAssessment` — this was flagged as a mandatory review item in ARCH-001 C-5 and should be codified in the spec before development begins.
2. Confirm the target BC sandbox version matches `application: 22.0.0.0` / `runtime: 15.2` declared in `app.json` to rule out R-01.
3. Consider formalising at least one test codeunit per phase as a pre-condition for merge; the testing strategy in SPEC-001 §10 describes scenarios but no test objects are defined.

---

## Approval

| Role | Name | Decision | Date |
|---|---|---|---|
| Project Sponsor | | Pending | |
| Technical Lead | | Pending | |
| AL Analyst | Fernando Artigas Alfonso | GO | 2026-06-10 |

---

## Notes

- **Rate**: 100 EUR/h as specified. Figures exclude VAT and do not include project management, deployment coordination, or user training.
- **Scope freeze**: cost and time estimates are valid only for the scope defined in SPEC-001 (14 objects, 2 phases). Any scope change requires a CCN amendment.
- **Next action**: Architect to review the three non-blocking advisories above, update SPEC-001 and ARCH-001 as appropriate, then hand off Phase 1 to the AL Developer.
- **Downstream stories**: US-002 through US-005 are each subject to their own CCN. This CCN covers US-001 only.
