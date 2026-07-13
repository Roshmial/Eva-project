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

# Pitfalls

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
