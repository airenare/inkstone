---
website: true
title: Dataview Queries
date: 2026-05-22
summary: Server-side TABLE and LIST queries with FROM, WHERE, SORT, LIMIT, and GROUP BY.
tags:
  - dataview
  - writing
  - database
featured: true
priority: 5
---











> [!note] No plugin required
> Queries run server-side at page load — no JavaScript Dataview plugin required in Obsidian.

## TABLE

> [!bug] Known bug `TABLE`
> The first column of tables ("File") is getting dropped for some reason. Although it can manually be added by `file.link AS File

Basic table of published notes from the `writing` folder with their dates and summary:

```dataview
TABLE file.link AS File, date, summary
FROM "InkStone_Docs/writing"
WHERE !contains(type, listing)
```

---

## LIST

Simple list of note titles from `features` folder and their summaries:

```dataview
LIST summary
FROM "InkStone_Docs/features"
```

---

## FROM

> [!bug] Known bug `AND/OR`
> When querying `FROM "InkStone_Docs/writing" OR "InkStone_Docs/features"`, the InkStone gets only the last argument (`"InkStone_Docs/features"`in this case).

Restrict the source set. Sources can be combined with `AND`/`OR`:

```dataview
LIST 
FROM "InkStone_Docs/writing" OR "InkStone_Docs/features" OR "InkStone_Docs/deployment"
WHERE type != listing
```

> [!bug] Known bug `TABLE` `AND/OR`
> Tables with `AND/OR` operator in `FROM` block are not rendered on the website at all.

```dataview
TABLE
FROM "InkStone_Docs/writing" OR "InkStone_Docs/features"
WHERE type != listing
```

---

## WHERE

> [!bug] Known bug `WHERE`
> The results of `WHERE type = listing` and `WHERE type != listing` are swapped. This syntax is supported in the InkStone and renders the correct result, but are incorrect in the Obsidian editor.
> The Dataview syntax that actually works correctly in Obsidian is `WHERE contains(type, listing)` or `WHERE !contains(type, listing)`. This is not supported in the InkStone yet, but needs to be.


Filter rows by a condition:

```dataview
TABLE summary
WHERE type = "listing"
```

---
```dataview
TABLE title, date
WHERE featured = true
```

```dataview
TABLE date
WHERE author = "Anton Bakulin"
```

## SORT
	
```dataview
TABLE date, title
SORT date DESC
```

## LIMIT

Return only the first N results:

```dataview
TABLE date, title
SORT date DESC
LIMIT 5
```

## GROUP BY


> [!NOTE] Note
> This is a cool one, as it renders a separate table for each group (folders in this case), but does not work like that in Obsidian, so to view the result you will have to render in on the website.

Group results under a heading per unique value:
Each group gets its own heading; rows under it list notes from that folder.

```dataview
TABLE title, date
GROUP BY file.folder
```

---

## Inline queries

Inline queries use the `"= expression"` syntax inside backticks. 
Use backtick expressions in running text for single-value outputs:

```markdown
Live example — This note is called `= this.title`.

There are `= dv.pages("#python").length` Python posts in the vault.
```


Live example — This page is called `= this.title` and the vault currently has `= dv.pages("#database").length` Python-tagged posts.


> [!bug] Known bug
> Obsidian supports JS queries (it needs to be turned on in settings first). So, for such queries as `'= dv.pages("#python").length'` the correct working obsidian syntax would be `'$= dv.pages("#database").length'`. But it shows Dataview error in the Obsidian editor. However it shows correctly in InkStone. While the JS query is not rendered in InkStone at all. So `'$='` syntax needs to be supported by InkStone as well.
> Example: These two lines must show a number:
> 
> 1. `$= dv.pages("#database").length`
> 2. `= dv.pages("#database").length`



