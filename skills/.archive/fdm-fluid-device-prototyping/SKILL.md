---
name: fdm-fluid-device-prototyping
description: "Use when reviewing FDM fluid devices with hot water."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [engineering, 3d-printing, fdm, prototyping, fluidics, thermal]
---

# FDM Fluid Device Prototyping

## When to use

Use when the user wants to design or review a 3D-printed functional device that:
- carries water or another liquid;
- includes tanks, ports, valves, mixers, nozzles, or hoses;
- operates under gravity feed or low pressure;
- may see warm or hot liquid;
- must mount to furniture, bathroom hardware, or another support;
- is intended for real printing, not only concept art.

Typical examples:
- portable or semi-portable showers;
- rinse devices;
- gravity-fed wash stations;
- printed tanks with removable inserts;
- mixed printed/non-printed wet assemblies.

## Default review structure

Deliver in this order:
1. Short conclusion.
2. What is confirmed.
3. What is risky or immature.
4. Corrected calculations.
5. Realistic architecture options.
6. Recommended next mechanical step.

Separate clearly:
- confirmed facts;
- assumptions;
- engineering interpretation;
- practical recommendation.

## Core design rules

### 1. Separate dry structure from the wet hot contour

For hot-liquid devices, do not treat the printed body as one undifferentiated object.
Split the system into:
- dry structural frame;
- removable reservoirs;
- lower wet module / manifold;
- support mounting interface;
- optional orientation or rotation module.

This prevents accidental reliance on FDM parts in the highest thermal-risk zone.

### 2. Treat the hot contour as a first-class risk boundary

If the user's real-world source is kettle-hot water or another easy path to very hot input, review not only the hot tank but the entire hot-side contour:
- tank outlet;
- lower port;
- fittings;
- mixer body;
- seals;
- hose transitions;
- any printed part touched by pre-mix hot water.

Do not say "only the tank is the problem" if hot liquid still passes through printed ports or mixer elements.

Decision rule:
- If pre-mix hot water may exceed the safe working range of the printed material, recommend a non-printed hot contour up to the mixing point.
- Only allow printed post-mix parts where the temperature is already materially lower.

### 3. Open-top tanks are a different class from sealed tanks

Open-top removable tanks are substantially easier and more realistic for FDM than sealed hot tanks.
For open-top tanks, review these specific risks:
- splash and wave freeboard;
- side-wall spreading;
- bottom stiffness;
- lower outlet leakage;
- safe fill level;
- removal and cleaning ergonomics.

Do not evaluate them as if they were pressure-tight canisters.

### 4. Prefer removable tanks over monolithic bodies

When practical, recommend:
- one structural frame;
- removable tanks with a common footprint;
- different heights for different volumes;
- a lower service interface in the frame;
- top retention beyond gravity alone.

This improves:
- filling;
- cleaning;
- replacement;
- reprinting only damaged parts;
- parameter iteration.

### 5. Two-point mounting is the default when rotation matters

For wall, rail, or bar mounting, treat two-point fixation as the default when the device carries water and can twist.

Interpretation:
- two points on a vertical rail prevent horizontal twisting around the rail;
- two points on a horizontal bar prevent yaw/roll relative to the support.

Do not design such devices around a one-point mount unless the load is very low and anti-rotation is solved elsewhere.

### 6. Rotation should be optional and downstream of the rigid mount

If the user wants a rotating version, do not make the support clamp itself the rotating joint.
Architecture should be:
- support;
- rigid two-point adapter;
- optional rotary module;
- device frame.

Prefer indexed/discrete rotation for early prototypes over free-friction rotation.

## Hydraulics review rules

### 7. Recalculate gravity-fed flow explicitly

For low-pressure or gravity-fed systems, do not trust intuitive estimates.
Recalculate flow using a simple orifice approximation and state the assumed head.

Baseline formula:
Q = Cd × A × sqrt(2gh)

Use explicit assumptions for:
- discharge coefficient;
- head height;
- restriction diameter;
- whether the nozzle is becoming a second throttle.

### 8. Do not let the shower head become the hidden main restriction

When the design has a main interchangeable restrictor, ensure the nozzle or mini-shower head does not dominate the pressure loss.
For multi-hole outlets, check equivalent opening area and compare it to the chosen main restriction.

Practical default for gravity-fed mini-shower concepts:
- prefer a few larger holes and short soft streams;
- avoid "mist" or highly atomized spray concepts in early FDM gravity prototypes.

### 9. Distinguish gross volume from practical usable volume

Always report both:
- gross internal volume;
- practical usable volume after freeboard / splash margin / non-usable bottom zone.

For open-top tanks, usable volume is the only number that matters for runtime.

### 10. Report runtime as a range, not one number

State continuous runtime at several realistic flow settings.
Make clear that intermittent real use lasts longer than continuous discharge.

## Thermal review rules

### 11. Do not optimize around a temperature that is annoying to produce in real life

If the user can easily produce boiling water but not reliably produce a pre-mixed 55–60 °C source, do not anchor the concept around a fragile "just fill with 58 °C" operating assumption.

Instead assess:
- whether the device should accept kettle-hot input at all;
- whether pre-mix is realistic for this user scenario;
- whether the hot contour should be non-printed;
- whether geometry/volume ratio should change to reach the desired final mix using real household behavior.

### 12. Separate thermal feasibility from user convenience

A temperature may be materially safer for FDM but still be inconvenient in daily use.
Call this out directly instead of presenting the safer number as if it were automatically practical.

## Printability rules

### 13. Review not only final dimensions, but build-volume fit and orientation

For large frames, check:
- flat-bed fit;
- side orientation fit;
- whether splitting the frame is more realistic than forcing a bad orientation;
- where to place mechanical joints if split printing is needed.

A device that is conceptually compact but awkward to print as one part should be redesigned around the printer's real build volume.

### 14. Prefer moderate dimensional optimization over over-tight packaging

Small wins such as reducing side margins, center gaps, top margins, and insertion clearances are useful.
But do not over-compress the geometry if it harms:
- service access;
- wet-module integration;
- seal access;
- user handling with wet hands.

## Recommended answer patterns

### If the user asks "can this handle very hot water?"
Review in this order:
1. material limit;
2. whether the hot contour includes printed wet parts before mixing;
3. user's real heating method;
4. practical alternatives:
   - lower operating temperature;
   - more heat-tolerant material;
   - non-printed hot contour;
   - hybrid architecture.

### If the user asks for final characteristics
Report at least:
- overall envelope;
- envelope with mounting hardware;
- tank dimensions;
- gross and practical usable volume;
- estimated liquid mass;
- estimated total assembled mass;
- flow range at realistic head;
- continuous runtime range;
- recommended operating temperature window;
- nozzle recommendation;
- main unresolved engineering risk.

## Pitfalls

- Do not present sealed hot printed tanks as easy just because FDM can hold water in cold tests.
- Do not review only the tank and ignore the rest of the hot contour.
- Do not give a single optimistic runtime number without a flow assumption.
- Do not confuse gross tank volume with useful shower runtime.
- Do not recommend a one-point support for a water-carrying device that will twist under asymmetric mass.
- Do not assume "temperature that is nice for the plastic" is also easy for the user to prepare.

## References

See `references/hot-contour-boundary.md` for a compact decision note on when to stop using printed parts before the mixing point in hot-water devices.
