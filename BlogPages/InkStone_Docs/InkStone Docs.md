---
website: true
type: homepage
title: InkStone
language: en
show_search: true
default_theme: dark
icon: /static/InkStoneLogo.png
featured: true
---
# InkStone

![[InkStoneLogo.png|left 270]]
# Turn your Obsidian vault into a website.


**InkStone** is a Python/Flask server that reads your Obsidian vault and serves it as a live website. 

Add `website: true` to any note — it's published. 

Your folder structure becomes your URL structure. 

No build step, no export.

---

## Documentation
### [[Getting Started]] — Three ways to run InkStone and your first published note.
```dataview
LIST summary 
FROM "InkStone_Docs/getting-started"
WHERE type != "listing"
SORT priority ASC
```
---
### [[Writing]] — How to write and publish notes with InkStone.
```dataview
LIST summary 
FROM "InkStone_Docs/writing"
WHERE type != "listing"
SORT priority ASC
```
---
### [[Site Structure]] — How vault folders, file types, and frontmatter map to URLs and pages.
```dataview
LIST summary 
FROM "InkStone_Docs/site-structure"
WHERE type != "listing"
SORT priority ASC
```
---
### [[Features]] — Theming, search, multilingual, private notes, SEO, and more.
```dataview
LIST summary 
FROM "InkStone_Docs/features"
WHERE type != "listing"
SORT priority ASC
```
---
### [[Deployment]] — Local development, Docker, and production deployment options.
```dataview
LIST summary 
FROM "InkStone_Docs/deployment"
WHERE type != "listing"
SORT priority ASC
```

