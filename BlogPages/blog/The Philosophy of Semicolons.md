---
website: true
tags:
  - blog
  - programming
  - philosophy
  - languages
date: 2026-02-20
title: The Philosophy of Semicolons
summary: An investigation into why some languages use them, some don't, and why developers fight about it anyway.
---

# The Philosophy of Semicolons

The semicolon is the most philosophically loaded character in programming. A single `;` at the end of a line means: "I have completed a thought. I am certain. I am done."

Python disagrees entirely.

## The Two Schools

| School | Belief | Example languages |
|--------|--------|-------------------|
| Terminators | Statements must end with `;` | C, Java, Rust |
| Separators | Semicolons go *between* things | Pascal |
| Nihilists | Semicolons are unnecessary | Python, Ruby |
| Anarchists | Optional, do whatever | JavaScript |

## JavaScript: A Special Case

JavaScript chose violence. Semicolons are *technically* optional due to Automatic Semicolon Insertion (ASI), a feature so misunderstood it has its own acronym.

```javascript
// What you wrote:
const x = 1
const y = 2
[x, y].forEach(console.log)

// What JS parsed (ASI failed you here):
const x = 1
const y = 2[x, y].forEach(console.log)
// TypeError: Cannot read properties of undefined
```

## Conclusion

Semicolons are not about syntax. They are about *commitment*. When you type `;`, you are telling the compiler — and yourself — that you stand behind this statement.

Or you're just following the style guide. Either way.
