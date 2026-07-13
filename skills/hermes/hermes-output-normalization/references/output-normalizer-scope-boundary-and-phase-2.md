# Output normalizer scope boundary and phase-2 planning

Use this note when a working terminal-output normalizer starts to drift into a false claim that Hermes token optimization is broadly solved.

## What the session clarified

A successful `terminal` normalizer rollout is valuable, but it only closes one layer of the broader problem:
- terminal tool outputs are normalized before the next agent turn
- terminal tool outputs can use `output_persistable` for durable storage
- this helps both active context and `state.db`

It does **not** mean all major token-heavy paths are optimized.

## Durable lesson

When discussing impact, separate these levels clearly:
1. tool-output optimization for one family, such as `terminal`
2. multi-tool output mediation across other heavy-text tools
3. agent-context shaping across what actually enters the next prompt
4. persistence/retrieval shaping for what later comes back through history and search

Do not let the conversation drift from level 1 success into a level 2/3/4 completion claim.

## Recommended phase-2 targets

Best next targets after terminal:
- `read_file`
- `search_files`
- `web_extract`
- `session_search`
- `process` / long log outputs

Why these first:
- they often inject large text blocks into context
- they are structurally similar to terminal normalization
- they can usually be improved without new infrastructure

## User-facing framing to keep

When the user’s original goal is token efficiency beyond tools, say explicitly:
- terminal normalization is phase 1
- it already improves live context and persistence on the terminal path
- broader token-efficiency work still remains

This keeps delivery honest and prevents local optimization work from being overstated.
