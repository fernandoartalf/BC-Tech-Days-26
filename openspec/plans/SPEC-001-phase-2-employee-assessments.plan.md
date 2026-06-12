---
id: SPEC-001-phase-2
title: "SPEC-001 Phase 2 — Employee Skill Assessments"
phase: 2
slug: employee-assessments
spec: SPEC-001
user_story: US-001
status: completed
estimated_hours: "9–13"
branch: feature/esm-employee-assessments
depends_on:
  - SPEC-001-phase-1
related_docs:
  - openspec/specs/employee-skill-catalog-and-profile.spec.md
  - openspec/user-stories/US-001-employee-skill-catalog-and-profile.userstory.md
  - openspec/plans/SPEC-001-phase-1-catalog-foundation.plan.md
assignee:
created_date: 2026-06-10
approved_date:
---

# SPEC-001 Phase 2 — Employee Skill Assessments

## References

- Spec: [SPEC-001](../specs/employee-skill-catalog-and-profile.spec.md)
- User Story: [US-001](../user-stories/US-001-employee-skill-catalog-and-profile.userstory.md)
- Depends on: [Phase 1](SPEC-001-phase-1-catalog-foundation.plan.md)

---

## Goal

Deliver the transactional layer: the immutable `Employee Skill Assessment` ledger table, the `Skill Mgt.` codeunit with all business logic, the Employee Skill Profile ListPart and the Assessment History list, and the Employee Card extension that surfaces both. After this phase the full US-001 acceptance criteria are met end-to-end.

---

## Branch

`feature/esm-employee-assessments`

---

## Tasks

- [ ] **T2.1** Create `Table 51102 Employee Skill Assessment` with fields per spec §3.3 (Entry No. PK, Employee No., Skill Code, Proficiency Level, Effective Date, Status, Created By, Created DateTime, Confirmed By, Confirmed DateTime). Add secondary key on (Employee No., Skill Code, Effective Date). Add `OnBeforeModify` trigger: `Error('...')`. Add `OnBeforeDelete` trigger: `Error('...')`. Add `OnBeforeInsert` trigger: auto-set Entry No., Created By, Created DateTime. File: `src/tables/Table51102.EmployeeSkillAssessment.al` *(satisfies AC3, AC4)*
- [ ] **T2.2** Create `Codeunit 51100 Skill Mgt.` with five procedures: `AddSkillAssessment` (with `InitialStatus` parameter), `GetCurrentProficiency` (filter Status = Confirmed), `ConfirmAssessment` (direct field update bypassing Modify trigger via `ModifyAll` on PK or a dedicated internal accessor), `BlockSkill`, `CanDeleteSkill` — per spec §4. File: `src/codeunits/Codeunit51100.SkillMgt.al` *(satisfies AC2, AC3)*
- [ ] **T2.3** Create `Page 51103 Employee Skill Profile` (ListPart, source: Employee Skill Assessment 51102). **Inline editable**. Page `OnBeforeInsert` sets `InitialStatus` (ESM FULL user → Confirmed, otherwise → Pending Confirmation) then calls `Skill Mgt.`.`AddSkillAssessment`. Columns: Skill Code, Skill Description, Proficiency Level, Effective Date, Status (with `StyleExpr` = Ambiguous for Pending). Add **Confirm** action (visible to ESM FULL only) calling `ConfirmAssessment`. File: `src/pages/Page51103.EmployeeSkillProfile.al` *(satisfies AC2, AC4)*
- [ ] **T2.4** Create `Page 51104 Employee Skill Assessment History` (List, source: Employee Skill Assessment 51102). Columns: Skill Code, Proficiency Level, Effective Date, Status, Created By, Created DateTime, Confirmed By, Confirmed DateTime. Read-only. Sorted descending by Effective Date. File: `src/pages/Page51104.EmployeeSkillHistory.al` *(satisfies AC4)*
- [ ] **T2.5** Create `PageExtension 51100 Employee Card ESM Ext` extending `Employee Card` (Page 5200). Add FactBox `Employee Skill Profile (51103)` with `SubPageLink` = `Employee No. = FIELD(No.)`. Add action "Skill History" in Navigate group opening Page 51104 filtered to current employee. File: `src/pageextensions/PageExt51100.EmployeeCardESMExt.al` *(satisfies AC2)*
- [ ] **T2.6** Update `PermissionSet 51100 ESM BASIC` to add Read (R) on Table 51102 and Pages 51103, 51104. Update `PermissionSet 51101 ESM FULL` to add Insert (I) on Table 51102 (no M or D — enforced by table triggers). File: amend `src/permissionsets/PermissionSet51100.ESMBasic.al` and `PermissionSet51101.ESMFull.al` *(satisfies AC4)*

