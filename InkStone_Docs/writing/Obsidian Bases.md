---
website: true
title: Obsidian Bases
date: 2026-05-21
summary: Publish .base table views as auto-updating post indexes with filters and sorting.
featured: true
priority: 7
tags:
  - writing
  - base
  - database
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

> [!tip] Tip
> Just use Obsidian's native bases editor. It gives a real time feedback and easy to use GUI.

| Filter expression | Matches |
|---|---|
| `file.hasTag("python")` | Notes tagged `#python` |
| `file.tags.contains("python")` | Same — alternative syntax |
| `file.inFolder("blog")` | Notes inside the `blog/` folder (path relative to vault root) |
| `date > 2025-01-01` | Notes published after Jan 1 2025 |
| `featured = true` | Featured notes |
| `filter1 and filter2` | Both conditions must match |
| `filter1 or filter2` | Either condition matches |
| `not filter` | Negation |

## Behaviour

- Column order, sort direction, and limit from the base YAML are respected.
- The engine executes the filter against the live post index — the table updates automatically when notes change (no restart needed).
- The rendered table links each title to the post's URL.

## Embedding a base in a note

Embed a published base table inline inside any markdown note:

```
![[Posts__website.base]]
![[Posts__website]]
```

Obsidian's link picker may insert a full vault-relative path — that works too:

```
![[writing/Posts__website.base|Posts__website]]
```

InkStone strips the path prefix, `.base` extension, and `__website` marker automatically, so both the resolved URL and the displayed link text are clean.

## Example
[[Writing Reference Base__website.base]]

![[Writing Reference Base__website.base]]