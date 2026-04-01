---
tags:
  - blog
labels:
  - python
  - automation
  - humour
date: 2026-02-10
title: Python Ate My Homework
summary: A cautionary tale about automating things that probably should not be automated.
---

# Python Ate My Homework

It started innocently enough. I wrote a script to organize my files. Then another to rename them. Then one to back them up. Then one to back up the backups.

By Tuesday I had forty-seven Python processes running and could not find a single file on my computer.

## Lessons Learned

- Automation is a force multiplier — for both good ideas and bad ones.
- Always test on a copy first.
- `shutil.rmtree` does exactly what it says.

## The Code That Did It

```python
import shutil
import os

# "clean up old stuff" -- what could go wrong
for folder in os.listdir("."):
    if os.path.isdir(folder):
        shutil.rmtree(folder)  # narrator: it went wrong
```

> [!warning] Don't run this
> This is a faithful reproduction of the original script. It will delete everything in the current directory.

## Recovery

Step 1: cry.

Step 2: remember you have a backup.

Step 3: realize the backup script also deleted the backups.

Step 4: start over with a blank slate and, apparently, a blog post.
