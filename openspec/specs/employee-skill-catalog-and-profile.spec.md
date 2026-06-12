---
id: SPEC-001
title: Employee Skill Catalog and Skill Profile Management
version: 1.0.0
type: features
status: implemented
user_story: US-001
priority: high
complexity: medium
estimated_effort: 13–18 h
module: Human Resources
prefix: ESM
customer: BC Tech Days 26 (Demo)
id_range: "51100–51149"
prepared_by: Fernando Artigas Alfonso
created_date: 2026-06-10
approved_date:
---

# SPEC-001 — Employee Skill Catalog and Skill Profile Management

## User Story Reference
<!-- section-key: UserStoryReference -->

> **US-001 (approved 2026-06-10)**
> **As an** HR administrator, **I want** to define a central skill catalog and record each employee's skills with a proficiency level and an effective date, while preserving every previous assessment, **so that** employee competencies are measured consistently and their progression can be traced and audited over time.

### Acceptance Criteria Summary

| AC | Title | Key behaviour |
|---|---|---|
| AC1 | Skill catalog maintenance | Create/edit/block skills with unique code; link to a proficiency scale; block-only deletion when in use |
| AC2 | Employee skill profile maintenance | Add catalog-only skills per employee; no duplicate current; current = latest effective |
| AC3 | Effective-dated skill assessment | Mandatory effective date defaulting to work date; "current" = latest on or before work date |
| AC4 | Immutable skill history and auditability | No overwrite/delete of prior entries; chronological history with user/date stamps; read-only to non-admins |

---

## Technical Design Overview
<!-- section-key: TechnicalDesignOverview -->

### 2.1 Architecture Overview

The extension introduces three new tables forming a master-data / transaction pattern:

```
Skill Category (51101)
      │ 1:N
Skill (51100)  ──────────── Skill Proficiency Level Enum (51100)
      │ 1:N (Skill Code FK)
Employee Skill Assessment (51102)
      │ N:1 (Employee No. FK → standard Employee table 5200)
```

- The **Skill** table is the catalog master. Each entry references a global `Skill Proficiency Level` enum for its scale.
- The **Employee Skill Assessment** table is append-only (no Modify/Delete in business logic). Every new assessment adds a row; history is the full set of rows per employee+skill.
- "Current proficiency" for a skill is computed by `Skill Mgt.` codeunit: filter on Employee No. + Skill Code, sort descending by Effective Date, take the first entry whose Effective Date ≤ WorkDate.
- The **Employee Skill Profile** page shows one row per (employee, skill) with the current proficiency computed at open time — it is a derived view, not a separate stored table.
- The standard `Employee Card` (Page 5200) is extended to surface the skill profile via a FactBox.

### 2.2 Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Proficiency scale | Global `Skill Proficiency Level` enum (0=Unassigned, 1=Beginner, 2=Intermediate, 3=Advanced, 4=Expert) | **OQ1 resolved.** Fixed 4-level enum is sufficient for v1; upgradable to a configurable scale table in a future story without breaking Table 51102. |
| Who may enter assessments | HR, line manager, and **employee self-service** — employee entries start as `Pending Confirmation` and only count as "current" after HR/manager confirms | **OQ2 resolved.** Requires `Status` field (Enum 51101) and `ConfirmAssessment` procedure. Pending entries are visible in the profile but excluded from `GetCurrentProficiency`. |
| Assessment mutability | Table trigger `OnBeforeModify` and `OnBeforeDelete` raise errors unconditionally | Guarantees AC4 immutability. The only write path is `Skill Mgt.`.`AddSkillAssessment`; confirmation uses a direct field pointer to bypass the Modify trigger. |
| Correction mechanism | None in v1 — incorrect assessments remain in history | **OQ3 resolved.** A correction-entry pattern can be added in a future story. |
| Current-proficiency calculation | On-demand via codeunit; **only `Status = Confirmed` rows are considered** | Avoids denormalization; pending employee entries do not affect reported current proficiency until confirmed. |
| Skill deletion guard | `OnBeforeDelete` on `Skill` checks `Employee Skill Assessment` for any row with matching `Skill Code` | Implements AC1 block-only deletion without a FlowField count. |
| Profile page UX | **Inline editable row** on the Employee Skill Profile ListPart | **OQ4 resolved.** No separate dialog page (Page 51105 is removed from scope); validation happens in `OnBeforeInsert`/`OnValidate`. |

