# Implementation-first corrections from token-optimization session

Use this note when working with Misha on architecture, token-efficiency, runtime, or implementation-priority tasks.

## Durable lesson
When Misha asks to implement, or reacts with phrases like:
- "давай делать уже"
- "не макулатуру"
- "реализовывать сразу"
- frustration that tokens are being burned on documents instead of code

then the task has switched into implementation-first mode.

## Required behavior in that mode
- Stop producing additional plan/backlog/framework/contract documents unless explicitly requested again.
- Deliver the next smallest real code change immediately.
- Verify with tests or other concrete tool output before reporting success.
- Prefer one safe high-ROI optimization step over a broader architectural rewrite.

## Specific fit for token-optimization work
For token-efficiency tasks, Misha wants:
- existing implemented logic to be reused and extended, not ignored;
- quick wins first;
- real measured effects;
- metrics added alongside the implementation when practical.

## Anti-pattern to avoid
Do not respond to an implementation request by producing another:
- architecture note
- framework description
- contract document
- backlog decomposition

unless Misha explicitly asks for planning/documentation.
