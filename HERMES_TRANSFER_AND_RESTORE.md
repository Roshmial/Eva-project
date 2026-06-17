# Hermes transfer and restore

## Что лежит в этом backup

- `skills/` — пользовательские и накопленные procedural skills Евы.
- `workspace-notes/` — `decision-log.md` и `interaction-notes.md`.
- `tg-api/` — operational код и конфигурация Telegram API/monitoring контура без secrets и runtime-данных.
- `hermes-runtime/config/config.yaml` — текущая Hermes-конфигурация.
- `hermes-runtime/cron/jobs.json` — актуальные cron job definitions.
- `hermes-runtime/scripts/` — локальные Hermes automation scripts.
- `hermes-runtime/transfer-kit/` — docs/scripts для bootstrap нового сервера.

## Базовый порядок переноса на чистый сервер

1. Установить Hermes: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`
2. Выполнить `hermes setup` или перенести curated `config.yaml` как основу.
3. Восстановить `~/.hermes/skills/` из `skills/`.
4. Восстановить `~/.hermes/scripts/` из `hermes-runtime/scripts/`.
5. Перенести `~/.hermes/cron/jobs.json`, затем проверить `hermes cron list`.
6. Для web-контура использовать `hermes-runtime/transfer-kit/` как стартовый пакет для нового Linux-сервера.
7. Для TG API развернуть `tg-api/`, затем отдельно внести локальные auth/session/env-файлы вне Git.

## Что нужно добавить вручную после переноса

- `~/.hermes/.env` и другие secrets;
- OAuth/auth tokens (`auth.json`, gateway auth, Google tokens и т.п.);
- TG API session и private env;
- runtime БД, session store и прочие state-файлы, если нужен именно continuity, а не только конфигурация.
