---
tags:
  - blog
date: 2026-03-01
title: Neon Dreams
summary: A series of procedurally generated cityscapes rendered at 2am for no particular reason.
---

# Neon Dreams

Every city looks better at 2am when rendered in 32 colors and viewed through a rain-slicked window. This series started as a shader experiment and became something I kept running long after the experiment ended.

## Process

The scenes are built from a handful of primitives — rectangles, gradients, noise fields — assembled by a script that has never once produced the same image twice.

```python
import random
import math

def neon_rect(canvas, x, y, w, h):
    hue = random.randint(180, 320)  # cyan to magenta range
    glow = math.sin(y * 0.05) * 0.5 + 0.5
    canvas.draw_rect(x, y, w, h, hsl(hue, 1.0, 0.5 * glow))
```

> [!note] On Randomness
> Each image is seeded with the current timestamp, so they're reproducible if you know when they were made. I don't keep records of when I run the script.

## Selected Outputs

The images in this post are placeholder solids. The real ones are on a hard drive somewhere, waiting.
