---
name: prompt-surface-optimization
description: "Use when Hermes needs material token savings safely."
version: 1.0.0
created_by: agent
---

# Prompt-surface optimization

## Procedure

1. Measure the correct fixed surface for the affected platform.
- Run `hermes prompt-size --platform <platform> --json` before changes.
- Compute fixed surface as `system_prompt + memory + user_profile + tools.json_bytes`.
- Treat `skills_index` as a diagnostic subset of `system_prompt`; never add it again to the total.

2. Measure actual use before restricting capability.
- Query the profile `state.db` read-only over at least 30 days.
- Count `skill_view` loads by skill, tool calls by tool name, model input/output/cache tokens, and completed delegations.
- Keep frequently used and essential skills visible. Do not decide from on-disk `SKILL.md` size: full skill bodies are not in every prompt.

3. Prefer a focused dynamic skill index over deletion.
- Select skills from recent `skill_view` frequency using explicit policy fields: platform, window days, minimum loads, and maximum visible skills.
- Keep the full installed catalog available through `skills_list` when no focused skill fits.
- Make telemetry lookup read-only and fail open to the complete index if the usage store cannot be queried; optimization must not remove capabilities during telemetry failure.
- Add a focused test with an isolated SQLite fixture covering frequent, rare, essential, and unavailable-store behavior.

4. Treat tool pruning separately.
- Do not remove terminal, file, browser, web, session search, or skills merely because their schemas are large when telemetry shows regular use.
- Consider on-demand exposure only for tools with low use and a verified discovery path.

5. Verify effect and live state.
- Run focused regression tests, `py_compile` for touched Python modules, and `git diff --check`.
- Re-run `hermes prompt-size` and report the measured before/after bytes and percentage.
- Distinguish saved configuration/source from live effect when the gateway has not loaded the new code. Do not restart an active gateway casually just to demonstrate the result.

## Acceptance threshold

Do not present cosmetic reductions as a completed optimization. For an established personal profile, target a material fixed-surface reduction, normally at least 15%, while retaining a full discovery path for rarely used capabilities.

## Pitfalls

- Preserve the full catalog behind `skills_list`; frequency filtering without discovery turns an optimization into silent capability loss.
- Count `system_prompt` only once; `skills_index` is already included and double-counting exaggerates savings.
- Avoid static per-session allowlists; frequency-driven policy adapts as the user’s work changes.
- Keep telemetry queries bounded and read-only because prompt assembly runs on the hot path.
