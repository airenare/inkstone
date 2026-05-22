---
website: true
title: Dataview Queries
date: 2026-05-22
summary: Server-side TABLE and LIST queries with FROM, WHERE, SORT, LIMIT, and GROUP BY.
tags:
  - dataview
featured: true
priority: 5
---

> [!note] No plugin required
> Queries run server-side at page load — no JavaScript Dataview plugin required in Obsidian.

## TABLE

Basic table of published notes from the `writing` folder with their dates and summary:


> [!bug] Investigation needed
> For some reason the WHERE logic is inverted in Obsidian editor. Shows correctly on the webpage though.

```dataview
TABLE date, summary
FROM "InkStone_Docs/writing"
WHERE type != listing
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

Restrict the source set. Sources can be combined with `AND`/`OR`:


> [!bug] Known bug
> Only applies the last argument, so the `AND/OR` operators don't work here.

```dataview
LIST 
FROM "InkStone_Docs/writing" OR "InkStone_Docs/features" OR "InkStone_Docs/deployment"
WHERE type != listing
```


> [!bug] Known bug
> Tables with `AND/OR` operator in `FROM` block are not rendered on the website.

```dataview
TABLE
FROM "InkStone_Docs/writing" OR "InkStone_Docs/features"
WHERE type != listing
```

---

## WHERE

Filter rows by a condition:

```dataview
TABLE summary
FROM "InkStone_Docs"
WHERE type = "listing"
```

```dataview
TABLE title, date
WHERE featured = true
```

```dataview
TABLE date
WHERE author = "Jane Doe"
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

Group results under a heading per unique value:

```dataview
TABLE title, date
GROUP BY file.folder
```

Each group gets its own heading; rows under it list notes from that folder.

## Inline queries

Use backtick expressions in running text for single-value outputs:

```markdown
This note is called `= this.title`.

There are `= dv.pages("#python").length` Python posts in the vault.
```

Inline queries use the `= expression` syntax inside backticks. Live example — this page is called `= this.title` and the vault currently has `= dv.pages("#python").length` Python-tagged posts.
