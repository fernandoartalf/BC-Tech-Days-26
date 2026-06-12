<!-- PLAN-DOC-BC-003 heading rules: H2s must NOT carry a manual numeric prefix (template auto-numbers) and MUST NOT end with a source-ID suffix like '(from US-NNN)'. H3 subsection labels keep the 'N.M ' prefix shape but translate the label text. See SKILL.md "Heading & full-content translation rules". -->
---
id: US-003
title: Employee Performance Review Process
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

# US-003 — Employee Performance Review Process

## User Story
<!-- section-key: UserStoryStatement -->

**As a** line manager (reviewer),
**I want** to schedule and execute periodic employee reviews that evaluate the employee's current skills and assigned goals, capture observations and recommendations, and store the outcome historically,
**so that** performance is assessed through one standardized, repeatable process and every review outcome is preserved and linked to the employee for audit.

## Business Context
<!-- section-key: BusinessContext -->

With skills (US-001) and goals (US-002) recorded, the organization needs a periodic event that brings them together: a review where a manager evaluates where the employee stands, documents conclusions, and produces an outcome that downstream processes (improvement recommendations US-004, reward eligibility US-005) can consume. Today reviews are run inconsistently and their outcomes live in disconnected documents.

The customer's pain points are:

- Reviews are conducted differently by each manager, so outcomes are not comparable across teams and cannot be reported on uniformly.
- Review conclusions are stored in documents outside Business Central and are not linked to the employee record, making history hard to retrieve for an audit.
- Because reviews do not read the employee's actual skills and goals from BC, the evaluation is subjective and disconnected from the data captured in US-001 and US-002.

## Current Situation (Standard Business Central)
<!-- section-key: CurrentSituation -->

Verified on Microsoft Learn (Business Central Human Resources documentation):

- Standard BC Human Resources lets you register and maintain employee records, employment details, qualifications, confidential information, contacts, and absences, but it has no performance-review object or process.
- There is no standard page or table to schedule a review, evaluate an employee's skills and goals at a point in time, or record reviewer observations and recommendations as a structured outcome.
- Standard BC has no historized review ledger linked to the employee, so prior review outcomes cannot be retrieved as immutable records.

**Conclusion:** Standard BC maintains employee master data but provides no performance-review capability. This story closes the gap with a schedulable, executable review that snapshots the employee's US-001 skills and US-002 goals, records observations and recommendations, and stores an immutable, employee-linked outcome.

## Acceptance Criteria
<!-- section-key: AcceptanceCriteria -->

### AC1 — Review scheduling

- A reviewer or HR administrator can schedule a review for a specific employee with a review period, a scheduled date, and an assigned reviewer; the review opens in status Scheduled.
- A review cannot be scheduled without an assigned reviewer and a scheduled date, and the scheduled employee must exist as a Business Central employee.

### AC2 — Review execution against skills and goals

- When the reviewer opens a Scheduled review for execution, the review captures the employee's current skill assessments (US-001) and assigned goals with their achievement status (US-002) as a point-in-time snapshot.
- The reviewer can rate or comment on each captured skill and goal line; the review cannot move to Completed while any mandatory evaluation line is blank.

### AC3 — Review outcome storage and employee link

- On completion the review records an overall outcome, the reviewer's observations, and recommendations; the completed review's status becomes Completed and its date-completed is stamped.
- The completed review and its captured lines are stored historically, linked to the employee record, and become read-only.

### AC4 — Review history and auditability

- All reviews for an employee (Scheduled, Completed, Cancelled) are listed chronologically and can be opened to inspect the exact skills, goals, observations, and recommendations captured at the time.
- A Completed review cannot be edited or deleted; corrections require a new review. Every status change retains timestamp and acting user for audit.

## Out of Scope
<!-- section-key: OutOfScope -->

- 360-degree / multi-rater feedback collection.
- The improvement-recommendation generation logic itself (US-004 consumes review results).
- Reward eligibility calculation (US-005).
- Definition and assessment of skills and goals (US-001 and US-002).
- Payroll and compensation posting.

## Open Questions
<!-- section-key: OpenQuestions -->

1. What review cadence and periods must be supported (annual, semi-annual, ad hoc), and can multiple open reviews coexist for the same employee?
2. Does the process require employee acknowledgement / sign-off of the completed review, and should the employee see the outcome through a self-service view?
3. Should review scheduling be automatable (e.g. via a recurring job) or is manual scheduling sufficient for the first release?
