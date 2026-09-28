---
name: print-first-short-contact-water-modules
description: Use for max-print redesign of short-contact water modules.
---

# Purpose

This skill covers compact liquid-delivery devices where the fluid is used shortly after filling and is not meant for long-term storage. Examples: gravity-fed rinse modules, compact shower/rinse tools, temporary-use hot/cold mixing devices, and similar print-first prototypes.

The goal is to avoid overengineering around bottles, storage-grade containers, and too many purchased plumbing parts when the real use case is: fill, use for a few minutes, empty, wash.

# When to use

Use when:
- the user wants maximum printability;
- fluid contact time is short;
- the design starts drifting toward external bottles, adapters, lids, and too many fittings;
- the real scenario is "pour water in and use now", especially from a kettle or similar hot-water source;
- the user wants a practical prototype, not a lab-grade liquid-storage system.

# Core decision rule

First classify the reservoirs correctly.

If the liquid is only present during active use plus a short pre/post window, treat the containers as:
- temporary fill reservoirs;
- removable cartridges;
- insertable tubs/cups/liners;
not as:
- storage bottles;
- shipping containers;
- long-term sealed vessels.

This single classification change should drive the architecture.

# Preferred architecture

Default to an integrated print-first layout:
- one printed structural housing;
- two internal removable reservoirs;
- a compact lower hydromodule;
- short lower outlets from each reservoir;
- a mixer in the lower block;
- a small mixing chamber;
- a combined on/off + flow-limited outlet stage;
- a shower head / nozzle after that.

Canonical chain:
`2 reservoirs -> ball-format mixer -> small mixing chamber -> on/off with fixed or swappable flow restriction -> outlet/nozzle`

# Reservoir strategy

Prefer:
- removable top-loaded reservoirs;
- open or semi-open tops for fast pouring;
- simple cleaning access;
- identical footprint where possible;
- different useful heights or fill levels instead of many different geometries.

Avoid by default:
- external bottles as the main concept;
- threaded bottle ecosystems;
- elaborate cap adapters;
- designing around storage-grade lab containers.

## Hot vs cold reservoir rule

Cold side can be more experimental.

Hot side deserves more caution:
- minimize hot-path length before mixing;
- avoid long horizontal hot channels;
- isolate the hottest interface to the smallest possible zone;
- use seals where contact pressure matters;
- do not assume a printed hot-side threaded wet joint is a good primary sealing method.

# Mixer logic

When the user prefers "ball mixer" or normal-shower logic, treat that as a product-format choice, not necessarily a literal off-the-shelf bathroom mixer.

Meaning:
- one control should set mix ratio / temperature;
- do not force the user to separately tune hot and cold every time;
- keep the lower hydromodule compact.

Do not casually replace this with two visible needle-valve controls in the final product. Separate dual regulators are acceptable only as temporary bench tooling during hydraulic experiments.

# Control count rule

Avoid 3 user-facing controls.

Preferred user-facing controls:
1. mixer control;
2. outlet on/off control.

If flow limiting is needed, hide it as:
- fixed geometry;
- a service insert;
- a swappable calibrated passage.

Do not add a third user control just for a throttle unless the user explicitly wants that complexity.

# On/off and flow-limiting rule

A good default is to combine outlet shutoff and max-flow limiting in one stage.

Meaning:
- user sees one start/stop control;
- engineering tuning of consumption happens via a fixed or swappable restriction inside that stage;
- the device keeps simple operation while still avoiding wasteful discharge.

# Maximum-print optimization sequence

When asked to optimize "everything" under maximum print:

1. Remove external storage components first.
2. Collapse hoses/adapters/fittings into internal geometry where safe.
3. Shorten hot and mixed paths.
4. Merge separate plumbing subassemblies into one lower hydromodule.
5. Replace bottle-retention mechanics with integrated reservoir guides and latches.
6. Reduce purchased parts to seals, a few critical fasteners, and only the smallest necessary valve internals.

Important: cost optimization should come primarily from architecture simplification, not from hunting slightly cheaper bottles or fittings.

# Printed vs non-printed boundary

Good candidates for printed parts:
- outer housing;
- removable reservoirs;
- guides, latches, service doors, covers;
- mixing-chamber body;
- nozzle body;
- mounting adapters;
- dry-side geometry and alignment features.

Better kept non-printed or combined in critical spots:
- O-rings / gaskets;
- heavily loaded clamp fasteners;
- critical wet sealing interfaces under compression;
- tiny valve internals if a reliable ready-made insert exists.

# Fastener policy

Do not default everything to screws.

Use printed latches / bayonets / slides / keyed geometry for:
- dry covers;
- reservoir retention;
- service access;
- cosmetic shells;
- secondary alignment.

Reserve metal fasteners for:
- main structural clamp paths;
- mounting to the support structure;
- compression of wet sealing joints;
- any joint where repeatable preload matters.

# User-specific delivery lesson

For this class of task, do not keep the discussion stuck in shopping-mode once the user reframes the problem.

If the user says they do not need full bottles and only need a container to pour water from a kettle and use immediately, pivot the architecture immediately:
- from external components and market catalog search;
- to integrated temporary-fill reservoirs and print-first redesign.

That pivot is not a minor parameter change. It changes the whole product architecture.

# Pitfalls

## Pitfall: overcommitting to bought reservoirs

If the design starts around bottles, caps, straps, and adapters, re-check whether the user actually needs storage. Often they do not.

## Pitfall: treating throttle as a third visible control

Users usually want simple operation. Hide flow-limiting as an internal or service-level restriction whenever possible.

## Pitfall: preserving old architecture after the user reframes the use case

Once the user clarifies short-contact temporary use, do not keep optimizing the older "external bottle carrier" concept. Rebuild the concept around removable internal reservoirs.

## Pitfall: using bench-debug parts as final-product logic

Needle valves and similar tuning hardware are acceptable for quick experiments. They are usually the wrong UX for the final device.

# Output pattern

When delivering a result in this class, structure it as:
- final architecture;
- printed parts;
- bought parts;
- which bought parts are truly mandatory vs optional;
- what was removed from the previous concept;
- why the new architecture is cheaper/simpler.
