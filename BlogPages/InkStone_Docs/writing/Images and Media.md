---
website: true
title: Images and Media
date: 2026-01-01
summary: "Lightbox images, sliders, captions, banner images, video, and audio embeds."
---

## Single image — lightbox

```markdown
![[photo.jpg]]
```

Renders as a clickable image that opens a full-screen lightbox.

## Caption

```markdown
![[photo.jpg|A descriptive caption]]
```

The caption is shown below the image and as alt text.

## Slider

Multiple embeds **on the same line** become a swipeable slider:

```markdown
![[photo1.jpg]] ![[photo2.jpg]] ![[photo3.jpg]]
```

## Separate gallery

Multiple embeds **on separate lines** become a lightbox gallery (thumbnails, numbered, navigable):

```markdown
![[photo1.jpg]]
![[photo2.jpg]]
![[photo3.jpg]]
```

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

## Video

```markdown
![[demo.mp4]]
```

Renders a native `<video>` element with controls.

## Audio

```markdown
![[podcast.mp3]]
```

Renders a native `<audio>` element with controls.

## Attachment lookup order

When InkStone resolves `![[filename]]`, it searches in this order:

1. `_attachments/` folder next to the current `.md` file
2. Vault root `_attachments/` folder
3. `ATTACHMENTS_PATH` environment variable (if set)

> [!tip] Keep images close to their notes
> Put images in a `_attachments/` subfolder next to the markdown file. A post in `blog/` uses `blog/_attachments/`. This keeps attachments scoped and portable.
