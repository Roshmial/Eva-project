# Open-top dual-tank gravity shower pattern

Use this reference when a user wants a compact FDM-printable gravity-fed shower or similar wet module with removable tanks.

## What changed the design materially
The concept became much stronger after these shifts:
- stop treating the reservoirs as sealed portable bottles;
- switch to open-top removable tanks;
- treat two-point mounting as anti-rotation, not duplicate support;
- make any rotation an optional intermediate adapter, not part of the primary clamp-to-support interface.

## Recommended architecture
Split into five modules:
1. structural rear frame;
2. two removable open-top tanks with identical footprint and different heights;
3. lower wet block / hydroblock;
4. universal mounting interface;
5. optional rotary adapter.

## Tank pattern
Preferred tank behavior:
- inserted from above into guide rails;
- seated onto a lower service port / pickup interface;
- positively retained at the top by latch / bridge / strap;
- open top with anti-splash rim or partial bridge;
- identical base dimensions, different heights for hot and cold volumes.

Why this works:
- easier filling and cleaning;
- easy replacement of one tank;
- easier iteration than integrated monolithic shells;
- frame and wet interface can evolve separately from tank geometry.

## Mounting interpretation
Two-point mounting is primarily about preventing rotation.

Cases:
- same rail, upper + lower points -> prevents rotation around a vertical support;
- same bar, left + right points -> prevents yaw/roll around a horizontal support.

Do not describe this merely as “stronger support”; the anti-rotation role is the key design reason.

## Optional rotation
If rotation is needed:
- keep the support adapter rigid and anti-rotational;
- place the rotary joint between the adapter and the frame;
- prefer discrete lock angles such as `0`, `±15`, `±30` for early versions.

Free friction-only rotation is less desirable under a water load because it invites creep and play.

## Gravity-flow correction
For self-flowing water with practical head around `0.5–0.7 m`, very small restrictions are often unusable.

Useful reference envelope from session work:
- `2.0 mm` -> economy;
- `2.2–2.5 mm` -> practical base flow;
- `2.8 mm` -> faster rinse.

This session specifically invalidated the earlier optimistic range around `0.8–1.5 mm` for a comfortable mini-shower.

## Print-strategy lesson
For this class of device, do not print everything at once.
Recommended sequence:
1. one tank sample + partial guide bay;
2. mounting adapter without water;
3. wet block fit and cold-water flow test;
4. full frame;
5. optional rotary adapter.

## Artifact lesson
When the user asks to refine the prototype, produce at least:
- engineering review with calculations;
- parametric CAD source such as `OpenSCAD`;
- README / print plan;
- optional inserts, adapters, or support parts as separate files.
