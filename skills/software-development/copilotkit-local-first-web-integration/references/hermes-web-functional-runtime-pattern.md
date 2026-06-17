# Hermes Web functional CopilotKit runtime pattern

Use this reference when CopilotKit packages and a standalone runtime already exist, but the product still lacks real frontend integration.

## Situation pattern

Typical symptoms:
- frontend source has no CopilotKit imports at all;
- backend exposes `/api/copilotkit/info`, but action/runtime endpoints are still preview-only or return `501`;
- a standalone local runtime is already listening on another port;
- the real product need is not a floating demo widget, but useful actions over existing app entities.

## Recommended wiring

1. Keep the existing backend as source of truth for product data.
2. Do not route CopilotKit through a preview-only backend stub.
3. Add a frontend proxy path such as `/copilotkit` to the standalone runtime.
4. Align the launcher/env defaults so the frontend uses that proxy path.
5. Expand runtime CORS to the actual frontend origins used in local development.
6. Add a simple runtime health route if missing, so connectivity can be checked independently from the app.

## Useful first actions for a chat-first admin/product UI

Prefer actions that bridge conversation into the app's existing workflows:
- navigate to a specific screen;
- open an existing thread/chat by id;
- prepare a message in the existing composer;
- prepare a recurring-job draft in the existing modal/form;
- open an existing user file by id.

These are better first steps than inventing a second state model inside CopilotKit.

## Readable context shape

Good first readable blocks:
- current screen;
- authenticated user summary;
- active thread summary;
- active job summary;
- lightweight lists of threads, files, and jobs;
- small metadata dictionaries already used by the UI.

Avoid dumping whole transcripts or oversized objects on the first pass.

## JSX integration warning

If `App.jsx` is large and uses a giant inline `return`, do not wrap the entire tree via a blind one-line replacement.

Safer sequence:
1. extract existing main tree into `appContent`;
2. return a small wrapper with `CopilotKit`, bridge component, main tree, and sidebar as distinct nodes;
3. build immediately after the structural patch;
4. only then add more actions/readables.

## Reporting standard

Report these separately:
- runtime transport/path prepared;
- frontend compile status;
- sidebar visibility status;
- action registration status;
- end-to-end action execution status.

Do not collapse them into a single "CopilotKit works" claim.
