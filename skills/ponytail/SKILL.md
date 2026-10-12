---
name: ponytail
description: Use when coding. Make the smallest complete safe change.
license: MIT
---

# Ponytail

Write the least code that fully solves the task. Prefer deletion and reuse over addition. Keep replies concise enough to understand in one read.

## Before editing

Read the task and every affected code path. Check callers, tests, fixtures, configuration, exports, data-loss risks, security boundaries, and user-visible behavior.

## Decision ladder

Take the first option that completely works:

1. Skip functionality, options, and flexibility the task does not require.
2. Reuse an existing helper, component, service, or project pattern.
3. Use the standard library or native platform capability.
4. Use an already installed dependency; do not add one for a few lines.
5. Use a clear one-liner when it remains readable.
6. Otherwise write the minimum complete implementation.

## Rules

- Finish the whole requested change, including affected callers, tests, and fixtures.
- Avoid speculative abstractions, wrappers, configuration, boilerplate, and future-proofing.
- Preserve the repository's established structure and conventions.
- Fix root causes in shared code after checking every caller.
- Preserve validation and error handling when moving or combining code.
- Prefer the option that handles edge cases when alternatives are equally small.
- Add one focused test or assertion for new non-trivial logic involving branches, loops, parsing, money, security, or a new script/application.
- Do not cut trust-boundary validation, data-loss protection, security, accessibility, hardware calibration, or anything explicitly requested.
- End coding-task reports with what was not checked and any remaining risk.

This is adapted from DietrichGebert/ponytail, version 5.1.0, commit 9cc65d03aa2da1db7121b912d03596409ee340b8, MIT license.