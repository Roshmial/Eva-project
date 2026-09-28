# Chat error leak triage

Use this when a user reports raw HTML, SVG, or long path fragments inside Telegram/chat output and the system under investigation also has a split frontend/backend web contour.

## Why this matters

A visible garbage payload in chat is not sufficient evidence that the web frontend or frontend proxy is broken. The same payload may originate in:
- a provider-side HTML error page
- a gateway/agent fallback that stringifies `error`
- a backend error that was copied into a chat surface

If you misclassify the source, you will fix the wrong host or wrong contour and create fake progress.

## Fast classification

Check three surfaces separately:
1. live web surface
   - reproduce from the browser-facing port or `/api/*` path
2. backend surface
   - reproduce from backend health or target endpoint directly
3. agent/gateway/provider path
   - inspect logs for the same fragment, especially HTML titles, Cloudflare pages, permission pages, or SVG/path fragments

## Strong signals of agent/provider propagation

- the fragment appears in agent/gateway logs before or without direct reproduction from the web port
- the payload looks like a complete HTML error page or contains SVG/logo path data
- the chat response was assembled from `error` fallback text rather than a normal `final_response`
- the split frontend/backend path is otherwise healthy on live checks

## Response pattern

Do not say "this is definitely frontend" unless the same payload is reproducible from the live frontend/proxy path.

Instead state:
- what contour was checked
- whether the payload reproduced from live HTTP
- whether the same fragment was found in agent/gateway logs
- whether the leak is classified as web-surface, backend-surface, or agent/provider propagation

## Durable fix pattern

If the root cause is agent/provider propagation, sanitize at both layers:
- where the conversation result stores or returns `error`
- where the gateway/chat delivery falls back from empty `final_response` to `error`

Goal: user-facing chat must emit a short normalized message, never raw HTML/SVG/provider pages.
