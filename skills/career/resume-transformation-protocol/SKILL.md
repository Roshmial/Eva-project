---
name: career:resume-transformation-protocol
description: Specific rules for transforming Misha's career history into high-impact resume content.
category: career
user_locked: true
priority: 95
tags:
  - resume
  - protocol
  - career
version: 1
---

# Skill: Resume Transformation Protocol (Misha Edition)

This skill defines the specific rules for transforming Misha's career history into high-impact resume content.

## Core Principles

1. **Role-Based Identity**: Always frame achievements within the "Strategic IT Architect & Value Manager" persona.
2. **The Four Pillars (Kept Role)**:
    - Case 5 (Architecture/Design)
    - Case 10 (Predictive Modeling)
    - Case 11 (Strategic Selection/Vendor Management)
    - Case 1 (Cost Optimization/ITFM)
3. **Dual-Language Output**:
    - **English (Global Standard)**: Use strong action verbs (Architected, Spearheaded, Orchestrated), focus on business impact and scale.
    - **Russian (Professional Business Style)**: Focus on precision, management terminology, and professional maturity.
    - By default, prepare the pair together: EN as impact-driven market version, RU as exact business version.
4. **Experience Structure**:
    - Flagship roles: Full Impact / project portfolio format.
    - Mid-career roles: Selected Highlights unless more detail is needed to support target positioning.
    - Legacy roles: compact Legacy List.
5. **Fact Fidelity**:
    - Preserve facts, role scope, constraints, and result status 1:1 by meaning.
    - Do not invent metrics, KPI, scale, budgets, or implementation results.
    - If effect is unknown or not measured, keep it explicitly unknown rather than implying achieved business impact.
4. **Handling Unverified Results**:
    - If implementation impact is unknown, focus on:
        - Quality of deliverables (Roadmaps, TCO, Architecture docs).
        - Successful client acceptance (Stakeholder management).
        - Readiness for implementation (Strategic foundation).
5. **Structural Approach**:
    - For flagship roles: Use the "Project Portfolio" structure (Role summary -> Key Strategic Projects).
    - For mid-career: Use "Selected Highlights" (1 strong line) unless the role contains important evidence for the current positioning; in that case, expand it beyond a single line.
    - For legacy: Use "Legacy List" (Name/Role/Dates).

6. **Positioning Guardrail for Misha**:
    - Do not default to "Program Manager" framing when the stronger signal is strategic architecture, IT strategy, value management, or transformation.
    - Prefer positioning that highlights the intersection of enterprise architecture, digital transformation, and IT economics.
    - Treat finance -> strategy -> process management -> digitalization -> architecture as a coherent trajectory, not as disconnected role changes.

7. **Side-Step Roles**:
    - If the user says a role was a side-step or a temporary detour, do not force it into the main career storyline as a "bridge" role.
    - Either compress it heavily or exclude it from the main version if it dilutes the target positioning.
6. **Primary Positioning Bias**:
    - Default away from presenting Misha primarily as a "Program Manager" unless the target vacancy explicitly requires that framing.
    - Prefer positioning around strategic IT architecture, IT strategy, transformation, and value / IT economics.
    - "Program Manager" can remain as a secondary supporting layer, but should not dilute the stronger market signal of architecture + decision support + IT value management.

## Practical Editing Order

When strengthening an already-drafted resume, prefer this safe sequence:
1. Update the headline first to reflect the chosen market identity.
2. Rewrite the top summary so it explicitly connects architecture, transformation, and IT economics.
3. Re-align the core competencies block to match the chosen identity.
4. Only then tighten flagship experience bullets (especially Kept) so the body of the resume confirms the top-level positioning.
5. After the strengthening pass, do a separate readability pass focused on first-impression scanning.

## Readability Pass for Misha

When the resume is already factually strong, improve the overall perception before adding more content:
- Shorten the summary if it starts to read like a dense paragraph; keep the role identity clear in the first 1-2 sentences.
- Reduce "longread" feel in flagship cases by shortening project titles and removing words that do not add signal.
- Prefer compact phrasing over consultant-style heaviness when the same meaning can be preserved.
- Make the top of the resume scannable in 15-20 seconds: headline -> summary -> flagship role identity -> 3-4 strongest signals.
- Treat this as polishing, not amplification: do not add new facts, new metrics, or stronger claims during the readability pass.

## Positioning Pitfalls

- Do not let delivery/program wording overpower the more valuable architecture-and-value narrative.
- Do not describe strong strategic cases as generic project execution if the actual contribution was architecture, roadmap design, TCO logic, operating model definition, or decision support.

## Workflow

1. Receive raw facts/notes from user.
2. Identify which "Pillar" the case belongs to.
3. Draft English version (Impact-driven).
4. Draft Russian version (Management-focused).
5. Review against "Fact Fidelity" rule (no hallucinations).

## Resume Asset Management for Misha

When the user asks whether the latest resume version exists, or asks to continue resume work from a prior session, do not answer from memory alone.

- Verify the actual resume artifacts in the workspace before claiming which version is current.
- Report explicit document names and file paths in the reply so Misha can immediately tell which file is which.
- Treat the RU and EN resumes as a maintained pair: if one is updated, check whether the matching counterpart also needs to be synchronized.
- Keep a single canonical artifact set. Do not create mirrored resume copies in nested folders such as `workspace/workspace/` just to "sync" versions.
- If duplicate resume files already exist, verify which set is canonical, remove the redundant copies, and report only the surviving canonical paths to the user.
- If an alternative positioning version exists for a neighboring target role, present it as a separate track rather than mixing both identities into one resume.
- When summarizing what changed, separate:
  - factual updates pulled from source material;
  - positioning changes;
  - readability/polish changes.
- When choosing a nearby alternative role, prefer the strongest adjacent trajectory that can be supported by existing facts with minimal stretching.

## Session Output Pattern

For resume update sessions with multiple artifacts, end with a concise inventory:
- main RU resume;
- main EN resume;
- alternative RU resume, if created;
- alternative EN resume, if created;
- short note on what changed in each track.