---

## AL Object Inventory
<!-- section-key: AlObjectInventory -->

#### Enums

| ID | Name | Values |
|---|---|---|
| 51100 | Skill Proficiency Level | 0 Unassigned, 1 Beginner, 2 Intermediate, 3 Advanced, 4 Expert |
| 51101 | Skill Assessment Status | 0 Confirmed, 1 Pending Confirmation |

#### Tables

| ID | Name | Purpose | Key fields |
|---|---|---|---|
| 51100 | Skill | Skill catalog master | Code (PK, Code[20]), Description (Text[100]), Category Code (Code[20] → Skill Category), Blocked (Boolean) |
| 51101 | Skill Category | Optional grouping for skills | Code (PK, Code[20]), Description (Text[100]) |
| 51102 | Employee Skill Assessment | Immutable assessment ledger | Entry No. (PK, Integer, auto-increment), Employee No. (Code[20] → Employee), Skill Code (Code[20] → Skill), Proficiency Level (Enum 51100), Effective Date (Date), Status (Enum 51101), Created By (Code[50]), Created DateTime (DateTime), Confirmed By (Code[50]), Confirmed DateTime (DateTime) |

#### Pages

| ID | Name | Type | Source table |
|---|---|---|---|
| 51100 | Skill List | List | Skill (51100) |
| 51101 | Skill Card | Card | Skill (51100) |
| 51102 | Skill Category List | List | Skill Category (51101) |
| 51103 | Employee Skill Profile | ListPart | Employee Skill Assessment (51102) — filtered to show current per skill |
| 51104 | Employee Skill Assessment History | List | Employee Skill Assessment (51102) |

#### Codeunits

| ID | Name | Responsibilities |
|---|---|---|
| 51100 | Skill Mgt. | `AddSkillAssessment`, `GetCurrentProficiency`, `ConfirmAssessment`, `BlockSkill`, `CanDeleteSkill` |

#### Page Extensions

| ID | Name | Extends | Change |
|---|---|---|---|
| 51100 | Employee Card ESM Ext | Employee Card (5200) | Add FactBox: Employee Skill Profile (51103); add action: Skill History |

#### Permission Sets

| ID | Name | Access level |
|---|---|---|
| 51100 | ESM BASIC | Read-only on all ESM objects |
| 51101 | ESM FULL | Read+Write on all ESM objects |

---

## Table Field Definitions
<!-- section-key: TableFieldDefinitions -->

### 3.1 Table 51100 — Skill

| Field ID | Name | Type | Length | Constraints |
|---|---|---|---|---|
| 1 | Code | Code | 20 | PK, NotBlank |
| 2 | Description | Text | 100 | NotBlank |
| 3 | Category Code | Code | 20 | TableRelation: Skill Category.Code; optional |
| 4 | Blocked | Boolean | — | Default: false |

- `OnBeforeDelete`: call `Skill Mgt.`.`CanDeleteSkill` — error if any `Employee Skill Assessment` row exists with this `Skill Code`.
- `DrillDownPageID = 51100`, `LookupPageID = 51100`.

### 3.2 Table 51101 — Skill Category

| Field ID | Name | Type | Length | Constraints |
|---|---|---|---|---|
| 1 | Code | Code | 20 | PK, NotBlank |
| 2 | Description | Text | 100 | NotBlank |

- `OnBeforeDelete`: error if any `Skill` row references this `Category Code`.

### 3.3 Table 51102 — Employee Skill Assessment

| Field ID | Name | Type | Length | Constraints |
|---|---|---|---|---|
| 1 | Entry No. | Integer | — | PK; auto-incremented in `OnBeforeInsert` |
| 2 | Employee No. | Code | 20 | TableRelation: Employee.No.; NotBlank |
| 3 | Skill Code | Code | 20 | TableRelation: Skill.Code; NotBlank |
| 4 | Proficiency Level | Enum | 51100 | NotBlank (≠ Unassigned) |
| 5 | Effective Date | Date | — | NotBlank; validated: ≤ Today + 365 days |
| 6 | Status | Enum | 51101 | Set by `AddSkillAssessment` caller; HR/manager pass Confirmed, employee passes Pending Confirmation |
| 7 | Created By | Code | 50 | Auto-set in `OnBeforeInsert` to `UserId` |
| 8 | Created DateTime | DateTime | — | Auto-set in `OnBeforeInsert` to `CurrentDateTime` |
| 9 | Confirmed By | Code | 50 | Set by `ConfirmAssessment`; blank until confirmed |
| 10 | Confirmed DateTime | DateTime | — | Set by `ConfirmAssessment`; blank until confirmed |

