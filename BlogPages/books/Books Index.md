---
website: true
type: homepage
title: Books
banner: "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1500&auto=format&fit=crop"
banner_x: 0.5
banner_y: 0.4
---

# Books list

Each book below is a note in the vault. The tables are generated automatically via Dataview queries — adding a new book note with the `📚Book` tag makes it appear here instantly, no manual editing required.

## 📚 My Bookshelf

```dataview
TABLE WITHOUT ID
    rows.file.link as Book,
    status as Status
FROM #📚Book
WHERE !contains(file.path, "Templates")
GROUP BY status
SORT status
```

## 📊 Books on Data Science

```dataview
TABLE WITHOUT ID
    status as Status,
    "![|60](" + cover + ")" as Cover,
    link(file.link, title) as Title,
    author as Author,
    publish as Published,
	total as Pages
FROM #📚Book
WHERE !contains(file.path, "Templates") & contains(tags, "datascience")
SORT status DESC, file.ctime ASC
```

## List of all books

```dataview
TABLE WITHOUT ID
    status as Status,
    "![|60](" + cover + ")" as Cover,
    link(file.link, title) as Title,
    author as Author,
    publish as Published,
	total as Pages
FROM #📚Book
WHERE !contains(file.path, "Templates")
SORT status DESC, file.ctime ASC
```
