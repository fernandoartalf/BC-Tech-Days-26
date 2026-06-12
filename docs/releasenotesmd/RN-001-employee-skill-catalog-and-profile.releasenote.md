---
id: RN-001
title: Employee Skill Catalog and Skill Profile Management
customer: BC Tech Days 26 (Demo)
version: 1.0.0.0
status: draft
clientName: BC Tech Days 26 (Demo)
ccnNumber: CCN-001
issueNumber: RN-001
releaseDate: 2026-06-10
releasedBy: BC Tech Days 2026
prepared_by: Fernando Artigas
module: Employee Skill Management
createdDate: 2026-06-10
approvedDate: ""
label_rn_id: "Release note ID"
label_version: "Version"
label_created_date: "Created date"
label_prepared_by: "Prepared by"
---

# RN-001 – Employee Skill Catalog and Skill Profile Management

## Release Summary
<!-- section-key: ReleaseSummary -->

This release delivers the **Employee Skill Management (ESM)** extension for Microsoft Dynamics 365 Business Central. It introduces a skill catalog, skill category grouping, employee skill assessments with a two-tier permission model (read-only vs. full), and an integrated Skill Profile FactBox on the Employee Card. HR administrators and managers can now record, review, and confirm employee proficiency levels directly within Business Central, replacing manual tracking outside the system.

## Scope of Change
<!-- section-key: ScopeOfChange -->

**Enumerations**

- Enum 51100 "Skill Proficiency Level" — Extensible proficiency scale: Unassigned, Beginner, Intermediate, Advanced, Expert.
- Enum 51101 "Skill Assessment Status" — Assessment lifecycle: Confirmed, Pending Confirmation.

**Tables**

- Table 51100 "Skill" — Skill catalog master: Code, Description, Category Code, Blocked flag. Delete-guarded (cannot delete if assessments exist).
- Table 51101 "Skill Category" — Optional grouping for skills: Code, Description. Delete-guarded (cannot delete if skills assigned).
- Table 51102 "Employee Skill Assessment" — Immutable ledger of skill assessments per employee: Entry No. (auto-increment), Employee No., Skill Code, Proficiency Level, Effective Date, Status, Created By, Created DateTime, Confirmed By, Confirmed DateTime.

**Pages**

- Page 51100 "Skill List" — List of active skills (default filter: not blocked). Caption: Skills.
- Page 51101 "Skill Card" — Card for creating and editing skill records.
- Page 51102 "Skill Category List" — List of skill categories. Caption: Skill Categories.
- Page 51103 "Employee Skill Profile" — Editable ListPart showing an employee's current skill assessments. Includes a **Confirm** action visible only to ESM FULL users.
- Page 51104 "Empl. Skill Asmt. History" — Read-only list of all assessment history entries, sorted by Effective Date descending. Caption: Employee Skill Assessment History.

**Page Extensions**

- PageExtension 51100 "Employee Card ESM Ext" — Extends the standard Employee Card (Page 5200): adds the Skill Profile FactBox and a Skill History navigation action.

**Codeunits**

- Codeunit 51100 "Skill Mgt." — Business logic for the ESM module: `AddSkillAssessment`, `GetCurrentProficiency`, `ConfirmAssessment` (ModifyAll bypass pattern per ARCH-001 ADR-3), `BlockSkill`, `CanDeleteSkill`, `UserHasESMFullPermission`.

**Permission Sets**

- PermissionSet 51100 "ESM BASIC" — Read-only access to all ESM tables and pages. Assignable to all employees.
- PermissionSet 51101 "ESM FULL" — Full RIMD access to catalog tables plus RI on assessments. Includes ESM BASIC. Assignable to HR administrators.

## Change Request Details
<!-- section-key: ChangeRequestDetails -->

This release implements **CCN-001 — Employee Skill Catalog and Skill Profile Management**, approved on 2026-06-10, derived from User Story US-001 and Technical Specification SPEC-001 (phases 1 and 2 both delivered in this release).

The extension introduces a two-phase implementation:

- **Phase 1** — Skill Catalog: the Skill and Skill Category tables, their list/card pages, and the initial ESM permission sets.
- **Phase 2** — Employee Assessments: the Employee Skill Assessment table (immutable ledger), the Skill Mgt. codeunit, the Skill Profile FactBox, the Assessment History page, and the Employee Card extension.

The assessment table enforces immutability at the table trigger level (`OnModify` and `OnDelete` both raise errors). The `ConfirmAssessment` procedure in Codeunit 51100 uses `ModifyAll` to bypass these guards intentionally, as documented in ARCH-001 ADR-3.

No breaking changes were introduced to any standard Business Central object. No data migration or upgrade codeunit is required for this initial install.

