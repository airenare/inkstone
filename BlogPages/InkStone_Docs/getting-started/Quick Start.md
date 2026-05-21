---
website: true
title: Quick Start
date: 2026-01-01
summary: "Get InkStone running and publish your first note in under 5 minutes."
featured: true
priority: 0
---

> [!tip]+ Local (recommended for writing)
> ```bash
> git clone https://github.com/airenare/inkstone.git
> cd inkstone
> pip install -r requirements.txt
> VAULT_PATH=/path/to/your/vault python3 app.py
> ```
> Open [http://localhost:5000](http://localhost:5000).

> [!info]+ Docker
> ```bash
> docker run -p 8000:8000 \
>   -e VAULT_PATH=/vault \
>   -v /path/to/your/vault:/vault \
>   inkstone
> ```
> No Python installation required.

> [!note]+ Production
> See [[Production Deployment]] for Coolify, webhooks, and SSL setup.

---

## Your first note

Create any `.md` file in your vault and add this frontmatter:

```yaml
---
website: true
title: Hello World
date: 2026-01-01
---

This is my first published note.
```

> [!note] The server hot-reloads — save your note and refresh the browser. No restart needed.

The note is now live at `/hello-world`. That's it.

For the full frontmatter reference, see [[Frontmatter Reference]].
