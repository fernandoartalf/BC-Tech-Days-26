---
id: ANALYSIS-001
title: Feasibility Analysis — Employee Skill Catalog and Skill Profile Management
customer: BC Tech Days 26 (Demo)
version: 1.0.0
status: draft
spec: SPEC-001
user_story: US-001
ccn: CCN-001
prepared_by: Fernando Artigas Alfonso
date: 2026-06-10
recommendation: GO
related_docs:
  - openspec/specs/employee-skill-catalog-and-profile.spec.md
  - openspec/user-stories/US-001-employee-skill-catalog-and-profile.userstory.md
  - openspec/architecture/ARCH-001-employee-skill-catalog-and-profile.architecture.md
  - docs/ccn/CCN-001-employee-skill-catalog-and-profile.md
---

# ANALYSIS-001 — Feasibility Analysis for SPEC-001

This document is the AL Analyst's working artefact backing [CCN-001](../../docs/ccn/CCN-001-employee-skill-catalog-and-profile.md). It provides the formal feasibility decision — effort, cost, SWOT, and risk register — for the change described in [SPEC-001](../specs/employee-skill-catalog-and-profile.spec.md), originating from [US-001](../user-stories/US-001-employee-skill-catalog-and-profile.userstory.md) and supported by [ARCH-001](../architecture/ARCH-001-employee-skill-catalog-and-profile.architecture.md).

---

## References
<!-- section-key: References -->

| Artefact | Path | Status |
|---|---|---|
| User Story | `openspec/user-stories/US-001-employee-skill-catalog-and-profile.userstory.md` | Approved (2026-06-10) |
| Technical Spec | `openspec/specs/employee-skill-catalog-and-profile.spec.md` | Draft |
| Architecture | `openspec/architecture/ARCH-001-employee-skill-catalog-and-profile.architecture.md` | Draft |
| Phase 1 Plan | `openspec/plans/SPEC-001-phase-1-catalog-foundation.plan.md` | Draft |
| Phase 2 Plan | `openspec/plans/SPEC-001-phase-2-employee-assessments.plan.md` | Draft |
| CCN | `docs/ccn/CCN-001-employee-skill-catalog-and-profile.md` | Pending Approval |

---

## Change summary
<!-- section-key: ChangeSummary -->

**New objects introduced (greenfield — no prior ESM objects exist in the codebase):**

- Enum 51100 `Skill Proficiency Level` (Beginner → Expert, 4 values + Unassigned)
- Enum 51101 `Skill Assessment Status` (Confirmed / Pending Confirmation)
- Table 51100 `Skill` — catalog master with delete guard
- Table 51101 `Skill Category` — optional grouping with delete guard
- Table 51102 `Employee Skill Assessment` — append-only assessment ledger (10 fields, unconditional modify/delete errors)
- Page 51100 `Skill List`, Page 51101 `Skill Card`, Page 51102 `Skill Category List`
- Page 51103 `Employee Skill Profile` (inline editable ListPart with confirmation workflow)
- Page 51104 `Employee Skill Assessment History` (read-only list)
- Codeunit 51100 `Skill Mgt.` — 5 procedures including the `ConfirmAssessment` ModifyAll bypass
- PageExtension 51100 `Employee Card ESM Ext` — FactBox + navigation action on Employee Card (5200)
- Permission Set 51100 `ESM BASIC` (read-only), Permission Set 51101 `ESM FULL` (read + insert)

**Existing objects modified:**

- None. All touches to standard Employee Card (Page 5200) are via PageExtension only.

**Zero legacy objects touched; no data migration required; no external API endpoints added.**

**Open Questions status:** All 4 Open Questions from US-001 resolved before spec was baselined — proficiency scale (OQ1), self-service + confirmation workflow (OQ2), correction mechanism deferred to v2 (OQ3), inline editable ListPart chosen (OQ4). No unresolved functional unknowns.

---

## Scope & impact
<!-- section-key: ScopeAndImpact -->

| Dimension | Value |
|---|---|
| New AL objects | 14 (2 enums, 3 tables, 5 pages, 1 codeunit, 1 page extension, 2 permission sets) |
| Existing AL objects modified | 0 |
| Standard BC objects touched | Employee Card (Page 5200) — extension only, no field or trigger changes |
| BC modules impacted | Human Resources (primary); Security / Role Center (permission sets) |
| External dependencies added | None |
| Object IDs consumed | 51100–51104 (5 IDs from the 51100–51149 range; 44 IDs remain) |
| Net new AL LoC estimate | ~550 |
| Deployment complexity | Low — .app package upload + permission set assignment |
| Open Questions resolution | All 4 resolved (see US-001 §Open Questions) |
| Downstream stories unblocked | US-002 through US-005 depend on Phase 1 Skill catalog contract |