Source artefacts: SPEC-001, ARCH-001, ANALYSIS-001, CCN-001.

## Testing Setup
<!-- section-key: TestingSetup -->

| Prerequisite | Value |
|---|---|
| BC Runtime | 15.2 or higher |
| Application version | 22.0.0.0 or higher |
| Extension version | 1.0.0.0 |
| Extension publisher | BC Tech Days 2026 |
| Dependencies | None |
| Permission sets required | ESM BASIC (read-only testers), ESM FULL (confirmation testers) |
| Master data required | At least one active Employee record in the target company |
| Sandbox recommended | Yes — deploy to a sandbox before production |

## Testing Steps
<!-- section-key: TestingSteps -->

### 1. Permission Set Assignment

1. Navigate to **Permission Sets** and verify that `ESM BASIC` and `ESM FULL` are present.
2. Assign `ESM BASIC` to a read-only test user.
3. Assign `ESM FULL` to an administrator test user.
4. Confirm that a user with only `ESM BASIC` cannot see the **Confirm** action on the Skill Profile FactBox.

### 2. Skill Categories

1. Search for **Skill Categories** using the global search (Tell Me).
2. Create a new category: Code = `TECH`, Description = `Technical Skills`.
3. Attempt to delete the category — the system should allow deletion (no skills assigned yet).
4. Verify that the description is saved correctly.

### 3. Skill Catalog

1. Search for **Skills** using the global search.
2. Create a new skill: Code = `AL-DEV`, Description = `AL Development`, Category Code = `TECH`, Blocked = No.
3. Open the Skill Card and verify all fields are visible.
4. Create a second skill: Code = `SQL`, Description = `SQL Database`, Blocked = No.
5. Set the `AL-DEV` skill to **Blocked = Yes** and verify it disappears from the default Skill List view (default filter hides blocked skills).
6. Clear the filter and verify the blocked skill reappears.
7. Attempt to delete `AL-DEV` — the system should allow deletion (no assessments exist yet).

### 4. Employee Skill Profile FactBox

1. Open the **Employee Card** for an existing employee.
2. Verify the **Skill Profile** FactBox is visible in the FactBox pane.
3. Log in as the ESM FULL user. In the Skill Profile FactBox, add a new row: Skill Code = `SQL`, Proficiency Level = `Intermediate`, Effective Date = today.
4. Verify that Status is automatically set to **Confirmed** for an ESM FULL user.
5. Log in as the ESM BASIC user. Add a new row: Skill Code = `SQL`, Proficiency Level = `Beginner`, Effective Date = today.
6. Verify that Status is automatically set to **Pending Confirmation** for an ESM BASIC user.
7. Verify that the **Confirm** action is **not visible** for the ESM BASIC user.

### 5. Confirm Assessment

1. Log in as the ESM FULL user. Open the Employee Card.
2. In the Skill Profile FactBox, locate the row with Status = **Pending Confirmation**.
3. Select it and click **Confirm**.
4. Verify the Status changes to **Confirmed**, and that **Confirmed By** and **Confirmed DateTime** are populated.
5. Attempt to click Confirm again on the now-confirmed row — the system should show an error: "Assessment entry N is already confirmed."

### 6. Assessment History

1. From the Employee Card, click the **Skill History** action in the Navigate menu.
2. Verify the **Employee Skill Assessment History** page opens filtered to the current employee.
3. Confirm all assessment entries are visible (including the confirmed one and any pending ones).
4. Verify the list is sorted by **Effective Date** descending.
5. Verify the page is read-only (no inline editing possible).

### 7. Delete Guard — Skill

1. Attempt to delete the `SQL` skill (which now has assessments).
2. Verify the system raises an error: "You cannot delete Skill SQL because it has one or more employee skill assessments."

### 8. Block Skill Guard

1. Attempt to add a new Skill Profile row for the blocked skill `AL-DEV`.
2. Verify the system raises an error when the skill code is validated against the blocked flag.

## Known Limitations
<!-- section-key: KnownLimitations -->

- The page name for the Assessment History page is abbreviated to `Empl. Skill Asmt. History` (30-character AL object name limit) but the user-facing Caption reads "Employee Skill Assessment History" correctly.
- The `ESM FULL` permission check in `UserHasESMFullPermission` queries the `Access Control` table directly; in multi-company environments with mixed permission assignments, the check is scoped to the current session's user security ID and company.
- No XLF translation files are included in this release. All captions and tooltips are in English only.

## Approvals
<!-- section-key: Approvals -->

| Role | Name | Decision | Date | Signature |
|---|---|---|---|---|
| Prepared by | Fernando Artigas | | | |
| Technical Lead | | | | |
| Client Sign-off | | | | |
