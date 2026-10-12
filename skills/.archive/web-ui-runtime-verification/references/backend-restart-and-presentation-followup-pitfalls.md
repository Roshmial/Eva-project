# Backend restart and presentation follow-up pitfalls

When verifying Hermes Web or similar local-first web runtimes on live contour, two failures can masquerade as content bugs while actually being runtime/route bugs.

## 1. Restart the backend through the wrapper, not raw `waitress-serve`

If the backend is normally started through `run_backend_service.sh` or a systemd unit that sources `scripts/runtime_env.sh`, do not restart it by invoking raw `waitress-serve` directly.

Why this matters:
- the wrapper loads `HERMES_WEB_MODE`
- it loads `HERMES_WEB_HERMES_API_BASE_URL`
- it loads `HERMES_WEB_HERMES_API_KEY` / `API_SERVER_KEY`
- it loads DB/env contour variables

A raw restart can leave the process alive and health-checkable, but the runtime silently degrades to the wrong contour or to `mock-hermes`-style behavior.

Verification after restart:
1. Check `/api/health` for live mode and model.
2. If behavior still looks suspicious, inspect the running backend process environment and confirm the expected env keys are present.
3. Only then continue with user-path validation.

## 2. Presentation follow-up after clarification must anchor to the real draft, not the clarification turn

Failure pattern:
- user asks for `pptx` or a presentation draft
- assistant asks a clarification question
- user then asks: add formatting, markup, images, or links
- route logic treats the latest clarification message as the prior assistant context
- follow-up either goes to the wrong route or reformats only the tail instead of the whole draft

What to verify:
1. The follow-up is classified as a presentation-enhancement follow-up, not as a fresh collection/clarification turn.
2. Focused follow-up context uses the last substantive presentation draft, skipping `clarification_request` / `approval_request` assistant messages.
3. The prompt explicitly says to rebuild the whole deck, not just the last items.
4. If the user asks for internet images/links and live web search is unavailable, the system must produce honest recommendations, not invented URLs.

## 3. Guard against slide explosion on re-export

Even after follow-up routing is fixed, a second defect can remain in `markup -> PPTX` conversion.

Failure pattern:
- LLM returns a cleaner deck with inline subheads like `Типовые слои`, `Шаг 1`, `Лучшие практики`
- PPTX parser mistakes these subheads for new top-level slides
- export balloons from the intended compact deck into dozens of slides

Guardrail:
- when asking for presentation enhancement, tell the model to preserve the original slide order and approximate slide count, and not to split one slide into many unless the source explicitly requires it
- on the export side, if explicit `Слайд N:` blocks exist, prefer them as the authoritative segmentation boundary

## Recommended live-check order

1. Reproduce on the named prod contour.
2. Confirm backend restart path preserved env.
3. Confirm `/api/health` mode/model after restart.
4. Reproduce the exact follow-up turn and inspect whether focused context ignores clarification messages.
5. Validate the LLM reply text before exporting.
6. Then validate the generated PPTX structure and actual slide count.