---

## Time estimate
<!-- section-key: TimeEstimate -->

Rate: **100 EUR/h**, 1 AL developer, 8 productive hours/day. A 20% contingency is applied to the Expected total to cover the non-standard `ConfirmAssessment` bypass pattern, inline-editable ListPart edge cases, and permission-set sandbox verification — areas without precedent in the current codebase.

### Per-phase hours

| Phase | Tasks | Optimistic (h) | Expected (h) | Pessimistic (h) |
|---|---|---|---|---|
| Phase 1 — Catalog Foundation | Enum 51100/51101; Tables 51100/51101 + delete guards; Pages 51100/51101/51102; Permission Sets 51100/51101 | 4.5 | 6 | 7 |
| Phase 2 — Employee Assessments | Table 51102 (10 fields, 3 triggers, secondary key); Codeunit 51100 (5 procedures + ModifyAll bypass); Pages 51103/51104 (StyleExpr, Confirm action, permission guard); PageExtension 51100; permission set updates | 8.5 | 11 | 13 |
| Code review (1 round) | AL Reviewer — naming, performance, ARCH-001 ADRs compliance, C-5 runtime guard check | 1 | 1.5 | 2 |
| Integration test on sandbox | HR user + employee self-service flows; ESM BASIC / FULL permission verification | 1 | 1.5 | 2 |
| **Subtotal** | | **15** | **20** | **24** |
| Contingency (20 % on Expected) | | — | **4** | — |
| **Total** | | **15 h** | **24 h** | **24 h** |

> *Pessimistic already includes contingency implicitly; the 20% contingency is applied only to Expected. Optimistic scenario assumes no review cycles and clean first-pass sandbox validation.*

### Calendar duration

| Scenario | Hours | Working days (8 h/day) | Wall-clock |
|---|---|---|---|
| Optimistic | 15 h | 2 days | ~1 week |
| Expected (with contingency) | 24 h | 3 days | ~1 week |
| Pessimistic | 24 h | 3 days | ~1 week |

---

## Cost estimate
<!-- section-key: CostEstimate -->

**Rate: 100 EUR/h** (as specified by the project sponsor). Figures exclude VAT, project management overhead, deployment coordination, and user training unless stated.

### Cost by scenario

| Scenario | Hours | Total cost (EUR) |
|---|---|---|
| Optimistic | 15 h | 1,500 EUR |
| Expected (with contingency) | 24 h | 2,400 EUR |
| Pessimistic | 24 h | 2,400 EUR |

### Per-phase cost breakdown (Expected scenario)

| Phase | Expected hours | Cost (EUR) |
|---|---|---|
| Phase 1 — Catalog Foundation | 6 h | 600 EUR |
| Phase 2 — Employee Assessments | 11 h | 1,100 EUR |
| Code review | 1.5 h | 150 EUR |
| Integration testing | 1.5 h | 150 EUR |
| Contingency (20%) | 4 h | 400 EUR |
| **Total** | **24 h** | **2,400 EUR** |

*Assisted go-live (app deployment, permission set assignment, initial catalog data entry): additional 1–2 h (100–200 EUR) not included above.*

### Assumptions

1. **Developer familiarity**: 1 experienced AL developer familiar with BC 22 table trigger mechanics and permission set design. No ramp-up time included.
2. **Testing approach**: manual integration testing on a BC 22 SaaS sandbox with representative employee and skill data. No automated test codeunits are scoped in this CCN (flagged as non-blocking advisory).
3. **Scope freeze**: estimates are valid only for SPEC-001 as baselined. Any scope change requires a CCN amendment.
4. **Exclusions**: translation (XLF), AppSource packaging, any external system integration, user training documentation, and production deployment coordination are excluded.
5. **Architect review cycles**: one review cycle per phase is included in the code-review line. A second cycle would add approximately 1–2 h per phase.
6. **BC platform**: `application 22.0.0.0`, `runtime 15.2`, `NoImplicitWith` enabled — verified against `app.json`. The `ModifyAll` trigger-bypass behavior (ARCH-001 ADR-3) is a documented AL platform contract on this runtime.

---

## SWOT analysis
<!-- section-key: Swot -->

### Strengths

