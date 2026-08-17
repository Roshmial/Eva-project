---
name: functional-3d-prototype-delivery
description: Use for print-ready FDM device prototypes from concepts.
version: 1.0.0
tags: [engineering, 3d-printing, prototyping, mechanical-design, fdm]
---

# Functional 3D Prototype Delivery

## When to use
Use this skill when the user has a device concept and wants more than discussion:
- review the concept logic;
- check feasibility with simple engineering calculations;
- optimize layout, dimensions, and modular breakdown;
- define print requirements for FDM;
- produce concrete prototype artifacts such as `.scad`, dimension sheets, and print plans.

Typical cases:
- bathroom, kitchen, home, lab, or workshop devices;
- holders, carriers, adapters, housings, reservoirs, manifolds, clamps;
- local-first prototyping where the user wants to print parts on an existing FDM printer instead of outsourcing.

## Delivery standard
The expected output is a prototype package, not just commentary.
Default package:
1. short engineering conclusion;
2. confirmed logic vs weak points;
3. explicit assumptions;
4. calculations for the governing constraints;
5. recommended architecture and modular split;
6. print requirements by part;
7. one or more concrete artifacts (`.scad`, dimension drawing, README, test plan).

If CAD export tools are unavailable in the runtime, still deliver the parametric source artifacts and say clearly what was not generated.

## Procedure

### 1. Reframe the concept as a system
Split the idea into:
- structural frame;
- removable/service parts;
- wet/loaded/hot/precision interfaces;
- mounting interfaces;
- optional modules.

Do not keep the whole object as one monolith if different parts have different risk profiles.

### 2. Separate confirmed logic from optimistic assumptions
Always distinguish:
- what is structurally sound;
- what depends on real measurements;
- what is only a hypothesis until tested.

For fluid or gravity-fed devices, challenge optimistic intuition early. Simple hand-wavy flow assumptions are often wrong.

### 3. Check the governing physics with simple calculations
Use lightweight calculations first.
Typical checks:
- gravity head / pressure;
- orifice flow / restriction sizing;
- equivalent passage of multiple outlet holes;
- mass of filled reservoirs;
- likely load on brackets and clamps;
- rough capacity from internal dimensions.

For gravity-fed water devices, explicitly calculate whether the proposed restriction/orifice is realistic. If not, correct the design around the real flow envelope.

### 4. Prefer modular architecture over clever monoliths
Default pattern for functional FDM devices:
- structural carrier/frame;
- removable containers or service modules;
- separate wet block / manifold / interface block;
- independent mounting adapters;
- optional convenience features layered later.

This is especially important when a concept mixes:
- water contact;
- load-bearing structure;
- user handling;
- adjustable mounting;
- optional motion.

### 5. Treat anti-rotation as a first-class mounting requirement
When the device hangs from a rod, bar, rail, or pipe, ask separately:
- what holds the weight;
- what prevents rotation.

If the user identifies two-point fixation, model it explicitly as anti-rotation, not as a duplicate support detail.

Preferred interpretation:
- two vertically separated points on one rail prevent rotation around a vertical support;
- two horizontally separated points on a crossbar prevent yaw/roll relative to the support;
- optional rotation should be implemented between a rigid base adapter and the device, not by making the support clamp itself sloppy or freely rotating.

### 6. Open-top removable tanks: special rules
When the concept moves from sealed containers to open-top removable tanks, reassess the design instead of treating it as a minor change.

Implications:
- sealed-top complexity drops sharply;
- cleaning and filling become easier;
- spill control and wall stiffness become more important;
- the product shifts from “portable vessel” toward “hung service module”.

Preferred pattern:
- removable open-top tanks with identical footprint and different heights;
- insertion from above into guide rails;
- lower seating onto a service port or pickup interface;
- top latch, bridge, strap, or other positive retention;
- anti-splash rim or partial top bridge;
- lower wet interface belongs to the frame, not loose hoses.

### 7. Printing requirements must be part-specific
Do not give one generic material recommendation for the whole device.
Split by part class:
- frame / clamps / structural adapters;
- reservoirs / wet-contact shells;
- inserts / restrictors / fine detail parts;
- soft interfaces such as pads or TPU liners.

For each class state:
- recommended material;
- wall thicknesses;
- orientation;
- perimeter / infill guidance;
- known risk zones.

### 8. Build in stages
For devices with multiple interacting uncertainties, recommend a staged print and test order.
Preferred sequence:
1. validate one critical interface first;
2. print a partial fixture or sample bay;
3. test mounting without water;
4. test wet subsystem cold-only;
5. print the full frame;
6. tune optional modules last.

Avoid jumping straight to the full elegant assembly.

## Pitfalls
- Do not treat FDM watertightness as guaranteed just because the geometry is simple.
- Do not keep sealed-tank assumptions after the user switches to open-top tanks.
- Do not model two-point mounting as mere redundancy; it is often the anti-rotation mechanism.
- Do not put optional rotation inside the primary clamp-to-support relationship.
- Do not answer with only conceptual advice when the user asked to `доработать прототип` or `подготовить макет к печати`. Produce the files.
- Do not use a single undifferentiated print recipe for all parts.
- Do not freeze dimensions before identifying the real installation scenario and support geometry.

## Artifact expectations
Good artifacts for this class of work:
- parametric `OpenSCAD` source for the structural concept;
- dimension sheet or SVG schematic;
- engineering review document with assumptions and calculations;
- print/assembly README;
- staged prototype test checklist.

## References
- See `references/open-top-dual-tank-gravity-shower.md` for a compact pattern: removable open-top tanks, dual anti-rotation mounting, optional rotary adapter, and gravity-flow sizing corrections.
