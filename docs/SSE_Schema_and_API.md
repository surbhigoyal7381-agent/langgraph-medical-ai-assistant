# SSE Schema and API Changes (Feature 1)

This document specifies the SSE message schema, new API behaviors, and frontend contract for streaming chat with diagnostics.

## SSE message format
Each SSE `data:` payload will be a JSON object. Fields:

- `type` (string) — one of: `chunk`, `progress`, `warning`, `error`, `meta`, `end`.
- `id` (string, optional) — unique message id for the stream event.
- `chunk` (string, optional) — partial text for `type==='chunk'`.
- `progress` (number 0..100, optional) — percent complete for `type==='progress'`.
- `warning` (string, optional) — human-friendly warning text.
- `error` (string, optional) — human-friendly error summary.
- `meta` (object, optional) — structured metadata (e.g., model name, tokens, latency ms).

Example events:

data: {"type":"chunk","id":"m-1","chunk":"Hello"}

data: {"type":"progress","progress":40}

data: {"type":"warning","warning":"Rate limit approaching"}

data: {"type":"error","error":"Model backend unavailable"}

data: {"type":"end","meta":{"tokens":123}}

## API changes (backend)
- Endpoint: `POST /chat` (existing) — unchanged contract but now streams structured SSE events.
- New optional query/body flags:
  - `diagnostics: boolean` — if true, backend will include a `meta.diagnostics` array with internal steps useful for debugging (non-PII).
- Server behavior:
  - Immediately respond 200 and start streaming `meta` (if any), then `progress` and `chunk` events, and finally `end` or `error`.
  - On exception, send `type: "error"` SSE message with `error` and `meta` before closing the stream.

## Frontend contract
- The frontend must:
  - Parse SSE `data:` JSON and handle `type` values.
  - Render `chunk` events incrementally into the current AI message.
  - Show a progress bar for `progress` events if present.
  - Surface `warning` as non-blocking notices.
  - On `error`, show a contextual dialog with a Retry button and a "Show diagnostics" toggle to reveal `meta.diagnostics` if available.

## Backward compatibility
- If server emits simple plain-text SSE (legacy), the frontend will fallback to parsing text pieces and treat them as `chunk`.
