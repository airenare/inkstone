---
website: true
title: Social Links
date: 2026-05-21
summary: Add social profile links to the site footer — icon + handle, detected automatically from the URL.
featured: true
priority: 6
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

`rel="me"` is set on GitHub, Mastodon, and Bluesky — the platforms used for identity verification.

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

Links appear in the footer in a fixed order: GitHub → Mastodon → Bluesky → X → Instagram → LinkedIn → Facebook → YouTube. Platforms you haven't set are simply omitted.
