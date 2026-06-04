---
website: true
title: Social Links
date: 2026-05-21
summary: Add social profile links to the site footer — icon + handle, detected automatically from the URL.
featured: true
priority: 6
tags:
  - features
---

Add one key per platform to your **root homepage** frontmatter. InkStone detects the network from the key name, extracts the handle from the URL, and renders icon + handle in the footer.

```yaml
---
website: true
type: homepage
title: My Site
github: https://github.com/yourname
mastodon: https://mastodon.social/@yourname
bluesky: https://bsky.app/profile/yourname.bsky.social
twitter: https://x.com/yourname
instagram: https://instagram.com/yourname
linkedin: https://linkedin.com/in/yourname
youtube: https://youtube.com/@yourname
---
```

---

## Multiple accounts on the same platform

If you have more than one profile on the same network, use the `social_links` list. Each entry is a plain URL — InkStone detects the network automatically from the domain.

```yaml
---
website: true
type: homepage
title: My Site
social_links:
  - https://github.com/personal-account
  - https://github.com/work-org
  - https://bsky.app/profile/main.bsky.social
  - https://bsky.app/profile/alt.bsky.social
---
```

`social_links` entries are appended after any per-key entries, so you can mix both styles. Duplicate URLs are silently ignored.

---

## Supported platforms

| Key | Network | `rel="me"` |
|---|---|---|
| `github` | GitHub | ✓ |
| `mastodon` | Mastodon | ✓ |
| `bluesky` | Bluesky | ✓ |
| `twitter` | X / Twitter | |
| `instagram` | Instagram | |
| `linkedin` | LinkedIn | |
| `facebook` | Facebook | |
| `youtube` | YouTube | |
| `telegram` | Telegram | |

`rel="me"` is set on GitHub, Mastodon, and Bluesky — the platforms used for identity verification.

URL-based detection in `social_links` works for all platforms above. Mastodon detection covers the most common hosted instances; self-hosted instances that aren't recognised fall back to the per-key `mastodon:` key instead.

---

## Handle extraction

InkStone takes the last path segment and prepends `@` where appropriate:

| URL | Displayed |
|---|---|
| `https://github.com/airenare` | `@airenare` |
| `https://mastodon.social/@airenare` | `@airenare` |
| `https://bsky.app/profile/airenare.bsky.social` | `@airenare` |
| `https://linkedin.com/in/airenare` | `airenare` |

---

## Ordering

Per-key links appear first, in registry order: GitHub → Mastodon → Bluesky → X → Instagram → LinkedIn → Facebook → YouTube. `social_links` entries follow in the order they are listed. Platforms you haven't set are simply omitted.
