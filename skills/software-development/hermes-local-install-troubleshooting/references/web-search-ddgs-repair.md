# web_search / ddgs repair pattern

Use this when Hermes runs normally but `web_search` is unavailable or errors because the active Hermes virtualenv lacks DuckDuckGo provider packages.

## Symptoms

- `web_search` fails at runtime with a missing-module error.
- Direct import checks show:
  - `ddgs: MISSING`
  - sometimes also `duckduckgo_search: MISSING`
- `hermes doctor` may show the `web` toolset unavailable before repair.

## Repair steps

1. Confirm the active Hermes interpreter.
   - Example: `/home/hermes/apps/hermes-agent/.venv/bin/python3`

2. Verify the missing modules directly.
   - `python - <<'PY'`
     `import importlib.util`
     `for m in ['ddgs','duckduckgo_search']:`
     `    print(m, 'FOUND' if importlib.util.find_spec(m) else 'MISSING')`
     `PY`

3. Install into the Hermes venv, not system Python.
   - `.../.venv/bin/python -m pip install ddgs duckduckgo_search`

4. Run post-install checks.
   - `.../.venv/bin/python -m pip check`
   - `.../.venv/bin/hermes doctor`

5. Verify the exact runtime path, not just imports.
   - Example live check:
   - `from tools.web_tools import web_search_tool`
   - `print(web_search_tool('OpenAI latest news', 3))`

## Extra step if doctor reports config migration

Run:
- `hermes doctor --fix`
- then `hermes config check`

## Important pitfall

Do not conclude that `web_search` is generally broken. In this case the durable lesson is narrower:
- Hermes may be healthy overall,
- but the active venv can still be missing optional search-provider packages,
- and the repair must be validated through the exact tool code path.
