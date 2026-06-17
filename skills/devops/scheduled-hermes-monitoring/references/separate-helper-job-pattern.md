# Separate helper-job pattern for optional daily content

Use this pattern when a user-facing recurring brief has one optional block that is slower, noisier, or less reliable than the core message.

Example shape:
- helper job at 09:00 gathers one optional result;
- main daily brief at 09:30 consumes that result through `context_from`;
- if the helper finds nothing reliable, it returns a sentinel like `NO_AFISHA` and the main brief omits the block.

Why this helps:
- keeps the main brief prompt simpler;
- isolates unstable retrieval from the core message;
- makes "show it only when found" easy to implement;
- avoids mixing test runs and live user-facing delivery.

Recommended rules:
- helper output should be structured and minimal;
- use one explicit success marker, for example `AFISHA_FOUND: yes`;
- use one explicit empty marker, for example `NO_AFISHA`;
- main brief should trust helper context only when the success marker and a concrete link are present;
- keep both jobs in `deliver=local` until the user approves live delivery.

Style lesson from this session:
- for Misha's proactive daily self-development notes, the optional leisure block should live outside the main prompt whenever it needs web lookup;
- the main daily text should stay natural and practical, while helper jobs can stay more mechanical and structured.
