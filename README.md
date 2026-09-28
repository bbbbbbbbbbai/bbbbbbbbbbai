# Laobai Diary: Design V2

Versioned source references, reconstruction ledgers, extracted artwork, and
visual evidence for the second design iteration.

## Source of Truth

- Figma file key: `ptA7IsUhV0rHsp8yRLFRVj`
- Original design atlas: `design/manifest.json` and `design/index.html`
- Editable Figma node mapping: `design/rebuild/figma-nodes.json`
- Current progress: `design/rebuild/rebuild-status.json`
- Source measurement and QA evidence: `design/rebuild/`

The scope contains 45 functional pages and 15 interaction-state groups
(75 individual states). A frame or screenshot is not final acceptance.
The `acceptedScreens` and `accepted` lists record actual final acceptance.
They must not be inferred from the number of Figma nodes.

## Versioning Policy

- Preserve the original atlas and all earlier application repositories.
- Work on `codex/figma-reconstruction-20260928`, not the remote default branch.
- Commit a checkpoint after each coherent reconstructed and inspected batch.
- Keep reference images, component/node IDs, screenshots, and limitations together.
- Never commit API keys, credentials, authentication responses, or private keys.
- Do not force-push. Fetch and inspect the destination before the first push.
- Final acceptance and in-progress snapshots must be clearly distinguished.

The requested destination is `bbbbbbbbbbai/bbbbbbbbbbai` on GitHub.
Local commits do not imply successful remote synchronization.
See `REMOTE-SYNC.md` for the current remote status.

## Refresh a Snapshot

Run from PowerShell with the working atlas path:

```powershell
./scripts/snapshot-design.ps1 -SourceRoot "<working atlas directory>"
git diff --stat
git status --short
```

The script performs a non-destructive, hash-checked copy into `design/`,
rejects known credential patterns, and skips caches. It does not delete
destination files and does not commit or push automatically.

## Editable Scope

Text, forms, controls, layout, charts, and reusable component instances are
native Figma layers. Extracted illustrations, photos, and some source icons
remain replaceable raster artwork. The source font is unknown; current
reconstruction uses Noto Sans SC with per-screen metric adjustments.

This repository versions the evidence and construction metadata. It is not
a downloadable native `.fig` backup of the complete cloud document.