- `OnBeforeModify`: error unconditionally — assessments are immutable.
- `OnBeforeDelete`: error unconditionally — assessments are immutable.
- Keys: PK (Entry No.); Key2 (Employee No., Skill Code, Effective Date) — used by `GetCurrentProficiency`.

### Codeunit 51100 — Skill Mgt.

| Procedure | Signature | Behaviour |
|---|---|---|
| `AddSkillAssessment` | `(EmployeeNo: Code[20]; SkillCode: Code[20]; ProfLevel: Enum "Skill Proficiency Level"; EffectiveDate: Date; InitialStatus: Enum "Skill Assessment Status")` | Validates Employee exists; Skill exists and not Blocked; ProfLevel ≠ Unassigned; EffectiveDate not blank. Inserts a new `Employee Skill Assessment` row with the supplied `InitialStatus`. HR/manager callers pass `Confirmed`; employee self-service callers pass `Pending Confirmation`. |
| `GetCurrentProficiency` | `(EmployeeNo: Code[20]; SkillCode: Code[20]; AsOfDate: Date): Enum "Skill Proficiency Level"` | Filters `Employee Skill Assessment` on Employee No. + Skill Code + Effective Date ≤ AsOfDate + **Status = Confirmed**; sorts descending by Effective Date; returns first `Proficiency Level`; returns Unassigned if none found. |
| `ConfirmAssessment` | `(EntryNo: Integer)` | Retrieves the row by Entry No.; errors if already Confirmed. Sets `Status = Confirmed`, `Confirmed By = UserId`, `Confirmed DateTime = CurrentDateTime` using `Rec.Modify(true)` — which raises the immutability error. Therefore this procedure must use a direct SQL update (`ModifyAll` on PK) or a dedicated internal-access bypass. Caller must hold ESM FULL. |
| `BlockSkill` | `(SkillCode: Code[20])` | Sets `Skill.Blocked = true`; does not delete any assessments. |
| `CanDeleteSkill` | `(SkillCode: Code[20]): Boolean` | Returns `false` if any `Employee Skill Assessment` row has `Skill Code = SkillCode`; raises error if false. |

---

## Page Design Notes
<!-- section-key: PageDesignNotes -->

### Page 51103 — Employee Skill Profile (ListPart)

- **SubPageLink:** `Employee No.` = FIELD(No.) from the Employee Card
- **Inline editable** — new rows are entered directly in the ListPart; no separate dialog page.
- Page `OnBeforeInsert` determines `InitialStatus`: if the current user has ESM FULL → `Confirmed`; otherwise → `Pending Confirmation`.
- Displayed columns: Skill Code, Skill Description (relation), Proficiency Level, Effective Date, Status
- `StyleExpr` on Status: `Pending Confirmation` rows render as **Ambiguous** (orange) to distinguish from confirmed current data.
- A **Confirm** action (visible only to ESM FULL users) calls `ConfirmAssessment` for the selected row.
- The FactBox title is "Skill Profile".

### Page 51104 — Employee Skill Assessment History

- Filters on a single employee; opened from the Employee Card action "Skill History"
- Columns: Skill Code, Proficiency Level, Effective Date, Created By, Created DateTime
- Sorted descending by Effective Date (most recent first)
- Read-only for non-admin users (handled via permission set)

### PageExtension 51100 — Employee Card ESM Ext

- Adds FactBox `51103` in the `FactBoxes` area with `SubPageLink` = Employee No.
- Adds action "Skill History" in the `Navigate` group → opens Page 51104 filtered to current employee

---

## Technical Acceptance Criteria
<!-- section-key: TechnicalAcceptanceCriteria -->