- **Master-data / append-only ledger is a proven BC pattern**: mirrors Item Ledger Entry and G/L Entry; any BC developer can maintain the design. Reduces onboarding risk for future team members.
- **Fully greenfield**: no existing ESM objects exist in the repository — the implementation is unconstrained by legacy technical debt. ID range 51100–51149 is entirely free.
- **All Open Questions resolved before implementation**: SPEC-001 has zero unresolved functional unknowns. The confirmation workflow (OQ2) and inline-editable UX (OQ4) are fully specified. Estimation uncertainty is lower than average for a medium-complexity story.
- **Phased deliverability**: Phase 1 (catalog + enums) is independently deployable and unblocks US-002 through US-005. The business receives value in ~2 days even if Phase 2 is delayed.
- **Zero standard object modifications**: the extension-only approach (PageExtension on Employee Card) eliminates the risk of breaking standard BC functionality during BC version upgrades.

### Weaknesses

- **`ConfirmAssessment` uses a non-standard write path** (`ModifyAll` to bypass `OnBeforeModify`): correct and documented (ARCH-001 ADR-3), but unusual enough that a future developer unfamiliar with the design could inadvertently break it by adding a second immutability check or removing the bypass.
- **No correction mechanism in v1**: an incorrectly confirmed assessment is permanent. This is an accepted product decision (OQ3) but is likely to generate post-go-live support requests when the first data entry mistake surfaces.
- **No automated test codeunits are defined**: the testing strategy in SPEC-001 §10 is narrative; no test codeunit objects are in scope. Manual sandbox testing reduces regression confidence for follow-on stories that depend on Codeunit 51100's public API.
- **`GetCurrentProficiency` performance is untested at scale**: the secondary-key + `SetLoadFields` pattern is sound for typical HR headcounts, but no load test is planned. Above approximately 200 confirmed entries per employee+skill the query behavior is an open question (ARCH-001 C-4).
- **Runtime permission guard absent from `ConfirmAssessment`**: the ESM FULL check is currently only at the page-action level (ARCH-001 C-5). A peer extension or test codeunit can invoke `ConfirmAssessment` without authorization. Flagged as a mandatory review item.

### Opportunities

- **Foundation multiplier for 4 downstream stories**: US-002 (goals), US-003 (performance review), US-004 (training), US-005 (reward eligibility) all depend on the Skill catalog and `GetCurrentProficiency`. A well-implemented Phase 1 directly reduces the effort of those stories.
- **RapidStart catalog portability**: Tables 51100 and 51101 are clean master-data tables with no blobs or system-computed mandatory fields — ideal for configuration packages, enabling rapid onboarding of new customers with pre-populated skill catalogs.
- **Reusable `UserHasESMFullPermission` helper**: if added as a named procedure in Codeunit 51100 (non-blocking advisory), it becomes a reusable role-check utility for all future ESM pages without requiring a custom setup table.
- **Natural Application Insights telemetry target**: `AddSkillAssessment` and `ConfirmAssessment` are high-value business events for workforce analytics. The `bc-telemetry-generator` skill can instrument them in a follow-on story at low marginal cost.
- **Demonstrates SDD methodology end-to-end**: this is the first story to go through the full US → Spec → Architecture → Analysis → CCN pipeline for this project. A successful delivery validates the workflow for US-002 through US-005.

### Threats

- **Cost of not implementing** (do-nothing baseline): skill data remains fragmented across spreadsheets and manager notes, incomparable across teams, and invisible to any BC reporting. US-002 through US-005 cannot be delivered without the catalog and ledger foundation — deferral blocks the entire HR upskilling roadmap, not just this story.
- **Scope creep post-go-live**: once employees can see the inline skill profile FactBox, stakeholders frequently request near-scope additions (bulk skill import, skill gap reports, manager dashboard, email notifications on pending confirmation) before the core story is signed off. Each request requires a separate CCN; the CCN process is the primary mitigation.
- **BC platform version drift**: the target sandbox version must be confirmed as BC application 22 / runtime 15.2. A mismatch (particularly on `ModifyAll` trigger semantics or `NoImplicitWith` enforcement) could invalidate Phase 2 assumptions and require rework.
- **Orphan skill assessments on employee deletion** (ARCH-001 C-6): if an employee record is deleted in BC, their `Employee Skill Assessment` rows become orphaned. Standard BC does not notify extensions of Employee deletion. Acceptable for v1 but a potential data quality issue in environments with high employee turnover.
- **Concurrent manager confirmation audit gap** (ARCH-001 C-7): two managers confirming the same Pending row simultaneously will both succeed; only the last `Confirmed By` / `Confirmed DateTime` survives. A minor audit discrepancy — acceptable for a demo/hackathon context but a compliance risk in regulated environments.

---

