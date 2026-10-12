---
name: infrastructure-resource-cost-estimation
description: Use when pricing infra resources on a named provider.
triggers:
  - The user asks `сколько это будет стоить`, `оцени по ресурсам`, `what would this cost on X`, or similar.
  - The infrastructure shape is already given as CPU/RAM/storage and key managed services.
  - There is a risk of drifting into migration complexity, fit-gap analysis, or redesign instead of pricing.
---

# Purpose

This skill keeps provider cost estimation anchored to the user’s actual question: price the stated resource envelope on the named platform.

# Core rule

If the user asks for cost, answer cost first.

Do not replace a pricing request with migration-risk commentary, architecture redesign, or provider-fit discussion unless the user explicitly asks for that second layer.

# When to use

Use for:
- cloud-to-cloud price checks;
- provider migration pre-estimates when the user only wants the monthly bill shape;
- rough budget sizing for Kubernetes, VMs, managed databases, Kafka, OpenSearch, storage, and related infra;
- cases where the user already has resource totals and wants a provider-side estimate.

Do not use this skill for full migration assessments, fit-gap discovery, or target-architecture design unless the user asks for those explicitly.

# Procedure

1. Lock onto the requested unit of analysis.
   - Confirm internally: is the user asking about cost, migration effort, or both?
   - If they asked for cost, price the envelope before anything else.

2. Extract the known resource envelope.
   - Separate prod/dev if present.
   - Capture compute, RAM, storage, and any named managed services.
   - Note whether the totals appear to include only compute nodes or also managed-service placement.

3. Use live provider tariffs whenever possible.
   - Prefer current official tariff pages or calculator-backed tariff docs.
   - Map the stated envelope to the nearest explicit tariff rows you can verify.
   - If the exact placement is unknown, choose a defensible closest mapping and label it.

4. Build the estimate around placement assumptions.
   - If the totals are fully specified and clearly all-in, produce a lower-bound estimate.
   - If managed services may sit outside the raw compute totals, add a base estimate with explicit managed-service uplift.
   - If uncertainty remains material, provide a corridor such as minimum / base / upper.

5. Keep the answer structurally simple.
   - What is known.
   - What assumption was used for placement.
   - Monthly estimate.
   - Main uncertainty points.

6. Stop at the budget answer.
   - Mention migration-risk or compatibility factors only as side notes if they directly affect the estimate.
   - Do not turn the reply into a migration memo unless the user asks for that next.

# Output shape

Default answer shape:
- direct monthly estimate or corridor;
- 2–4 short lines on what drives the number;
- explicit uncertainty points;
- links to the tariff sources when useful.

# Pitfalls

- Treating a cost request as an invitation to discuss migration complexity.
- Hiding uncertainty by pretending the totals are unambiguous when managed services may sit outside raw VM totals.
- Refusing to estimate just because the placement is imperfectly known.
- Giving only architecture commentary and no number.
- Using stale or memory-based tariffs when live official tariffs are available.
- Mixing one lower-bound estimate with a totally different architecture alternative without labeling the scenario change.

# For Misha

- If he says `по ресурсам`, `сколько стоит`, or `оцени как есть`, treat that as a scope boundary.
- He strongly prefers a priced answer with explicit assumptions over a technically correct but off-target migration lecture.
- If a previous turn discussed migration, do not let that context override a newer direct cost question.
