---
title: "UX: Global Undo and soft-delete for patient edits"
labels: ux, backend
---

Implement soft-delete and 30-day retention; provide Undo snackbar and revert API.

Acceptance criteria:
- Soft-delete flag implemented in backend store for patient profile edits.
- UI shows Undo snackbar after destructive action for 10s.
- Revert endpoint returns previous version and UI applies it on Undo.