---

## Acceptance Criteria (Phase 2)

- AC2.1: `AddSkillAssessment` inserts a new row; calling it twice for the same employee + skill produces two rows (no error).
- AC2.2: `AddSkillAssessment` rejects a Blocked skill with a clear error message.
- AC2.3: `AddSkillAssessment` rejects an Unassigned proficiency level.
- AC2.4: `GetCurrentProficiency` returns the proficiency whose Effective Date is the latest on or before the supplied AsOfDate, among rows with Status = Confirmed only.
- AC2.5: `GetCurrentProficiency` returns Unassigned when no Confirmed assessment exists for the employee+skill on or before AsOfDate.
- AC2.6: Attempting to modify any field of an `Employee Skill Assessment` row raises an error.
- AC2.7: Attempting to delete an `Employee Skill Assessment` row raises an error.
- AC2.8: The Employee Card FactBox shows the skill profile for the open employee.
- AC2.9: The Skill History action on the Employee Card opens Page 51104 showing all assessments for that employee, sorted newest first.
- AC2.10: An ESM BASIC user can view the skill profile and history but cannot add new rows or invoke Confirm.
- AC2.11: A row entered by an ESM BASIC user on Page 51103 has Status = Pending Confirmation immediately after insert.
- AC2.12: The Confirm action on Page 51103 is visible only to ESM FULL users and, on execution, sets Status = Confirmed, Confirmed By, and Confirmed DateTime on the selected row.
- AC2.13: A Pending Confirmation row is excluded from `GetCurrentProficiency` results regardless of effective date.

---

## Out of Scope for This Phase

- Development goal linkage (US-002)
- Performance review snapshot of skills (US-003)
- Any UI beyond the Employee Card extension (dedicated HR workspace pages — future)

---

## Notes for the AL Developer

- **`GetCurrentProficiency`**: use `SetRange` on Employee No. + Skill Code, `SetRange` on Status = Confirmed, `SetFilter` on Effective Date `'..%1'` passing `AsOfDate`, `SetCurrentKey` on the secondary key `(Employee No., Skill Code, Effective Date)`, then `FindLast`. Use `SetLoadFields` to load only `Proficiency Level` and `Effective Date` — performance best practice.
- **`ConfirmAssessment` bypass pattern**: because Table 51102's `OnBeforeModify` raises an unconditional error, `ConfirmAssessment` must NOT call `Rec.Modify()`. Use `EmployeeSkillAssessment.ModifyAll(EmployeeSkillAssessment.FieldNo(Status), ...)` on a filtered recordset (filter to Entry No.) plus separate `ModifyAll` calls for Confirmed By and Confirmed DateTime, OR use an `internal` procedure on a dedicated helper with `Access = Internal` that bypasses the trigger via `SkipTriggers := true`. Agree the chosen approach with the Reviewer before implementation.
- **Page 51103 `OnBeforeInsert` pattern**: check `UserHasESMFullPermission()` (helper that checks permission set assignment) and set `Rec.Status` accordingly before the record is passed to `AddSkillAssessment`. The ESM FULL user insert path sets Status = Confirmed; the ESM BASIC path sets Status = Pending Confirmation.
- **`StyleExpr` on Status**: declare a `Text` variable `StatusStyle` populated in `OnAfterGetRecord`; set to `'Ambiguous'` when `Rec.Status = "Skill Assessment Status"::"Pending Confirmation"`, `''` otherwise. Bind the column `StyleExpr` to this variable.
- **Confirm action visibility**: use `Visible := UserHasESMFullPermission()` in the action's trigger, or use a `Boolean` page variable `IsESMFull` set in `OnOpenPage`.

---

## Dependencies

- **Phase 1 must be merged and deployed first** — Table 51100 (Skill) and Enum 51100 must exist for Table 51102 FK relations and codeunit logic.
- **Downstream consumers**: US-002 (goals) will reference `Skill Mgt.`.`GetCurrentProficiency` and Table 51102 for progress tracking — treat the codeunit signature as a stable contract from this phase.

---

## Testing Notes

- Run `AddSkillAssessment` for an employee with two skills; run it again for one of the skills with a different effective date — verify 3 rows exist in Table 51102.
- Call `GetCurrentProficiency` with AsOfDate = an intermediate date — verify it returns the correct row.
- Attempt `Rec.Modify()` and `Rec.Delete()` on Table 51102 from a test codeunit — verify both raise errors.
- Open Employee Card; verify FactBox populates; open Skill History; verify history is read-only and sorted newest first.
