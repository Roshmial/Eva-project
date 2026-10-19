# Bounded closeout for implementation-first optimization

Use this note when the user stops the endless quick-win loop and asks for a turnkey finish.

## Trigger
- `сразу под ключ`
- `без постоянных улучшений`
- `хватит улучшать, доведи до конца`

## Operating shift
Move from `find the next small win` to `assemble a bounded v1 package`.

## Minimum closeout package
1. State the v1 boundary explicitly:
   - what is in scope;
   - what is out of scope for now.
2. Finish obvious remaining integration on the current path.
3. Finish telemetry/reporting so the whole path is measurable, not only isolated optimizations.
4. Run focused regression on the touched area.
5. Run at least one live or synthetic probe with concrete before/after sizes.
6. Record the boundary in `decision-log.md`.
7. Report back as a closed package, not as another menu of future improvements.

## Good wording for the final reply
Separate:
- what now exists in v1;
- what was verified;
- what was intentionally left outside v1.

## Pitfall
Do not treat `под ключ` as permission to expand scope into a universal framework. The right move is to close the current class of work cleanly, not to restart architecture expansion under a new name.
