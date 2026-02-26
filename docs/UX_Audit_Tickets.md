# UX Audit — Detailed Tickets

This file expands the UX audit items into actionable tickets with acceptance criteria.

## Ticket 1 — Improve Backend Connectivity Errors
- Title: UX: Friendly, actionable network error UI
- Description: Replace opaque "network error" alerts with contextual error UI that
  - shows likely cause (CORS, network, server down)
  - offers a Retry button and a "Diagnostics" toggle that shows request/response and SSE partials
  - uses optimistic UI where safe
- Acceptance criteria:
  - On fetch failure, UI shows a friendly message and a Retry button.
  - Diagnostics panel shows request URL, headers (non-sensitive), and last server SSE events.
  - Integration test simulates backend close and asserts UI shows Retry.
  - Document UX copy in `frontend/components/Chat.js`.

## Ticket 2 — Global Undo / Safety Net
- Title: UX: Global Undo and soft-delete for patient edits
- Description: Implement soft-delete and 30-day retention; provide Undo snackbar and revert API.
- Acceptance criteria:
  - Soft-delete flag implemented in backend store for patient profile edits.
  - UI shows Undo snackbar after destructive action for 10s.
  - Revert endpoint returns previous version and UI applies it on Undo.

## Ticket 3 — Persistent Patient Summary with Diffs
- Title: UX: Compact patient summary + change explanations
- Description: Add a persistent, collapsible patient summary in `PatientSidebar` showing last-updated time and a diff view.
- Acceptance criteria:
  - Summary panel present on main view; updates in real-time (polling or websocket).
  - Diff UI highlights changes and provides "Why this changed" metadata from backend.

## Ticket 4 — Streaming & Perceived Performance
- Title: UX: Streaming partial responses and skeletons
- Description: Frontend must render partial SSE chunks as they arrive, use skeleton loaders, and start a local cache of recent replies to make UI feel instantaneous.
- Acceptance criteria:
  - Chat displays incremental text as SSE chunks arrive.
  - Skeleton UI shown during initial model call (<300ms perceived start).
  - Integration test verifies partial updates on streaming.

## Ticket 5 — Privacy & Consent Notices
- Title: UX: Permission explanations and data footprint UI
- Description: Add contextual explainers near permission/consent points and a Data Footprint panel allowing export/delete of PII.
- Acceptance criteria:
  - Consent UI with short explanation before collecting any PII.
  - Data Footprint panel shows stored keys and allows export/delete calls.
