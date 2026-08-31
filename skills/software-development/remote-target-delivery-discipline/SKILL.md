---
name: remote-target-delivery-discipline
description: Use when a named remote host needs live turnkey delivery.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Remote target delivery discipline

## When to use

Use this skill when:
- the user names a concrete remote runtime such as a prod server, VPS, or known SSH host;
- the user asks to build, fix, deploy, or finish something on that target;
- the user expects not just code changes, but a real end-to-end result on the live host.

## Core rule

Treat the named remote host as part of the deliverable, not as optional follow-up context.

If the host was already identified earlier in the thread, do not bounce back into repeated host clarification until you have re-checked the existing thread context and the live paths you already used in the same session.

## Workflow

1. Re-anchor on the exact target.
- Re-read the thread for the canonical host mapping.
- Prefer the already established live target over re-asking.
- Ask only when the mapping is genuinely missing or conflicting.

2. Verify live access first.
- Confirm SSH or the relevant remote access method works.
- Confirm the project path, service name, and runtime entrypoint on that host.

3. Implement locally only as an intermediate step.
- Make the code or config change.
- Run minimal local syntax checks when cheap.
- Move the artifact to the named host.

4. Verify on the target.
- Run target-side tests.
- Restart or reload the real service.
- Check service status after restart.
- Hit the live endpoint on the remote host.

5. Close with a real end-to-end user flow.
- Do not stop at health or CRUD checks if the user asked for a full cycle.
- Create a deterministic demo entity or fixture.
- Drive that entity through the whole product chain using only the shipped functionality.
- Capture the resulting artifact or report path.

## User-specific pitfall

### Pitfall: losing the target nickname mapping mid-session
Symptom:
- the user says a short name like `178` that was previously established as a real production host;
- the assistant treats it as unknown and asks for the IP again.

Why this is bad:
- it signals avoidable context loss;
- it delays action on the exact runtime the user already meant.

Correction:
- before asking again, search the active thread mentally and any current deployment notes for the mapping;
- if the runtime was already named earlier, act on it immediately and verify.

### Pitfall: reporting backend readiness without a full product pass
Symptom:
- tests pass and the service is up;
- but no single character, item, or user-facing entity was driven through the full chain.

Correction:
- create one deterministic fixture character or entity;
- run import/create/process/review/accept/query through the live API or UI;
- report the exact result and where the detailed report is stored.

## Minimum completion bar

A remote turnkey task is not complete until all of these are true:
- the named host was actually used;
- target-side tests passed;
- the live service is active after restart;
- one end-to-end scenario completed on the real target;
- the final answer names the exact artifact, id, or report proving that scenario.
