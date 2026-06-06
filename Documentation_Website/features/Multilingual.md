---
website: true
title: Multilingual
date: 2026-05-21
updated: 2026-06-03
summary: Publish notes in multiple languages with filename suffixes and UI translations.
featured: true
priority: 3
tags:
  - features
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
Updated: Обновлено
"No tags yet.": Тегов пока нет.
"No posts yet.": Постов пока нет.
"Read more": Читать далее
Previous: Назад
Next: Далее
```
````

Keys are the English UI strings exactly as shown in the reference below — spelling and punctuation must match precisely.

## Full string reference

| Key | Where it appears |
|---|---|
| `Search` | Nav bar search link |
| `Tags` | Nav bar tags link |
| `All tags` | Tags index heading |
| `No tags yet.` | Tags page when no tags exist |
| `No posts yet.` | Listing/feed page when section is empty |
| `No results` | Search page when query has no hits |
| `results` | Search result count (plural) |
| `result` | Search result count (singular) |
| `for` | Search: "No results **for** …" |
| `tagged` | Search: "results **tagged** …" |
| `Featured` | Listing page section heading |
| `All Posts` | Listing page section heading |
| `Read more` | Feed page: link to full post |
| `Previous` | Feed/listing pagination: previous page |
| `Next` | Feed/listing pagination: next page |
| `See also` | Related posts heading |
| `Contents` | Table of contents heading |
| `Updated` | Post meta: "**Updated** Jan 1, 2026" |
| `by` | Post meta: "**by** Author Name" |
| `min read` | Post meta: "5 **min read**" |
| `Read it in` | Language unavailable placeholder |
| `Not yet translated` | Language unavailable placeholder |
| `Translation unavailable` | Language unavailable placeholder |
| `This page is not yet available in` | Language unavailable placeholder |
| `built with` | Footer attribution line |

### Date localisation

`localize_date` translates the month name and date format. Override month names individually and set `date_format` to rearrange the order:

````markdown
```yaml
date_format: "{day} {month} {year}"
January: января
February: февраля
March: марта
April: апреля
May: мая
June: июня
July: июля
August: августа
September: сентября
October: октября
November: ноября
December: декабря
```
````

See [[Page Types#translations]] for the full type reference.
