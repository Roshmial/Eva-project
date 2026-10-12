---
name: infrastructure-diagnostic-questionnaires
description: Use when designing infrastructure diagnostic questionnaires.
version: 1.0.0
metadata:
  hermes:
    tags: [consulting, infrastructure, questionnaire, cloud, rsm]
---

# Infrastructure diagnostic questionnaires

## Framing

- Define the subject as the infrastructure contour: data centers, compute, hardware, virtualization, networks, storage, private/public cloud, shared platform services, observability, operations, resilience, lifecycle, capacity, and infrastructure economics.
- Default AI scope to infrastructure readiness: compute/GPU capacity, storage, network, data access paths, isolation, provisioning, observability, utilization, and cost. When the user explicitly wants the employee-facing layer, include external AI-service usage, understandable data-handling rules, approved access paths, integration, ownership, and Shadow AI; label these as an adjacent user/governance module so they do not distort the infrastructure maturity score.
- Present cloud and hybrid placement as possible outcomes of analysis, never as predetermined answers.
- Start with situations clients actually recognize: demand outgrows capacity, costs rise, support becomes more expensive, provisioning is slow, repetitive work is manual, failures are hard to diagnose, visibility is incomplete, business/security requirements grow, and vendor or regulatory conditions change.
- Convert vague phrases into observable symptoms. Replace “lack of control” with missing visibility into assets, utilization, dependencies, owners, cost, changes, and policies.
- Avoid claiming outage frequency is universally rising. Say complexity, localization difficulty, external/cyber risks, and consequences of downtime are increasing unless specific evidence supports more frequent incidents.

## Scope, title, and research promise

Lock the object before writing titles or questions. Distinguish three adjacent scopes and never substitute one for another:

- `all IT` includes applications, product delivery, data, organization, and business demand; use it only when those areas are genuinely in scope;
- `infrastructure management practices` is a narrow governance/process lens; use it for a maturity module, not as the title of a broader infrastructure study;
- `the infrastructure contour` covers resilience, operations, capacity, cost, lifecycle, modernization, platform controls, and readiness for new workload classes.

For a broad infrastructure study, prefer a concrete title pattern: `ИТ-инфраструктура компаний: устойчивость, эффективность и приоритеты развития`. Follow it with a scope subtitle that names the covered areas. Avoid abstract stacks of nouns such as “state, efficiency and development” when the title can name the decisions or outcomes directly.

Use headings that tell the participant what the section is about. Prefer `Как проходит исследование`, `Что получит участник`, `Какие темы мы изучаем`, and `Вопросы об устойчивости и восстановлении`. Avoid process jargon such as `архитектура диалога`, `единая рамка результата`, `маршрутизация`, and `предметное продолжение` in participant-facing copy; reserve methodological terms for internal instructions.

## Unified front door and routing

When several questionnaires cover adjacent topics, do not present them as competing products. Build one front door and route from the management problem:

1. Run a 20–30 minute executive conversation before any detailed questionnaire.
2. Fix six fields: what changed; business consequence; feared or blocked scenario; available evidence; decision to prepare; owner and decision horizon.
3. Branch by task model. For presale, select one primary track and at most one linked secondary track. For comparative research, require the same compact core from every participant, then open at most two applicable modules; otherwise branching destroys benchmark comparability.
4. Use topic modules for resilience/recovery, service provisioning, operations, capacity/platforms, infrastructure economics, AI readiness, and engineering standardization. Treat a cross-domain maturity benchmark as an analysis mode assembled from the common core, not as another competing module.
5. Record why a module was skipped: insufficient data, outside the respondent's responsibility, not applicable, or not shown by branching. Never merge these codes.
6. Choose depth only after routing: express survey, expert session, or comprehensive diagnosis.

For sales communication, keep a four-part one-pager: `Что` (one entry and routed diagnosis), `Для кого` (decision owners), `Зачем` (the decision enabled), and `Что сказать` (a short client-ready opening). Lead with business pressure and the decision to prepare; keep technology and products downstream.

