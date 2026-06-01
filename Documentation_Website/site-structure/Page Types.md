---
website: true
title: Page Types
date: 2026-05-21
summary: homepage, listing, book, and translations — what each type does.
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
