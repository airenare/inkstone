---
website: true
title: Dataview Queries
date: 2026-05-21
summary: Server-side TABLE and LIST queries with FROM, WHERE, SORT, LIMIT, and GROUP BY.
tags:
  - dataview
featured: true
priority: 5
---

> [!note] No plugin required
> Queries run server-side at page load — no JavaScript Dataview plugin required in Obsidian.

## TABLE

Basic table of all published notes with their dates:

```dataview
TABLE date, summary FROM ""
```

With column aliases using `AS`:

```dataview
TABLE date AS "Published", author AS "By", summary AS "Description"
```

## LIST

Simple list of note titles:

```dataview
LIST FROM ""
```

## FROM

Restrict the source set. Sources can be combined with `AND`/`OR`:

```dataview
LIST FROM #python
```

```dataview
TABLE date FROM "blog"
```

```dataview
TABLE date FROM [[Getting Started]]
```

## WHERE

Filter rows by a condition:

```dataview
TABLE date, summary
WHERE date > 2025-01-01
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
