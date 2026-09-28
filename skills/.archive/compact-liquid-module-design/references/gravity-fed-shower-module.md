# Gravity-fed shower module pattern

Session pattern extracted from a compact printed rinse-module design.

## User scenario
- Two liquids: hot and cold.
- Hot liquid may come directly from a kettle.
- Liquids are present only during use plus a few minutes.
- User wants maximum printability and minimum purchased parts.
- User rejected architectures that introduce three user-facing control points.

## Architecture chosen
- Single printed outer housing.
- Two internal removable reservoirs inserted from the top.
- Short lower outlets from each reservoir into a compact lower wet module.
- Mixer in a ball-style product format.
- Small integrated mixing chamber.
- Combined `on/off + flow limiting` dispensing element.
- Printed outlet head.

## Key design decisions
1. Treat the reservoirs as temporary fill containers, not storage bottles.
2. Drop external bottle logic when it adds cost, adapters, and hoses without solving a real problem.
3. Keep the hot path short.
4. Prefer a small mixing chamber; do not add a third large tank.
5. Use only two user-facing controls:
   - mixer;
   - on/off.
6. If flow restriction is needed, hide it inside the on/off element or a service insert.
7. Move as much non-critical fastening as possible to printed latches, guides, and slide locks.
8. Keep metal fasteners only for structural mounting and wet-joint gasket compression.

## Why this matters
This pattern is a good default whenever a 3D-printed liquid prototype is drifting toward too many external containers, hoses, and fittings. The first optimization lever is often architectural simplification, not cheaper components.
