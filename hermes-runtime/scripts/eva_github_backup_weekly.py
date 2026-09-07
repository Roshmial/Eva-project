from pathlib import Path
import shutil
import subprocess

SRC_SKILLS = Path('/home/hermes/.hermes/skills')
BACKUP = Path('/home/hermes/workspace/eva-github-backup')
WORKSPACE = Path('/home/hermes/workspace')
HERMES_HOME = Path('/home/hermes/.hermes')
ALLOWED_DIRS = {'references', 'templates', 'scripts', 'assets'}
TG_API = WORKSPACE / 'TG-API'
WEB_DEPLOY_PACKAGE = WORKSPACE / 'hermes-web-mvp-react-8793' / 'deploy' / 'package'

TG_API_EXCLUDE_DIR_NAMES = {
    'node_modules', '.venv', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.cache', '.git',
    'session', 'runtime', 'raw_logs', 'archive', 'exports', 'reports', 'analytics'
}
TG_API_EXCLUDE_FILE_SUFFIXES = {'.pyc', '.pyo', '.log', '.sqlite', '.sqlite3', '.duckdb', '.db', '.wal', '.shm', '.session', '.jsonl', '.html'}
TG_API_EXCLUDE_FILE_NAMES = {
    '.env', 'private-profile.env', 'auth_link_state.json', 'api_server.log',
    '.tg-monitor-profile-name', '.tg-monitor-config-name', '.tg-monitor-instance-id',
    'tg-since-id-it_consulting.json'
}
TG_API_EXCLUDE_PREFIXES = ('telegram_channel_analytics_', 'history-')

HERMES_SCRIPT_EXCLUDE = {'.pyc', '.pyo', '.log'}
TRANSFER_DOCS = [
    'README.md',
    'dependency-inventory.md',
    'HERMES_ZERO_SERVER_CHECKLIST.md',
    'bootstrap-hermes-zero-server.sh',
    'install-project-deps.sh',
    'install-systemd-user.sh',
    'verify-deployment.sh',
    'env/hermes-web.env.example',
    'systemd/hermes-web-backend-8791.service',
    'systemd/hermes-web-frontend-8793.service',
    'systemd/hermes-web-copilotkit-8794.service',
]


def reset_curated_tree() -> None:
    for name in ['skills', 'workspace-notes', 'docs', 'tg-api', 'hermes-runtime']:
        target = BACKUP / name
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)


def copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def copy_workspace_notes() -> None:
    copy_if_exists(WORKSPACE / 'decision-log.md', BACKUP / 'workspace-notes' / 'decision-log.md')
    copy_if_exists(WORKSPACE / 'interaction-notes.md', BACKUP / 'workspace-notes' / 'interaction-notes.md')


def copy_eva_data_docs() -> None:
    base = WORKSPACE / 'eva-data'
    for rel in ['README.md', 'ARCHITECTURE.md', 'refresh_eva_hub.py']:
        copy_if_exists(base / rel, BACKUP / 'docs' / 'eva-data' / rel)


def copy_skills() -> None:
    for path in SRC_SKILLS.rglob('*'):
        if path.is_dir():
            continue
        rel = path.relative_to(SRC_SKILLS)
        keep = False
        if path.name == 'SKILL.md':
            keep = True
        elif len(rel.parts) >= 2 and rel.parts[-2] in ALLOWED_DIRS:
            keep = True
        if keep:
            dst = BACKUP / 'skills' / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dst)


def should_keep_tg_api(rel: Path) -> bool:
    if any(part in TG_API_EXCLUDE_DIR_NAMES for part in rel.parts):
        return False
    if rel.name in TG_API_EXCLUDE_FILE_NAMES:
        return False
    if rel.name.startswith(TG_API_EXCLUDE_PREFIXES):
        return False
    if any(rel.name.endswith(s) for s in TG_API_EXCLUDE_FILE_SUFFIXES):
        return False
    return True


def copy_tg_api() -> None:
    if not TG_API.exists():
        return
    target_root = BACKUP / 'tg-api'
    for src in TG_API.rglob('*'):
        if src.is_dir():
            continue
        rel = src.relative_to(TG_API)
        if not should_keep_tg_api(rel):
            continue
        dst = target_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def copy_hermes_runtime() -> None:
    target = BACKUP / 'hermes-runtime'
    copy_if_exists(HERMES_HOME / 'config.yaml', target / 'config' / 'config.yaml')
    copy_if_exists(HERMES_HOME / 'cron' / 'jobs.json', target / 'cron' / 'jobs.json')

    scripts_src = HERMES_HOME / 'scripts'
    if scripts_src.exists():
        for src in scripts_src.rglob('*'):
            if src.is_dir():
                continue
            if any(src.name.endswith(s) for s in HERMES_SCRIPT_EXCLUDE):
                continue
            rel = src.relative_to(scripts_src)
            dst = target / 'scripts' / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    for rel in TRANSFER_DOCS:
        copy_if_exists(WEB_DEPLOY_PACKAGE / rel, target / 'transfer-kit' / rel)


