from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone

LOCAL_PROJECT = Path('/home/hermes/workspace/hermes-web-mvp-react-8793')
LOCAL_TG_API = Path('/home/hermes/workspace/TG-API')
LOCAL_BACKUP = Path('/home/hermes/workspace/cons-github-backup')
LOCAL_SYSTEMD = Path('/home/hermes/.config/systemd/user')
REMOTE_HOST = '178.104.207.89'
REMOTE_PROJECT = '/home/hermes/workspace/hermes-web-mvp-react-8793'
REMOTE_SYSTEMD = '/home/hermes/.config/systemd/user'
EXCLUDE_DIR_NAMES = {'node_modules', '.venv', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.cache', 'dist', '.git'}
EXCLUDE_FILE_SUFFIXES = {'.pyc', '.pyo', '.log', '.sqlite', '.sqlite3', '.duckdb', '.db', '.wal', '.shm', '.tgz'}
EXCLUDE_FILE_NAMES = {'.env', '.env.local', '.env.production', '.env.development'}
ROOT_FILES = [
    'README.md', 'RUNTIME-RUNBOOK.md', 'REACT_MIGRATION_STATUS.md', 'package.json', 'package-lock.json',
    'vite.config.js', 'docker-compose.yml', 'run_backend_service.sh', 'run_frontend_react_service.sh',
    'run_frontend_service.sh', 'run_copilotkit_runtime_service.sh'
]
TREE_DIRS = ['services', 'deploy/package', 'scripts', 'docs']
LOCAL_SYSTEMD_FILES = ['hermes-web-frontend-8803.service']
LOCAL_SYSTEMD_DROPINS = [('hermes-web-frontend-8803.service.d', 'backend-override.conf')]
REMOTE_SYSTEMD_FILES = [
    'hermes-web-backend-8791.service', 'hermes-web-backend-8791-public.service',
    'hermes-web-frontend-8793.service', 'hermes-web-copilotkit-8794.service'
]
REMOTE_SYSTEMD_DROPINS = [('hermes-web-backend-8791.service.d', 'public-bind.conf'), ('hermes-web-backend-8791.service.d', 'timeout.conf')]
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


def run(cmd, *, check=True, capture_output=True, text=True, input=None):
    return subprocess.run(cmd, check=check, capture_output=capture_output, text=text, input=input)


def reset_tree() -> None:
    LOCAL_BACKUP.mkdir(parents=True, exist_ok=True)
    for name in ['local-95', 'remote-178']:
        target = LOCAL_BACKUP / name
        if target.exists():
            shutil.rmtree(target)
    for name in ['local-95/project', 'local-95/tg-api', 'local-95/runtime-systemd', 'remote-178/project', 'remote-178/runtime-systemd']:
        (LOCAL_BACKUP / name).mkdir(parents=True, exist_ok=True)


def should_keep(rel: Path) -> bool:
    if any(part in EXCLUDE_DIR_NAMES for part in rel.parts):
        return False
    if rel.name in EXCLUDE_FILE_NAMES:
        return False
    if any(rel.name.endswith(s) for s in EXCLUDE_FILE_SUFFIXES):
        return False
    norm = '/' + '/'.join(rel.parts) + '/'
    if '/services/backend/data/' in norm:
        return False
    return True


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


def copy_local_project() -> None:
    target_root = LOCAL_BACKUP / 'local-95' / 'project'
    for rel_name in ROOT_FILES:
        src = LOCAL_PROJECT / rel_name
        if src.exists() and src.is_file() and should_keep(Path(rel_name)):
            dst = target_root / rel_name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    for rel_name in TREE_DIRS:
        base = LOCAL_PROJECT / rel_name
        if not base.exists():
            continue
        for src in base.rglob('*'):
            if src.is_dir():
                continue
            rel = src.relative_to(LOCAL_PROJECT)
            if not should_keep(rel):
                continue
            dst = target_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def copy_local_tg_api() -> None:
    if not LOCAL_TG_API.exists():
        return
    target_root = LOCAL_BACKUP / 'local-95' / 'tg-api'
    for src in LOCAL_TG_API.rglob('*'):
        if src.is_dir():
            continue
        rel = src.relative_to(LOCAL_TG_API)
        if not should_keep_tg_api(rel):
            continue
        dst = target_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def copy_local_systemd() -> None:
    target = LOCAL_BACKUP / 'local-95' / 'runtime-systemd'
    for name in LOCAL_SYSTEMD_FILES:
        src = LOCAL_SYSTEMD / name
        if src.exists():
            shutil.copy2(src, target / name)
    for dirname, filename in LOCAL_SYSTEMD_DROPINS:
        src = LOCAL_SYSTEMD / dirname / filename
        if src.exists():
            dst = target / dirname / filename
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def ssh_cat_bytes(remote_path: str) -> bytes:
    result = subprocess.run(['ssh', REMOTE_HOST, f'cat {remote_path}'], check=True, capture_output=True)
    return result.stdout


def copy_remote_file(remote_path: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(ssh_cat_bytes(remote_path))


def list_remote_files() -> list[str]:
    script = r'''
from pathlib import Path
root = Path("''' + REMOTE_PROJECT + '''")
root_files = ''' + repr(ROOT_FILES) + r'''
tree_dirs = ''' + repr(TREE_DIRS) + r'''
exclude_dir_names = ''' + repr(EXCLUDE_DIR_NAMES) + r'''
exclude_file_suffixes = ''' + repr(EXCLUDE_FILE_SUFFIXES) + r'''
exclude_file_names = ''' + repr(EXCLUDE_FILE_NAMES) + r'''

def should_keep(rel):
    if any(part in exclude_dir_names for part in rel.parts):
        return False
    if rel.name in exclude_file_names:
        return False
    if any(rel.name.endswith(s) for s in exclude_file_suffixes):
        return False
    norm = '/' + '/'.join(rel.parts) + '/'
    if '/services/backend/data/' in norm:
        return False
    return True

for rel_name in root_files:
    p = root / rel_name
    if p.exists() and p.is_file() and should_keep(Path(rel_name)):
        print(p)
for rel_name in tree_dirs:
    base = root / rel_name
    if not base.exists():
        continue
    for p in base.rglob('*'):
        if p.is_dir():
            continue
        rel = p.relative_to(root)
        if should_keep(rel):
            print(p)
'''
    result = run(['ssh', REMOTE_HOST, 'python3 -'], input=script)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def copy_remote_project() -> None:
    target_root = LOCAL_BACKUP / 'remote-178' / 'project'
    for remote_file in list_remote_files():
        rel = Path(remote_file).relative_to(REMOTE_PROJECT)
        copy_remote_file(remote_file, target_root / rel)


def copy_remote_systemd() -> None:
    target = LOCAL_BACKUP / 'remote-178' / 'runtime-systemd'
    for name in REMOTE_SYSTEMD_FILES:
        copy_remote_file(f'{REMOTE_SYSTEMD}/{name}', target / name)
    for dirname, filename in REMOTE_SYSTEMD_DROPINS:
        remote_path = f'{REMOTE_SYSTEMD}/{dirname}/{filename}'
        copy_remote_file(remote_path, target / dirname / filename)


def write_root_files() -> None:
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    (LOCAL_BACKUP / 'README.md').write_text(
        '# Cons project backup\n\n'
        'Это curated backup составного живого контура Hermes Web: frontend 8803 на сервере 95.182.85.233 + backend/runtime-контур на 178.104.207.89 + TG API contour на 95.\n\n'
        'Что включено:\n'
        '- local-95: production frontend contour 8803, project code, launcher-скрипты и systemd units\n'
        '- local-95/tg-api: код, конфиги, cron/install-логика и документация TG API контура\n'
        '- remote-178: backend/runtime/deploy contour, project code, launcher-скрипты и systemd units\n'
        '- deploy/package, docs, scripts, backend/frontend-react/frontend компоненты\n'
        '- отдельные root-docs по архитектуре, логике и границам prod-контура\n\n'
        'Что исключено:\n'
        '- node_modules, dist, .venv\n'
        '- services/backend/data и runtime DB\n'
        '- TG API session/runtime/raw_logs/exports/reports/analytics и секретные env/state-файлы\n'
        '- .env*, логи, кэши, __pycache__, runtime-артефакты\n\n'
        'Назначение:\n'
        '- backup полного рабочего контура агента под репозиторий Cons-project\n'
        '- хранение frontend 8803, backend 178 и TG API в одном private GitHub repo\n\n'
        f'Последнее обновление: {timestamp}\n',
        encoding='utf-8',
    )
    (LOCAL_BACKUP / '.gitignore').write_text('.DS_Store\n*.pyc\n__pycache__/\n*.log\n.env\n', encoding='utf-8')
    (LOCAL_BACKUP / 'BACKUP_SCOPE.md').write_text(
        '# Backup scope\n\n'
        '- `local-95/project/**` — локальный prod/frontend contour 8803\n'
        '- `local-95/tg-api/**` — код и конфигурация TG API контура на 95\n'
        '- `local-95/runtime-systemd/**` — unit/drop-in фронта 8803\n'
        '- `remote-178/project/**` — backend/runtime/deploy contour 178\n'
        '- `remote-178/runtime-systemd/**` — systemd units и backend drop-ins 178\n\n'
        'Осознанно исключено:\n'
        '- runtime-данные, БД, логи, кэши, `.env*`, TG API session/export-артефакты и generated analytics\n',
        encoding='utf-8'
    )
    (LOCAL_BACKUP / 'CONTOUR_MAP.md').write_text(
        '# Contour map\n\n'
        '## Сервер 95.182.85.233\n\n'
        '- `hermes-web-mvp-react-8793` — локальный project snapshot, из которого берётся production frontend contour `8803`.\n'
        '- `local-95/runtime-systemd/hermes-web-frontend-8803.service` — unit фронта `8803`.\n'
        '- `local-95/tg-api/**` — Telegram API/monitoring contour: сбор, подготовка daily digest, web auth, cron/install-скрипты, channel-конфиги и вспомогательная аналитика.\n'
        '- Логическая роль: пользовательский frontend и TG API находятся на 95, но являются частью общего рабочего контура агента.\n\n'
        '## Сервер 178.104.207.89\n\n'
        '- `remote-178/project/services/backend/**` — основной backend/API-контур `8791`.\n'
        '- `remote-178/project/services/frontend/**` и `services/frontend-react/**` — кодовые артефакты backend-side web проекта и deploy package.\n'
        '- `remote-178/project/deploy/package/**` — package/deploy/runbook/install-логика.\n'
        '- `remote-178/runtime-systemd/**` — unit-файлы backend, frontend `8793`, CopilotKit `8794` и backend drop-ins.\n\n'
        '## Логика хранения\n\n'
        '- Репозиторий `Cons-project` — это не просто snapshot одного хоста, а curated combined backup общего боевого контура.\n'
        '- `local-95` хранит то, что физически живёт на 95 и нужно для работы контура 178.\n'
        '- `remote-178` хранит runtime/deploy/backend часть, которая физически живёт на 178.\n',
        encoding='utf-8'
    )
    (LOCAL_BACKUP / 'DEPLOYMENT_AND_BACKUP_LOGIC.md').write_text(
        '# Deployment and backup logic\n\n'
        '## Что считается боевым контуром\n\n'
        '- UI для пользователей: frontend на `95.182.85.233:8803`.\n'
        '- Основной API/runtime: backend на `178.104.207.89:8791`.\n'
        '- Дополнительные runtime-компоненты: frontend `8793` и CopilotKit `8794` на 178 как часть deploy/runtime контура.\n'
        '- Telegram data contour: `TG-API` на 95 как отдельный, но связанный operational компонент.\n\n'
        '## Почему backup комбинированный\n\n'
        '- Если сохранять только 178, теряется реальный production frontend `8803`.\n'
        '- Если сохранять только 95, теряется backend/deploy/runtime часть 178.\n'
        '- Поэтому weekly refresh собирает combined backup из двух хостовых зон в один GitHub repo `Cons-project`.\n\n'
        '## Что делает weekly refresh\n\n'
        '1. Очищает только рабочие каталоги backup, не трогая `.git`.\n'
        '2. Копирует локальный web project с 95 в `local-95/project`.\n'
        '3. Копирует локальный TG API contour в `local-95/tg-api`, но без session/runtime/secrets.\n'
        '4. Копирует relevant systemd unit/drop-in фронта `8803`.\n'
        '5. По SSH забирает curated snapshot проекта и systemd-логики с 178 в `remote-178/**`.\n'
        '6. Перегенерирует описательные root-файлы репозитория.\n'
        '7. Делает `git add`, commit и push в `origin/main`, если есть изменения.\n\n'
        '## Расписание\n\n'
        '- Hermes cron job: `cons-project-backup-weekly`\n'
        '- Job id: `cf27d7146dc2`\n'
        '- Schedule: `0 1 * * 1` (это `04:00 МСК`, то есть внутри окна `03:00–06:00 МСК`).\n\n'
        '## Что не попадает в GitHub backup\n\n'
        '- secrets и `.env*`;\n'
        '- runtime DB и локальные state-файлы;\n'
        '- TG API `session/`, `runtime/`, `raw_logs/`, `exports/`, `reports/`, `analytics/`;\n'
        '- кэши, `node_modules`, `.venv`, build artifacts, логи.\n',
        encoding='utf-8'
    )
    (LOCAL_BACKUP / 'TG_API_SCOPE.md').write_text(
        '# TG API scope inside Cons-project backup\n\n'
        '## Что включено\n\n'
        '- Основной Python-код: `app.py`, `monitor_client.py`, `telegram_monitor_pipeline.py`, `collect_daily_pipeline.py` и связанные модули.\n'
        '- Auth/web-flow: `telegram_web_auth.py`, `create_auth_link.py`, `check_chat_access.py`, `login.py`, `ensure_api.py`.\n'
        '- Build/analytics helpers: `build_digest_context.py`, `build_export_dashboard.py`, `build_local_analytics_dashboard.py`, `generate_processed_csv.py`, `weekly_monitor_qa.py`.\n'
        '- Конфиги и справочные файлы: `channels*.yml`, `requirements.txt`, `post_type_glossary.md`, `private_profile_setup.md`, `telegram_web_auth.md`, `instruction_for_tg_login.txt`, `run_tg_api_service.sh`, `install_hermes_tg_cron.py`, `hermes_tg_cron_manifest.json`.\n\n'
        '## Что исключено\n\n'
        '- `session/` и `*.session`;\n'
        '- `runtime/`, `raw_logs/`, `archive/`, `exports/`, `reports/`;\n'
        '- `private-profile.env`, auth/state-файлы и прочие чувствительные локальные артефакты;\n'
        '- `.venv`, `__pycache__`, логи и временные generated outputs.\n\n'
        '## Зачем TG API лежит в этом backup\n\n'
        '- Это operational часть общего пользовательского контура на 95.\n'
        '- Без неё backup `Cons-project` не отражал бы весь фактический runtime и вспомогательную автоматизацию агента.\n',
        encoding='utf-8'
    )
    (LOCAL_BACKUP / 'PROD_CONTOUR_ARCHITECTURE.md').write_text(
        '# Production contour architecture\n\n'
        '## Короткая схема\n\n'
        '```\n'
        'Пользователь / браузер\n'
        '        |\n'
        '        v\n'
        '95.182.85.233 :8803  (production frontend)\n'
        '        |\n'
        '        | HTTP / API proxy\n'
        '        v\n'
        '178.104.207.89 :8791 (backend API)\n'
        '        |\\\n'
        '        | \\\n'
        '        |  +--> Hermes / jobs / chat runtime\n'
        '        |\n'
        '        +----> 178 :8794 (CopilotKit runtime, when needed)\n'
        '\n'
        '95.182.85.233 : TG-API\n'
        '        |\n'
        '        +--> Telegram monitoring / digest / auth helper contour\n'
        '```\n\n'
        '## Архитектурные роли\n\n'
        '- `95:8803` — пользовательская точка входа и production UI.\n'
        '- `178:8791` — канонический backend/API и логика чатов, задач, jobs, dashboard и routing.\n'
        '- `178:8794` — вспомогательный runtime для CopilotKit-сценариев.\n'
        '- `95/TG-API` — отдельный operational контур Telegram-данных, связанный с общим продуктовым контуром, но не являющийся частью browser UI runtime.\n\n'
        '## Что важно не путать\n\n'
        '- Физическое размещение и логическая принадлежность — не одно и то же.\n'
        '- Frontend `8803` физически живёт на 95, но логически относится к prod-контуру агента на 178.\n'
        '- Поэтому архитектурно контур split-host, а backup должен быть combined.\n',
        encoding='utf-8'
    )
    (LOCAL_BACKUP / 'PROD_CONTOUR_LOGIC.md').write_text(
        '# Production contour logic\n\n'
        '## Логическая схема запросов\n\n'
        '1. Пользователь открывает UI на `95:8803`.\n'
        '2. Frontend рендерит chat-first интерфейс и отправляет API-запросы в backend-контур `178:8791`.\n'
        '3. Backend обрабатывает auth, chat, jobs, dashboard, memory/personalization и связанные runtime-пайплайны.\n'
        '4. При специальных сценариях backend/контур может опираться на `8794` как на дополнительный runtime-слой.\n'
        '5. Вне UI параллельно работает `TG-API` на 95: сбор Telegram-данных, auth-link flow, daily/weekly мониторинг и digest pipeline.\n\n'
        '## Почему это один product contour\n\n'
        '- Пользователь видит единый продуктовый интерфейс.\n'
        '- Backend-логика и часть operational automation физически разнесены, но вместе обеспечивают один рабочий сервис.\n'
        '- Потеря любой из этих частей делает восстановление неполным: без `8803` нет реального prod UI; без `8791` нет business logic; без `TG-API` пропадает связанная operational автоматизация.\n\n'
        '## Почему эти документы лежат в Cons-project\n\n'
        '- Чтобы при переносе, аудите или аварийном восстановлении не приходилось заново восстанавливать картину по кускам.\n'
        '- Чтобы было явно видно, какие части относятся к 95, какие к 178 и как они логически связаны.\n',
        encoding='utf-8'
    )


def ensure_repo() -> None:
    if not (LOCAL_BACKUP / '.git').exists():
        run(['git', 'init', '-b', 'main', str(LOCAL_BACKUP)])


def git(*args: str) -> str:
    return run(['git', '-C', str(LOCAL_BACKUP), *args]).stdout.strip()


def commit_and_push() -> str:
    status = git('status', '--short')
    if not status:
        return 'cons-github-backup: изменений нет, push не требуется'
    git('add', '.')
    run(['git', '-C', str(LOCAL_BACKUP), '-c', 'user.name=Cons Backup', '-c', 'user.email=cons-backup@local', 'commit', '-m', 'Weekly curated backup refresh'])
    remote = subprocess.run(['git', '-C', str(LOCAL_BACKUP), 'remote', 'get-url', 'origin'], text=True, capture_output=True)
    head = git('log', '--oneline', '-1')
    if remote.returncode != 0:
        return f'cons-github-backup: локальный commit создан, origin ещё не настроен\n{head}'
    push = subprocess.run(['git', '-C', str(LOCAL_BACKUP), 'push', '-u', 'origin', 'main'], text=True, capture_output=True)
    if push.returncode != 0:
        return f'cons-github-backup: commit создан, но push не прошёл\n{head}\n{(push.stderr or push.stdout).strip()}'
    return f'cons-github-backup: обновлено и отправлено в origin/main\n{head}'


def main() -> None:
    ensure_repo()
    reset_tree()
    copy_local_project()
    copy_local_tg_api()
    copy_local_systemd()
    copy_remote_project()
    copy_remote_systemd()
    write_root_files()
    print(commit_and_push())


if __name__ == '__main__':
    main()
