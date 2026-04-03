---
website: true
tags:
  - generative-art
  - algorithms
  - simulation
date: 2026-03-15
title: Watercolor Algorithms
summary: Simulating the wet bleed of watercolor paint using diffusion equations and deliberate imprecision.
---

# Watercolor Algorithms

Watercolor is defined by what it refuses to do. It bleeds past boundaries. It dries unevenly. It leaves tide marks. Every attempt to simulate it perfectly produces something that looks like a very clean digital painting. The trick is to simulate the flaws.

## Wet-on-Wet Diffusion

The characteristic bleed of wet-on-wet watercolor comes from diffusion — pigment molecules spreading through the water already on the paper.

```python
def diffuse(grid, iterations=50, rate=0.2):
    for _ in range(iterations):
        new_grid = grid.copy()
        for y in range(1, grid.height - 1):
            for x in range(1, grid.width - 1):
                neighbors = (
                    grid[y-1][x] + grid[y+1][x] +
                    grid[y][x-1] + grid[y][x+1]
                )
                new_grid[y][x] = (
                    grid[y][x] * (1 - rate) +
                    neighbors * (rate / 4)
                )
        grid = new_grid
    return grid
```

## The Tide Mark Problem

Real watercolor leaves a darker edge as it dries — the tide mark. This happens because pigment particles are pushed to the boundary of the wet area by capillary flow and deposited there as the water evaporates.

To simulate it: increase pigment concentration near the wet/dry boundary.

> [!abstract] The Larger Point
> The best simulations of natural media are not physics simulations — they are aesthetic models. You are not simulating water molecules; you are simulating the *impression* of watercolor on a viewer. These are quite different problems.

## Connection to Other Gallery Posts

See also [[Recursive Landscapes]] for terrain generation and [[Neon Dreams]] for a completely different aesthetic built on similar procedural foundations.
