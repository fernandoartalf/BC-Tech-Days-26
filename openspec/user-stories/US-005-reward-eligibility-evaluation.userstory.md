<!-- PLAN-DOC-BC-003 heading rules: H2s must NOT carry a manual numeric prefix (template auto-numbers) and MUST NOT end with a source-ID suffix like '(from US-NNN)'. H3 subsection labels keep the 'N.M ' prefix shape but translate the label text. See SKILL.md "Heading & full-content translation rules". -->
---
id: US-005
title: Reward Eligibility Evaluation
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

# US-005 — Reward Eligibility Evaluation

## User Story
<!-- section-key: UserStoryStatement -->

**As an** HR administrator,
**I want** to evaluate an employee's reward eligibility against configurable policies that weigh review outcomes and goal achievement, and to store the resulting decision,
**so that** compensation and reward decisions are calculated consistently from objective criteria and every decision is auditable.

## Business Context
<!-- section-key: BusinessContext -->

The final step of the growth process is turning measured performance into a defensible reward decision. The organization wants the inputs already captured — completed reviews (US-003) and achieved development goals (US-002) — fed into a configurable policy that yields a clear Eligible / Not Eligible result, stored for audit. Today reward eligibility is decided on judgement, applied inconsistently, and poorly documented.

The customer's pain points are:

- Reward decisions are made subjectively, so comparable employees can receive different outcomes and the basis cannot be explained.
- The criteria that should drive eligibility (review outcome, goal achievement) are not encoded anywhere, so the rule effectively changes from manager to manager.
- Decisions are not recorded against the employee with their inputs, leaving no audit trail to justify a reward — or its absence — after the fact.

## Current Situation (Standard Business Central)
<!-- section-key: CurrentSituation -->

Verified on Microsoft Learn (Business Central Human Resources documentation):

- Standard BC Human Resources maintains employee records and can reimburse employees for expenses, but it has no concept of reward or compensation eligibility based on performance criteria.
- There is no standard policy object that weighs review outcomes or goal achievement, and no standard calculation that produces an eligibility decision.
- Standard BC offers no historized store of reward decisions linked to the employee and the inputs that produced them.

**Conclusion:** Standard BC has no performance-driven reward eligibility capability. This story closes the gap with configurable eligibility policies that consume US-003 review outcomes and US-002 goal achievement, compute an eligibility decision, and store that decision with its inputs for audit. Payroll and actual payout remain out of scope.

## Acceptance Criteria
<!-- section-key: AcceptanceCriteria -->

### AC1 — Configurable reward policy

- An HR administrator can define one or more reward eligibility policies, each with a code, description, validity period, and a set of weighted criteria referencing review outcome and goal achievement.
- A policy must specify an objective eligibility threshold (e.g. minimum weighted score) so that the eligibility result is deterministic for a given set of inputs.
- A policy that has been used to produce a stored decision cannot be edited in place; a new version must be created, preserving the policy as it stood when past decisions were made.

### AC2 — Eligibility calculation

- For a selected employee and an applicable policy, the system computes eligibility from the employee's completed review outcome(s) in the period and the achievement status of their development goals.
- The calculation produces a deterministic result — Eligible / Not Eligible — together with the contributing input values and the resulting score; running the calculation twice on unchanged inputs yields the same result.
- The calculation refuses to run when no completed review exists for the employee in the policy's period, and reports that precondition clearly.

### AC3 — Decision storage and auditability

- The eligibility result is stored as a reward decision linked to the employee, the policy (and its version), the review(s) and goals used as inputs, the computed score, the outcome, the decision date, and the deciding user.
- Stored reward decisions are read-only and retained historically; a superseding decision creates a new record rather than overwriting the prior one.
- All reward decisions for an employee, and across employees for a period, are listable and filterable for audit.

## Out of Scope
<!-- section-key: OutOfScope -->

- Payroll processing and the actual payout or posting of any reward.
- Employee benefits administration.
- Approval workflow / routing of the reward decision (may be a future enhancement).
- The review process and goal/skill data themselves (US-001 through US-003).

## Open Questions
<!-- section-key: OpenQuestions -->

1. What exactly are the weighted criteria and threshold for the initial policy (e.g. review outcome ≥ X AND ≥ N% of goals Achieved), and who signs off on the policy definition?
2. Does a reward decision require an approval step before it is considered final, or is the calculated, stored decision sufficient for the first release?
3. How should already-stored decisions behave when a contributing review is later found to be in error — locked as historical fact, or superseded by a new decision that references the correction?
