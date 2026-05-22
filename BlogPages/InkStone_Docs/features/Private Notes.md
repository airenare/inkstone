---
website: true
title: Private Notes
date: 2026-05-21
summary: Per-note access tokens and the master ACCESS_TOKEN for protecting content.
featured: true
priority: 4
---

## Notes without website: true

Any note without `website: true` is not publicly served. If someone navigates to its URL, they see a placeholder page — the note content is never exposed.

These notes are still indexed by the Dataview engine and can appear in query results (titles and metadata only, not body content).

## Per-note access token

Add `access_token:` to a note's frontmatter to share it privately:

```yaml
---
website: true
access_token: mysecret
title: Draft Post
---
```

Share the note as `/draft-post?token=mysecret`. Once a visitor visits with the correct token, their session tracks that URL as unlocked — they can navigate away and return without needing the token again.

Each note has its own independent token. Unlocking one note does not unlock others.

## Master key

The `ACCESS_TOKEN` environment variable acts as a single key that unlocks **all** private notes:

```bash
ACCESS_TOKEN=master-unlock-key
```

A visitor who knows the master key can pass it as `?token=master-unlock-key` on any URL.

## Coexistence

Both methods work simultaneously. A visitor with the master key can unlock everything; a visitor with a per-note token can only unlock that specific note.

> [!warning] Tokens are in the URL
> Access tokens appear in the query string and browser history. Don't use this for truly sensitive production content — it's suitable for drafts, previews, and content shared with trusted collaborators.
