---
website: true
title: Page Types
date: 2026-05-21
summary: "homepage, listing, feed, book, and translations — what each type does."
featured: true
priority: 1
---

The `type:` frontmatter field controls how InkStone renders a note. Most notes have no `type:` and render as standard posts.

## homepage

Renders the file's own markdown content at the section root URL. Use for a custom landing page for a section (or for `/` at the vault root).

```yaml
---
website: true
type: homepage
title: My Blog
language: en
default_theme: dark
show_search: true
---
```

Only one `homepage` per section. If multiple exist, the last one loaded wins (undefined behaviour — avoid).

## listing

Auto-generates a post index at the section root URL. Shows featured posts in a highlighted row, then all remaining posts sorted by date.

```yaml
---
website: true
type: listing
title: Blog
summary: "All posts about programming and ideas."
---
```

The file's markdown content (if any) is shown above the generated list as an intro. Only one `listing` per section.

## feed

Renders an inline post stream — like a traditional blog feed. Each post shows its title, date, an excerpt of the content, and a "Read more" link. Posts are sorted newest-first.

```yaml
---
website: true
type: feed
title: Blog
---
Optional intro text shown above the stream.
```

The file's own markdown content (if any) is shown above the stream as an intro.

**Controlling the excerpt cut point** — add `<!-- more -->` anywhere in a post's body. Everything before the marker becomes the feed excerpt; everything after it only appears on the full post page:

```markdown
This paragraph and the next will appear in the feed preview.

More context here, still visible in the feed.

<!-- more -->

This paragraph only appears when a reader opens the full post.
```

If a post has no `<!-- more -->` marker, InkStone automatically excerpts the first paragraph(s) up to roughly 500 characters of readable text.

**Posts without a date** appear at the bottom of the feed. Add a `date:` field to every post in a feed section to get predictable ordering.

Only one `feed` (or `listing`) per section.

## book

Renders with a special book template that includes a cover image, ISBN, rating, and genre metadata in the header.

```yaml
---
website: true
type: book
title: "The Pragmatic Programmer"
author: "David Thomas, Andrew Hunt"
date: 2026-01-15
---
```

## translations

Provides UI string overrides for a language. Does not need `website: true`. Strings go in a fenced `yaml` block in the note body (not in frontmatter).

```yaml
---
type: translations
lang: ru
---
```

Note body:

````markdown
```yaml
Search: Поиск
Tags: Теги
"All tags": Все теги
"min read": мин чтения
Featured: Избранное
```
````

The `lang:` value must match the language code used in `_RU.md` filename suffixes or `lang:` frontmatter on content notes.