Before building a slide, Gamma deck, or polished visual, agree the content architecture with the user. Treat visual-production wording as permission to execute only after the positioning and slide logic are explicit; otherwise a polished artifact can prematurely lock the wrong commercial model.

## Deliverable architecture

When consolidating several questionnaires into one final document, preserve four distinct layers in this order:

1. `OnePager` — the participant invitation: subject, audience, relevance, time, confidentiality, what the participant receives, and how to take part.
2. `Концепция` — research purpose, scope boundary, target sample, unit and period of analysis, branching, scales, evidence rules, confidentiality, analysis method, and output policy.
3. `Входной опрос` — respondent profile, object of analysis, current context, and routing into applicable modules.
4. `Детальный опрос` — complete questions by selected infrastructure module, response scales, safe evidence prompts, and rules for interpretation.

If the primary model is presale or a paid diagnostic product, adapt these four layers explicitly to that model. Never let a sales-oriented template silently redefine a research task.

Do not compress these layers into one attractive process diagram. A one-page view may summarize the full architecture, but it must retain the commercial promise, target audience, trigger situations, routing tracks, client output, data captured, and conversion into a value proposition. If all fields cannot remain readable, keep the full DOCX as the source of truth and derive visuals only after approval.

First establish whether the primary purpose is research, presale qualification, or a paid diagnostic product; do not merge these models. When the stated task is to conduct a market or industry study, keep the study primary throughout the OnePager, concept, entry questionnaire, and detailed questionnaire. Invite representatives transparently, explain who runs the study, how answers are used, confidentiality, time required, and what the participant receives. Use the entry block to establish respondent profile and route applicable sections, not to qualify a sales lead. Use comparable scales, explicit “unable to assess” and “not applicable” options, respondent-role checks, and branching rules. Return an individual profile and benchmark only after a sufficient comparable sample exists. Keep expert or commercial follow-up optional and downstream of the participant receiving the research result. Avoid synthetic presale phrases such as “diagnostic entry,” “value hypothesis,” and “subject-matter continuation” when natural research language is available.

## Diagnostic structure

Use dimensions that connect naturally to decisions:

1. Business demand, capacity, and growth constraints.
2. Full infrastructure economics and cost transparency.
3. Provisioning speed and process handoffs.
4. Reliability, operations, and manual work.
5. Architecture, governance, and security consistency.
6. Automation and AI in infrastructure operations.
7. Criteria and readiness for cloud/hybrid placement.
8. External constraints and investment priorities.

Use a descriptive 1–4 or 1–5 practice-stage scale consistently; choose the length before the pilot and do not change it mid-sample. Measure coverage, evidence quality, actual ranges, and skip reason separately: one maturity score must not mix existence, regularity, reach, formalization, and measurability. Treat inability to assess as a transparency signal, never as zero or a neutral mature answer.

## Engineering profile and efficiency

Always inventory the engineering profile before claiming a market position or efficiency gap. Ask for ranges rather than confidential exact values, and keep descriptive profile variables outside the maturity index:

- approximate physical-host count, virtual workloads, container nodes, sites/regions, and managed platforms;
- CPU/RAM utilization, workload density, capacity reserve, and CPU/RAM oversubscription by workload class;
- normalized unit cost such as vCPU-hour only when the TCO boundary, reserved capacity, utilization basis, and service level are comparable;
- storage mix across classical arrays, software-defined storage, and cloud block/object/file services; avoid value-laden wording such as “still uses SAN”;
- number of server, storage, and network equipment brands, plus whether diversity is deliberate resilience or unmanaged fragmentation;
- share of Shadow IT / unknown assets, workloads, spend, or environments outside inventory and standard controls;
- EOL/EOS exposure, platform diversity, supplier concentration, and key-person dependency;
- lead time and repeatability of onboarding a team, service, platform, or environment;
- codified delivery and controls: IaC, policy as code, architecture as code, backup/DR as code, observability as code, standard modules, golden paths, and exception handling.

