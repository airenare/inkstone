---
website: true
title: Images and Media
date: 2026-05-21
summary: Lightbox images, sliders, float layout, centered figures, captions, banners, video, and audio.
featured: true
priority: 4
banner: /_attachments/desk.jpg
---


> [!Tip] Disclaimer
> Some media placement variants may not render correctly inside Obsidian, but they will appear as intended on the website. If needed, run InkStone locally to preview the final result.

## Single image — lightbox

```markdown
![[terminal.jpg]]
```
![[terminal.jpg]]
> Renders as a clickable image that opens a full-screen lightbox.

---
## Caption

```markdown
![[keyboard.jpg|The caption is shown below the image and as alt text.]]
```

![[keyboard.jpg|The caption is shown below the image and as alt text.]]

---
## Centered image

Use the `inline` flag to render a centered block figure that is not part of the lightbox:

```markdown
![[desk.jpg|inline]]
![[desk.jpg|inline 400]]
![[desk.jpg|inline 400 A caption]]
```

![[desk.jpg|inline]]
![[desk.jpg|inline 400]]
![[desk.jpg|inline 400 A caption]]

---
## Float image beside text

Use `left` or `right` to float an image so surrounding text wraps beside it:

```markdown
![[desk.jpg|left]]
![[desk.jpg|right 300]]
![[desk.jpg|left 300 A caption]]
```
![[desk.jpg|left]]

---

![[desk.jpg|right 300]]

---

![[desk.jpg|left 300 A caption]]

---

The image floats until the text runs out or until a horizontal rule `---` clears the float (until a better way found):

---

```markdown
![[desk.jpg|left 250]]
This paragraph wraps beside the image.

| ------------------------------------------------------------>

| ------------------------------------------------------------>

| ------------------------------------------------------------>

---

This paragraph is below the image at full width. ------------------------------------------------------------> 
```

![[desk.jpg|left 250]]
This paragraph wraps beside the image.

| ------------------------------------------------------------>

| ------------------------------------------------------------>

| ------------------------------------------------------------>

---

This paragraph is below the image at full width. ------------------------------------------------------------> 
> [! note]
> Float images do not open a lightbox when clicked.

---
## Slider

Multiple embeds **on the same line** become a swipeable slider:

```markdown
![[desk.jpg]] ![[keyboard.jpg]] ![[terminal.jpg]]
```

![[desk.jpg]] ![[keyboard.jpg]] ![[terminal.jpg]]

---
## Separate gallery

Multiple embeds **on separate lines** become a lightbox gallery (thumbnails, numbered, navigable):

```markdown
![[desk.jpg]]
![[keyboard.jpg]]
![[terminal.jpg]]
```

![[desk.jpg]]
![[keyboard.jpg]]
![[terminal.jpg]]

---
## Banner image

Set a banner with `banner:` in frontmatter. The value is the filename inside `_attachments/`:

```yaml
---
website: true
banner: cover.jpg
banner_y: 0.3
---
```

`banner_y` is the vertical focal point: `0.0` = top crop, `1.0` = bottom crop, `0.5` = centre (default).

---
## Video

```markdown
![[demo.mp4]]
```

Renders a native `<video>` element with controls.

---
## Audio

```markdown
![[podcast.mp3]]
```

Renders a native `<audio>` element with controls.

---
## Attachment lookup order

When InkStone resolves `![[filename]]`, it searches in this order:

1. `_attachments/` folder next to the current `.md` file
2. Vault root `_attachments/` folder
3. `ATTACHMENTS_PATH` environment variable (if set)

> [!tip] Keep images close to their notes
> Put images in a `_attachments/` subfolder next to the markdown file. A post in `blog/` uses `blog/_attachments/`. This keeps attachments scoped and portable.

---
## Flag reference

| Syntax | Effect |
|--------|--------|
| `![[img.jpg]]` | Lightbox gallery image |
| `![[img.jpg\|inline]]` | Centred block figure, not in lightbox |
| `![[img.jpg\|left]]` | Float left, text wraps right |
| `![[img.jpg\|right]]` | Float right, text wraps left |
| `![[img.jpg\|300]]` | Max-width 300 px |
| `![[img.jpg\|My Caption]]` | Caption below image |
| `![[img.jpg\|left 300 My Caption]]` | Combine flags freely |
