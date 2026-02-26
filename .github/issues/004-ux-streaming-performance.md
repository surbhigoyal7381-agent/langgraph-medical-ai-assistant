---
title: "UX: Streaming & Perceived Performance"
labels: ux, frontend
---

Ensure partial SSE responses render immediately and add skeletons to improve perceived performance.

Acceptance criteria:
- Chat displays incremental text as SSE chunks arrive.
- Skeleton UI shown during initial model call (<300ms perceived start).
- Integration test verifies partial updates on streaming.