Do not infer maturity from a raw number alone. High oversubscription, many brands, classical storage, or a low vCPU price can each be appropriate in context; interpret them with workload class, resilience, utilization, support model, and lifecycle constraints.

## Interpretation

Map combinations of symptoms to management scenarios rather than products:

- demand growth + capacity shortage + weak forecast → capacity model and placement options;
- rising cost + low transparency → service economics and RSM/TBM/FinOps mechanisms;
- slow provisioning + manual work → process redesign, service catalog, IaC, self-service;
- incidents + weak observability + key-person dependency → observability and operations automation;
- growing security requirements + fragmented platforms → common policies and automated controls;
- AI demand + GPU scarcity + project-based provisioning → shared AI capacity service and hybrid placement;
- EOL/licensing/vendor pressure + legacy → modernization and migration scenarios.

Keep RSM, automation, security, AI, and hybrid infrastructure as derived responses to diagnosed constraints. Do not force every scenario to include every solution.

## Output contract

For comparative research, lead with the participant promise: `understand your market position and identify development points`. Return two distinct products:

1. Individual result: participant value, median and interquartile range for a comparable group, whole-sample reference, sample size, data period, strengths, notable deviations, data gaps, and up to three development points.
2. Aggregate study: research passport, market context, distributions, differences between comparable groups, problem map, practice radar, 12–24 month priorities, applicability conditions, and evidence-backed conclusions.

Borrow the result logic of benchmark products such as TeDo MAYAK and industrial technology radars: show the participant beside a peer group and turn aggregate findings into a connected story. Do not copy branding or claim a comparison before the sample supports it.

Show diagnostic tracks through one management card so results remain comparable:

`safe fact → business consequence → status and confidence → options → possible first-wave action → expected output → owner and review date`.

Use examples only to illustrate the result format. Label every number as illustrative unless it comes from real responses or a cited source. Never name or rank real companies in maturity examples without a published, methodologically compatible source; use anonymized company profiles instead. Do not turn a missing fact into a negative maturity score. A short survey returns development points and hypotheses; concrete recommendations and 30/60/90 plans require deeper evidence or a separate diagnostic.

## Quality review

Before delivery, review the complete chain rather than each questionnaire in isolation:

- Connectedness: the OnePager promise must be fulfilled by the entry questions, detailed track, and result card.
- Logic: every entry answer must influence routing, qualification, or the next meeting; remove questions that have no decision use.
- Currency: use current official frameworks only as methodological references, not as borrowed authority or invented benchmarks.
- Liveliness: phrase questions as recognizable management situations and follow-ups, not as an audit checklist.
- Survey validity: ask one construct per question; remove double-barreled formulations, leading answers, vendor vocabulary, and assumptions that a practice must exist. Make response options exhaustive, mutually intelligible, time-bounded where needed, and include `затрудняюсь оценить` and `неприменимо`.
- Clarity: define the infrastructure boundary, object, time period, evidence standard, respondent role, and the difference between facts, interpretation, and potential effect.
- Headings and wording: read every participant-facing title as a representative of the target role would. Reject abstract nouns, internal consulting language, hidden sales framing, and labels broader or narrower than the actual questionnaire scope.
- Client interest: every block must answer why the representative should participate and what useful result they receive from the study itself; optional expert or commercial discussion comes after that result.
- Preservation: when adapting or shortening, inventory all semantic blocks first and explicitly verify that target audience, client triggers, key questions, routing, participant output, research data, and next step remain present.
- Benchmark readiness: define peer-group dimensions, minimum core-question coverage, missing-value handling, minimum group size, suppression rules for small cells, statistics, and data-validity period before promising “market position.” Prefer median and interquartile range over an unsupported league table.
- Launch gate: treat 5–8 interviews as a wording/timing pilot, not a market benchmark. After the pilot, calibrate question comprehension, answer ranges, branch rates, duration, and interviewer consistency before broad fieldwork.
