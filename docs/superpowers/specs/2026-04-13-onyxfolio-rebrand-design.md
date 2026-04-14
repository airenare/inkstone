# OnyxFolio Rebrand — Design Spec

**Date:** 2026-04-13
**Status:** Approved

## Decision

Rename the project from **Obsidian Blog Engine** to **OnyxFolio**.

## Rationale

The original name ("Obsidian Blog Engine") was a placeholder. It has three problems:

1. **Implies official affiliation** with the Obsidian app — it isn't one
2. **Undersells scope** — the engine publishes any markdown vault as a full website, not just a blog
3. **Not a real brand** — generic, forgettable, no identity

**OnyxFolio** solves all three:

- **Onyx** — volcanic glass, a quiet nod to Obsidian without being derivative; rewards the curious
- **Folio** — a published collection of pages; also implies portfolio, which is a natural use case
- **Together** — sounds like a real product; distinctive, memorable, easy to spell and say

## Positioning

> A markdown publishing engine. Write in your vault, publish to the web.

OnyxFolio is built primarily as a personal tool, open-sourced freely. It works with any structured markdown vault but is optimised for Obsidian — wiki-links, callouts, dataview queries, frontmatter, and media embeds all render correctly. The Obsidian connection is a feature, not the identity.

## Scope of Changes

### Required
- [ ] Rename GitHub repo: `Obsidian-Blog-Engine` → `onyxfolio`
- [ ] Update `README.md` — new name, tagline, and project description
- [ ] Update `CLAUDE.md` — replace all references to "Obsidian Blog Engine"
- [ ] Update vault homepage `BlogPages/Test Website.md` — project name in content
- [ ] Search codebase for any hardcoded "Obsidian Blog Engine" strings and replace

### Optional (future)
- [ ] Register a domain (`onyxfolio.com` / `.dev` / `.app`)
- [ ] Design a logo mark (onyx stone / folio page motif)
- [ ] Add branding to the default theme (site footer attribution)

## Tagline Candidates

1. *"Your notes, published."* — minimal, universal
2. *"Markdown publishing for your vault."* — descriptive, technical
3. *"From vault to web."* — action-oriented, hints at the Obsidian workflow

## What Does Not Change

- All code, architecture, and functionality — this is a rename only
- The LICENSE, versioning scheme, and workflow rules
- The Obsidian-optimised feature set — that remains a selling point, just not the name
