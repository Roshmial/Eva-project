# Hot contour boundary for FDM water devices

Use this note when a user wants a 3D-printed water device that may see kettle-hot or otherwise very hot liquid.

## Core rule

Do not review only the tank.
The hot contour includes every part touched by pre-mix hot liquid before cooling by cold water.

Typical hot contour:
- hot reservoir;
- outlet boss / lower port;
- pickup or outlet tube;
- fittings;
- hose;
- mixer body;
- seals and gaskets in the pre-mix path.

## Decision rule

If the real user path is "easy to get boiling water, annoying to get 55–60 °C precisely", then the design must answer one of these questions explicitly:

1. Can the printed hot contour safely tolerate near-boiling input, even briefly?
2. If not, where exactly does the design stop using printed wet parts before the mixing point?
3. If neither is true, is the user experience realistic at all?

## Practical recommendation ladder

### A. Mostly printed, limited-temperature design
Use when:
- the user accepts controlled hot fill temperatures;
- the goal is a fast prototype;
- the hot contour is still printed.

Implications:
- state a practical operating range;
- do not market kettle input as normal use;
- make the thermal limit explicit.

### B. Hybrid design with non-printed hot contour
Use when:
- the user will likely use kettle water;
- convenience matters more than fully printed purity;
- reliability matters more than conceptual elegance.

Implications:
- keep the frame and possibly the cold tank printed;
- move the hot reservoir and pre-mix hot path to non-printed components;
- allow printed parts again after mixing where the temperature is materially lower.

### C. High-temperature ambition
Use only if:
- the user explicitly wants a higher-end build;
- materials, seals, and wet hardware are chosen around heat first;
- the printed parts are no longer assumed to carry the critical hot wet load by default.

## Pitfall to call out explicitly

A common false compromise is:
- "the hot tank is not printed, so the problem is solved".

This is wrong if hot liquid still reaches:
- printed ports;
- printed mixer internals;
- printed connectors;
- printed wet manifold parts before cooling.

## Household-behavior note

When the user says that 100 °C from a kettle is easy but 55 °C is annoying, treat that as a design input, not as a minor user inconvenience.
That signal usually means the architecture should move away from a fully printed hot wet contour.