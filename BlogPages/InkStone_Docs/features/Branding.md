---
website: true
title: Branding
date: 2026-05-21
summary: Favicon override, site icon beside the title, and per-section header title — all via frontmatter.
featured: true
priority: 1
---

Three branding elements are controllable from your vault: the **favicon**, the **icon** beside the site title, and the **header title text** (`site_title`).

---

## Favicon

InkStone serves its built-in favicon by default. To override it, place a file named `favicon.ico`, `favicon.png`, or `favicon.svg` in the **vault root**. InkStone checks for it on every request and serves it instead. Priority: `.ico` → `.png` → `.svg`.

```
your-vault/
  favicon.png   ← place here to override
  Home.md
  blog/
```

No config needed — hot-reload picks it up automatically.

---

## Site icon

`icon:` in frontmatter shows an image beside the site title in the header.

```yaml
---
website: true
type: homepage
title: My Site
icon: _attachments/logo.png
---
```

### Path formats

| Value | How it resolves |
|---|---|
| `_attachments/logo.png` | Vault-relative — served via `/attachments/` |
| `/static/logo.svg` | Engine static file |
| `https://example.com/logo.svg` | External URL, used as-is |

### Icon inheritance

The icon cascades down the URL tree. Set it on a section homepage and every post in that section inherits it unless overridden. Resolution order for `/a/b/c`:

1. `/a/b/c` (the post itself)
2. `/a/b`
3. `/a`
4. `/` (root homepage)

First ancestor with `icon:` set wins.

---

## Site title override

`site_title:` replaces the displayed header title for a page and all its children — without changing the page's own `title:` (which drives the URL and `<title>` tag).

```yaml
---
website: true
type: homepage
title: InkStone Docs
site_title: "InkStone"
---
```

Useful when a section has a distinct brand from the root. Cascade rules are identical to `icon:`.

---

## Full example

Root homepage — default icon and title for the whole site:

```yaml
---
website: true
type: homepage
title: Anton Bakulin
icon: _attachments/avatar.jpg
---
```

Sub-section homepage — overrides both for everything under `/inkstone`:

```yaml
---
website: true
type: homepage
title: InkStone Docs
icon: /static/InkStoneLogo.png
site_title: "InkStone"
---
```

---

## See also

- [[Frontmatter Reference]] — complete field list
- [[Theming]] — dark/light mode and CSS themes
