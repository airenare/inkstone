---
tags:
  - blog
date: 2026-03-05
title: Pixel Sunset
summary: What happens when you reduce a photograph to 64x64 pixels and then blow it back up to poster size.
---

# Pixel Sunset

Downsampling is a kind of translation. You take something dense with detail and ask: if you could only keep 4096 numbers, which ones would you keep?

The answer, it turns out, is surprisingly beautiful.

## The Technique

1. Take a photograph (preferably a sunset — the color gradients are forgiving)
2. Resize to 64×64 pixels using nearest-neighbor interpolation (no blurring)
3. Scale back up to 2048×2048 using nearest-neighbor again
4. Print at A2

The result is a mosaic of hard-edged color blocks that, from across a room, resolve back into the original image.

## Why It Works

Human vision performs its own upsampling. We are very good at inferring smooth shapes from discontinuous signals. The pixelated image is just an explicit version of what our visual cortex does constantly.

> [!info] Nearest-Neighbor vs Bilinear
> Bilinear interpolation blends adjacent pixels when scaling. Nearest-neighbor snaps to the closest pixel value. For this effect, always use nearest-neighbor — the blocky edges are the entire point.
