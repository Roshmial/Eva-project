---
name: comparative-research-delivery
description: Deliver iterative comparative research and client-facing studies without drifting from the user's requested comparison frame, unit of analysis, or structural format.
---

# When to use

Use for client-facing analytical documents, market studies, vendor comparisons, shortlist memos, and any iterative rewrite where the user specifies **how the comparison must be structured**.

Typical triggers:
- the user asks to compare vendors / products / solutions in a specific frame;
- the user says "compare each system by ..." or "do not compare by class / by market in general";
- the document is being revised section by section and the user is correcting structure, not only wording;
- the work mixes analytical framing, shortlist logic, and delivery into a final document.

# Core rule: preserve the comparison frame exactly

In these tasks, the biggest failure mode is not factual error but **frame drift**: the agent silently changes the unit of analysis or the comparison logic.

Before editing, identify which of these modes the user wants:

1. **Per-system by criteria blocks**
   - Example: "compare each system by 10 blocks of criteria".
   - Output shape: system A -> blocks 1..N; system B -> blocks 1..N.

2. **Per-criteria market synthesis**
   - Example: "show what the market usually reveals on security / pricing / governance".
   - Output shape: block 1 -> market picture; block 2 -> market picture.

3. **By solution class / segment**
   - Example: "separate agent platforms, embedded AI, document AI, RPA, ML platforms".
   - Output shape: class A -> members / characteristics; class B -> members / characteristics.

These three modes are **not interchangeable**. If the user asked for one, do not substitute another just because it seems analytically cleaner.

# Mandatory workflow for iterative corrections

When the user objects to structure, do this:

1. Extract the exact complaint.
   - Example: "not by classes; compare each system by 10 blocks".
2. Restate the target shape in one sentence internally before editing.
3. Edit only toward that shape.
4. Verify that the new section's headings and repeated pattern actually match the requested frame.
5. In the reply, explicitly acknowledge the previous frame mistake if there was one.

Do not answer with "fixed" unless the section was actually rewritten and the artifact rebuilt.

# Structural translation guide

If the user asks for **each system by 10 blocks**, the section should normally look like:

- System 1
  - Block 1: ...
  - Block 2: ...
  - ...
  - Block 10: ...
- System 2
  - Block 1: ...
  - ...

Not acceptable substitutes:
- one aggregated table for all systems with generic ratings;
- one section per block describing the market overall;
- one section per solution class instead of one section per system.

# Comparison without fake precision

When the user rejects "high / low", "good / bad", or synthetic scores:
- keep the same comparison frame;
- replace ratings with factual descriptors;
- use formulations like:
  - what is publicly stated;
  - what appears to be the main scenario;
  - what remains unclear from open materials;
  - what requires demo / pilot / technical session / reference check.

Important: removing ratings does **not** justify changing from per-system to per-class or per-market structure.

# Handling user frustration correctly

If the user says variants of:
- "that wasn't the question";
- "why is it structured like this?";
- "not this, do it by ...";
- "each system, not the market overall";

treat this as a workflow correction. The answer should:
1. acknowledge the mismatch briefly;
2. switch to the requested unit of comparison;
3. avoid defending the previous analytical choice.

# Practical checklist before final delivery

Confirm all of the following:
- The section uses the user-requested unit of analysis.
- Headings and repetition pattern match that unit.
- No hidden drift from per-system to per-class or per-market summary.
- No synthetic scoring if the user banned it.
- If the task is document editing, the final artifact has been rebuilt after the rewrite.
- For a strategy, transformation, architecture, or market-study document, constraints are covered in a distinct block instead of being diluted into generic risks: regulation and safety, legacy data and integration, external dependencies, organizational authority, economics, data rights, cybersecurity, and realistic time horizon.

# Strategy and transformation documents: constraints are part of the frame

A document about a future operating model is incomplete when it describes only the target state, use cases, and roadmap. Add a visible **Constraints / limitations** section unless the user explicitly requests a short concept note.

Separate two layers:
- **Risks:** what may go wrong during implementation or operation.
- **Constraints:** durable boundaries that shape what is feasible, in what sequence, and for which scope.

For regulated, multi-party industries such as aviation, check at least:
- safety, certification, passenger rights, labour rules, and other regulation;
- legacy systems, fragmented ownership, data latency, and data quality;
- dependencies on airports, regulators, partners, or public infrastructure;
- economic proof and the cost of integration and change;
- authorization boundaries, explainability, manual override, and fallback procedures;
- privacy, consent, and cybersecurity;
- a realistic horizon for a limited internal rollout versus a cross-industry end state.

# Evidence maturity in case-based market research

When a report uses public company cases to support a transformation thesis, classify every example before writing it into the document. Do not let an attractive press release turn an announced direction into a working operating model.

Use a visible, compact vocabulary:
- **in regular operation** — source confirms use in production and, where possible, scope or duration;
- **limited rollout / pilot** — source confirms trial, beta, selected locations, or a bounded customer group;
- **announced direction** — partnership, plan, target, or intent; no evidence of scaled use yet;
- **industry infrastructure / standard** — regulator, association, or interoperability programme; not a carrier case;
- **manufacturer or supplier R&D** — technology trajectory, demo, prototype, or enabling component; not proof of airline adoption.

Countercheck each case against the primary source immediately before final delivery:
1. Verify the exact actor: airline, airport, regulator, manufacturer, supplier, or research partner.
2. Verify the verb and tense: launched, operates, trialled, plans, announced, explores, or demonstrated.
3. Verify scope, geography, and date when the claim depends on them.
4. Separate company-reported KPIs from independent evidence; retain attribution to the company.
5. Mark illustrative scenario numbers as illustrative, never as a case KPI.
6. If an exact statement cannot be confirmed publicly, narrow the wording or remove it.

For future-vision sections, distinguish three voices:
- **carrier practice** — what has been deployed or tested;
- **industry and regulator direction** — IATA, ICAO, EASA, FAA, CAAC, EUROCONTROL and similar bodies;
- **manufacturer horizon** — Boeing, Airbus, COMAC and other OEMs, whose work indicates technology direction but does not establish airline-operating maturity.

# Pitfalls

## Pitfall: presenting an announcement, industry programme, or OEM demo as a deployed airline case

A partnership announcement, a trade-association programme, and a manufacturer's autonomous-flight demonstration carry different evidentiary weight. In a case matrix, label their maturity and actor explicitly. Keep them useful as signals of the future, but do not use them to prove that an airline has already transformed its operation.

## Pitfall: replacing the user's frame with a "cleaner" analytical frame

A common mistake is to decide that class-based comparison or market-level synthesis is methodologically better and silently replace the user's requested structure with it. In consulting delivery this is a real error, even if the alternative is analytically defensible.

## Pitfall: preserving the criteria but changing the comparison unit

Using the same 10 blocks is not enough if they are applied to the market overall instead of to each system. The blocks and the unit of analysis must both match the user's request.

## Pitfall: reporting completion before the artifact reflects the change

For file deliverables, do not claim the section is corrected until the file was actually rewritten and rebuilt.

# Preferred delivery style for this class of task

- Calm and direct.
- Briefly separate: what was wrong in the previous framing, what was changed now.
- Do not over-explain methodology after the user already gave the structural instruction.
- In Russian-language client documents, prefer dense business phrasing over abstract meta-commentary.