## Risk assessment
<!-- section-key: RiskAssessment -->

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | `ConfirmAssessment` `ModifyAll` bypass behaves unexpectedly on target BC runtime (triggers fire or fail to fire) | Low | High | Verify BC platform trigger behavior on target sandbox before merging Phase 2; reference ADR-3 in ARCH-001; include an explicit test case in Phase 2 integration testing |
| R-02 | HR users encounter first data entry error post-go-live and demand a correction path, escalating to scope change | Medium | Medium | Brief HR users on the no-correction policy before go-live; document C-3 in ARCH-001 as known limitation; keep the correction-entry pattern design note available for US-006 |
| R-03 | `ConfirmAssessment` missing runtime permission guard (ARCH-001 C-5) allows privilege escalation by a peer extension or test codeunit | Low | Medium | Add `UserHasESMFullPermission()` runtime guard as the first statement of `ConfirmAssessment`; treat as a **blocking AL Reviewer comment** before Phase 2 merge |
| R-04 | `GetCurrentProficiency` degrades above ~200 confirmed entries per employee+skill (e.g. after bulk data import) | Low | Low | `SetLoadFields` + secondary key limits the query; bulk import is explicitly out of scope for v1; document threshold in ARCH-001 C-4 |
| R-05 | Phase 1 delay blocks US-002 spec work because the Skill catalog contract is not yet stable | Low | Medium | Phase 1 is 5–7 h and independently deployable; complete and merge Phase 1 before starting US-002 development design |
| R-06 | Concurrent manager confirmation produces audit discrepancy (ARCH-001 C-7) | Low | Low | Acceptable for BC Tech Days demo context; a `LockTable` guard can be added in <1 h if compliance requirement surfaces in a regulated go-live |
| R-07 | BC sandbox version does not match `application 22.0.0.0` / `runtime 15.2` declared in `app.json` | Low | Medium | Confirm sandbox version before Phase 1 development begins; if mismatch, update `app.json` and re-validate ARCH-001 ADR-3 assumptions |

**Overall risk rating: LOW–MEDIUM**

The only High-Impact risk (R-01) has Low Likelihood and a clear in-phase mitigation (sandbox verification + targeted test case). No risk combination reaches Medium–High.

---

## Feasibility recommendation
<!-- section-key: FeasibilityRecommendation -->

### **GO** — unconditional

SPEC-001 is technically sound, functionally complete with all four Open Questions resolved, and architecturally consistent with BC SaaS extension best practices. The implementation is 100% additive — no existing objects are modified — which means it carries no regression risk for the standard BC HR module. At an expected 24 h / 2,400 EUR it is a well-scoped, low-risk delivery that directly unblocks four subsequent user stories (US-002 through US-005) and eliminates a material operational pain point (skill data fragmented in spreadsheets outside BC).

The most material technical complexity — the `ConfirmAssessment` `ModifyAll`-bypass pattern — is fully documented in ARCH-001 ADR-3 and mitigated by a mandatory AL Reviewer check. No risk in the register rises to a level that justifies delaying or descoping this change.

### Non-blocking advisories at kick-off

1. **Add runtime `UserHasESMFullPermission()` guard to `ConfirmAssessment`** (ARCH-001 C-5) — codify this in SPEC-001 §4 before Phase 2 development begins; treat as a blocking AL Reviewer comment if absent at merge.
2. **Confirm target sandbox BC version** matches `application 22.0.0.0` / `runtime 15.2` in `app.json` before Phase 1 development begins (R-07).
3. **Define at least one test codeunit per phase** as a merge pre-condition (e.g. `Codeunit 51110 ESM Phase 1 Tests`, `Codeunit 51111 ESM Phase 2 Tests`) — the `bc-test-codeunit-generator` skill can scaffold these from SPEC-001 §10.
4. **Reserve the Skill catalog population task** (initial seed data for Skill Category + Skill entries) as a separate go-live activity; do not include it in the development estimate.
5. **Log a backlog item for the correction-entry pattern** (US-006 candidate) so the decision to defer OQ3 is visible to the product owner and does not resurface as an unplanned Phase 2 addition.

---

## Handoff back to the Architect
<!-- section-key: HandoffToArchitect -->

- **On approval**: set `SPEC-001` status to `approved`, set `ANALYSIS-001` status to `approved`, set `CCN-001` approval table entries. The Architect may then hand off Phase 1 to the AL Developer.
- **Advisory 1 (runtime guard)**: update SPEC-001 §4 (`ConfirmAssessment` procedure description) to explicitly include the `UserHasESMFullPermission()` runtime check as part of the procedure contract before developer handoff.
- **Advisory 2 (test codeunits)**: decide whether to define test codeunit objects in SPEC-001 §10 or in separate plan files before developer handoff.
- **On rejection or conditional approval**: identify which SWOT weakness or risk drove the objection, revise SPEC-001 / ARCH-001 accordingly, and request a re-analysis. A revised analysis does not require a new ANALYSIS ID — increment the `version` field in this document's frontmatter.
