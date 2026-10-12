# Tool guardrail halt vs real job success

## Session lesson

A user surfaced a concrete failure mode: the agent produced a guardrail-halt message after repeated `web_extract` failures, and then later spoke about the situation as if something had "worked" or "отработало".

The durable lesson is not about `web_extract` itself. It is about state separation.

## Wrong interpretation

Guardrail text such as:

`I stopped retrying web_extract because it hit the tool-call guardrail ...`

must not be described as:
- successful job execution;
- proof that a weekly job ran;
- proof that delivery happened;
- proof that the requested task completed.

## Correct interpretation

That message proves only this:
- the agent detected a non-progressing tool loop;
- the agent stopped repeating the same failing tool path;
- a different strategy is required.

## Reporting rule

When a similar incident appears, explicitly separate:
1. agent-side tool stop;
2. request handled;
3. job created;
4. job run;
5. delivery completed;
6. correct content delivered.

Use blunt wording if needed:
- "Это stop на стороне агента, а не подтверждение, что job отработал."
- "Это не delivery и не success, а только halt по guardrail."

## Related runtime improvement

The runtime message was updated so the synthesized halt text now explicitly says:
- this is an agent-side stop;
- it is not evidence that the user's task or job succeeded.
