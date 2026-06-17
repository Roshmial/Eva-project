#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

import duckdb

BASE_DIR = Path('/home/hermes/workspace/eva-data')
DB_PATH = BASE_DIR / 'eva_hub.duckdb'
TMP_DIR = BASE_DIR / 'tmp'
BACKUPS_DIR = BASE_DIR / 'backups'
HERMES_STATE_DB = Path('/home/hermes/.hermes/state.db')
HERMES_CRON_JOBS_JSON = Path('/home/hermes/.hermes/cron/jobs.json')
APP_BACKEND_DB = Path('/home/hermes/workspace/hermes-web-mvp/services/backend/data/hermes_web_app.duckdb')
TG_DIR = Path('/home/hermes/workspace/TG-API')
TENDERS_DIR = Path('/home/hermes/workspace/tenders')
WORKSPACE_DIR = Path('/home/hermes/workspace')
TG_CACHE_DOCS_DIR = Path('/home/hermes/.hermes/cache/documents')
INTERACTION_NOTES_PATH = WORKSPACE_DIR / 'interaction-notes.md'
DECISION_LOG_PATH = WORKSPACE_DIR / 'decision-log.md'

if str(TG_DIR) not in sys.path:
    sys.path.insert(0, str(TG_DIR))

from telegram_monitor_pipeline import derive_rows  # type: ignore  # noqa: E402


@dataclass
class SourceFile:
    domain: str
    dataset: str
    path: Path
    file_tag: str


