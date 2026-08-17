---
name: short-contact-fluid-module-design
description: Use when reservoirs are temporary-use liquid feeds.
version: 1.0.0
tags: [engineering, 3d-printing, fluidics, prototyping, thermal]
---

# Short-Contact Fluid Module Design

## When to use
Use this skill when designing compact liquid-delivery devices with:
- short usage windows;
- manual fill from kettle, bottle, or faucet;
- 3D-printed carriers or frames;
- external reservoirs that are inserted, removed, and washed;
- mixed hot/cold paths where temperature risk matters.

Typical examples:
- portable shower/feed modules;
- gravity-fed rinse systems;
- temporary dual-reservoir prototypes;
- carrier-mounted liquid cartridges.

## Core principle
First decide whether the container is:
1. a storage vessel; or
2. a temporary-use feed reservoir.

If the user only needs to pour liquid in, use it for a few minutes, and empty/wash it soon after, treat it as a temporary-use feed reservoir. Do not over-specify it like long-term storage packaging unless there is a real contamination, sealing, or shelf-life requirement.

## Design consequences of temporary-use reservoirs
When the reservoir is temporary-use rather than storage:
- prioritize fill convenience, cleaning, thermal tolerance, and stable seating;
- relax long-term storage assumptions;
- prefer open-top or simple insertable containers over full bottle logic when possible;
- do not force laboratory bottles or threaded-cap architectures unless they materially improve the design.

## Architecture preference
Default to a layered architecture:
1. printed structural carrier/frame;
2. removable temporary-use reservoirs;
3. separate lower wet/hydraulic module;
4. non-printed hot path up to the mixing point when hot water may be materially above ~55-60 C.

Treat the printed structure as mechanics, not as the primary hot wet path.

## Reservoir selection rule
Before recommending commercial bottles, ask: does the device really need a bottle?

If no, prefer:
- insertable cups/containers/cartridges;
- carrier-frame seating with bottom support + side guides + top strap;
- simplified fill-from-top workflow.

If yes, then compare commercial bottles by:
- footprint depth first;
- height second;
- ease of seating/replacement;
- thermal suitability;
- only then by mouth size and premium lab-grade features.

## Cost control rule
For early prototypes, avoid paying lab-container premiums unless they solve a real constraint.

Good optimization levers:
- replace lab bottles with simpler temporary-use containers when storage is not required;
- make the frame a tolerant carrier, not a precision bottle socket;
- use one shared external container geometry on both sides and vary fill level instead of making two special reservoir forms;
- keep the hot path short and simple;
- avoid over-buying a polished mixer for v1 when two simple regulated channels plus a collector prove the concept.

## Hot-path rule
If the user may fill from a kettle or otherwise use very hot water:
- treat the whole hot path as the risk zone, not only the reservoir;
- avoid relying on FDM printed wet parts as the primary hot hydraulic boundary before mixing;
- prefer thermally tolerant hoses, fittings, adapters, and wet interfaces before the mixing point.

## Carrier mechanics rule
For removable external containers, default to:
- bottom shelf/support;
- lateral guides;
- front anti-slip stop if needed;
- top strap or simple retainer.

Do not over-constrain the reservoir with a full tight socket unless dimensional repeatability is proven.

## User-specific delivery lesson
When discussing compact fluid prototypes for this user:
- do not assume premium external lab containers are the baseline if the usage is only a short fill-and-use cycle;
- explicitly test whether the real need is a temporary fill reservoir rather than a full bottle;
- prefer simpler, cheaper carrier-style architectures before recommending expensive container SKUs.

## Pitfalls
- Confusing temporary-use contact with long-term storage requirements.
- Optimizing for bottle elegance instead of fill/use/clean workflow.
- Treating only the hot reservoir as risky while forgetting the hot fittings, ports, and mixer path.
- Making the printed frame a precision enclosure when a tolerant carrier would broaden component choice and cut cost.
- Using different left/right reservoir geometries too early when fill level can create the hot/cold asymmetry.

## References
- Add session-specific component shortlists and pricing notes under `references/`.
