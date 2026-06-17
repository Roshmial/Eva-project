# Hermes Web job recipient acceptance on split runtime

Use this when live acceptance must prove that job/cron delivery works for more than the owner, especially when frontend and backend live on different hosts.

## What to prove

1. A job with `fixed_user` recipient can be created on the live backend.
2. Manual run succeeds.
3. Owner and recipient each receive a job thread for the same `job_id`.
4. Those threads have different `thread.id` values when the UX promise is "separate chat per recipient".
5. Delivered message content is clean: no technical footer, routing metadata, model metadata, or personalization preview.
6. Temporary acceptance artifacts are cleaned up.

## Reliable procedure

- Create temporary admin directly in the live DB when normal demo credentials are unknown or unavailable.
- Log in through `/api/auth/login` to get a real token.
- Create temporary recipient through `/api/admin/users`.
- Create temporary shared job with:
  - owner recipient
  - `fixed_user` recipient pointing to the created user id
- Trigger `/api/jobs/<job_id>/run`.
- Poll `/api/jobs/<job_id>/runs` until terminal status.
- Log in as recipient and compare `/api/threads` for owner vs recipient.
- Read recipient thread detail and inspect the last delivered message.
- Remove temporary job, runs, threads, messages, sessions, and users.

## Practical note

For this class of acceptance, long inline SSH heredocs are brittle because of nested quoting inside Python + SQL + JSON. Prefer:

1. write the verification script locally;
2. `scp` it to the backend host;
3. run it with the backend `.venv` Python;
4. let the script clean up after itself.

This pattern is more stable than trying to inline the whole acceptance flow in one shell command.