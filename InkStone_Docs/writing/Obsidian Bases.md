---
website: true
title: Obsidian Bases
date: 2026-01-01
summary: "Publish .base table views as auto-updating post indexes with filters and sorting."
---

## Publishing a base

**Filename marker (recommended):**

```
Posts__website.base
Posts__website__featured.base   ← also marks it as featured in its parent listing
```

**Legacy YAML** (Obsidian may overwrite on save — prefer the filename marker):

```yaml
website: true
```

The title is the filename with `__website` (and `__featured`) stripped.

## Supported view

Only `type: table` is supported. The base YAML must declare it:

```yaml
type: table
fields:
  - name: title
  - name: date
  - name: summary
filters:
  - type: property
    name: featured
    operator: eq
    value: true
sort:
  - field: date
    direction: desc
limit: 10
```

## Filters

| Filter expression | Matches |
|---|---|
| `file.hasTag("python")` | Notes tagged `#python` |
| `file.tags.contains("python")` | Same — alternative syntax |
| `file.inFolder("blog")` | Notes inside the `blog/` folder |
| `date > 2025-01-01` | Notes published after Jan 1 2025 |
| `featured = true` | Featured notes |
| `filter1 and filter2` | Both conditions must match |
| `filter1 or filter2` | Either condition matches |
| `not filter` | Negation |

## Behaviour

- Column order, sort direction, and limit from the base YAML are respected.
- The engine executes the filter against the live post index — the table updates automatically when notes change (no restart needed).
- The rendered table links each title to the post's URL.