def load_hermes_cron_jobs() -> list[dict]:
    if not HERMES_CRON_JOBS_JSON.exists():
        return []
    payload = json.loads(HERMES_CRON_JOBS_JSON.read_text(encoding='utf-8'))
    jobs = payload.get('jobs', []) if isinstance(payload, dict) else []
    return jobs if isinstance(jobs, list) else []


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_rub(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    text = value.strip().replace('\xa0', ' ')
    if not text or text.lower() == 'не указано':
        return None
    cleaned = text.replace('₽', '').replace(' ', '').replace(',', '.').strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def safe_json(value) -> str:
    return json.dumps(value, ensure_ascii=False) if value is not None else 'null'


def file_mtime_iso(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def configure_connection(conn: duckdb.DuckDBPyConnection) -> None:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    conn.execute("SET threads = 2")
    conn.execute("SET memory_limit = '1GB'")
    conn.execute(f"SET temp_directory = '{TMP_DIR.as_posix()}'")
    conn.execute("SET preserve_insertion_order = false")
    conn.execute("SET enable_object_cache = true")


def reset_schema(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("DROP SCHEMA IF EXISTS eva CASCADE")
    conn.execute("DROP SCHEMA IF EXISTS web CASCADE")
    conn.execute("CREATE SCHEMA eva")
    conn.execute(
        """
        CREATE TABLE eva.import_runs (
            imported_at TIMESTAMPTZ,
            status VARCHAR,
            note VARCHAR
        );

        CREATE TABLE eva.db_settings (
            setting_name VARCHAR,
            setting_value VARCHAR,
            applied_at TIMESTAMPTZ
        );

        CREATE TABLE eva.source_files (
            domain VARCHAR,
            dataset VARCHAR,
            file_tag VARCHAR,
            file_path VARCHAR,
            file_mtime TIMESTAMPTZ,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.hermes_sessions (
            id VARCHAR,
            source VARCHAR,
            user_id VARCHAR,
            model VARCHAR,
            title VARCHAR,
            started_at DOUBLE,
            ended_at DOUBLE,
            message_count BIGINT,
            tool_call_count BIGINT,
            input_tokens BIGINT,
            output_tokens BIGINT,
            estimated_cost_usd DOUBLE,
            actual_cost_usd DOUBLE,
            completion_status VARCHAR,
            last_user_message_id BIGINT,
            last_assistant_message_id BIGINT,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.hermes_messages (
            id BIGINT,
            session_id VARCHAR,
            role VARCHAR,
            content VARCHAR,
            tool_name VARCHAR,
            timestamp DOUBLE,
            token_count BIGINT,
            finish_reason VARCHAR,
            platform_message_id VARCHAR,
            observed BOOLEAN,
            request_status VARCHAR,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.workspace_documents (
            document_key VARCHAR,
            source_path VARCHAR,
            title VARCHAR,
            content VARCHAR,
            content_format VARCHAR,
            line_count BIGINT,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.workspace_decision_log_entries (
            entry_date DATE,
            topic VARCHAR,
            context_text VARCHAR,
            agreed_text VARCHAR,
            rejected_text VARCHAR,
            model_stack_tools_text VARCHAR,
            reflection_text VARCHAR,
            open_questions_text VARCHAR,
            raw_block VARCHAR,
            source_path VARCHAR,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.app_users_raw (
            id BIGINT,
            email VARCHAR,
            role VARCHAR,
            name VARCHAR,
            timezone VARCHAR,
            language VARCHAR,
            team VARCHAR,
            title VARCHAR,
            goals VARCHAR,
            style VARCHAR,
            constraints_text VARCHAR,
            pinned_json VARCHAR,
            assistant_profile_json VARCHAR,
            onboarding_completed BOOLEAN,
            created_at TIMESTAMPTZ,
            updated_at TIMESTAMPTZ,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.app_threads_raw (
            id BIGINT,
            user_id BIGINT,
            title VARCHAR,
            preview VARCHAR,
            archived BOOLEAN,
            created_at TIMESTAMPTZ,
            updated_at TIMESTAMPTZ,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.app_messages_raw (
            id BIGINT,
            thread_id BIGINT,
            role VARCHAR,
            content VARCHAR,
            created_at TIMESTAMPTZ,
            meta_json VARCHAR,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.app_feedback_raw (
            id BIGINT,
            user_id BIGINT,
            message_id BIGINT,
            useful BOOLEAN,
            reason_codes_json VARCHAR,
            comment VARCHAR,
            created_at TIMESTAMPTZ,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.app_jobs_raw (
            id VARCHAR,
            user_id BIGINT,
            name VARCHAR,
            description VARCHAR,
            job_type VARCHAR,
            visibility VARCHAR,
            status VARCHAR,
            schedule_kind VARCHAR,
            days_of_week_json VARCHAR,
            time_of_day VARCHAR,
            start_date DATE,
            timezone VARCHAR,
            prompt_template VARCHAR,
            parameters_json VARCHAR,
            next_run_at TIMESTAMPTZ,
            last_run_at TIMESTAMPTZ,
            last_run_status VARCHAR,
            last_run_summary VARCHAR,
            last_error VARCHAR,
            created_at TIMESTAMPTZ,
            updated_at TIMESTAMPTZ,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.app_job_acl_raw (
            id VARCHAR,
            job_id VARCHAR,
            user_id BIGINT,
            role VARCHAR,
            created_at TIMESTAMPTZ,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.app_job_recipients_raw (
            id VARCHAR,
            job_id VARCHAR,
            recipient_type VARCHAR,
            target_value VARCHAR,
            label VARCHAR,
            created_at TIMESTAMPTZ,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.app_job_subscriptions_raw (
            id VARCHAR,
            job_id VARCHAR,
            user_id BIGINT,
            created_at TIMESTAMPTZ,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.app_job_runs_raw (
            id VARCHAR,
            job_id VARCHAR,
            triggered_by_user_id BIGINT,
            trigger_type VARCHAR,
            status VARCHAR,
            started_at TIMESTAMPTZ,
            finished_at TIMESTAMPTZ,
            duration_ms BIGINT,
            summary VARCHAR,
            result_text VARCHAR,
            error_text VARCHAR,
            delivered_to_json VARCHAR,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.telegram_archive_messages_raw (
            file_tag VARCHAR,
            chat VARCHAR,
            message_id BIGINT,
            message_date VARCHAR,
            edit_date VARCHAR,
            original_url VARCHAR,
            message_text VARCHAR,
            has_text BOOLEAN,
            views BIGINT,
            forwards BIGINT,
            replies_count BIGINT,
            comments_enabled BOOLEAN,
            media_type VARCHAR,
            grouped_id BIGINT,
            post_author VARCHAR,
            reactions_json VARCHAR,
            external_links_json VARCHAR,
            raw_json VARCHAR,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.telegram_summary_messages (
            file_tag VARCHAR,
            summary_input_path VARCHAR,
            raw_log_path VARCHAR,
            config_name VARCHAR,
            profile_name VARCHAR,
            chat VARCHAR,
            message_id BIGINT,
            message_date VARCHAR,
            original_url VARCHAR,
            text VARCHAR,
            text_length BIGINT,
            views BIGINT,
            forwards BIGINT,
            media_type VARCHAR,
            reactions_json VARCHAR,
            external_links_json VARCHAR,
            raw_json VARCHAR,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.telegram_digest_rows (
            file_tag VARCHAR,
            summary_input_path VARCHAR,
            chat VARCHAR,
            message_id BIGINT,
            message_datetime_msk VARCHAR,
            original_url VARCHAR,
            brief_text VARCHAR,
            summary_text VARCHAR,
            post_type VARCHAR,
            score DOUBLE,
            selection_reasons_json VARCHAR,
            classification_confidence DOUBLE,
            classification_alternative VARCHAR,
            external_links_json VARCHAR,
            raw_json VARCHAR,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.telegram_collection_runs (
            file_tag VARCHAR,
            report_path VARCHAR,
            started_at VARCHAR,
            finished_at VARCHAR,
            status VARCHAR,
            config_name VARCHAR,
            profile_name VARCHAR,
            total_messages BIGINT,
            non_empty_messages BIGINT,
            empty_messages_skipped BIGINT,
            raw_log_path VARCHAR,
            summary_input_path VARCHAR,
            archive_path VARCHAR,
            since_updated BOOLEAN,
            raw_json VARCHAR,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.tender_items (
            dataset VARCHAR,
            file_tag VARCHAR,
            customer VARCHAR,
            description VARCHAR,
            quantity_text VARCHAR,
            tender_date VARCHAR,
            submit_date VARCHAR,
            cost_text VARCHAR,
            cost_rub DOUBLE,
            source_name VARCHAR,
            source_url VARCHAR,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.tender_source_status (
            dataset VARCHAR,
            file_tag VARCHAR,
            source_name VARCHAR,
            status VARCHAR,
            result_text VARCHAR,
            limitation VARCHAR,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.tender_run_summaries (
            file_tag VARCHAR,
            run_date VARCHAR,
            enabled_sources_json VARCHAR,
            total_rows BIGINT,
            by_source_json VARCHAR,
            status_by_source_json VARCHAR,
            csv_path VARCHAR,
            latest_csv_path VARCHAR,
            status_csv_path VARCHAR,
            latest_status_csv_path VARCHAR,
            config_path VARCHAR,
            raw_json VARCHAR,
            imported_at TIMESTAMPTZ
        );

        CREATE TABLE eva.tender_sources_config (
            source_key VARCHAR,
            source_name VARCHAR,
            enabled BOOLEAN,
            kind VARCHAR,
            params_json VARCHAR,
            config_path VARCHAR,
            imported_at TIMESTAMPTZ
        );
        """
    )


def create_views(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute(
        """
        CREATE VIEW eva.hermes_dialogue AS
        SELECT
            m.session_id,
            s.source AS session_source,
            s.user_id,
            s.title,
            m.id AS message_row_id,
            m.role,
            m.tool_name,
            m.content,
            to_timestamp(m.timestamp) AS message_ts,
            length(coalesce(m.content, '')) AS content_length,
            m.token_count
        FROM eva.hermes_messages m
        LEFT JOIN eva.hermes_sessions s ON s.id = m.session_id;

        CREATE VIEW eva.hermes_recent_user_threads AS
        WITH first_user_messages AS (
            SELECT
                m.session_id,
                min(m.id) AS first_user_message_id
            FROM eva.hermes_messages m
            WHERE m.role = 'user'
            GROUP BY 1
        )
        SELECT
            s.id AS session_id,
            s.source AS session_source,
            s.user_id,
            s.title,
            to_timestamp(s.started_at) AS started_ts,
            to_timestamp(s.ended_at) AS ended_ts,
            s.message_count,
            s.tool_call_count,
            s.input_tokens,
            s.output_tokens,
            m.content AS first_user_message,
            left(m.content, 220) AS first_user_message_short
        FROM eva.hermes_sessions s
        LEFT JOIN first_user_messages f ON f.session_id = s.id
        LEFT JOIN eva.hermes_messages m ON m.id = f.first_user_message_id
        ORDER BY started_ts DESC;

        CREATE VIEW eva.hermes_tool_failures AS
        SELECT
            session_id,
            message_row_id,
            tool_name,
            message_ts,
            left(content, 500) AS error_excerpt
        FROM eva.hermes_dialogue
        WHERE role = 'tool'
          AND (
              lower(coalesce(content, '')) LIKE '%error%'
              OR lower(coalesce(content, '')) LIKE '%traceback%'
              OR lower(coalesce(content, '')) LIKE '%exception%'
              OR lower(coalesce(content, '')) LIKE '%timed out%'
              OR lower(coalesce(content, '')) LIKE '%failed%'
          )
        ORDER BY message_ts DESC;

        CREATE VIEW eva.hermes_recent_user_questions AS
        SELECT
            session_id,
            session_source,
            user_id,
            title,
            message_row_id,
            message_ts,
            content,
            left(content, 220) AS content_short,
            content_length,
            token_count
        FROM eva.hermes_dialogue
        WHERE role = 'user'
          AND coalesce(trim(content), '') <> ''
        ORDER BY message_ts DESC;


        CREATE VIEW eva.hermes_open_user_requests AS
        SELECT
            d.session_id,
            d.session_source,
            d.user_id,
            d.title,
            d.message_row_id,
            d.message_ts,
            d.content,
            d.content_short
        FROM eva.hermes_recent_user_questions d
        LEFT JOIN eva.hermes_messages m ON m.id = d.message_row_id
        WHERE coalesce(m.request_status, '') = 'not_done'
        ORDER BY d.message_ts DESC;

        CREATE VIEW eva.hermes_session_status AS
        SELECT
            id AS session_id,
            source AS session_source,
            user_id,
            title,
            to_timestamp(started_at) AS started_ts,
            to_timestamp(ended_at) AS ended_ts,
            message_count,
            completion_status,
            last_user_message_id,
            last_assistant_message_id
        FROM eva.hermes_sessions
        ORDER BY started_ts DESC;

        CREATE VIEW eva.interaction_notes_current AS
        SELECT
            source_path,
            title,
            content,
            line_count,
            imported_at
        FROM eva.workspace_documents
        WHERE document_key = 'interaction-notes';

        CREATE VIEW eva.decision_log_latest AS
        SELECT
            entry_date,
            topic,
            agreed_text,
            rejected_text,
            open_questions_text,
            source_path,
            imported_at
        FROM eva.workspace_decision_log_entries
        ORDER BY entry_date DESC, topic;

        CREATE VIEW eva.actor_directory AS
        WITH app_users AS (
            SELECT
                'app_web' AS source_system,
                'user' AS actor_type,
                concat('app_user:', id::VARCHAR) AS actor_key,
                id::VARCHAR AS source_actor_id,
                name AS display_name,
                email,
                role,
                timezone,
                language,
                team,
                title,
                goals,
                style,
                constraints_text,
                pinned_json,
                assistant_profile_json,
                onboarding_completed,
                created_at,
                updated_at,
                imported_at,
                NULL::VARCHAR AS source_thread_hint,
                NULL::VARCHAR AS source_profile_json
            FROM eva.app_users_raw
        ),
        hermes_users AS (
            SELECT
                'hermes' AS source_system,
                'runtime_user' AS actor_type,
                concat('hermes_user:', coalesce(user_id, 'unknown')) AS actor_key,
                coalesce(user_id, 'unknown') AS source_actor_id,
                coalesce(user_id, 'unknown') AS display_name,
                NULL::VARCHAR AS email,
                NULL::VARCHAR AS role,
                NULL::VARCHAR AS timezone,
                NULL::VARCHAR AS language,
                NULL::VARCHAR AS team,
                NULL::VARCHAR AS title,
                NULL::VARCHAR AS goals,
                NULL::VARCHAR AS style,
                NULL::VARCHAR AS constraints_text,
                NULL::VARCHAR AS pinned_json,
                NULL::VARCHAR AS assistant_profile_json,
                NULL::BOOLEAN AS onboarding_completed,
                min(to_timestamp(started_at)) AS created_at,
                max(coalesce(to_timestamp(ended_at), to_timestamp(started_at))) AS updated_at,
                max(imported_at) AS imported_at,
                NULL::VARCHAR AS source_thread_hint,
                NULL::VARCHAR AS source_profile_json
            FROM eva.hermes_sessions
            GROUP BY 1, 2, 3, 4, 5
        ),
        telegram_channels AS (
            SELECT
                'telegram' AS source_system,
                'channel' AS actor_type,
                concat('telegram_channel:', chat) AS actor_key,
                chat AS source_actor_id,
                chat AS display_name,
                NULL::VARCHAR AS email,
                'channel' AS role,
                'Europe/Moscow' AS timezone,
                'ru' AS language,
                NULL::VARCHAR AS team,
                NULL::VARCHAR AS title,
                NULL::VARCHAR AS goals,
                NULL::VARCHAR AS style,
                NULL::VARCHAR AS constraints_text,
                NULL::VARCHAR AS pinned_json,
                NULL::VARCHAR AS assistant_profile_json,
                NULL::BOOLEAN AS onboarding_completed,
                min(try_cast(message_date AS TIMESTAMPTZ)) AS created_at,
                max(try_cast(coalesce(edit_date, message_date) AS TIMESTAMPTZ)) AS updated_at,
                max(imported_at) AS imported_at,
                NULL::VARCHAR AS source_thread_hint,
                NULL::VARCHAR AS source_profile_json
            FROM eva.telegram_archive_messages_raw
            GROUP BY 1, 2, 3, 4, 5, 8, 9
        )
        SELECT * FROM app_users
        UNION ALL
        SELECT * FROM hermes_users
        UNION ALL
        SELECT * FROM telegram_channels;

        CREATE VIEW eva.thread_catalog AS
        SELECT
            'app_web' AS source_system,
            concat('app_thread:', t.id::VARCHAR) AS thread_key,
            t.id::VARCHAR AS source_thread_id,
            concat('app_user:', t.user_id::VARCHAR) AS actor_key,
            t.user_id::VARCHAR AS source_actor_id,
            t.title,
            t.preview,
            t.archived,
            t.created_at,
            t.updated_at,
            t.imported_at,
            NULL::VARCHAR AS parent_thread_key,
            NULL::VARCHAR AS source_meta_json
        FROM eva.app_threads_raw t

        UNION ALL

        SELECT
            'hermes' AS source_system,
            concat('hermes_session:', s.id) AS thread_key,
            s.id AS source_thread_id,
            concat('hermes_user:', coalesce(s.user_id, 'unknown')) AS actor_key,
            coalesce(s.user_id, 'unknown') AS source_actor_id,
            s.title,
            NULL::VARCHAR AS preview,
            FALSE AS archived,
            to_timestamp(s.started_at) AS created_at,
            coalesce(to_timestamp(s.ended_at), to_timestamp(s.started_at)) AS updated_at,
            s.imported_at,
            NULL::VARCHAR AS parent_thread_key,
            NULL::VARCHAR AS source_meta_json
        FROM eva.hermes_sessions s;

        CREATE VIEW eva.message_facts AS
        SELECT
            'app_web' AS source_system,
            concat('app_message:', m.id::VARCHAR) AS message_key,
            m.id::VARCHAR AS source_message_id,
            concat('app_thread:', m.thread_id::VARCHAR) AS thread_key,
            concat('app_user:', t.user_id::VARCHAR) AS actor_key,
            t.user_id::VARCHAR AS source_actor_id,
            m.role,
            m.content,
            length(coalesce(m.content, '')) AS content_length,
            m.created_at AS created_at,
            m.meta_json AS source_meta_json,
            FALSE AS is_tool_event,
            FALSE AS is_feedback_event,
            NULL::VARCHAR AS delivery_channel,
            t.title AS thread_title,
            t.archived AS thread_archived,
            NULL::VARCHAR AS external_message_ref,
            m.imported_at
        FROM eva.app_messages_raw m
        JOIN eva.app_threads_raw t ON t.id = m.thread_id

        UNION ALL

        SELECT
            'hermes' AS source_system,
            concat('hermes_message:', m.id::VARCHAR) AS message_key,
            m.id::VARCHAR AS source_message_id,
            concat('hermes_session:', m.session_id) AS thread_key,
            concat('hermes_user:', coalesce(s.user_id, 'unknown')) AS actor_key,
            coalesce(s.user_id, 'unknown') AS source_actor_id,
            m.role,
            m.content,
            length(coalesce(m.content, '')) AS content_length,
            to_timestamp(m.timestamp) AS created_at,
            json_object(
                'tool_name', m.tool_name,
                'platform_message_id', m.platform_message_id,
                'request_status', m.request_status,
                'finish_reason', m.finish_reason,
                'observed', m.observed,
                'token_count', m.token_count
            )::VARCHAR AS source_meta_json,
            m.tool_name IS NOT NULL AS is_tool_event,
            FALSE AS is_feedback_event,
            s.source AS delivery_channel,
            s.title AS thread_title,
            FALSE AS thread_archived,
            m.platform_message_id AS external_message_ref,
            m.imported_at
        FROM eva.hermes_messages m
        LEFT JOIN eva.hermes_sessions s ON s.id = m.session_id

        UNION ALL

        SELECT
            'telegram' AS source_system,
            concat('telegram_message:', chat, ':', message_id::VARCHAR) AS message_key,
            message_id::VARCHAR AS source_message_id,
            concat('telegram_channel:', chat) AS thread_key,
            concat('telegram_channel:', chat) AS actor_key,
            chat AS source_actor_id,
            'channel_post' AS role,
            message_text AS content,
            length(coalesce(message_text, '')) AS content_length,
            try_cast(message_date AS TIMESTAMPTZ) AS created_at,
            json_object(
                'views', views,
                'forwards', forwards,
                'replies_count', replies_count,
                'comments_enabled', comments_enabled,
                'media_type', media_type,
                'grouped_id', grouped_id,
                'post_author', post_author,
                'reactions_json', reactions_json,
                'external_links_json', external_links_json
            )::VARCHAR AS source_meta_json,
            FALSE AS is_tool_event,
            FALSE AS is_feedback_event,
            'telegram' AS delivery_channel,
            chat AS thread_title,
            FALSE AS thread_archived,
            original_url AS external_message_ref,
            imported_at
        FROM eva.telegram_archive_messages_raw;

        CREATE VIEW eva.feedback_facts AS
        SELECT
            'app_web' AS source_system,
            concat('app_feedback:', f.id::VARCHAR) AS feedback_key,
            f.id::VARCHAR AS source_feedback_id,
            concat('app_user:', f.user_id::VARCHAR) AS actor_key,
            concat('app_message:', f.message_id::VARCHAR) AS message_key,
            f.useful,
            f.reason_codes_json,
            f.comment,
            f.created_at,
            m.thread_id::VARCHAR AS source_thread_id,
            t.title AS thread_title,
            f.imported_at
        FROM eva.app_feedback_raw f
        LEFT JOIN eva.app_messages_raw m ON m.id = f.message_id
        LEFT JOIN eva.app_threads_raw t ON t.id = m.thread_id;

        CREATE VIEW eva.actor_activity_summary AS
        WITH message_stats AS (
            SELECT
                actor_key,
                count(*) AS message_count,
                count(DISTINCT thread_key) AS thread_count,
                sum(CASE WHEN role = 'user' THEN 1 ELSE 0 END) AS user_messages,
                sum(CASE WHEN role = 'assistant' THEN 1 ELSE 0 END) AS assistant_messages,
                sum(CASE WHEN is_tool_event THEN 1 ELSE 0 END) AS tool_events,
                min(created_at) AS first_message_at,
                max(created_at) AS last_message_at
            FROM eva.message_facts
            GROUP BY 1
        ),
        feedback_stats AS (
            SELECT
                actor_key,
                count(*) AS feedback_count,
                sum(CASE WHEN useful THEN 1 ELSE 0 END) AS useful_feedback_count,
                sum(CASE WHEN NOT useful THEN 1 ELSE 0 END) AS not_useful_feedback_count,
                max(created_at) AS last_feedback_at
            FROM eva.feedback_facts
            GROUP BY 1
        )
        SELECT
            a.source_system,
            a.actor_type,
            a.actor_key,
            a.source_actor_id,
            a.display_name,
            a.email,
            a.role,
            a.team,
            a.title,
            coalesce(ms.thread_count, 0) AS thread_count,
            coalesce(ms.message_count, 0) AS message_count,
            coalesce(ms.user_messages, 0) AS user_messages,
            coalesce(ms.assistant_messages, 0) AS assistant_messages,
            coalesce(ms.tool_events, 0) AS tool_events,
            coalesce(fs.feedback_count, 0) AS feedback_count,
            coalesce(fs.useful_feedback_count, 0) AS useful_feedback_count,
            coalesce(fs.not_useful_feedback_count, 0) AS not_useful_feedback_count,
            ms.first_message_at,
            ms.last_message_at,
            fs.last_feedback_at,
            greatest(
                coalesce(ms.last_message_at, TIMESTAMPTZ '1970-01-01 00:00:00+00'),
                coalesce(fs.last_feedback_at, TIMESTAMPTZ '1970-01-01 00:00:00+00'),
                coalesce(a.updated_at, TIMESTAMPTZ '1970-01-01 00:00:00+00')
            ) AS last_activity_at,
            a.imported_at
        FROM eva.actor_directory a
        LEFT JOIN message_stats ms ON ms.actor_key = a.actor_key
        LEFT JOIN feedback_stats fs ON fs.actor_key = a.actor_key;

        CREATE VIEW eva.thread_activity_summary AS
        WITH message_stats AS (
            SELECT
                thread_key,
                count(*) AS message_count,
                sum(CASE WHEN role = 'user' THEN 1 ELSE 0 END) AS user_messages,
                sum(CASE WHEN role = 'assistant' THEN 1 ELSE 0 END) AS assistant_messages,
                sum(CASE WHEN is_tool_event THEN 1 ELSE 0 END) AS tool_events,
                min(created_at) AS first_message_at,
                max(created_at) AS last_message_at
            FROM eva.message_facts
            GROUP BY 1
        ),
        last_messages AS (
            SELECT
                thread_key,
                content AS last_message_excerpt,
                row_number() OVER (PARTITION BY thread_key ORDER BY created_at DESC, message_key DESC) AS rn
            FROM eva.message_facts
        )
        SELECT
            t.source_system,
            t.thread_key,
            t.source_thread_id,
            t.actor_key,
            t.source_actor_id,
            t.title,
            t.preview,
            t.archived,
            coalesce(ms.message_count, 0) AS message_count,
            coalesce(ms.user_messages, 0) AS user_messages,
            coalesce(ms.assistant_messages, 0) AS assistant_messages,
            coalesce(ms.tool_events, 0) AS tool_events,
            t.created_at AS thread_created_at,
            t.updated_at AS thread_updated_at,
            ms.first_message_at,
            ms.last_message_at,
            lm.last_message_excerpt,
            t.parent_thread_key,
            t.source_meta_json,
            t.imported_at
        FROM eva.thread_catalog t
        LEFT JOIN message_stats ms ON ms.thread_key = t.thread_key
        LEFT JOIN last_messages lm ON lm.thread_key = t.thread_key AND lm.rn = 1;

        CREATE VIEW eva.source_system_summary AS
        WITH actor_counts AS (
            SELECT source_system, count(*) AS actor_count
            FROM eva.actor_directory
            GROUP BY 1
        ),
        thread_counts AS (
            SELECT source_system, count(*) AS thread_count
            FROM eva.thread_catalog
            GROUP BY 1
        ),
        message_counts AS (
            SELECT
                source_system,
                count(*) AS message_count,
                sum(CASE WHEN is_tool_event THEN 1 ELSE 0 END) AS tool_event_count,
                max(created_at) AS latest_message_at
            FROM eva.message_facts
            GROUP BY 1
        ),
        feedback_counts AS (
            SELECT source_system, count(*) AS feedback_count
            FROM eva.feedback_facts
            GROUP BY 1
        )
        SELECT
            coalesce(a.source_system, t.source_system, m.source_system, f.source_system) AS source_system,
            coalesce(a.actor_count, 0) AS actor_count,
            coalesce(t.thread_count, 0) AS thread_count,
            coalesce(m.message_count, 0) AS message_count,
            coalesce(m.tool_event_count, 0) AS tool_event_count,
            coalesce(f.feedback_count, 0) AS feedback_count,
            m.latest_message_at,
            current_timestamp AS generated_at
        FROM actor_counts a
        FULL OUTER JOIN thread_counts t ON t.source_system = a.source_system
        FULL OUTER JOIN message_counts m ON m.source_system = coalesce(a.source_system, t.source_system)
        FULL OUTER JOIN feedback_counts f ON f.source_system = coalesce(a.source_system, t.source_system, m.source_system);

        CREATE VIEW eva.app_job_catalog AS
        WITH run_stats AS (
            SELECT
                job_id,
                count(*) AS run_count,
                max(started_at) AS latest_run_at,
                max(CASE WHEN status = 'success' THEN started_at END) AS latest_success_at,
                max(CASE WHEN status = 'error' THEN started_at END) AS latest_error_at
            FROM eva.app_job_runs_raw
            GROUP BY 1
        ),
        acl_stats AS (
            SELECT
                job_id,
                count(*) AS acl_entries,
                string_agg(DISTINCT role, ', ' ORDER BY role) AS acl_roles
            FROM eva.app_job_acl_raw
            GROUP BY 1
        ),
        recipient_stats AS (
            SELECT
                job_id,
                count(*) AS recipient_count,
                string_agg(DISTINCT recipient_type, ', ' ORDER BY recipient_type) AS recipient_types
            FROM eva.app_job_recipients_raw
            GROUP BY 1
        ),
        subscription_stats AS (
            SELECT
                job_id,
                count(*) AS subscriber_count
            FROM eva.app_job_subscriptions_raw
            GROUP BY 1
        )
        SELECT
            j.id AS job_id,
            j.name,
            j.description,
            j.job_type,
            j.visibility,
            j.status,
            j.schedule_kind,
            j.days_of_week_json,
            j.time_of_day,
            j.start_date,
            j.timezone,
            j.prompt_template,
            j.parameters_json,
            j.next_run_at,
            j.last_run_at,
            j.last_run_status,
            j.last_run_summary,
            j.last_error,
            j.created_at,
            j.updated_at,
            j.imported_at,
            j.user_id AS owner_user_id,
            u.name AS owner_name,
            u.email AS owner_email,
            u.role AS owner_role,
            coalesce(a.acl_entries, 0) AS acl_entries,
            a.acl_roles,
            coalesce(r.recipient_count, 0) AS recipient_count,
            r.recipient_types,
            coalesce(s.subscriber_count, 0) AS subscriber_count,
            coalesce(rs.run_count, 0) AS run_count,
            rs.latest_run_at,
            rs.latest_success_at,
            rs.latest_error_at
        FROM eva.app_jobs_raw j
        LEFT JOIN eva.app_users_raw u ON u.id = j.user_id
        LEFT JOIN run_stats rs ON rs.job_id = j.id
        LEFT JOIN acl_stats a ON a.job_id = j.id
        LEFT JOIN recipient_stats r ON r.job_id = j.id
        LEFT JOIN subscription_stats s ON s.job_id = j.id;

        CREATE VIEW eva.app_job_access_matrix AS
        SELECT
            j.id AS job_id,
            j.name AS job_name,
            j.visibility,
            j.user_id AS subject_user_id,
            u.name AS subject_name,
            u.email AS subject_email,
            'owner' AS access_role,
            'owner' AS access_source
        FROM eva.app_jobs_raw j
        LEFT JOIN eva.app_users_raw u ON u.id = j.user_id

        UNION ALL

        SELECT
            a.job_id,
            j.name AS job_name,
            j.visibility,
            a.user_id AS subject_user_id,
            u.name AS subject_name,
            u.email AS subject_email,
            a.role AS access_role,
            'acl' AS access_source
        FROM eva.app_job_acl_raw a
        JOIN eva.app_jobs_raw j ON j.id = a.job_id
        LEFT JOIN eva.app_users_raw u ON u.id = a.user_id

        UNION ALL

        SELECT
            s.job_id,
            j.name AS job_name,
            j.visibility,
            s.user_id AS subject_user_id,
            u.name AS subject_name,
            u.email AS subject_email,
            'subscriber' AS access_role,
            'subscription' AS access_source
        FROM eva.app_job_subscriptions_raw s
        JOIN eva.app_jobs_raw j ON j.id = s.job_id
        LEFT JOIN eva.app_users_raw u ON u.id = s.user_id;

        CREATE VIEW eva.app_job_delivery_matrix AS
        SELECT
            r.job_id,
            j.name AS job_name,
            r.recipient_type,
            r.target_value,
            r.label,
            r.created_at,
            r.imported_at
        FROM eva.app_job_recipients_raw r
        JOIN eva.app_jobs_raw j ON j.id = r.job_id;

        CREATE VIEW eva.app_job_run_summary AS
        SELECT
            r.job_id,
            j.name AS job_name,
            count(*) AS run_count,
            sum(CASE WHEN r.status = 'success' THEN 1 ELSE 0 END) AS success_runs,
            sum(CASE WHEN r.status = 'error' THEN 1 ELSE 0 END) AS error_runs,
            max(r.started_at) AS latest_started_at,
            max(r.finished_at) AS latest_finished_at,
            round(avg(CASE WHEN r.duration_ms IS NOT NULL THEN r.duration_ms END), 1) AS avg_duration_ms
        FROM eva.app_job_runs_raw r
        JOIN eva.app_jobs_raw j ON j.id = r.job_id
        GROUP BY 1, 2;

        CREATE VIEW eva.app_jobs_open AS
        SELECT *
        FROM eva.app_job_catalog
        WHERE status = 'active'
        ORDER BY updated_at DESC, job_id DESC;

        CREATE VIEW eva.telegram_posts AS
        WITH latest_summary AS (
            SELECT * EXCLUDE(rn)
            FROM (
                SELECT
                    s.*,
                    row_number() OVER (
                        PARTITION BY s.chat, s.message_id
                        ORDER BY s.summary_input_path DESC, s.file_tag DESC
                    ) AS rn
                FROM eva.telegram_summary_messages s
            )
            WHERE rn = 1
        ),
        latest_digest AS (
            SELECT * EXCLUDE(rn)
            FROM (
                SELECT
                    d.*,
                    row_number() OVER (
                        PARTITION BY d.chat, d.message_id
                        ORDER BY d.summary_input_path DESC, d.file_tag DESC
                    ) AS rn
                FROM eva.telegram_digest_rows d
            )
            WHERE rn = 1
        )
        SELECT
            s.chat,
            s.message_id,
            s.message_date,
            try_cast(s.message_date AS TIMESTAMPTZ) AS message_ts,
            date_trunc('day', try_cast(s.message_date AS TIMESTAMPTZ)) AS message_day,
            s.original_url,
            s.text,
            s.text_length,
            s.views,
            s.forwards,
            s.media_type,
            d.post_type,
            d.score,
            d.classification_confidence,
            d.classification_alternative,
            d.brief_text,
            d.summary_text,
            d.selection_reasons_json,
            s.summary_input_path
        FROM latest_summary s
        LEFT JOIN latest_digest d
            ON d.chat = s.chat AND d.message_id = s.message_id;

        CREATE VIEW eva.telegram_post_type_stats AS
        SELECT
            post_type,
            count(*) AS posts_count,
            round(avg(score), 3) AS avg_score,
            round(avg(classification_confidence), 3) AS avg_confidence
        FROM eva.telegram_posts
        GROUP BY 1
        ORDER BY posts_count DESC, post_type;

        CREATE VIEW eva.telegram_channel_stats AS
        SELECT
            chat,
            count(*) AS posts_count,
            round(avg(coalesce(score, 0)), 3) AS avg_score,
            round(avg(coalesce(classification_confidence, 0)), 3) AS avg_confidence,
            sum(CASE WHEN post_type = 'кейс' THEN 1 ELSE 0 END) AS case_posts,
            sum(CASE WHEN post_type = 'требует уточнения' THEN 1 ELSE 0 END) AS needs_review_posts
        FROM eva.telegram_posts
        GROUP BY 1
        ORDER BY posts_count DESC, chat;

        CREATE VIEW eva.telegram_top_posts AS
        SELECT
            chat,
            message_ts,
            post_type,
            score,
            classification_confidence,
            brief_text,
            summary_text,
            original_url
        FROM eva.telegram_posts
        WHERE score IS NOT NULL
        ORDER BY score DESC, message_ts DESC;

        CREATE VIEW eva.telegram_cases AS
        SELECT
            chat,
            message_ts,
            score,
            classification_confidence,
            brief_text,
            summary_text,
            original_url
        FROM eva.telegram_posts
        WHERE post_type = 'кейс'
        ORDER BY message_ts DESC, score DESC;

        CREATE VIEW eva.telegram_high_signal_posts AS
        SELECT
            chat,
            message_ts,
            post_type,
            score,
            classification_confidence,
            brief_text,
            summary_text,
            original_url
        FROM eva.telegram_posts
        WHERE coalesce(score, 0) >= 9
          AND coalesce(classification_confidence, 0) >= 0.55
          AND coalesce(post_type, '') <> 'требует уточнения'
        ORDER BY message_ts DESC, score DESC;

        CREATE VIEW eva.telegram_daily_feed AS
        SELECT
            message_day,
            count(*) AS posts_count,
            sum(CASE WHEN post_type = 'кейс' THEN 1 ELSE 0 END) AS case_posts,
            sum(CASE WHEN post_type = 'аналитика' THEN 1 ELSE 0 END) AS analytics_posts,
            sum(CASE WHEN post_type = 'исследование' THEN 1 ELSE 0 END) AS research_posts,
            round(avg(coalesce(score, 0)), 3) AS avg_score
        FROM eva.telegram_posts
        GROUP BY 1
        ORDER BY message_day DESC;

        CREATE VIEW eva.telegram_channel_leaderboard AS
        SELECT
            chat,
            posts_count,
            avg_score,
            avg_confidence,
            case_posts,
            posts_count * avg_score AS weighted_signal,
            round(case_posts * 1.0 / nullif(posts_count, 0), 3) AS case_share
        FROM eva.telegram_channel_stats
        ORDER BY weighted_signal DESC, avg_score DESC, posts_count DESC;

        CREATE VIEW eva.telegram_client_digest_candidates AS
        WITH ranked AS (
            SELECT
                chat,
                message_ts,
                post_type,
                score,
                classification_confidence,
                brief_text,
                summary_text,
                original_url,
                CASE
                    WHEN post_type = 'кейс' THEN 'A'
                    WHEN post_type IN ('аналитика', 'исследование', 'обзор рынка') THEN 'B'
                    WHEN post_type IN ('продукт/решение', 'интервью/комментарий', 'партнерство') THEN 'C'
                    ELSE 'D'
                END AS priority_bucket,
                row_number() OVER (
                    PARTITION BY chat
                    ORDER BY coalesce(score, 0) DESC, coalesce(classification_confidence, 0) DESC, message_ts DESC
                ) AS channel_rank
            FROM eva.telegram_posts
            WHERE coalesce(post_type, '') NOT IN ('требует уточнения', 'корпоративная новость', 'мероприятие')
              AND coalesce(score, 0) >= 8.5
              AND coalesce(classification_confidence, 0) >= 0.5
        )
        SELECT
            priority_bucket,
            chat,
            message_ts,
            post_type,
            score,
            classification_confidence,
            channel_rank,
            brief_text,
            summary_text,
            original_url
        FROM ranked
        ORDER BY priority_bucket, score DESC, classification_confidence DESC, message_ts DESC;

        CREATE VIEW eva.tender_summary AS
        SELECT
            tender_date,
            source_name,
            count(*) AS tenders_count,
            round(sum(coalesce(cost_rub, 0)), 2) AS total_cost_rub
        FROM eva.tender_items
        GROUP BY 1, 2
        ORDER BY tender_date DESC, source_name;

        CREATE VIEW eva.tenders_recent AS
        SELECT
            coalesce(
                try_strptime(tender_date, '%d.%m.%Y %H:%M'),
                try_strptime(tender_date, '%d.%m.%Y')
            ) AS tender_dt,
            coalesce(
                try_strptime(submit_date, '%d.%m.%Y %H:%M'),
                try_strptime(submit_date, '%d.%m.%Y')
            ) AS submit_dt,
            source_name,
            customer,
            description,
            cost_rub,
            cost_text,
            source_url
        FROM eva.tender_items
        ORDER BY tender_dt DESC, submit_dt DESC, cost_rub DESC NULLS LAST;

        CREATE VIEW eva.tender_source_health AS
        SELECT
            source_name,
            status,
            count(*) AS status_count,
            max(imported_at) AS last_seen_at,
            string_agg(distinct coalesce(limitation, ''), ' | ') AS limitations
        FROM eva.tender_source_status
        GROUP BY 1, 2
        ORDER BY source_name, status;

        CREATE VIEW eva.tender_source_leaderboard AS
        SELECT
            source_name,
            count(*) AS tenders_count,
            round(sum(coalesce(cost_rub, 0)), 2) AS total_cost_rub,
            round(avg(cost_rub), 2) AS avg_cost_rub,
            max(coalesce(
                try_strptime(tender_date, '%d.%m.%Y %H:%M'),
                try_strptime(tender_date, '%d.%m.%Y')
            )) AS latest_tender_dt
        FROM eva.tender_items
        GROUP BY 1
        ORDER BY tenders_count DESC, total_cost_rub DESC;

        CREATE VIEW eva.tender_priority_queue AS
        WITH normalized AS (
            SELECT
                coalesce(
                    try_strptime(tender_date, '%d.%m.%Y %H:%M'),
                    try_strptime(tender_date, '%d.%m.%Y')
                ) AS tender_dt,
                coalesce(
                    try_strptime(submit_date, '%d.%m.%Y %H:%M'),
                    try_strptime(submit_date, '%d.%m.%Y')
                ) AS submit_dt,
                source_name,
                customer,
                description,
                cost_rub,
                cost_text,
                source_url,
                row_number() OVER (
                    PARTITION BY
                        source_name,
                        trim(lower(regexp_replace(coalesce(customer, ''), '\\s+', ' '))),
                        trim(lower(regexp_replace(coalesce(description, ''), '\\s+', ' '))),
                        coalesce(cost_rub, -1),
                        coalesce(submit_date, '')
                    ORDER BY imported_at DESC
                ) AS rn
            FROM eva.tender_items
        )
        SELECT DISTINCT
            tender_dt,
            submit_dt,
            source_name,
            customer,
            description,
            cost_rub,
            cost_text,
            source_url,
            CASE
                WHEN coalesce(cost_rub, 0) >= 5000000 THEN 'A'
                WHEN coalesce(cost_rub, 0) >= 1000000 THEN 'B'
                ELSE 'C'
            END AS budget_bucket,
            CASE
                WHEN submit_dt IS NOT NULL THEN greatest(0, datediff('day', current_timestamp, submit_dt))
                ELSE NULL
            END AS days_to_deadline,
            coalesce(
                least(coalesce(cost_rub, 0) / 1000000.0, 20),
                0
            )
            + CASE
                WHEN submit_dt IS NULL THEN 0
                WHEN datediff('day', current_timestamp, submit_dt) <= 3 THEN 8
                WHEN datediff('day', current_timestamp, submit_dt) <= 7 THEN 5
                WHEN datediff('day', current_timestamp, submit_dt) <= 14 THEN 2
                ELSE 0
              END AS priority_score
        FROM normalized
        WHERE rn = 1
        ORDER BY priority_score DESC, submit_dt ASC NULLS LAST, cost_rub DESC NULLS LAST;
        """
    )


def record_settings(conn: duckdb.DuckDBPyConnection, imported_at: str) -> None:
    rows = [
        ('threads', '2', imported_at),
        ('memory_limit', '1GB', imported_at),
        ('temp_directory', str(TMP_DIR), imported_at),
        ('preserve_insertion_order', 'false', imported_at),
        ('enable_object_cache', 'true', imported_at),
    ]
    conn.executemany("INSERT INTO eva.db_settings VALUES (?, ?, ?)", rows)


def replace_hermes_data(conn: duckdb.DuckDBPyConnection, imported_at: str) -> None:
    src = sqlite3.connect(HERMES_STATE_DB)
    src.row_factory = sqlite3.Row
    cur = src.cursor()

    session_rows = [dict(row) for row in cur.execute(
        """
        SELECT id, source, user_id, model, title, started_at, ended_at,
               message_count, tool_call_count, input_tokens, output_tokens,
               estimated_cost_usd, actual_cost_usd
        FROM sessions
        """
    )]
    message_rows = [dict(row) for row in cur.execute(
        """
        SELECT id, session_id, role, content, tool_name, timestamp,
               token_count, finish_reason, platform_message_id, observed
        FROM messages
        ORDER BY session_id, id
        """
    )]
    src.close()

    session_stats: dict[str, dict[str, object]] = {}
    for row in message_rows:
        stats = session_stats.setdefault(row['session_id'], {
            'last_user_message_id': None,
            'last_assistant_message_id': None,
            'completion_status': 'not_done',
        })
        role = row.get('role')
        if role == 'user':
            stats['last_user_message_id'] = row['id']
            stats['completion_status'] = 'not_done'
        elif role == 'assistant':
            stats['last_assistant_message_id'] = row['id']
            stats['completion_status'] = 'done'

    sessions = []
    for row in session_rows:
        stats = session_stats.get(row['id'], {})
        sessions.append((
            row['id'], row['source'], row['user_id'], row['model'], row['title'],
            row['started_at'], row['ended_at'], row['message_count'], row['tool_call_count'],
            row['input_tokens'], row['output_tokens'], row['estimated_cost_usd'], row['actual_cost_usd'],
            stats.get('completion_status', 'not_done'),
            stats.get('last_user_message_id'),
            stats.get('last_assistant_message_id'),
            imported_at,
        ))

    replied_after_user: dict[str, bool] = {}
    for row in reversed(message_rows):
        session_id = row['session_id']
        role = row.get('role')
        if role == 'assistant':
            replied_after_user[session_id] = True
            row['request_status'] = 'done'
        elif role == 'user':
            row['request_status'] = 'done' if replied_after_user.get(session_id) else 'not_done'
        else:
            row['request_status'] = None

    messages = [
        (
            row['id'], row['session_id'], row['role'], row['content'], row['tool_name'],
            row['timestamp'], row['token_count'], row['finish_reason'], row['platform_message_id'],
            row['observed'], row.get('request_status'), imported_at,
        )
        for row in message_rows
    ]

    if sessions:
        conn.executemany(
            "INSERT INTO eva.hermes_sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            sessions,
        )
    if messages:
        conn.executemany(
            "INSERT INTO eva.hermes_messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            messages,
        )


def replace_app_data(conn: duckdb.DuckDBPyConnection, imported_at: str) -> list[tuple]:
    if not APP_BACKEND_DB.exists():
        return []

    conn.execute(f"ATTACH '{APP_BACKEND_DB.as_posix()}' AS app_src (READ_ONLY)")
    try:
        conn.execute(
            """
            INSERT INTO eva.app_users_raw
            SELECT
                id,
                email,
                role,
                name,
                timezone,
                language,
                team,
                title,
                goals,
                style,
                constraints_text,
                pinned_json,
                assistant_profile_json,
                onboarding_completed,
                created_at,
                updated_at,
                ?
            FROM app_src.app.users
            """,
            [imported_at],
        )
        conn.execute(
            """
            INSERT INTO eva.app_threads_raw
            SELECT id, user_id, title, preview, archived, created_at, updated_at, ?
            FROM app_src.app.threads
            """,
            [imported_at],
        )
        conn.execute(
            """
            INSERT INTO eva.app_messages_raw
            SELECT id, thread_id, role, content, created_at, meta_json, ?
            FROM app_src.app.messages
            """,
            [imported_at],
        )
        conn.execute(
            """
            INSERT INTO eva.app_feedback_raw
            SELECT id, user_id, message_id, useful, reason_codes_json, comment, created_at, ?
            FROM app_src.app.feedback
            """,
            [imported_at],
        )
        hermes_jobs = load_hermes_cron_jobs()
        if hermes_jobs:
            conn.executemany(
                """
                INSERT INTO eva.app_jobs_raw
                (id, user_id, name, description, job_type, visibility, status, schedule_kind,
                 days_of_week_json, time_of_day, start_date, timezone, prompt_template,
                 parameters_json, next_run_at, last_run_at, last_run_status, last_run_summary,
                 last_error, created_at, updated_at, imported_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        str(job.get('id') or ''),
                        None,
                        str(job.get('name') or job.get('id') or 'Hermes cron'),
                        (f"Hermes cron script: {job.get('script')}" if job.get('script') else (' '.join(str(job.get('prompt') or '').split())[:220] or 'Hermes cron job')),
                        'custom',
                        'private',
                        'paused' if (str(job.get('state') or '').lower() == 'paused' or not bool(job.get('enabled', True))) else 'active',
                        str((job.get('schedule') or {}).get('kind') or 'cron'),
                        '[]',
                        '',
                        None,
                        '',
                        str(job.get('prompt') or ''),
                        safe_json({
                            'deliver': job.get('deliver'),
                            'script': job.get('script'),
                            'skills': job.get('skills') or [],
                            'profile': job.get('profile'),
                            'workdir': job.get('workdir'),
                            'toolsets': job.get('enabled_toolsets') or [],
                            'no_agent': bool(job.get('no_agent')),
                        }),
                        job.get('next_run_at'),
                        job.get('last_run_at'),
                        job.get('last_status'),
                        job.get('last_error') or '',
                        job.get('last_error') or '',
                        job.get('created_at'),
                        job.get('last_run_at') or job.get('created_at'),
                        imported_at,
                    )
                    for job in hermes_jobs
                ],
            )
            conn.executemany(
                """
                INSERT INTO eva.app_job_acl_raw
                (id, job_id, user_id, role, created_at, imported_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        f"{job.get('id')}:admin", str(job.get('id') or ''), None, 'admin', job.get('created_at'), imported_at
                    )
                    for job in hermes_jobs
                ],
            )
            conn.executemany(
                """
                INSERT INTO eva.app_job_recipients_raw
                (id, job_id, recipient_type, target_value, label, created_at, imported_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        f"{job.get('id')}:admin", str(job.get('id') or ''), 'admin', 'admin', 'Администратор', job.get('created_at'), imported_at
                    )
                    for job in hermes_jobs
                ],
            )
            conn.executemany(
                """
                INSERT INTO eva.app_job_runs_raw
                (id, job_id, triggered_by_user_id, trigger_type, status, started_at, finished_at,
                 duration_ms, summary, result_text, error_text, delivered_to_json, imported_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        f"{job.get('id')}:last",
                        str(job.get('id') or ''),
                        None,
                        'hermes-cron',
                        job.get('last_status') or 'unknown',
                        job.get('last_run_at'),
                        job.get('last_run_at'),
                        None,
                        job.get('last_error') or 'Последний запуск зафиксирован Hermes',
                        '',
                        job.get('last_error') or '',
                        safe_json({'deliver': job.get('deliver')}),
                        imported_at,
                    )
                    for job in hermes_jobs if job.get('last_run_at')
                ],
            )
    finally:
        conn.execute("DETACH app_src")

    return [
        ('app', 'backend_duckdb', APP_BACKEND_DB.name, str(APP_BACKEND_DB), file_mtime_iso(APP_BACKEND_DB), imported_at),
    ]


def parse_decision_log_entries(content: str) -> list[dict[str, str]]:
    blocks = re.split(r'(?=^\[\d{4}-\d{2}-\d{2}\]\s+—\s+)', content, flags=re.M)
    entries = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        header = lines[0].strip()
        match = re.match(r'^\[(\d{4}-\d{2}-\d{2})\]\s+—\s+(.*)$', header)
        if not match:
            continue
        entry = {
            'entry_date': match.group(1),
            'topic': match.group(2).strip(),
            'context_text': '',
            'agreed_text': '',
            'rejected_text': '',
            'model_stack_tools_text': '',
            'reflection_text': '',
            'open_questions_text': '',
            'raw_block': block,
        }
        current_key = None
        mapping = {
            'Context:': 'context_text',
            'Agreed:': 'agreed_text',
            'Rejected:': 'rejected_text',
            'Model / stack / tools:': 'model_stack_tools_text',
            'Reflection (agent’s view):': 'reflection_text',
            'Open questions:': 'open_questions_text',
        }
        buffers = {v: [] for v in mapping.values()}
        for line in lines[1:]:
            stripped = line.strip()
            if stripped in mapping:
                current_key = mapping[stripped]
                continue
            if current_key:
                buffers[current_key].append(line.rstrip())
        for key, buf in buffers.items():
            entry[key] = '\n'.join(buf).strip()
        entries.append(entry)
    return entries


def replace_workspace_documents(conn: duckdb.DuckDBPyConnection, imported_at: str) -> list[tuple]:
    tracked_files = []
    documents = []
    for document_key, path, title in [
        ('interaction-notes', INTERACTION_NOTES_PATH, 'Interaction notes'),
        ('decision-log', DECISION_LOG_PATH, 'Decision log'),
    ]:
        if not path.exists():
            continue
        content = path.read_text(encoding='utf-8')
        line_count = len(content.splitlines())
        documents.append((document_key, str(path), title, content, 'markdown', line_count, imported_at))
        tracked_files.append(('workspace', document_key, path.name, str(path), file_mtime_iso(path), imported_at))
    if documents:
        conn.executemany(
            "INSERT INTO eva.workspace_documents VALUES (?, ?, ?, ?, ?, ?, ?)",
            documents,
        )

    if DECISION_LOG_PATH.exists():
        entries = parse_decision_log_entries(DECISION_LOG_PATH.read_text(encoding='utf-8'))
        if entries:
            conn.executemany(
                "INSERT INTO eva.workspace_decision_log_entries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        e['entry_date'], e['topic'], e['context_text'], e['agreed_text'],
                        e['rejected_text'], e['model_stack_tools_text'], e['reflection_text'],
                        e['open_questions_text'], e['raw_block'], str(DECISION_LOG_PATH), imported_at,
                    )
                    for e in entries
                ],
            )
    return tracked_files

