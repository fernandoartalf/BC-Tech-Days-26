---
id: SPEC-001-phase-1
title: "SPEC-001 Phase 1 — Skill Catalog Foundation"
phase: 1
slug: catalog-foundation
spec: SPEC-001
user_story: US-001
status: completed
estimated_hours: "5–7"
branch: feature/esm-skill-catalog
depends_on: []
related_docs:
  - openspec/specs/employee-skill-catalog-and-profile.spec.md
  - openspec/user-stories/US-001-employee-skill-catalog-and-profile.userstory.md
assignee:
created_date: 2026-06-10
approved_date:
---

# SPEC-001 Phase 1 — Skill Catalog Foundation

## References

- Spec: [SPEC-001](../specs/employee-skill-catalog-and-profile.spec.md)
- User Story: [US-001](../user-stories/US-001-employee-skill-catalog-and-profile.userstory.md)

---

## Goal

Establish the master data layer for the skill module: the `Skill Proficiency Level` enum, the `Skill Category` table and list, and the `Skill` table with its card and list pages. After this phase HR administrators can maintain the full skill catalog and the two permission sets are available. No employee data is touched yet.

This phase is self-contained and deployable — US-002 through US-005 can reference the objects delivered here without waiting for Phase 2.

---

## Branch

`feature/esm-skill-catalog`

---

## Tasks

- [ ] **T1.1** Create `Enum 51100 Skill Proficiency Level` with values: 0 Unassigned, 1 Beginner, 2 Intermediate, 3 Advanced, 4 Expert. File: `src/enums/Enum51100.SkillProficiencyLevel.al`
- [ ] **T1.1b** Create `Enum 51101 Skill Assessment Status` with values: 0 Confirmed, 1 Pending Confirmation. File: `src/enums/Enum51101.SkillAssessmentStatus.al` *(needed by Table 51102 in Phase 2; defined here so Phase 1 is independently compilable)*
- [ ] **T1.2** Create `Table 51101 Skill Category` with fields: Code (PK, Code[20]), Description (Text[100]). Add `OnBeforeDelete` trigger that errors if any `Skill` row references the category. Set `DrillDownPageID = 51102`, `LookupPageID = 51102`. File: `src/tables/Table51101.SkillCategory.al` *(satisfies AC1)*
- [ ] **T1.3** Create `Table 51100 Skill` with fields: Code (PK, Code[20]), Description (Text[100]), Category Code (Code[20], TableRelation: Skill Category.Code), Blocked (Boolean). Add `OnBeforeDelete` trigger that errors if any `Employee Skill Assessment` row exists for this code. Set `DrillDownPageID = 51100`, `LookupPageID = 51100`. File: `src/tables/Table51100.Skill.al` *(satisfies AC1)*
- [ ] **T1.4** Create `Page 51102 Skill Category List` (List, source: Skill Category 51101). Columns: Code, Description. Editable. File: `src/pages/Page51102.SkillCategoryList.al`
- [ ] **T1.5** Create `Page 51100 Skill List` (List, source: Skill 51100). Columns: Code, Description, Category Code, Blocked. Editable; filter `Blocked = false` by default (user can show all). File: `src/pages/Page51100.SkillList.al` *(satisfies AC1)*
- [ ] **T1.6** Create `Page 51101 Skill Card` (Card, source: Skill 51100). Fields: Code, Description, Category Code, Blocked. File: `src/pages/Page51101.SkillCard.al` *(satisfies AC1)*
- [ ] **T1.7** Create `PermissionSet 51100 ESM BASIC` — Read (R) on Table 51100, 51101, 51102; Read on Pages 51100–51104. File: `src/permissionsets/PermissionSet51100.ESMBasic.al`
- [ ] **T1.8** Create `PermissionSet 51101 ESM FULL` — includes ESM BASIC plus Insert+Modify+Delete on Tables 51100, 51101 and Insert on 51102 (no Modify/Delete on 51102). File: `src/permissionsets/PermissionSet51101.ESMFull.al`

---

## Acceptance Criteria (Phase 1)

- AC1.1: HR can create a Skill Category with Code and Description.
- AC1.2: HR can create a Skill with Code, Description, and optional Category Code.
- AC1.3: A Skill can be marked Blocked; it no longer appears in the default Skill List filter.
- AC1.4: Deleting a Skill Category that is referenced by a Skill raises an error.
- AC1.5: Deleting a Skill that is referenced by an Employee Skill Assessment raises an error (guard in Table 51100 `OnBeforeDelete` — Table 51102 does not need to exist yet to compile; the guard does a `FINDFIRST` that simply returns false if the table is empty in Phase 1).
- AC1.6: ESM BASIC user can read but not write Skill or Skill Category.
- AC1.7: ESM FULL user can create and edit Skills and Skill Categories.

---

## Out of Scope for This Phase

- Employee Skill Assessments (Table 51102) — Phase 2
- Codeunit 51100 Skill Mgt. — Phase 2
- Employee Card extension — Phase 2
- Pages 51103, 51104 — Phase 2

---

## Notes for the AL Developer

- Use `NoImplicitWith` (already set in `app.json`).
- Prefix all object names with the app name context — no explicit affix was defined in `app.json`; use `Skill` as the natural prefix for catalog objects (e.g., `Skill`, `Skill Category`).
- Table 51100 `OnBeforeDelete` references Table 51102. To avoid a forward-reference compiler error, use a conditional check: only filter Table 51102 if it exists (`TableNo` guard or compile with Phase 2 included). Alternatively, declare a stub reference — coordinate with Phase 2 strategy.
- Permission set for Table 51102 (Phase 2 object) can be added as an amendment in Phase 2; keep ESM BASIC/FULL focused on Phase 1 objects for now and note the amendment in Phase 2 plan.

---

## Dependencies

- None (Phase 1 is the base layer for the entire extension)

---

## Testing Notes

- Create a Skill Category, then a Skill referencing it; verify the relation and lookup.
- Attempt to delete the Skill Category — expect error.
- Block a Skill; verify it disappears from the default list filter.
- Sign in as ESM BASIC user; attempt to create a Skill — expect permission error.
