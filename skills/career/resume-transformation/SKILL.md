---
name: career:resume-transformation
description: Transforms raw, task-oriented career descriptions into high-impact, achievement-oriented professional summaries and case studies in English and Russian.
user_locked: true
priority: 100
tags:
  - resume
  - career
  - rewriting
  - bilingual
version: 1
---

# Resume Transformation

## Overview

Transforms raw, task-oriented career descriptions into high-impact, achievement-oriented professional summaries and case studies in English and Russian.

## Core Principles

1. **Intellectual Honesty (The Golden Rule):**
   Never invent numbers, percentages, growth metrics, savings, or performance improvements.
   If the user says "designed a system", do not rewrite it as "increased efficiency by 20%".

2. **Impact-Driven Language:**
   Shift emphasis from tasks performed to value delivered.
   Prefer strong action verbs such as "Architected", "Delivered", "Orchestrated", and "Spearheaded".

3. **Artifact-Centricity:**
   For strategy, architecture, operating model, governance, or advisory projects where implementation impact is not directly measurable, focus on the quality, acceptance, and business significance of the deliverables.
   Examples: roadmap, target architecture, TCO model, transformation plan, governance framework, operating model, approved concept.

4. **Bilingual Standard and Naturalness:**
   Always provide two versions unless the user explicitly requests only one:
   - **English (Global Standard):** Use internationally recognizable terminology such as TCO, SLA, scalability, enterprise architecture, operating model, and governance.
   - **Russian (Professional Business):** Do not translate literally. Rewrite into natural, executive-level Russian business language and syntax.

5. **Persona Alignment:**
   Align tone and framing with the user's chosen professional persona, for example "Strategic IT Architect & Value Manager".

6. **Strict Rewrite over Interpretation:**
   Prefer rewriting, clarifying, and strengthening the user's original meaning over combining facts into new conclusions.
   Summarize or infer only when the user explicitly asks for summary, synthesis, or interpretation.

## Transformation Workflow

1. Extract only explicit facts from the raw source text.
2. Separate responsibilities, deliverables, decisions, and measurable outcomes.
3. Identify the primary value point:
   - a measurable outcome, if explicitly present;
   - otherwise the most important accepted deliverable or strategic contribution.
4. Draft the English version using concise, impact-focused business language.
5. Draft the Russian version using natural professional Russian phrasing, not literal translation.
6. Verify that no unverified claims, metrics, or invented business effects were added.
7. Return both language versions in clearly labeled sections.

## Output Rules

- Prefer bullet points over long paragraphs when writing resume-style content.
- Keep each bullet focused on one contribution or outcome.
- Remove repetition, weak fillers, and vague phrases such as:
  - responsible for
  - participated in
  - helped with
  - was involved in
- Replace weak phrasing with precise contribution wording, but only within the bounds of the original facts.
- If the user provides insufficient detail, ask a targeted follow-up instead of fabricating stronger content.

## Pitfalls and Lessons Learned

- **Interpretation Trap:** Do not merge separate facts into a stronger combined claim unless the source explicitly supports it.
- **Translation Syndrome:** Russian output must sound like original Russian executive writing, not translated English.
- **Language Consistency:** Keep explanations in the user's current language unless asked otherwise.
- **Metric Inflation:** If no metric exists, do not imply one.

## Default Output Structure

### English Version

- Bullet 1
- Bullet 2
- Bullet 3

### Russian Version

- Пункт 1
- Пункт 2
- Пункт 3