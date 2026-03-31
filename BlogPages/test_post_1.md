---
tags:
  - blog
date: 2026-01-15
title: Test Post One
---

# Test Post One

This post covers text formatting, tables, code blocks, callouts, and checkboxes. See also [[Test Post Two]] for media and more callout types.

---

## Text Formatting

Normal paragraph with **bold text**, *italic text*, and ***bold italic***. You can also use ~~strikethrough~~ and `inline code`.

> This is a regular blockquote.
> It can span multiple lines.

---

## Code Blocks

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

for person in ["Alice", "Bob", "Charlie"]:
    print(greet(person))
```

```bash
# Install dependencies and run
pip install -r requirements.txt
python app.py
```

---

## Tables

| Feature       | Status  | Notes                  |
|---------------|---------|------------------------|
| Wiki-links    | Done    | Converts `[[Title]]`   |
| Callouts      | Done    | All Obsidian types     |
| Checkboxes    | Done    | Nested supported       |
| Media         | Done    | Lightbox + slider      |
| Search        | Done    | Title and content      |

---

## Callouts

> [!note] A Note
> This is a note callout. Use it for supplementary information that is helpful but not critical.

> [!warning] Watch Out
> This is a warning callout. Use it to flag something that might cause problems if ignored.

---

## Checkboxes

- [x] Flask routes working
- [x] Markdown pipeline implemented
- [ ] Add RSS feed
- [ ] Add pagination
    - [ ] Determine page size
    - [x] Design URL structure (`/page/2`)
    - [ ] Update index template

---

## Single Image

![[test_image_1.png]]

---

## Image Gallery

Two images below form a thumbnail gallery. Click either to open the lightbox.

![[test_image_1.png]]
![[test_image_2.png]]
