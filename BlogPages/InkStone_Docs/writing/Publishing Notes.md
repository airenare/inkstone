---
website: true
title: Publishing Notes
date: 2026-05-21
summary: The minimum frontmatter to publish a note, plus all optional fields.
featured: true
priority: 0
---

## Minimum frontmatter

The only required field is `website: true`:

```yaml
---
website: true
---
```

That's a valid published note. Everything else is optional.

## URL derivation

The URL is derived from the note's location in the vault:

- `blog/My Post.md` → `/blog/my-post`
- `gallery/arts/Photo.md` → `/gallery/arts/photo`
- `About.md` (vault root) → `/about`

The slug part comes from the title, following these rules:

- Spaces become hyphens
- Text is lowercased
- Non-ASCII characters are transliterated to ASCII (e.g. Cyrillic, Greek)
- Special characters are stripped

## Title resolution order ^important-para

InkStone resolves the post title in this priority order:

1. `title:` in frontmatter
2. First `# H1` heading in the note body
3. The filename (without `.md`)

## YAML quoting warning

Any frontmatter value containing a colon must be quoted, or YAML will silently break it:

```yaml
# BROKEN — YAML parses this as a nested mapping
title: From Vault to Web: How This Blog Works

# CORRECT
title: "From Vault to Web: How This Blog Works"
```

InkStone logs a warning and falls back to the H1/filename when it detects a broken `title`.

To include literal quote characters in a title, use single-quote wrapping:

```yaml
title: '"Hello World" Considered Harmful'
# → renders as: "Hello World" Considered Harmful
```

## Manual slug override

Use `slug:` to set the URL slug explicitly, bypassing title transliteration:

```yaml
---
website: true
title: "Привет мир"
slug: hello-world
---
```

The note will be served at `/hello-world` instead of `/privet-mir` regardless of the title.

For the full list of frontmatter fields, see [[Frontmatter Reference]].
