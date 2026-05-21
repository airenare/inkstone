---
website: true
title: Theming
date: 2026-01-01
summary: Dark/light/system mode toggle, default theme, and the Omarchy theme.
featured: true
priority: 0
---

## Three-state theme toggle

Every page includes a theme toggle in the header with three states:

| Symbol | Mode |
|---|---|
| ⊙ | System — follows the visitor's OS preference |
| ☀ | Light |
| ☾ | Dark |

The selection is stored in `localStorage` and persists across page loads.

## Default theme

Set the initial theme for first-time visitors in the root homepage frontmatter:

```yaml
---
website: true
type: homepage
default_theme: dark
---
```

Accepted values: `dark`, `light`, `system`. Defaults to `system` if omitted.

> [!tip] Set `default_theme: system` to follow the visitor's OS preference. This is the most accessible option and requires no choice from the visitor.

## Built-in themes

**Default (Catppuccin-inspired)** — loaded from `obsidian.css`. A dark/light pair with warm purples and clean typography.

**Omarchy** — loaded from `omarchy.css`. An alternative palette for sites that match the Omarchy desktop environment.

To switch to the Omarchy theme, add `theme: omarchy` in the root homepage frontmatter:

```yaml
---
website: true
type: homepage
theme: omarchy
---
```

## CSS files

| File | Purpose |
|---|---|
| `obsidian.css` | Base dark/light theme (Catppuccin-inspired) + header and listing styles |
| `omarchy.css` | Alternative Omarchy-native palette |
| `callouts.css` | Per-type callout colours and icons |
| `omarchy-callouts.css` | Callout styles for the Omarchy theme |
| `code.css` | Code block styling with language labels and copy button |

All CSS files are in `frontend/static/`.
