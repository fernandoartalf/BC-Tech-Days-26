<!-- PLAN-DOC-BC-003 heading rules: H2s must NOT carry a manual numeric prefix (template auto-numbers) and MUST NOT end with a source-ID suffix like '(from US-NNN)'. H3 subsection labels keep the 'N.M ' prefix shape but translate the label text. See SKILL.md "Heading & full-content translation rules". -->
---
id: US-004
title: Skill Improvement Recommendations
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

# US-004 — Skill Improvement Recommendations

## User Story
<!-- section-key: UserStoryStatement -->

**As a** reviewer (line manager or HR),
**I want** the system to identify the skills that need improvement from a completed review and let me record recommended development actions,
**so that** every review with an identified gap produces a concrete, trackable improvement plan rather than an undocumented intention.

## Business Context
<!-- section-key: BusinessContext -->

A review (US-003) is only valuable if its conclusions drive action. Once a review is completed, the organization wants the gaps between current and expected proficiency surfaced automatically, and a structured place for the reviewer to record what the employee should do next. Today the gap analysis is done in the reviewer's head and the recommended actions, if written at all, are not linked to the skills they address.

The customer's pain points are:

- After a review, skill gaps are identified informally and inconsistently, so two reviewers looking at the same data recommend different things.
- Recommended development actions are not linked to the specific skill they target, so progress against them cannot be measured later.
- There is no list of "employees with identified improvement areas," so HR cannot see across the organization where development effort is needed.

## Current Situation (Standard Business Central)
<!-- section-key: CurrentSituation -->

Verified on Microsoft Learn (Business Central Human Resources documentation):

- Standard BC Human Resources stores qualifications and employee master data but contains no mechanism to compare a current proficiency against an expected/target level.
- There is no standard concept of a "skill gap" nor any object to record recommended development actions against an employee or a skill.
- Standard BC provides no cross-employee view of identified improvement areas resulting from an evaluation.

**Conclusion:** Standard BC has neither gap detection nor a recommendation record. This story closes the gap by deriving skills-to-improve from a completed review (US-003) using the catalogued skills and goal targets (US-001, US-002), and by capturing recommended development actions linked to the specific skills they address.

## Acceptance Criteria
<!-- section-key: AcceptanceCriteria -->

### AC1 — Gap identification from a completed review

- For a Completed review, the system lists the employee's skills whose current proficiency is below the relevant target (the target from a linked development goal where one exists, otherwise a configurable expected level).
- Each identified gap shows the skill, current proficiency, target proficiency, and the size of the shortfall.
- If no skill is below target, the review explicitly records "no improvement areas identified" rather than leaving the result blank.

### AC2 — Recommended development action entry

- For each identified gap, the reviewer can add one or more recommended development actions, each with a description and an optional target date, linked to the specific skill.
- The reviewer can also add a recommended action manually for a skill that the gap logic did not flag.
- A recommendation cannot be saved without a linked skill and a non-empty description.

### AC3 — Improvement plan visibility and auditability

- All recommendations for an employee are viewable as an improvement plan, grouped by skill, showing source review, recommended action, target date, and status (Open / Done / Cancelled).
- A cross-employee list shows all employees with at least one open improvement area, filterable by skill and by review period.
- Recommendations and their status changes are retained with timestamp and acting user, and remain available for audit after the originating review is closed.

## Out of Scope
<!-- section-key: OutOfScope -->

- Execution or delivery of the development actions (e.g. booking training, LMS enrollment).
- Automatic creation of US-002 development goals from recommendations (may be a future enhancement).
- Reward eligibility calculation (US-005).
- The review process and skill/goal data capture themselves (US-003, US-001, US-002).

## Open Questions
<!-- section-key: OpenQuestions -->

1. When no development goal exists for a skill, what defines the "expected level" used to detect a gap — a per-role expected profile, a per-skill default, or reviewer judgement only?
2. Should a recommendation be auto-converted into a development goal (US-002), or do the two remain deliberately separate artefacts?
3. Who can close or cancel a recommendation — the originating reviewer only, any manager, or HR — and is employee confirmation required?
