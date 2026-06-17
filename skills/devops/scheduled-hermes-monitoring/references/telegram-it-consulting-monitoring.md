# Telegram IT-consulting daily monitoring — session notes

## User correction captured

The user rejected a design where the assistant only created a script and told him to configure scheduling/summarization manually.

Correct interpretation of the task:
- the pipeline must be operated by Hermes tools;
- Hermes should participate from API startup/check through final summary delivery;
- scheduling should be Hermes cron, not manual OS cron/Task Scheduler instructions;
- summarization should be performed by the Hermes agent/model, not hardcoded calls to external LLM APIs unless explicitly requested;
- setup should proceed step by step: perform one step, test it, report the result, then wait for approval/adjustment.

## Working project context from the session

Project/workdir found:
- `D:/LLM/workspace/TG-API`

Relevant files observed:
- `app.py` — Flask API exposing `/export`.
- `channels.yml` — profile/channel configuration.
- `monitor_client.py` — collector script for incremental fetch/state handling.
- `tg-since-id-it_consulting.json` — per-channel last processed Telegram message IDs.
- `profile_1.session` and `session/profile_1.session` — Telegram session files.

Configured channels at that time:
- `b1_news`
- `Axenix_Ru`
- `beringpro`
- `Softline`
- `k2_tech`
- `Lanit_life`
- `InnotechCompany`
- `YakovPartners`
- `delret`
- `tedo_business`
- `kept_business`
- `Reksoft_group`
- `norbit_ru`

## Durable technical lesson

For local Hermes operation, the source API must be able to load configs from the local project directory, not only from Docker-mounted paths.

A useful pattern in `app.py` is to have config discovery try:
1. local files next to `app.py`;
2. legacy container paths.

This preserves compatibility while allowing Hermes to start and test the API locally.

## Boundary discovered

A local API test can start successfully yet still fail with Telegram authorization. Treat this as an authentication boundary, not as a pipeline failure.

Correct behavior:
- verify session authorization before building/scheduling downstream steps;
- if Telegram requires code/2FA, stop and ask for user participation;
- do not fabricate a successful digest until `/export` returns real messages or a confirmed empty result.

## Suggested first test sequence for future sessions

1. Locate `D:/LLM/workspace/TG-API` and inspect `app.py`, `channels.yml`, and state JSON.
2. Start or verify the Flask API under Hermes.
3. Check Telegram session validity.
4. Call `/export` with current `since` state.
5. Only after a successful response, proceed to collector, summarization prompt, and Hermes cron.