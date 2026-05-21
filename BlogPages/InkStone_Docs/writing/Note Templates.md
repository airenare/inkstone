---
website: true
title: Note Templates
date: 2026-01-01
summary: Create notes with correct InkStone frontmatter using QuickAdd or Obsidian's Templates plugin.
featured: true
priority: 8
---

The demo vault ships with five ready-to-use templates in `templates/`. Two Obsidian plugins can use them to auto-fill frontmatter when you create a new note.

---

## Available templates

| File | Page type | Use for |
|---|---|---|
| `templates/web page template.md` | regular post | blog posts, standalone pages |
| `templates/homepage template.md` | `type: homepage` | section root with custom content |
| `templates/listing page template.md` | `type: listing` | auto-generated post index |
| `templates/book template.md` | `type: book` | book entries with cover/author layout |
| `templates/translations template.md` | `type: translations` | UI label overrides for a language |

---

## QuickAdd (recommended)

QuickAdd prompts you for values when creating a note, then fills frontmatter automatically. All five commands are pre-configured in the demo vault and available via `Ctrl+P`.

**Usage:**
1. Press `Ctrl+P` → type the command (e.g. **New Post**)
2. QuickAdd prompts for title, summary, etc.
3. Choose a folder — the note opens with frontmatter ready

`{{VALUE:Label}}` prompts for user input. `{{DATE:YYYY-MM-DD}}` inserts today's date.

---

## Template contents

### web page template

```yaml
---
website: true
title: {{VALUE:Title}}
date: {{DATE:YYYY-MM-DD}}
summary: "{{VALUE:Summary}}"
tags:
  - 
---
```

### homepage template

```yaml
---
website: true
type: homepage
title: {{VALUE:Title}}
date: {{DATE:YYYY-MM-DD}}
language: en
show_search: false
show_tags: false
---
```

### listing page template

```yaml
---
website: true
type: listing
title: {{VALUE:Title}}
date: {{DATE:YYYY-MM-DD}}
summary: "{{VALUE:Summary}}"
---
```

### book template

```yaml
---
website: true
type: book
title: {{VALUE:Title}}
date: {{DATE:YYYY-MM-DD}}
author: "{{VALUE:Author}}"
summary: "{{VALUE:Summary}}"
tags:
  - 
---
```

### translations template

Frontmatter:
```yaml
---
type: translations
lang: {{VALUE:Language code (e.g. ru, fr, de)}}
---
```

Body (a fenced `yaml` block — add your translated strings):
```yaml
Search: 
Tags: 
"All tags": 
"min read": 
Featured: 
"All Posts": 
```

> [!tip] Translations notes don't need `website: true`
> They are loaded automatically. Strings go in the note body, not frontmatter.

---

## Core Templates (simpler alternative)

Obsidian's built-in Templates plugin inserts a template into the current note but can't prompt for values.

1. Enable **Templates** in Settings → Core plugins
2. Set **Template folder location** to `templates/`
3. Open a new note → run **Templates: Insert template** → pick a template
4. Fill in the frontmatter fields manually

---

## Optional fields to add manually

The templates cover required fields only. Add these when needed:

| Field | When |
|---|---|
| `featured: true` | Highlight on the section listing |
| `updated: YYYY-MM-DD` | Show "Updated …" separately from `date` |
| `slug: custom-url` | Override auto-generated slug |
| `lang: ru` | Mark as a language variant |
| `banner: photo.jpg` | Hero image at the top |
| `menu_order: 1` | Pin to the top nav |
| `priority: 0` | Sort order among featured posts |

See [[Frontmatter Reference]] for the full list.
