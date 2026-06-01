---
website: true
title: Comments
date: 2026-05-21
summary: Add a Giscus comment section to posts using GitHub Discussions as the backend.
featured: true
priority: 5
tags:
  - features
---

InkStone supports opt-in comments via **Giscus** — a lightweight system backed by GitHub Discussions. When the three env vars are set, a comment section appears at the bottom of every post and book page.

---

## Setup

### 1. Prepare your GitHub repo

The repo must be:
- **Public**
- Have **Discussions** enabled (Settings → Features → Discussions ✓)

You can use your site's source repo or a dedicated discussions repo.

### 2. Get your IDs

Go to **[giscus.app](https://giscus.app)**, enter your repo, choose **Pathname** mapping, select a discussion category. The page gives you three values:

- `GISCUS_REPO` — e.g. `you/your-site`
- `GISCUS_REPO_ID` — a base64 string starting with `R_`
- `GISCUS_CATEGORY_ID` — a base64 string starting with `DIC_`

### 3. Set environment variables

```bash
GISCUS_REPO=you/your-site
GISCUS_REPO_ID=R_kgDO...
GISCUS_CATEGORY_ID=DIC_kwDO...
```

Add these to your `.env` (local) or deployment environment. When all three are present, InkStone injects the Giscus widget into `post.html` and `book.html` automatically. If any is missing, no widget appears.

---

## Theme sync

Giscus automatically follows InkStone's dark/light toggle — no page reload needed.

---

> [!note]
> Comments are site-wide when enabled. There is no per-post opt-out. Leave the env vars unset to disable comments everywhere.

---

## See also

- [[Configuration Reference]] — full env var reference
- [[Page Types]] — which templates render the comment section
