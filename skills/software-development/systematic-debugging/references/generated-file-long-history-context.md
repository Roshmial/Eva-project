# Long-history generate-and-attach: focused-context verification

Use this when a web/chat backend already has a dedicated `generate-and-attach` path, but real user threads with long history still fail or degrade.

## Symptom pattern

Typical smell:
- a clean acceptance thread works;
- the real production thread still fails;
- failure shows up as timeout, token explosion, or low-quality output;
- the generated attachment is no longer raw tool transcript, but the task still does not finish reliably.

## Root-cause pattern

The backend may have fixed the *output contract* but still sends the *entire thread history* into the generation call.

That history often contains:
- repeated file-request turns;
- earlier failed exports;
- `file_response` / `processing_status` assistant messages;
- apology / retry chatter;
- short technical confirmations with no semantic value.

In long threads this causes:
- prompt bloat;
- slower generation;
- higher timeout risk;
- contamination of the generated document by prior file-loop chatter.

## Better pattern

For `generate-and-attach` flows, build a focused context instead of passing the full thread.

Practical selection rule:
1. Walk backward through message history.
2. Keep only substantive assistant messages.
3. For each kept assistant message, also keep the nearest preceding relevant user turn.
4. Drop non-content rows:
   - `file_response`
   - `processing_status`
   - generic error placeholders
   - apology / retry loops
   - short technical file-request chatter
5. Use the focused subset to build the model messages.

## What counts as "substantive"

Good candidates:
- long assistant answers that contain the actual business/technical content;
- user turns that requested that content or refined it.

Bad candidates:
- "Готовлю ответ…"
- file-send confirmations
- timeout/error messages
- tool/service transcript leakage
- short turns that only say "пришли файл", "давай файл", etc.

## Verification rule

Do not stop after a green acceptance run on a fresh thread.

You must verify on the *original problematic thread* as well, because that is where long-history contamination exists.

Minimum proof:
- previous failing task id / message id / error;
- new rerun on the same thread id;
- completed status;
- lower prompt/token footprint if available;
- downloaded attachment is a real file;
- preview/content no longer contains transcript leakage.

## Decision rule

If a long-history thread times out after the output contract is already correct, prefer focused-context reduction before raising timeouts again.

Raising the timeout alone can hide the real issue while keeping prompt bloat and brittle generation behaviour.