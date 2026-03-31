---
tags:
  - website
  - homepage
title: Books
banner: "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1500&auto=format&fit=crop"
banner_x: 0.5
banner_y: 0.4
---

# Books list

## 📚 My Bookshelf

```dataview
TABLE WITHOUT ID
    status as Status,
    rows.file.link as Book
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
    join(list(publisher, publish)) as Publisher
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
    join(list(publisher, publish)) as Publisher
FROM #📚Book
WHERE !contains(file.path, "Templates")
SORT status DESC, file.ctime ASC
```
