---
name: pilot-to-framework-evolution
description: Plan and evolve a successful tool-specific or branch-specific pilot into a shared framework without creating a parallel second implementation track.
triggers:
  - The user has a working pilot in one tool/branch/path and wants to generalize it.
  - The task is to turn a local optimization or adapter-specific pattern into a broader core capability.
  - The user wants a roadmap/backlog for extracting shared logic from an existing runtime path.
  - There is a risk of proposing a fresh clean architecture that ignores already completed work.
---

# Purpose

This skill is for the transition from "we proved it in one place" to "now make it a reusable framework".

Its main job is to prevent a common failure mode: creating a second clean implementation track next to the pilot instead of extracting the pilot into a common core.

# Core rule

Do not plan the next phase as a sideways fork.

Start from the already working path and ask:
- what is already proven;
- what is pilot-specific;
- what should become common core;
- what should stay behind a strategy/adapter boundary;
- what seam would allow a later plugin/module split without forcing a plugin-first rewrite now.

# When to use

Use this skill when the user says or implies things like:
- "we already did this for terminal/tools/one branch, now make it general";
- "don't create another separate patch";
- "build on what we already implemented";
- "keep it in the common logic, but leave room to extract a plugin later".

Typical domains:
- tool output mediation;
- shared adapters and normalizers;
- backend/runtime core extraction;
- local-first framework growth;
- turning one-path pilots into reusable infrastructure.

# Required output structure

For this class of task, the answer or plan should normally contain:

1. Short conclusion
- State the architectural direction in 1–3 sentences.

2. What is already proven
- Name the current pilot/path/branch that already works.
- Separate proof of concept from unresolved generalization work.

3. Extraction model
- `common core now`
- `tool/adapter-specific for now`
- `wrap temporarily behind interface`
- `candidate for later plugin extraction`

4. Ordered backlog
- Start with contract and boundaries.
- Then audit current implementation.
- Then extraction map.
- Then shared registry/state/policy/lifecycle.
- Only after that expand coverage to more sources/tools.

5. Risks and anti-goals
- Call out the risk of building a second implementation stream.
- Call out the risk of plugin-first overengineering.

# Planning procedure

## Step 1: Audit before design
Before proposing a new structure, inspect or inventory the work already done in the current path.

Minimum questions:
- what parts already work in production/dev;
- what parts are duplicated or tightly coupled;
- what data/contracts already exist;
- what part of the current path is the real pilot worth preserving.

## Step 2: Define the extraction boundary
Create a simple split:
- core contract/lifecycle;
- strategy/adapter hooks;
- optional future plugin seam.

The goal is not maximum abstraction. The goal is a clean migration path from pilot to framework.

## Step 3: Produce an extraction map
For each meaningful existing piece, classify it:
- keep in place temporarily;
- move to shared core now;
- wrap behind interface/strategy;
- postpone or drop.

This prevents accidental rewrite-by-relabeling.

## Step 4: Sequence the backlog
Preferred order:
1. contract and boundaries;
2. audit of current implementation;
3. extraction map;
4. common registry/state model;
5. shared policy and selectors/derived views;
6. shared lifecycle/hooks/listeners;
7. convert the original pilot into the first implementation of the shared interface;
8. only then broaden to more tools/sources.

## Step 5: Keep plugin extraction optional
If future modularization is likely, define the seam early.
But do not force a plugin-first redesign before:
- the common contract exists;
- the lifecycle is understood;
- the first extracted shared implementation works.

# What good looks like

A good answer in this class:
- builds directly on the current working path;
- names reuse explicitly;
- avoids duplicate implementation tracks;
- produces a backlog that is incremental and reversible;
- keeps later modularization possible without making it a prerequisite.

# Common pitfalls

## Pitfall: clean-slate architecture fantasy
The plan looks elegant but ignores already completed work.

Fix:
- require an audit section;
- require an extraction map;
- explicitly state what is reused from the pilot.

## Pitfall: one more isolated patch
The plan says "just add another adapter/patch" without changing the architectural center of gravity.

Fix:
- move the next step into common lifecycle/contract first;
- treat tool-specific logic as strategies, not as the main architecture.

## Pitfall: plugin-first overengineering
The plan introduces a plugin/module system before the common core is real.

Fix:
- define the seam now;
- postpone the extraction until the shared contract has proved itself.

# User-specific note

For Misha, this is not a stylistic preference but a quality bar:
- do not ignore already completed work in `tools` or runtime branches;
- do not propose a second clean patch stream next to a live pilot;
- show how existing work is lifted into common logic, with a realistic path to optional plugin extraction later.
