---
name: compact-liquid-module-design
description: Use when designing small 3D-printed liquid modules.
---

# Purpose

This skill covers compact gravity-fed liquid modules that mix, buffer, and dispense small amounts of liquid in a mostly 3D-printed assembly.

Typical cases:
- shower-like rinse modules
- short-contact hot/cold liquid mixers
- removable fillable cartridges inside a printed housing
- prototypes where printability, compactness, and low BOM matter more than long-term storage

# Core rule

Start from the real usage scenario, not from generic bottle/tank assumptions.

If the liquid is only present during use plus a few minutes, do not over-design around long-term storage. Re-evaluate whether the system needs:
- external bottles at all;
- threaded caps and adapters;
- long hose runs;
- multiple user-visible valves.

Very often the better architecture is:
- one printed housing;
- internal removable fillable reservoirs;
- a compact lower wet module;
- only one mixing control and one start/stop control.

# Architecture preference order

## 1. Integrated printed housing first

Prefer a single printed housing that provides:
- structural support;
- reservoir guidance/retention;
- lower wet-module seat;
- mounting interface.

Avoid wrapping external commodity containers inside a large carrier unless the containers themselves solve a real problem.

## 2. Internal removable reservoirs before external bottles

When the liquids do not need long-term storage:
- prefer two removable internal reservoirs inserted from the top;
- make them easy to remove and wash;
- use simple open or semi-open tops for quick filling;
- avoid complex cap-based plumbing unless spill control truly requires it.

Use identical footprints when possible; vary useful height or fill level instead of making two unrelated form factors.

## 3. Keep the wet path short and low

Default path:
- reservoir A
- reservoir B
- two short lower outlets
- mixing element
- small mixing chamber
- on/off dispensing element with built-in flow limit
- outlet head

Do not design long internal hot paths or decorative routing. Gravity-fed compact modules benefit from short vertical paths and few transitions.

## 4. Separate functions by user intent

For user-facing controls, prefer only two logical actions:
- mixing control: sets hot/cold proportion and rough operating point;
- on/off: starts and stops dispensing.

Do not add a third active user control for flow restriction unless there is a strong reason.

If a flow limit is needed, hide it as:
- a fixed restriction;
- a swap-in insert;
- or part of the on/off valve geometry.

# Mixer guidance

When the user wants a "ball mixer" format, treat it as a product-logic constraint first, not necessarily a literal household plumbing cartridge.

Meaning:
- one compact mixing control;
- intuitive left/right or central proportion logic;
- mixing happens in one lower module;
- no two-knob lab-stand behavior unless the user explicitly wants it.

Practical interpretation:
- printed outer housing and handle are fine;
- critical wet internals may remain a small purchased element if reliability demands it.

# Maximum-printing optimization rules

When the user asks to optimize for maximum printing:
1. remove external bottles if they only add cost and interfaces;
2. remove unnecessary hoses and cap adapters;
3. merge flow restriction with the on/off element instead of adding a third control;
4. keep the mixing chamber small — a buffer, not a third tank;
5. replace secondary fasteners with printed guides, latches, bayonets, or slide locks;
6. keep metal fasteners only where they provide real value: structural mount points or gasket compression.

# Printed vs purchased parts

## Good candidates for printed parts
- main housing
- removable reservoirs
- guides and retention features
- service covers in dry zones
- lower wet-module body
- small mixing chamber body
- outlet head / spray head
- swap-in restriction inserts
- mounting adapters

## Better left purchased or hybrid
- O-rings and gaskets
- critical hot-side sealing interfaces
- wet moving internals of the mixer if tolerances are unforgiving
- any element whose main job is consistent compression of a seal under load

# Fastener policy

Use printed fastening for:
- reservoir retention
- service covers in dry zones
- cosmetic shells
- alignment and anti-misassembly features

Keep metal fasteners for:
- structural mounting to an external support
- compression of gasketed wet joints
- central load-bearing joints in split housings

# Session-specific note

See `references/gravity-fed-shower-module.md` for a concrete compact hot/cold rinse architecture: two internal removable reservoirs, a lower ball-format mixer, a small mixing chamber, and a combined on/off plus flow-limiting element.
