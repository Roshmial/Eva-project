# Hermes Web contour pitfall: split prod/frontend runtime

Use this as a compact reference when the same project serves multiple contours.

## Pattern

A frequent layout is:
- dev: frontend, backend, and auxiliary services on one host
- prod backend: different host
- prod frontend: original host, different port

In this shape, a frontend fix can be correct in code but still land on the wrong runtime surface.

## What to verify first

1. Is the named host already the current machine?
2. Which exact systemd unit serves the requested frontend port?
3. What `WorkingDirectory` and `ExecStart` does that unit use?
4. Does a drop-in override set the backend base URL?
5. Does live `/api/health` or `/api/service-info` through the frontend port resolve to the intended backend?

## Reliable proof points

- unit file for the frontend port
- override file carrying backend base URL
- live source markers from the served frontend
- live `/api/*` responses through the target frontend port

## Why this matters

This mistake creates a dangerous false positive:
- code changes exist
- build may pass
- some runtime responds
- but the requested prod surface is still untouched

Treat contour verification as a prerequisite, not as a post-hoc check.