def write_root_files() -> None:
    (BACKUP / 'README.md').write_text(
        '# Eva backup\n\n'
        'Это локальный backup-репозиторий ключевых элементов рабочей конфигурации Евы и комплекта для переноса на чистый сервер.\n\n'
        'Что включено:\n'
        '- skills из `~/.hermes/skills`\n'
        '- `decision-log.md`\n'
        '- `interaction-notes.md`\n'
        '- выборочные рабочие документы из `workspace/eva-data`\n'
        '- curated snapshot `workspace/TG-API`\n'
        '- `~/.hermes/config.yaml`, `~/.hermes/cron/jobs.json`, `~/.hermes/scripts/*`\n'
        '- transfer-kit для чистого Linux-сервера с Hermes\n\n'
        'Что намеренно исключено:\n'
        '- `~/.hermes/memories/*`\n'
        '- `~/.hermes/state.db*`\n'
        '- `~/.hermes/logs/*`\n'
        '- `~/.hermes/sessions/*`\n'
        '- `~/.hermes/cron/output/*`\n'
        '- TG API `session/`, `runtime/`, `raw_logs/`, `exports/`, `reports/`, `analytics/`\n'
        '- токены, auth/state-файлы, кэши, скриншоты и runtime-артефакты\n\n'
        'Назначение:\n'
        '- безопасный backup знаний, навыков и ключевой operational-конфигурации Евы\n'
        '- база для восстановления на новом сервере после установки Hermes\n\n'
        'Состояние отражает содержимое текущего snapshot.\n',
        encoding='utf-8',
    )
    (BACKUP / '.gitignore').write_text('.DS_Store\n*.pyc\n__pycache__/\n*.log\n.env\n', encoding='utf-8')
    (BACKUP / 'HERMES_TRANSFER_AND_RESTORE.md').write_text(
        '# Hermes transfer and restore\n\n'
        '## Что лежит в этом backup\n\n'
        '- `skills/` — пользовательские и накопленные procedural skills Евы.\n'
        '- `workspace-notes/` — `decision-log.md` и `interaction-notes.md`.\n'
        '- `tg-api/` — operational код и конфигурация Telegram API/monitoring контура без secrets и runtime-данных.\n'
        '- `hermes-runtime/config/config.yaml` — текущая Hermes-конфигурация.\n'
        '- `hermes-runtime/cron/jobs.json` — актуальные cron job definitions.\n'
        '- `hermes-runtime/scripts/` — локальные Hermes automation scripts.\n'
        '- `hermes-runtime/transfer-kit/` — docs/scripts для bootstrap нового сервера.\n\n'
        '## Базовый порядок переноса на чистый сервер\n\n'
        '1. Установить Hermes: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`\n'
        '2. Выполнить `hermes setup` или перенести curated `config.yaml` как основу.\n'
        '3. Восстановить `~/.hermes/skills/` из `skills/`.\n'
        '4. Восстановить `~/.hermes/scripts/` из `hermes-runtime/scripts/`.\n'
        '5. Перенести `~/.hermes/cron/jobs.json`, затем проверить `hermes cron list`.\n'
        '6. Для web-контура использовать `hermes-runtime/transfer-kit/` как стартовый пакет для нового Linux-сервера.\n'
        '7. Для TG API развернуть `tg-api/`, затем отдельно внести локальные auth/session/env-файлы вне Git.\n\n'
        '## Что нужно добавить вручную после переноса\n\n'
        '- `~/.hermes/.env` и другие secrets;\n'
        '- OAuth/auth tokens (`auth.json`, gateway auth, Google tokens и т.п.);\n'
        '- TG API session и private env;\n'
        '- runtime БД, session store и прочие state-файлы, если нужен именно continuity, а не только конфигурация.\n',
        encoding='utf-8',
    )
    (BACKUP / 'TG_API_SCOPE.md').write_text(
        '# TG API scope inside Eva backup\n\n'
        '## Что включено\n\n'
        '- основной Python-код и pipeline-скрипты;\n'
        '- web auth / login / access helpers;\n'
        '- channel-конфиги, glossary, requirements, install/service scripts;\n'
        '- cron manifest и setup-файлы.\n\n'
        '## Что исключено\n\n'
        '- `session/`, `runtime/`, `raw_logs/`, `exports/`, `reports/`, `analytics/`;\n'
        '- `private-profile.env`, auth/state-файлы и generated outputs.\n',
        encoding='utf-8',
    )


def run_git(*args: str) -> str:
    completed = subprocess.run(
        ['git', '-C', str(BACKUP), *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def ensure_repo() -> None:
    if not (BACKUP / '.git').exists():
        subprocess.run(['git', 'init', '-b', 'main', str(BACKUP)], check=True, text=True, capture_output=True)


def commit_and_push() -> str:
    status = run_git('status', '--short')
    if not status:
        return 'eva-github-backup: изменений нет, push не требуется'
    run_git('add', '.')
    subprocess.run(
        ['git', '-C', str(BACKUP), '-c', 'user.name=Eva Backup', '-c', 'user.email=eva-backup@local', 'commit', '-m', 'Weekly curated backup refresh'],
        check=True,
        text=True,
        capture_output=True,
    )
    push = subprocess.run(
        ['git', '-C', str(BACKUP), 'push', 'origin', 'main'],
        check=True,
        text=True,
        capture_output=True,
    )
    head = run_git('log', '--oneline', '-1')
    return f'eva-github-backup: обновлено и отправлено в origin/main\n{head}\n{push.stdout.strip()}'


def main() -> None:
    ensure_repo()
    reset_curated_tree()
    copy_workspace_notes()
    copy_eva_data_docs()
    copy_tg_api()
    copy_hermes_runtime()
    copy_skills()
    write_root_files()
    print(commit_and_push())


if __name__ == '__main__':
    main()
