---
website: true
title: Dataview Post
date: 2026-01-20
---

The title of this note is `= this.title`.

```dataview
LIST
FROM "blog"
WHERE title != "Dataview Post"
```

```dataview
TABLE
FROM "blog"
WHERE contains(type, listing)
```

Code block example that must not be evaluated:

```
`= this.title`
```
