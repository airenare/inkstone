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

Basic table of published notes from the `writing` folder with their dates and summary:

```dataview
TABLE date, summary
FROM "InkStone_Docs/writing"
WHERE !contains(type, listing)
```


> [!question] Investigation needed
> Obsidian loves to mirror '=' and '!=' results, even if the query is 'contains(foo, bar) / !contains(foo, bar)'. Both render correctly by InkStone though.


---

## LIST

Simple list of note titles from `features` folder and their summaries:

```dataview
LIST summary
FROM "InkStone_Docs/features"
SORT title asc
```

---

## FROM

All listing pages from three folders, using FROM to restrict the source set and combining sources with `AND`/`OR`:
```dataview
LIST summary
FROM "InkStone_Docs/writing" OR "InkStone_Docs/features" OR "InkStone_Docs/deployment"
WHERE type = listing
```
Same in form of a table:
```dataview
TABLE summary
FROM "InkStone_Docs/writing" OR "InkStone_Docs/features" OR "InkStone_Docs/deployment"
WHERE type = listing
```

---

## WHERE

Filter rows by a condition. Both  ` = ` /  ` != ` comparison syntax and `contains()` / `!contains()` syntax work — stick to `contains()` for compatibility with the Obsidian editor (but it can still be inverted in Obsidian):

```dataview
TABLE summary
WHERE contains(type, listing)
```

---
```dataview
TABLE title, date
WHERE featured = true
LIMIT 10
```
---

## SORT

```dataview
TABLE date, title
FROM "InkStone_Docs/features"
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


Both syntaxes work — use `$=` for compatibility with the Obsidian editor:

1. `$= dv.pages("#database").length`
2. `= dv.pages("#database").length`



