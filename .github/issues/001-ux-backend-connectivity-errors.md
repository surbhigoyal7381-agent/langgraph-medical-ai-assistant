---
title: "UX: Friendly, actionable network error UI"
labels: ux, frontend
---

Replace opaque network alerts with contextual diagnostics and retry.

Acceptance criteria:
- On fetch failure, UI shows a friendly message and a Retry button.
- Diagnostics panel shows request URL, headers (non-sensitive), and last server SSE events.
- Integration test simulates backend close and asserts UI shows Retry.
- Document UX copy in `frontend/components/Chat.js`.
