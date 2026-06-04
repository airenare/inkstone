---
website: true
title: Theming
date: 2026-05-21
updated: 2026-06-03
summary: Dark/light/system mode toggle, default theme, and built-in themes.
featured: true
priority: 0
tags:
  - features
---

## Three-state theme toggle

Every page includes a theme toggle in the header with three states:

| Symbol | Mode |
|---|---|
| 🖥️ | System — follows the visitor's OS preference |
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

Set a theme in the root homepage frontmatter:

```yaml
---
website: true
type: homepage
theme: nord
---
```

All themes ship with full dark and light variants.

| Theme | Value | Character |
|---|---|---|
| Obsidian (default) | `obsidian` | Catppuccin-inspired, warm purples |
| Omarchy | `omarchy` | Catppuccin Mocha/Latte, colorful headings |
| Nord | `nord` | Arctic blues, cool and desaturated |
| Gruvbox | `gruvbox` | Warm retro browns and yellows |
| Tokyo Night | `tokyo-night` | Deep navy with neon purple, pink, and cyan |
| Solarized | `solarized` | Ethan Schoonover's precision color palette |
| Paper | `paper` | Ink-on-paper minimal, sepia tones, no color gimmicks |

## Per-page theme override

Any individual page can override the site theme by adding `theme:` to its own frontmatter. This is useful for sections that need a distinct look.

```yaml
---
website: true
theme: gruvbox
---
```

## CSS files

| File | Purpose |
|---|---|
| `base.css` | Layout, typography, CSS variable tokens |
| `callouts-base.css` | Callout structure and icons |
| `code.css` | Code block styling with language labels and copy button |
| `theme-obsidian.css` | Default theme callout colours |
| `theme-omarchy.css` | Omarchy palette + callout colours |
| `theme-nord.css` | Nord palette + callout colours |
| `theme-gruvbox.css` | Gruvbox palette + callout colours |
| `theme-tokyo-night.css` | Tokyo Night palette + callout colours |
| `theme-solarized.css` | Solarized palette + callout colours |
| `theme-paper.css` | Paper palette + callout colours |

All CSS files are in `frontend/static/`.
