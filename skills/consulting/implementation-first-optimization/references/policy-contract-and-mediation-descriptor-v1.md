# Policy Contract and Mediation Descriptor v1

Use this note when a token/context optimization effort has already delivered several concrete wins and needs the smallest possible shared layer instead of a speculative framework.

## Recommended evolution order

1. exact reuse for identical large outputs
2. aggregate budget persistence/reuse
3. prompt-side compaction for persisted references
4. append-only log delta
5. top-level JSON delta
6. shared policy selector: `full / compact / reference / delta`
7. shared policy contract
8. lightweight mediation descriptor

## Minimal policy contract

Keep the first contract tiny:
- `policy`
- `source`
- `raw_chars`
- `surface_chars`
- `chars_saved`
- `changed`

Purpose:
- unify measurement across prompt-side and output-side mediation
- avoid string-only heuristics in later routing
- keep the contract cheap enough to add without restructuring the whole runtime

## Minimal mediation descriptor

Wrap the policy contract in a descriptor only after the contract already exists.

Recommended fields:
- `source`
- `policy`
- `policy_contract`
- `artifact_path`
- `raw_content_available`
- `reuse_applied`
- `delta_applied`

Purpose:
- describe what mediation already happened
- expose artifact/reuse/delta facts to later routing steps
- stay implementation-driven instead of framework-first

## Important discipline

- Do not start with the descriptor.
- Do not invent a universal mediation framework before several concrete optimizations are working.
- The selector, contract, and descriptor should be extracted from already validated behavior in code.
- Keep all of them task-local and low-risk until production value is proven.

## Practical reading of the layers

- selector = which surface policy was chosen
- contract = what that policy did to size
- descriptor = what operational facts downstream code should know