def telegram_archive_file() -> Optional[SourceFile]:
    archive = TG_DIR / 'archive' / 'telegram_messages.jsonl'
    if archive.exists():
        return SourceFile('telegram', 'archive_jsonl', archive, archive.name)
    return None


def telegram_summary_input_files() -> list[SourceFile]:
    return [
        SourceFile('telegram', 'summary_input_json', path, path.name)
        for path in sorted((TG_DIR / 'raw_logs').glob('raw_*_summary_input.json'))
    ]


def telegram_collection_report_files() -> list[SourceFile]:
    files = []
    latest = TG_DIR / 'raw_logs' / 'latest_collection_report.json'
    if latest.exists():
        files.append(SourceFile('telegram', 'collection_report_json', latest, latest.name))
    files.extend(
        SourceFile('telegram', 'collection_report_json', path, path.name)
        for path in sorted((TG_DIR / 'raw_logs' / 'reports').glob('collect_*.json'))
    )
    return files


def load_telegram_archive(conn: duckdb.DuckDBPyConnection, imported_at: str) -> list[tuple]:
    source = telegram_archive_file()
    file_rows = []
    if not source:
        return file_rows
    rows = []
    for line in source.path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        rows.append((
            source.file_tag,
            item.get('chat'),
            item.get('id'),
            item.get('date'),
            item.get('edit_date'),
            item.get('original_url'),
            item.get('message'),
            bool(item.get('has_text')),
            item.get('views'),
            item.get('forwards'),
            item.get('replies_count'),
            item.get('comments_enabled'),
            item.get('media_type'),
            item.get('grouped_id'),
            item.get('post_author'),
            safe_json(item.get('reactions')),
            safe_json(item.get('external_links')),
            safe_json(item),
            imported_at,
        ))
    if rows:
        conn.executemany(
            "INSERT INTO eva.telegram_archive_messages_raw VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        file_rows.append((source.domain, source.dataset, source.file_tag, str(source.path), file_mtime_iso(source.path), imported_at))
    return file_rows


def normalize_external_links(links):
    if links is None:
        return []
    normalized = []
    for item in links:
        if isinstance(item, str):
            normalized.append({'label': None, 'url': item})
        else:
            normalized.append(item)
    return normalized


def load_telegram_summary_and_digest(conn: duckdb.DuckDBPyConnection, imported_at: str) -> list[tuple]:
    file_rows = []
    summary_rows = []
    digest_rows = []
    for source in telegram_summary_input_files():
        payload = json.loads(source.path.read_text(encoding='utf-8'))
        config_name = payload.get('config_name', 'daily')
        profile_name = payload.get('profile_name', 'profile_1')
        raw_log_path = payload.get('raw_log')
        messages = payload.get('messages') or []
        for item in messages:
            meta = item.get('metadata') or {}
            text = item.get('text') or ''
            summary_rows.append((
                source.file_tag,
                str(source.path),
                raw_log_path,
                config_name,
                profile_name,
                item.get('chat'),
                item.get('id'),
                item.get('date'),
                item.get('original_url'),
                text,
                len(text),
                meta.get('views'),
                meta.get('forwards'),
                meta.get('media_type'),
                safe_json(meta.get('reactions')),
                safe_json(item.get('external_links')),
                safe_json(item),
                imported_at,
            ))
        derived = derive_rows(payload, config_name=config_name, profile_name=profile_name)
        for row in derived:
            digest_rows.append((
                source.file_tag,
                str(source.path),
                row.get('канал'),
                row.get('_id'),
                row.get('дата-время'),
                row.get('ссылка'),
                row.get('краткое содержание'),
                row.get('саммари'),
                row.get('тип поста'),
                row.get('_score'),
                safe_json(row.get('_selection_reasons')),
                row.get('_classification_confidence'),
                row.get('_classification_alternative'),
                safe_json(normalize_external_links(row.get('_external_links'))),
                safe_json(row),
                imported_at,
            ))
        file_rows.append((source.domain, source.dataset, source.file_tag, str(source.path), file_mtime_iso(source.path), imported_at))

    if summary_rows:
        conn.executemany(
            "INSERT INTO eva.telegram_summary_messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            summary_rows,
        )
    if digest_rows:
        conn.executemany(
            "INSERT INTO eva.telegram_digest_rows VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            digest_rows,
        )
    return file_rows


def load_telegram_collection_reports(conn: duckdb.DuckDBPyConnection, imported_at: str) -> list[tuple]:
    file_rows = []
    report_rows = []
    seen = set()
    for source in telegram_collection_report_files():
        path_key = str(source.path.resolve())
        if path_key in seen:
            continue
        seen.add(path_key)
        payload = json.loads(source.path.read_text(encoding='utf-8'))
        collector_payload = payload.get('collector_payload') or {}
        report_rows.append((
            source.file_tag,
            str(source.path),
            payload.get('started_at'),
            payload.get('finished_at'),
            payload.get('status'),
            collector_payload.get('config_name'),
            collector_payload.get('profile_name'),
            collector_payload.get('total_messages'),
            collector_payload.get('non_empty_messages'),
            collector_payload.get('empty_messages_skipped'),
            collector_payload.get('raw_log'),
            collector_payload.get('summary_input'),
            collector_payload.get('archive'),
            collector_payload.get('since_updated'),
            safe_json(payload),
            imported_at,
        ))
        file_rows.append((source.domain, source.dataset, source.file_tag, str(source.path), file_mtime_iso(source.path), imported_at))

    if report_rows:
        conn.executemany(
            "INSERT INTO eva.telegram_collection_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            report_rows,
        )
    return file_rows


def tender_item_files() -> list[SourceFile]:
    files: list[SourceFile] = []
    for path in sorted(TENDERS_DIR.glob('it_tenders*.csv')):
        files.append(SourceFile('tenders', 'it_tenders_csv', path, path.name))
    for path in sorted(WORKSPACE_DIR.glob('it_tenders*.csv')):
        files.append(SourceFile('tenders', 'it_tenders_csv', path, path.name))
    return files


def tender_status_files() -> list[SourceFile]:
    files: list[SourceFile] = []
    for path in sorted(TENDERS_DIR.glob('tender_sources_status*.csv')):
        files.append(SourceFile('tenders', 'tender_source_status_csv', path, path.name))
    for path in sorted(WORKSPACE_DIR.glob('tender_sources_status*.csv')):
        files.append(SourceFile('tenders', 'tender_source_status_csv', path, path.name))
    return files


def read_csv_semicolon(path: Path):
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        yield from csv.DictReader(f, delimiter=';')


def replace_tender_data(conn: duckdb.DuckDBPyConnection, imported_at: str) -> list[tuple]:
    tender_rows = []
    status_rows = []
    summary_rows = []
    config_rows = []
    file_rows = []

    for source in tender_item_files():
        for row in read_csv_semicolon(source.path):
            tender_rows.append((
                source.dataset,
                source.file_tag,
                row.get('кто'),
                row.get('что'),
                row.get('сколько'),
                row.get('дата тендера'),
                row.get('дата подачи'),
                row.get('стоимость'),
                parse_rub(row.get('стоимость')),
                row.get('источник'),
                row.get('ссылка на источник'),
                imported_at,
            ))
        file_rows.append((source.domain, source.dataset, source.file_tag, str(source.path), file_mtime_iso(source.path), imported_at))

    for source in tender_status_files():
        for row in read_csv_semicolon(source.path):
            status_rows.append((
                source.dataset,
                source.file_tag,
                row.get('источник'),
                row.get('статус'),
                row.get('что получилось'),
                row.get('ограничение'),
                imported_at,
            ))
        file_rows.append((source.domain, source.dataset, source.file_tag, str(source.path), file_mtime_iso(source.path), imported_at))

    summary_path = TENDERS_DIR / 'last_run_summary.json'
    if summary_path.exists():
        payload = json.loads(summary_path.read_text(encoding='utf-8'))
        summary_rows.append((
            summary_path.name,
            payload.get('date'),
            safe_json(payload.get('enabled_sources')),
            payload.get('total_rows'),
            safe_json(payload.get('by_source')),
            safe_json(payload.get('status_by_source')),
            payload.get('csv_path'),
            payload.get('latest_csv_path'),
            payload.get('status_csv_path'),
            payload.get('latest_status_csv_path'),
            payload.get('config_path'),
            safe_json(payload),
            imported_at,
        ))
        file_rows.append(('tenders', 'last_run_summary_json', summary_path.name, str(summary_path), file_mtime_iso(summary_path), imported_at))

    config_path = TENDERS_DIR / 'it_tender_sources.json'
    if config_path.exists():
        payload = json.loads(config_path.read_text(encoding='utf-8'))
        for source in payload.get('sources') or []:
            config_rows.append((
                source.get('key'),
                source.get('name'),
                source.get('enabled'),
                source.get('kind'),
                safe_json(source.get('params')),
                str(config_path),
                imported_at,
            ))
        file_rows.append(('tenders', 'sources_config_json', config_path.name, str(config_path), file_mtime_iso(config_path), imported_at))

    if tender_rows:
        conn.executemany(
            "INSERT INTO eva.tender_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            tender_rows,
        )
    if status_rows:
        conn.executemany(
            "INSERT INTO eva.tender_source_status VALUES (?, ?, ?, ?, ?, ?, ?)",
            status_rows,
        )
    if summary_rows:
        conn.executemany(
            "INSERT INTO eva.tender_run_summaries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            summary_rows,
        )
    if config_rows:
        conn.executemany(
            "INSERT INTO eva.tender_sources_config VALUES (?, ?, ?, ?, ?, ?, ?)",
            config_rows,
        )
    return file_rows


def register_source_files(conn: duckdb.DuckDBPyConnection, rows: list[tuple]) -> None:
    if rows:
        conn.executemany("INSERT INTO eva.source_files VALUES (?, ?, ?, ?, ?, ?)", rows)


def optimize_database(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("ANALYZE")
    conn.execute("CHECKPOINT")


def summarize(conn: duckdb.DuckDBPyConnection):
    return conn.execute(
        """
        SELECT 'hermes_sessions' AS dataset, count(*) AS rows FROM eva.hermes_sessions
        UNION ALL SELECT 'hermes_messages', count(*) FROM eva.hermes_messages
        UNION ALL SELECT 'app_users_raw', count(*) FROM eva.app_users_raw
        UNION ALL SELECT 'app_threads_raw', count(*) FROM eva.app_threads_raw
        UNION ALL SELECT 'app_messages_raw', count(*) FROM eva.app_messages_raw
        UNION ALL SELECT 'app_feedback_raw', count(*) FROM eva.app_feedback_raw
        UNION ALL SELECT 'app_jobs_raw', count(*) FROM eva.app_jobs_raw
        UNION ALL SELECT 'app_job_acl_raw', count(*) FROM eva.app_job_acl_raw
        UNION ALL SELECT 'app_job_recipients_raw', count(*) FROM eva.app_job_recipients_raw
        UNION ALL SELECT 'app_job_subscriptions_raw', count(*) FROM eva.app_job_subscriptions_raw
        UNION ALL SELECT 'app_job_runs_raw', count(*) FROM eva.app_job_runs_raw
        UNION ALL SELECT 'telegram_archive_messages_raw', count(*) FROM eva.telegram_archive_messages_raw
        UNION ALL SELECT 'telegram_summary_messages', count(*) FROM eva.telegram_summary_messages
        UNION ALL SELECT 'telegram_digest_rows', count(*) FROM eva.telegram_digest_rows
        UNION ALL SELECT 'telegram_collection_runs', count(*) FROM eva.telegram_collection_runs
        UNION ALL SELECT 'tender_items', count(*) FROM eva.tender_items
        UNION ALL SELECT 'tender_source_status', count(*) FROM eva.tender_source_status
        UNION ALL SELECT 'tender_run_summaries', count(*) FROM eva.tender_run_summaries
        UNION ALL SELECT 'tender_sources_config', count(*) FROM eva.tender_sources_config
        UNION ALL SELECT 'workspace_documents', count(*) FROM eva.workspace_documents
        UNION ALL SELECT 'workspace_decision_log_entries', count(*) FROM eva.workspace_decision_log_entries
        UNION ALL SELECT 'source_files', count(*) FROM eva.source_files
        ORDER BY 1
        """
    ).fetchall()


def main() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    imported_at = now_iso()
    conn = duckdb.connect(str(DB_PATH))
    configure_connection(conn)
    reset_schema(conn)
    record_settings(conn, imported_at)
    create_views(conn)
    replace_hermes_data(conn, imported_at)

    source_files = []
    source_files.extend(replace_app_data(conn, imported_at))
    source_files.extend(load_telegram_archive(conn, imported_at))
    source_files.extend(load_telegram_summary_and_digest(conn, imported_at))
    source_files.extend(load_telegram_collection_reports(conn, imported_at))
    source_files.extend(replace_tender_data(conn, imported_at))
    source_files.extend(replace_workspace_documents(conn, imported_at))
    register_source_files(conn, source_files)

    conn.execute(
        'INSERT INTO eva.import_runs VALUES (?, ?, ?)',
        [imported_at, 'ok', 'full refresh: hermes + app backend snapshot + telegram raw/classified + tenders + workspace docs + settings'],
    )
    optimize_database(conn)
    summary = summarize(conn)
    size_info = conn.execute("SELECT database_size, wal_size FROM pragma_database_size()") .fetchone()
    print(json.dumps({
        'db_path': str(DB_PATH),
        'imported_at': imported_at,
        'database_size': size_info[0],
        'wal_size': size_info[1],
        'summary': [{'dataset': ds, 'rows': cnt} for ds, cnt in summary],
    }, ensure_ascii=False, indent=2))
    conn.close()


if __name__ == '__main__':
    main()
