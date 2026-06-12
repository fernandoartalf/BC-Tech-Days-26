<!-- PLAN-DOC-BC-003 heading rules: H2s must NOT carry a manual numeric prefix (template auto-numbers) and MUST NOT end with a source-ID suffix like '(from US-NNN)'. H3 subsection labels keep the 'N.M ' prefix shape but translate the label text. See SKILL.md "Heading & full-content translation rules". -->
---
id: US-002
title: Employee Development Goal Management
customer: BC Tech Days 26 (Demo)
version: 1.0.0
status: draft
module: Human Resources
productOwner: Fernando Artigas Alfonso
prepared_by: Fernando Artigas Alfonso
created_date: 2026-06-10
approved_date:
template: 1_UserStory_Template.docx
language: en
---

# US-002 — Employee Development Goal Management

## User Story
<!-- section-key: UserStoryStatement -->

**As a** line manager (with employees monitoring their own plan),
**I want** to define development goals for an employee, link each goal to one or more skills with a target proficiency and a target completion date, and let the employee track progress,
**so that** individual growth is planned deliberately and progress toward agreed targets is visible to both manager and employee.

## Business Context
<!-- section-key: BusinessContext -->

Once skills are catalogued and assessed (US-001), the organization needs a forward-looking instrument: development goals that state where an employee should grow and by when. Without this, development conversations produce commitments that are never recorded in the system, progress is invisible between annual reviews, and goal achievement cannot later feed an objective reward decision.

The customer's pain points are:

- Development commitments are agreed verbally or in documents outside Business Central, so neither manager nor employee can see live progress against them.
- Goals are not tied to measurable skill targets, so "improve reporting skills" has no objective completion criterion.
- Because goals and their target dates are not held in BC, the review and reward processes (US-003, US-005) have nothing structured to evaluate.

## Current Situation (Standard Business Central)
<!-- section-key: CurrentSituation -->

Verified on Microsoft Learn (Business Central Human Resources documentation):

- The standard **Employee Card** stores employment details and related information (contracts, qualifications, confidential information, contacts) but contains no concept of a forward-looking development goal.
- Standard **Qualifications** are descriptive records of what an employee already holds; there is no target proficiency, target completion date, or progress-tracking model.
- Standard BC has no page or table that links a planned target to one or more skills, and no mechanism for an employee to monitor achievement progress over time.

**Conclusion:** Standard BC records current employment facts and qualifications but offers nothing to plan and track future skill development. This story closes the gap by adding development goals that link to catalogued skills (US-001), carry a target proficiency and target date, and expose live progress to the employee.

## Acceptance Criteria
<!-- section-key: AcceptanceCriteria -->

### AC1 — Goal definition and skill linkage

- A line manager can create a development goal for a specific employee, with a title, description, target completion date, and a status (Open / In Progress / Achieved / Cancelled).
- A goal can be linked to one or more skills drawn from the US-001 catalog; each linked skill carries a target proficiency level expressed on that skill's scale.
- A goal cannot be saved without at least one linked skill and a target completion date that is on or after the goal's creation date.

### AC2 — Progress tracking

- For each linked skill, the goal shows the employee's current proficiency (from US-001) alongside the target proficiency and a derived progress indicator.
- A goal is eligible to be marked Achieved only when every linked skill's current proficiency is greater than or equal to its target proficiency; the system prevents Achieved status while any linked skill is below target.
- Reaching or passing the target completion date without achievement flags the goal as Overdue without changing its status.

### AC3 — Employee development plan view

- An employee can open a read-only development plan that lists their assigned goals with status, target proficiency per skill, target date, and current achievement progress.
- The employee cannot edit goal definitions or targets from this view; it is informational only.

### AC4 — Auditability of goal changes

- Changes to a goal's status, target proficiency, or target date are retained with the previous value, new value, timestamp, and the user who made the change.
- Cancelled and Achieved goals remain visible in history and are available for later review and audit rather than being deleted.

## Out of Scope
<!-- section-key: OutOfScope -->

- The skill catalog and skill assessment mechanics themselves (owned by US-001).
- Performance review execution and reward eligibility (US-003 and US-005).
- Automatic generation of goals from review gaps (the recommendation engine is US-004).
- External LMS course enrollment or training-budget management.

## Open Questions
<!-- section-key: OpenQuestions -->

1. Can an employee propose or self-assign a goal (subject to manager approval), or are all goals created exclusively by the manager/HR?
2. How is "progress" quantified when a skill's scale is non-numeric (e.g. Beginner→Expert) — by ordinal step count, or only as a met / not-met flag?
3. Should goals support intermediate milestones or interim check-in dates, or only a single target completion date?
