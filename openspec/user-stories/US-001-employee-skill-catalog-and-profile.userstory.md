<!-- PLAN-DOC-BC-003 heading rules: H2s must NOT carry a manual numeric prefix (template auto-numbers) and MUST NOT end with a source-ID suffix like '(from US-NNN)'. H3 subsection labels keep the 'N.M ' prefix shape but translate the label text. See SKILL.md "Heading & full-content translation rules". -->
---
id: US-001
title: Employee Skill Catalog and Skill Profile Management
customer: BC Tech Days 26 (Demo)
version: 1.0.0
status: approved
module: Human Resources
productOwner: Fernando Artigas Alfonso
prepared_by: Fernando Artigas Alfonso
created_date: 2026-06-10
approved_date: 2026-06-10
template: 1_UserStory_Template.docx
language: en
---

# US-001 — Employee Skill Catalog and Skill Profile Management

## User Story
<!-- section-key: UserStoryStatement -->

**As an** HR administrator (with employees as secondary maintainers of their own profile),
**I want** to define a central skill catalog and record each employee's skills with a proficiency level and an effective date, while preserving every previous assessment,
**so that** employee competencies are measured consistently across the organization and their progression can be traced and audited over time.

## Business Context
<!-- section-key: BusinessContext -->

The organization needs an objective, auditable foundation for measuring employee growth. Today skills are tracked informally — in spreadsheets and managers' notes — which makes them inconsistent, non-comparable, and impossible to audit. This story establishes the master data (a skill catalog) and the transactional record (an employee skill profile with effective-dated, historically-preserved assessments) that every later capability (goals, reviews, reward eligibility) depends on.

The customer's pain points are:

- Skills are recorded in spreadsheets outside Business Central, with no shared catalog, so the same competency is named differently by different managers and cannot be reported on consistently.
- There is no agreed proficiency scale, so a statement like "knows SQL" carries a different meaning for each reviewer and cannot drive objective decisions.
- When a skill assessment changes, the previous value is overwritten and lost, so the organization cannot show how an employee progressed or prove a point-in-time competency level for an audit.

## Current Situation (Standard Business Central)
<!-- section-key: CurrentSituation -->

Verified on Microsoft Learn (Business Central Human Resources documentation):

- Standard Business Central keeps detailed employee records on the **Employee Card** page, where you register and maintain employment details and related information such as contracts, confidential information, qualifications, and employee contacts.
- Employees can have **Qualifications** registered against them (e.g. diplomas, certificates) with descriptive and date information, accessed from the Employee Card; qualifications are descriptive entries, not a graded proficiency model.
- Related employee information (alternate addresses, relatives, union membership, misc. articles) and **employee absences** are supported and can be filtered and analyzed.
- Standard BC does **not** provide a configurable proficiency-level scale, an organization-wide skill catalog with proficiency definitions, nor a historized record that preserves each prior skill assessment as an immutable, effective-dated entry.

**Conclusion:** Standard BC can store an employee's qualifications and basic descriptive HR data, but it has no graded skill catalog and no historized, effective-dated skill assessments. This user story closes that gap by adding a reusable Skill catalog and an employee Skill Profile whose changes are retained as a chronological, auditable history.

## Acceptance Criteria
<!-- section-key: AcceptanceCriteria -->

### AC1 — Skill catalog maintenance

- An HR administrator can create, edit, and block (but not hard-delete in use) skill catalog entries, each with a unique code, a description, and an optional category.
- Each skill catalog entry references a defined proficiency scale (see Open Question 1) so that every assessment uses the same set of levels.
- A skill code that is referenced by any employee skill assessment cannot be deleted; it can only be blocked from further use.

### AC2 — Employee skill profile maintenance

- For a given employee, an authorized user can add a skill (from the catalog only — free-text skills are rejected) and assign a proficiency level from the skill's scale.
- The same skill cannot appear twice as the employee's current assessment; recording a new level for an existing skill creates a new dated assessment rather than a duplicate current row.
- The employee's current skill profile shows, per skill, the latest effective proficiency level and its effective date.

### AC3 — Effective-dated skill assessment

- Every skill assessment is stored with a mandatory effective date; the effective date defaults to the work date and can be back- or forward-dated by an authorized user.
- The "current" proficiency for a skill is the assessment whose effective date is the latest on or before the work date.

### AC4 — Immutable skill history and auditability

- When an employee's proficiency for a skill changes, the previous assessment is retained unchanged; the system never overwrites or deletes a prior assessment.
- A chronological history view lists all assessments for an employee (and per skill), showing previous and new proficiency level, effective date, and the user who recorded each change.
- The history is read-only to non-administrators and is available for audit at any later date.

## Out of Scope
<!-- section-key: OutOfScope -->

- Recruitment, candidate management, and succession planning.
- Payroll processing and employee benefits administration.
- Integration with an external Learning Management System (LMS).
- Advanced competency-matrix or weighted scoring calculations.
- Development goals, performance reviews, and reward eligibility (covered by US-002 through US-005).

## Open Questions
<!-- section-key: OpenQuestions -->

1. What proficiency scale should the catalog use (e.g. 1–5 numeric, or Beginner/Intermediate/Advanced/Expert), and is a single global scale sufficient or must it vary per skill category?
2. Who may edit an employee's skill profile — HR administrators only, the line manager, and/or the employee themselves (self-service)? Does an employee-entered assessment require manager confirmation before it becomes "current"?
3. Should a skill assessment ever be correctable (e.g. a mistaken entry) and, if so, via a reversing/correction entry that itself remains in the audit history, rather than an edit?
