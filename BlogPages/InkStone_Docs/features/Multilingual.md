---
website: true
title: Multilingual
date: 2026-05-21
summary: Publish notes in multiple languages with filename suffixes and UI translations.
featured: true
priority: 3
---

## Language variants via filename suffix

Place translated notes alongside the original, appending `_XX` (ISO 639-1 code) before `.md`:

```
blog/My Post.md       → /blog/my-post        (default)
blog/My Post_RU.md    → /blog/my-post/ru     (Russian variant)
blog/My Post_DE.md    → /blog/my-post/de     (German variant)
```

Alternatively, use `lang:` in frontmatter:

```yaml
---
website: true
title: "Мой пост"
lang: ru
slug: my-post
---
```

## Language toggle

When language variants exist for a post, InkStone shows a language toggle in the post header. Clicking a language code switches to that variant.

`hreflang` meta tags are automatically added for SEO — search engines understand which pages are translations of each other.

## Auto-redirect

If a visitor navigates to a post URL that has no variant for their browser language, they get a placeholder page (not a 404) with links to available languages.

## Site default language

Set the `<html lang="">` attribute globally in the root homepage:

```yaml
---
website: true
type: homepage
language: en
---
```

## UI string translations

Override any UI string by creating a `type: translations` note. No `website: true` needed.

```yaml
---
type: translations
lang: ru
---
```

Put string overrides in a fenced `yaml` block in the note body:

````markdown
```yaml
Search: Поиск
Tags: Теги
"All tags": Все теги
"min read": мин чтения
Featured: Избранное
"Posted on": Опубликовано
"Updated": Обновлено
"Related": Похожие записи
```
````

Keys are the English UI strings. Values are the replacements shown when the visitor views a page with `lang: ru` content or when the site default language is Russian.

See [[Page Types#translations]] for the full type reference.