| AC | Technical implementation |
|---|---|
| AC1 — Skill catalog maintenance | Table 51100 + Pages 51100/51101; `OnBeforeDelete` guard via `Skill Mgt.`.`CanDeleteSkill`; Blocked field; Category Code relation to 51101 |
| AC2 — Employee skill profile maintenance | `AddSkillAssessment` validates Skill.Code exists and not Blocked; inline editable Page 51103; employee rows enter as Pending and excluded from `GetCurrentProficiency` until confirmed |
| AC3 — Effective-dated assessment | `Effective Date` field on Table 51102; `GetCurrentProficiency` filters Effective Date ≤ AsOfDate AND Status = Confirmed; default = WorkDate |
| AC4 — Immutable history | `OnBeforeModify`/`OnBeforeDelete` unconditional errors on Table 51102; `ConfirmAssessment` uses direct field update path; Page 51104 is read-only; ESM BASIC restricts write access |

---

## Integration with Standard BC Objects
<!-- section-key: IntegrationWithStandardBcObjects -->

| Standard object | Object ID | Touched by | Nature of interaction |
|---|---|---|---|
| Employee | Table 5200 | Table 51102 FK | `TableRelation: Employee.No.` on Field 2 of Table 51102; no triggers or fields on Table 5200 modified |
| Employee Card | Page 5200 | PageExtension 51100 | One FactBox (Page 51103) and one navigation action (Skill History) added; no existing fields or triggers changed |

---

## Dependencies
<!-- section-key: Dependencies -->

- Standard BC `Employee` table (5200) and `Employee Card` page (5200) — no modifications, extension only
- No AL-Go specific pipeline dependencies
- US-002 (Development Goals) will depend on `Skill Proficiency Level` enum 51100 and `Skill` table 51100 — stable contract established in Phase 1

---

## Phase Overview
<!-- section-key: PhaseOverview -->

| Phase | Slug | Scope | Estimated effort |
|---|---|---|---|
| 1 | `catalog-foundation` | Enum 51100/51101, Tables 51100/51101, Pages 51100/51101/51102, Permission Sets 51100/51101 | 5–7 h |
| 2 | `employee-assessments` | Table 51102, Codeunit 51100 (incl. `ConfirmAssessment`), Pages 51103/51104, PageExtension 51100 | 9–13 h |

---

## Architecture

Architecture document: [ARCH-001](../architecture/ARCH-001-employee-skill-catalog-and-profile.architecture.md)

Feasibility Analysis: [ANALYSIS-001](../analysis/ANALYSIS-001-employee-skill-catalog-and-profile.analysis.md)

---

## Testing Strategy
<!-- section-key: TestingStrategy -->

### Phase 1
- Skill can be created, edited, blocked
- Blocked skill cannot be deleted
- Skill with an assessment (from Phase 2 data setup) cannot be deleted
- Skill Category can be created; deletion blocked when skills reference it

### Phase 2
- `AddSkillAssessment` creates a row; second call for same employee+skill creates a second row (no duplicate error)
- `GetCurrentProficiency` returns correct level for multiple assessments with different effective dates
- Modify/Delete on `Employee Skill Assessment` raises error
- Employee Card FactBox shows current skills; History page shows all rows
- ESM BASIC user cannot insert/modify assessments

---

## Open Questions Tracking
<!-- section-key: OpenQuestionsTracking -->

| # | From | Status | Resolution |
|---|---|---|---|
| OQ1 | US-001 | Resolved | Fixed 4-level proficiency scale: Beginner / Intermediate / Advanced / Expert. Single global scale sufficient for v1. |
| OQ2 | US-001 | Resolved | Employees may enter their own assessments (Status = Pending Confirmation). HR/managers confirm via the Confirm action on Page 51103. Requires Enum 51101 and `ConfirmAssessment` procedure. |
| OQ3 | US-001 | Resolved | No correction mechanism in v1. Incorrect entries remain permanently in history. Correction-entry pattern deferred to a future story. |
| OQ4 | US-001 | Resolved | Inline editable ListPart for Page 51103. No separate dialog page required. |

---

## Phase Plans
<!-- section-key: PhasePlans -->

1. [Phase 1 — Catalog Foundation](../plans/SPEC-001-phase-1-catalog-foundation.plan.md)
2. [Phase 2 — Employee Assessments](../plans/SPEC-001-phase-2-employee-assessments.plan.md)
