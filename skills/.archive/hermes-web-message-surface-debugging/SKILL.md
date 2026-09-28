---
name: hermes-web-message-surface-debugging
description: Diagnose and fix Hermes Web incidents where chat messages, recurring deliveries, export/viewer output, and stored backend content disagree because display_text, recurring_summary, or serializer contracts diverge.
---

# Hermes Web message surface debugging

Use this skill when Hermes Web shows any of these symptoms:
- chat bubble shows internal planning / reasoning / instruction text;
- recurring or job-delivery messages render differently in chat vs export/viewer;
- markdown formatting is missing in one surface but preserved in another;
- backend tests pass for helper functions, but live UI still shows the wrong body;
- `content`, `meta.display_text`, `recurring_summary`, and user-visible output disagree.

This skill is specifically for *message surface contract* incidents: cases where the wrong text is stored, serialized, normalized, or selected for display.

## Core idea

In Hermes Web, do not treat `messages.content` as the same thing as the user-facing answer.
Several layers can exist at once:
- raw stored `content`;
- `meta.display_text`;
- recurring/job-delivery `recurring_summary.summary` and `status_detail`;
- export/viewer body;
- frontend selection logic such as `message.display_text -> meta.display_text -> content`.

Many incidents come from one layer being fixed while another still uses raw `content`.

## Default debugging sequence

1. **Separate the symptom class**
   Decide which surface is actually broken:
   - chat API serialization;
   - frontend rendering choice;
   - export/viewer path;
   - recurring/job-delivery ingestion from cron output;
   - historical bad data already stored in DB.

2. **Inspect real stored messages first**
   For the specific thread/message IDs, compare:
   - `content`
   - `meta_json.display_text`
   - `message_kind`
   - `output_path`
   - attachments / recurring metadata

   Ask: is the bad text already in storage, or is it introduced later by serialization/export/UI?

3. **Check serializer contract before blaming the frontend**
   In Hermes Web, the frontend often already prefers `display_text` over raw `content`.
   If the UI still shows bad text, verify whether backend `serialize_message(...)` is:
   - clearing `display_text`;
   - failing to derive it for recurring/job-delivery messages;
   - returning different values top-level vs inside `meta`.

4. **Test helper paths separately from main serialization**
   A common trap: helpers like output extractors or export builders are correct, while the main chat serializer is still wrong.
   Verify separately:
   - `extract_hermes_output_for_delivery(...)`
   - `build_message_display_text(...)`
   - `serialize_message(...)`
   - export/viewer builders

5. **Prefer targeted contract tests over broad app smoke first**
   Add or run focused tests that pin the expected user-facing body for:
   - reasoning-preface stripping;
   - recurring digest normalization;
   - serializer top-level `display_text`;
   - export `display_content`.

6. **Patch the highest shared layer**
   Fix the layer that all consumers should trust.
   Usually this is:
   - `serialize_message(...)` for main chat surfaces;
   - export body builder for viewer/export-only defects;
   - recurring delivery extraction for cron/job-delivery ingestion defects.

7. **Deploy and verify with real process reload**
   If the code changed on a live backend, make sure the running service actually rereads the file.
   On `systemd` units with `Restart=always`, killing the main PID can be a valid fallback when direct restart is blocked by gateway/process constraints.

## Important pitfall

Do **not** assume that fixing export/viewer or recurring-output normalization automatically fixes the chat API.
A recurring Hermes Web defect pattern is:
- helper/export path is already clean;
- `serialize_message(...)` still zeroes or ignores `display_text` for recurring messages;
- frontend then has no safe body to prefer.

If a targeted serializer test fails while helper tests are green, treat that as the main root cause.

## Specific recurring/job-delivery rule

For assistant messages with recurring/job-delivery semantics:
- never clear `display_text` just because `recurring_summary` exists;
- derive `display_text` from the cleanest available recurring body, typically:
  1. `recurring_summary.summary`
  2. `recurring_summary.status_detail`
  3. normalized fallback body
- then run the result through `build_message_display_text(...)`.

Otherwise chat consumers lose the safe user-facing text even when normalization helpers are already correct.

## Verification checklist

A fix is not complete until all of these are true:
- targeted serializer test passes;
- neighboring normalization/export tests still pass;
- live code is synced to the actual runtime host;
- runtime process has reloaded the updated file;
- if possible, inspect one real affected thread/message after restart.

## When to add a reference file

Add a `references/` note when you uncover a reusable pattern such as:
- serializer-vs-export mismatch;
- recurring digest storage defects;
- safe restart procedure for this runtime contour;
- exact failing/passing test names that define the contract.

Reference available:
- `references/kpi-digest-serializer-incident-2026-06-25.md` — concrete example where helper/export paths were green but `serialize_message(...)` still cleared recurring `display_text` on the main chat API path.
