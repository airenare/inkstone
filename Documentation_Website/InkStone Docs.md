---
website: true
type: homepage
title: InkStone
language: en
show_search: true
default_theme: dark
icon: _attachments/InkStoneLogo.png
summary: Homepage of the InkStone documentation website.
social_links:
  - https://github.com/airenare
---
# InkStone

![[InkStoneLogo.png|left 270]]
# Turn your Obsidian vault into a website.


**InkStone** is a Python/Flask server that reads your Obsidian vault and serves it as a live website. 

Add `website: true` to any note. It's published. 

Your folder structure becomes your URL structure. 

No build step, no export.

---

## Documentation
### [[Get Started]]: Three ways to run InkStone and your first published note.
```dataview
LIST summary 
FROM "getting-started"
WHERE type != "listing"
SORT priority ASC
```
---
### [[Writing]]: How to write and publish notes with InkStone.
```dataview
LIST summary 
FROM "writing"
WHERE type != "listing"
SORT priority ASC
```
---
### [[Site Structure]]: How vault folders, file types, and frontmatter map to URLs and pages.
```dataview
LIST summary 
FROM "site-structure"
WHERE type != "listing"
SORT priority ASC
```
---
### [[Features]]: Theming, search, multilingual, private notes, SEO, and more.
```dataview
LIST summary 
FROM "features"
WHERE type != "listing"
SORT priority ASC
```
---
### [[Deployment]]: Local development, Docker, and production deployment options.
```dataview
LIST summary 
FROM "deployment"
WHERE type != "listing"
SORT priority ASC
```

