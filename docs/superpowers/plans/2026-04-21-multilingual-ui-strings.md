# Multilingual UI Strings & Language Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Translate nav section labels, site title, and fixed UI strings (Tags, Search, search page copy) based on current language; user-controlled translation lookup table in Obsidian; session-based language persistence that keeps users in their preferred language as they browse.

**Architecture:** Three complementary layers — (1) server-side: use section post titles for nav labels, store per-lang homepage titles in `WEBSITE_NAMES`, load `type: translations` vault notes into `UI_TRANSLATIONS`, deduplicate listing pages by current lang so RU listings link to RU posts; (2) template layer: inject `ui_strings` per request, apply throughout `base.html`, `search.html`, `not_translated.html`; (3) client-side: `sessionStorage`-based redirect preserves language preference within a browser session without persisting across windows.

**Tech Stack:** Python/Flask (`posts.py`, `app.py`), Jinja2 templates, vanilla JS (`sessionStorage`)

---

## File Map

| File | What changes |
|------|-------------|
| `posts.py` | Add `WEBSITE_NAMES`, `UI_TRANSLATIONS` globals; populate both in `load_posts()`; update `maybe_reload()` return |
| `app.py` | `inject_globals`: build nav sections as `(url, label)` tuples, inject `website_name` per-lang, inject `ui_strings`; listing route: deduplicate by lang |
| `frontend/templates/base.html` | Nav sections use `(url, label)` tuples; Tags/Search labels use `ui_strings`; lang toggle gains `data-lang`; add sessionStorage redirect script in `<head>`; add lang-click JS in body |
| `frontend/templates/search.html` | All English UI strings use `ui_strings.get(key, fallback)` |
| `frontend/templates/not_translated.html` | All English UI strings use `ui_strings.get(key, fallback)` |
| `BlogPages/_UI Translations_RU.md` | New demo fixture: `type: translations` note with Russian UI strings |
| `TODO.md` | Add "System theme" idea to Ideas section |
| `VERSION` | Bump to 1.25.0 |
| `README.md` | Mention translation lookup table feature |
| `BlogPages/Test Website.md` | Add translation table to features list |

---

## Task 1: Fix nav section labels — use SECTION_ROUTES titles

**The bug**: `nav_sections` is a list of URL strings. `base.html` derives labels with
`url.lstrip("/") | title`, so `/blog/ru` becomes "Blog/Ru" instead of "Блог".

**Fix**: Change `nav_sections` from a list of URL strings to a list of `(url, label)` tuples,
using the title from `SECTION_ROUTES[url]["post"]["title"]`.

**Files:**
- Modify: `app.py:79-93` (inject_globals, both top_sections branches)
- Modify: `frontend/templates/base.html:135` (nav loop)

- [ ] **Step 1: Update inject_globals() to yield (url, label) tuples**

In `app.py`, replace the two `top_sections` assignments in `inject_globals()` with:

```python
# Language-aware top-level nav sections — (url, label) tuples
if not multilingual or current_lang == post_store.DEFAULT_LANG:
    top_sections = sorted(
        (url, route["post"].get("title", url.lstrip("/").title()))
        for url, route in post_store.SECTION_ROUTES.items()
        if url not in ("/", f"/{current_lang}")
        and url.count("/") == 1
        and route.get("lang", post_store.DEFAULT_LANG) == post_store.DEFAULT_LANG
    )
else:
    # Non-default language: show sections at /{section}/{lang}
    top_sections = sorted(
        (url, route["post"].get("title", url.lstrip("/").title()))
        for url, route in post_store.SECTION_ROUTES.items()
        if route.get("lang") == current_lang
        and url.count("/") == 2
    )
```

- [ ] **Step 2: Update base.html nav loop**

In `frontend/templates/base.html`, replace the nav loop on line 135:

Old:
```jinja
{% for url in nav_sections %}<a href="{{ url }}"{% if request.path == url or request.path.startswith(url + '/') %} class="nav-active"{% endif %}>{{ url.lstrip("/") | title }}</a>{% endfor %}
```

New:
```jinja
{% for url, label in nav_sections %}<a href="{{ url }}"{% if request.path == url or request.path.startswith(url + '/') %} class="nav-active"{% endif %}>{{ label }}</a>{% endfor %}
```

- [ ] **Step 3: Manual smoke test**

Start the server with `conda activate conda312 && python3 app.py` from the InkStone directory.
Visit `http://localhost:8000/ru` — nav should show "Блог" (not "Blog/Ru").
Visit `http://localhost:8000/` — nav should show "Blog" (title from Blog Index.md).

- [ ] **Step 4: Commit**

```bash
git add app.py frontend/templates/base.html
git commit -m "fix: nav section labels use SECTION_ROUTES titles instead of URL-derived strings"
```

---

## Task 2: Per-language site title (WEBSITE_NAMES)

**The problem**: `WEBSITE_NAME` is only set from the default-lang root homepage. When browsing
`/ru`, `website_name` still shows "InkStone" instead of "Тестовый сайт".

**Fix**: Add `WEBSITE_NAMES: dict` global in `posts.py` that maps `lang → title` for all
root homepages. `inject_globals()` uses `WEBSITE_NAMES.get(current_lang)` with `WEBSITE_NAME`
as fallback.

**Files:**
- Modify: `posts.py` (add global, populate in `load_posts()`, update `maybe_reload()`)
- Modify: `app.py:inject_globals()`

- [ ] **Step 1: Add WEBSITE_NAMES global to posts.py**

In `posts.py`, after the `WEBSITE_NAME = "My Blog"` line (line 19), add:

```python
# lang_code → site title for that language's root homepage
WEBSITE_NAMES: dict = {}
```

- [ ] **Step 2: Populate WEBSITE_NAMES in load_posts()**

In `load_posts()`, add `website_names = {}` to the local variable initializations at the top
of the function (alongside `website_name = "My Blog"` etc.).

Then in the `elif is_homepage:` block (around line 679), change:

```python
elif is_homepage:
    if section == "" and lang == default_lang:
        website_name = title
        show_search = bool(metadata.get("show_search"))
        show_tags = bool(metadata.get("show_tags"))
        site_theme = _resolve_theme(metadata.get("theme"), filepath)
        social_links = []
        for key, network in _SOCIAL_REGISTRY.items():
            url = metadata.get(key)
            if not url or not isinstance(url, str):
                continue
            url = url.strip()
            if not url.startswith("http"):
                continue
            try:
                handle = network["handle"](url)
            except Exception:
                handle = url
            social_links.append({
                "name": network["name"],
                "icon": network["icon"],
                "handle": handle,
                "url": url,
                "rel": network["rel"],
            })
    section_routes[section_url] = {
        "type": "homepage",
        "post": post_data,
        "lang": lang,
    }
```

to:

```python
elif is_homepage:
    if section == "":
        website_names[lang] = title
    if section == "" and lang == default_lang:
        website_name = title
        show_search = bool(metadata.get("show_search"))
        show_tags = bool(metadata.get("show_tags"))
        site_theme = _resolve_theme(metadata.get("theme"), filepath)
        social_links = []
        for key, network in _SOCIAL_REGISTRY.items():
            url = metadata.get(key)
            if not url or not isinstance(url, str):
                continue
            url = url.strip()
            if not url.startswith("http"):
                continue
            try:
                handle = network["handle"](url)
            except Exception:
                handle = url
            social_links.append({
                "name": network["name"],
                "icon": network["icon"],
                "handle": handle,
                "url": url,
                "rel": network["rel"],
            })
    section_routes[section_url] = {
        "type": "homepage",
        "post": post_data,
        "lang": lang,
    }
```

- [ ] **Step 3: Add website_names to load_posts() return tuple**

Change the `return` at the end of `load_posts()` (line 801):

Old:
```python
return (all_posts, section_routes, website_name, site_theme, dataview_index,
        private_routes, menu_posts, show_search, show_tags, all_tags,
        icon_overrides, default_lang, available_langs, lang_groups,
        social_links)
```

New:
```python
return (all_posts, section_routes, website_name, site_theme, dataview_index,
        private_routes, menu_posts, show_search, show_tags, all_tags,
        icon_overrides, default_lang, available_langs, lang_groups,
        social_links, website_names)
```

- [ ] **Step 4: Add WEBSITE_NAMES to maybe_reload() global declaration and unpack**

In `maybe_reload()`, add `WEBSITE_NAMES` to the global declaration line:

```python
global ALL_POSTS, SECTION_ROUTES, WEBSITE_NAME, WEBSITE_NAMES, SITE_THEME, \
    DATAVIEW_INDEX, PRIVATE_ROUTES, MENU_POSTS, SHOW_SEARCH, SHOW_TAGS, \
    ALL_TAGS, ICON_OVERRIDES, DEFAULT_LANG, AVAILABLE_LANGS, LANG_GROUPS, \
    SOCIAL_LINKS, LAST_SCAN_TIME, _last_check_time
```

Change the unpack line:

Old:
```python
(ALL_POSTS, SECTION_ROUTES, WEBSITE_NAME, SITE_THEME,
 DATAVIEW_INDEX, PRIVATE_ROUTES, MENU_POSTS,
 SHOW_SEARCH, SHOW_TAGS, ALL_TAGS, ICON_OVERRIDES,
 DEFAULT_LANG, AVAILABLE_LANGS, LANG_GROUPS,
 SOCIAL_LINKS) = load_posts()
```

New:
```python
(ALL_POSTS, SECTION_ROUTES, WEBSITE_NAME, SITE_THEME,
 DATAVIEW_INDEX, PRIVATE_ROUTES, MENU_POSTS,
 SHOW_SEARCH, SHOW_TAGS, ALL_TAGS, ICON_OVERRIDES,
 DEFAULT_LANG, AVAILABLE_LANGS, LANG_GROUPS,
 SOCIAL_LINKS, WEBSITE_NAMES) = load_posts()
```

- [ ] **Step 5: Update app.py initial load unpack**

In `app.py` at the bottom (the `if __name__ == "__main__":` block), add `post_store.WEBSITE_NAMES` to the unpack:

```python
(
    post_store.ALL_POSTS,
    post_store.SECTION_ROUTES,
    post_store.WEBSITE_NAME,
    post_store.SITE_THEME,
    post_store.DATAVIEW_INDEX,
    post_store.PRIVATE_ROUTES,
    post_store.MENU_POSTS,
    post_store.SHOW_SEARCH,
    post_store.SHOW_TAGS,
    post_store.ALL_TAGS,
    post_store.ICON_OVERRIDES,
    post_store.DEFAULT_LANG,
    post_store.AVAILABLE_LANGS,
    post_store.LANG_GROUPS,
    post_store.SOCIAL_LINKS,
    post_store.WEBSITE_NAMES,
) = post_store.load_posts()
```

- [ ] **Step 6: Inject per-lang website_name in inject_globals()**

In `app.py`'s `inject_globals()`, change the `"website_name"` line in the return dict:

Old:
```python
"website_name": post_store.WEBSITE_NAME,
```

New:
```python
"website_name": post_store.WEBSITE_NAMES.get(current_lang) or post_store.WEBSITE_NAME,
```

- [ ] **Step 7: Manual smoke test**

Visit `http://localhost:8000/ru` — the header H1 should show "Тестовый сайт" (or whatever
title the RU homepage has). Visit `http://localhost:8000/` — should still show "InkStone".

- [ ] **Step 8: Commit**

```bash
git add posts.py app.py
git commit -m "feat: per-language site title via WEBSITE_NAMES dict"
```

---

## Task 3: Translation lookup table — load `type: translations` vault notes

**Design**: User creates a vault note (anywhere, no `website: true` needed) with:
```yaml
---
type: translations
lang: ru
strings:
  Search: Поиск
  Tags: Теги
  "All tags": Все теги
  ...
---
```

`posts.py` detects these during pass 1, builds `UI_TRANSLATIONS: dict[str, dict]`
= `{"ru": {"Search": "Поиск", ...}}`.

**Files:**
- Modify: `posts.py` (add `UI_TRANSLATIONS` global, detect+load during pass 1, add to return)

- [ ] **Step 1: Add UI_TRANSLATIONS global to posts.py**

After the `WEBSITE_NAMES: dict = {}` line, add:

```python
# lang_code → {key: translated_string} — loaded from `type: translations` vault notes
UI_TRANSLATIONS: dict = {}
```

- [ ] **Step 2: Load translation notes in load_posts() pass 1**

Add `ui_translations = {}` to the local variable initializations at the top of `load_posts()`.

In pass 1, inside the `for root, dirs, files in os.walk(VAULT_PATH)` loop, after reading
`metadata` and `md` from the file, add detection logic for translation notes.

The existing code checks `if not metadata.get("website"): continue` to skip non-published notes.
Translation notes deliberately don't have `website: true`, so add this **before** that check:

```python
# Detect translation-table notes (don't need website: true)
if (metadata.get("type") or "").strip().lower() == "translations":
    note_lang = str(metadata.get("lang") or "").strip().lower()
    strings_raw = metadata.get("strings")
    if note_lang and isinstance(strings_raw, dict):
        ui_translations[note_lang] = {
            str(k): str(v) for k, v in strings_raw.items()
        }
    continue
```

The `continue` ensures the note is not processed further as a publishable post.

- [ ] **Step 3: Add ui_translations to load_posts() return tuple**

Change the return:

```python
return (all_posts, section_routes, website_name, site_theme, dataview_index,
        private_routes, menu_posts, show_search, show_tags, all_tags,
        icon_overrides, default_lang, available_langs, lang_groups,
        social_links, website_names, ui_translations)
```

- [ ] **Step 4: Add UI_TRANSLATIONS to maybe_reload() global declaration and unpack**

In `maybe_reload()`, add `UI_TRANSLATIONS` to the global declaration:

```python
global ALL_POSTS, SECTION_ROUTES, WEBSITE_NAME, WEBSITE_NAMES, SITE_THEME, \
    DATAVIEW_INDEX, PRIVATE_ROUTES, MENU_POSTS, SHOW_SEARCH, SHOW_TAGS, \
    ALL_TAGS, ICON_OVERRIDES, DEFAULT_LANG, AVAILABLE_LANGS, LANG_GROUPS, \
    SOCIAL_LINKS, UI_TRANSLATIONS, LAST_SCAN_TIME, _last_check_time
```

Change the unpack:

```python
(ALL_POSTS, SECTION_ROUTES, WEBSITE_NAME, SITE_THEME,
 DATAVIEW_INDEX, PRIVATE_ROUTES, MENU_POSTS,
 SHOW_SEARCH, SHOW_TAGS, ALL_TAGS, ICON_OVERRIDES,
 DEFAULT_LANG, AVAILABLE_LANGS, LANG_GROUPS,
 SOCIAL_LINKS, WEBSITE_NAMES, UI_TRANSLATIONS) = load_posts()
```

- [ ] **Step 5: Update app.py initial load unpack**

Add `post_store.UI_TRANSLATIONS` to the `__main__` unpack block:

```python
(
    post_store.ALL_POSTS,
    post_store.SECTION_ROUTES,
    post_store.WEBSITE_NAME,
    post_store.SITE_THEME,
    post_store.DATAVIEW_INDEX,
    post_store.PRIVATE_ROUTES,
    post_store.MENU_POSTS,
    post_store.SHOW_SEARCH,
    post_store.SHOW_TAGS,
    post_store.ALL_TAGS,
    post_store.ICON_OVERRIDES,
    post_store.DEFAULT_LANG,
    post_store.AVAILABLE_LANGS,
    post_store.LANG_GROUPS,
    post_store.SOCIAL_LINKS,
    post_store.WEBSITE_NAMES,
    post_store.UI_TRANSLATIONS,
) = post_store.load_posts()
```

- [ ] **Step 6: Create demo translation fixture**

Create `BlogPages/_UI Translations_RU.md`:

```markdown
---
type: translations
lang: ru
strings:
  Search: Поиск
  Tags: Теги
  "All tags": Все теги
  "No results": Нет результатов
  for: для
  result: Результат
  results: Результаты
  "tagged": с тегом
  "min read": мин чтения
  "Not yet translated": Ещё не переведено
  "Translation unavailable": Перевод недоступен
  "This page is not yet available in": Эта страница ещё не доступна на языке
  "Read it in": Читать на
---
```

The filename starts with `_` to make it sort first in Obsidian and visually distinguish it
as a metadata file; the `type: translations` frontmatter prevents it from being published.

- [ ] **Step 7: Commit**

```bash
git add posts.py BlogPages/_UI\ Translations_RU.md
git commit -m "feat: load type:translations vault notes into UI_TRANSLATIONS lookup table"
```

---

## Task 4: Inject ui_strings and apply throughout templates

**Files:**
- Modify: `app.py:inject_globals()`
- Modify: `frontend/templates/base.html` (Tags, Search nav labels)
- Modify: `frontend/templates/search.html` (all UI strings)
- Modify: `frontend/templates/not_translated.html` (all UI strings)

- [ ] **Step 1: Inject ui_strings in inject_globals()**

In `app.py`'s `inject_globals()`, add to the return dict:

```python
"ui_strings": post_store.UI_TRANSLATIONS.get(current_lang, {}),
```

- [ ] **Step 2: Apply translations in base.html — Tags and Search nav links**

In `base.html` line 135, change the Tags and Search link labels:

Old (within the nav string):
```jinja
{% if show_tags %}<a href="/tags"{% if request.path == '/tags' %} class="nav-active"{% endif %}>Tags</a>{% endif %}{% if show_search %}<a href="/search"{% if request.path == '/search' %} class="nav-active"{% endif %}>Search</a>{% endif %}
```

New:
```jinja
{% if show_tags %}<a href="/tags"{% if request.path == '/tags' %} class="nav-active"{% endif %}>{{ ui_strings.get('Tags', 'Tags') }}</a>{% endif %}{% if show_search %}<a href="/search"{% if request.path == '/search' %} class="nav-active"{% endif %}>{{ ui_strings.get('Search', 'Search') }}</a>{% endif %}
```

- [ ] **Step 3: Apply translations in search.html**

Replace the entire content of `frontend/templates/search.html` with:

```jinja
{% extends "base.html" %}

{% block content %}

<h2>{{ ui_strings.get('Search', 'Search') }}</h2>

<form class="search-form" action="/search">

<input type="text" name="q" value="{{ query }}" placeholder="{{ ui_strings.get('Search', 'Search') }}…">

{% if all_tags %}
<select name="tag">
<option value="">{{ ui_strings.get('All tags', 'All tags') }}</option>
{% for t in all_tags %}
<option value="{{ t }}"{% if t == selected_tag %} selected{% endif %}>{{ t }}</option>
{% endfor %}
</select>
{% endif %}

<button type="submit">{{ ui_strings.get('Search', 'Search') }}</button>

</form>

{% if (query or selected_tag) and not posts %}
<p class="search-empty">{{ ui_strings.get('No results', 'No results') }}{% if query %} {{ ui_strings.get('for', 'for') }} <strong>{{ query }}</strong>{% endif %}{% if selected_tag %} {{ ui_strings.get('tagged', 'tagged') }} <span class="tag-badge">{{ selected_tag }}</span>{% endif %}.</p>
{% endif %}

{% if posts %}

{% set count = posts | length %}
<h3>{{ count }} {{ ui_strings.get('results' if count != 1 else 'result', 'result' if count == 1 else 'results') }}{% if selected_tag %} {{ ui_strings.get('tagged', 'tagged') }} <span class="tag-badge">{{ selected_tag }}</span>{% endif %}</h3>

<ul class="search-results">

{% for post in posts %}

<li class="search-result">
<h4><a href="{{ post.url_path }}">{{ post.highlighted_title | safe }}</a></h4>
<div class="post-meta">
{% if post.date %}{{ post.date.strftime("%B %d, %Y") }}{% endif %}
{% if post.reading_time %} · {{ post.reading_time }} {{ ui_strings.get('min read', 'min read') }}{% endif %}
</div>
<p class="post-summary">{{ post.highlighted_summary | safe }}</p>
</li>

{% endfor %}

</ul>

{% endif %}

{% endblock %}
```

- [ ] **Step 4: Apply translations in not_translated.html**

Replace the content of `frontend/templates/not_translated.html` with:

```jinja
{% extends "base.html" %}

{% block content %}

<article class="private-note">

<h1>{{ ui_strings.get('Not yet translated', 'Not yet translated') }}</h1>

<div class="private-badge">
<span class="private-lock">🌐</span>
<span>{{ ui_strings.get('Translation unavailable', 'Translation unavailable') }}</span>
</div>

<p class="private-message">
{{ ui_strings.get('This page is not yet available in', 'This page is not yet available in') }} <strong>{{ default_lang | upper }}</strong>.
</p>

{% if lang_variants %}
<p class="private-message">{{ ui_strings.get('Read it in', 'Read it in') }}:</p>
<ul class="not-translated-langs">
{% for lang_code, lang_url in lang_variants.items() %}
<li><a href="{{ lang_url }}">{{ lang_code | upper }} →</a></li>
{% endfor %}
</ul>
{% endif %}

</article>

{% endblock %}
```

- [ ] **Step 5: Manual smoke test**

Start the server. Visit `http://localhost:8000/ru` — nav should show "Теги" and "Поиск"
(assuming `show_tags: true` and `show_search: true` on the root homepage).
Visit `http://localhost:8000/search` — page header and button should still say "Search"
(default lang, no translation applied). Visit `http://localhost:8000/ru` then click Поиск
link — search page should show "Поиск" heading and "Все теги" in the dropdown.

Wait — the search page is at `/search`, which `_detect_current_lang` maps to DEFAULT_LANG,
so `ui_strings` is `{}`. The translation only applies from `/ru` nav. This is expected.

- [ ] **Step 6: Commit**

```bash
git add app.py frontend/templates/base.html frontend/templates/search.html frontend/templates/not_translated.html
git commit -m "feat: apply ui_strings translations to nav labels and search/not-translated templates"
```

---

## Task 5: Language-aware listing deduplication

**The problem**: Section listings gather all posts in a section regardless of language. `/blog`
shows both `/blog/post-slug` (EN) and `/blog/post-slug/ru` (RU) as separate entries. `/blog/ru`
should show RU posts, falling back to EN for posts without RU versions.

**Fix**: After gathering `section_posts`, group by `base_url_path` and pick the version
matching the listing's language, falling back to `DEFAULT_LANG`.

**Files:**
- Modify: `app.py:serve()` listing branch (around line 377)

- [ ] **Step 1: Add deduplication logic to the listing route**

In `app.py`'s `serve()` function, inside the `if route["type"] == "listing":` branch,
right after `section_posts` is assembled (after the `if section:` / `else:` block):

Old (after section_posts is built):
```python
section_posts.sort(
    key=lambda x: x["date"] or datetime.min, reverse=True
)
```

New — insert the deduplication before the sort:

```python
# Deduplicate: for each logical post, show the version matching the
# listing's language. Falls back to DEFAULT_LANG if no match.
_route_lang = route.get("lang", post_store.DEFAULT_LANG)
_by_base = {}
for _p in section_posts:
    _base = _p.get("base_url_path") or _p["url_path"]
    _by_base.setdefault(_base, {})[_p.get("lang", post_store.DEFAULT_LANG)] = _p
_deduped = []
for _base, _versions in _by_base.items():
    if _route_lang in _versions:
        _deduped.append(_versions[_route_lang])
    elif post_store.DEFAULT_LANG in _versions:
        _deduped.append(_versions[post_store.DEFAULT_LANG])
    else:
        _deduped.append(next(iter(_versions.values())))
section_posts = _deduped

section_posts.sort(
    key=lambda x: x["date"] or datetime.min, reverse=True
)
```

- [ ] **Step 2: Manual smoke test**

Visit `http://localhost:8000/blog` — should show EN posts only (no "Python Ate My Homework"
appearing twice). Visit `http://localhost:8000/blog/ru` — should show the RU version of
"Python Ate My Homework" (title in Russian, linking to `/blog/python-ate-my-homework/ru`),
with EN-only posts also showing as fallbacks.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "fix: deduplicate listing posts by lang — RU listings show RU posts, EN listings show EN only"
```

---

## Task 6: Session language persistence (client-side)

**Design**: `sessionStorage.preferredLang` saves the user's explicit language choice.
On every page load, a script checks if the preferred lang has an `hreflang` alternate for
the current page and redirects if needed. Clicking the lang toggle saves the new preference.
Choosing the default lang (EN) clears any redirect behavior for that session.

**Files:**
- Modify: `frontend/templates/base.html`

- [ ] **Step 1: Add data-lang attribute to lang toggle links**

In `base.html` line 138, the lang-toggle `<a>` elements:

Old:
```jinja
<a href="{{ lu }}" class="lang-option{% if lc == current_lang %} lang-active{% endif %}" aria-label="{{ lc|upper }}">{{ lc|upper }}</a>
```

New:
```jinja
<a href="{{ lu }}" class="lang-option{% if lc == current_lang %} lang-active{% endif %}" aria-label="{{ lc|upper }}" data-lang="{{ lc }}">{{ lc|upper }}</a>
```

- [ ] **Step 2: Add sessionStorage redirect script in <head>**

In `base.html`, after the hreflang `{% if lang_variants %}` block (after line 25, the
closing `{% endif %}`), add:

```html
<script>
(function() {
    var pref = sessionStorage.getItem("preferredLang");
    if (!pref) return;
    var cur = "{{ current_lang }}";
    if (cur === pref) return;
    var alt = document.querySelector("link[rel=\"alternate\"][hreflang=\"" + pref + "\"]");
    if (alt) window.location.replace(alt.href);
})();
</script>
```

This runs synchronously in the `<head>`, after the hreflang `<link>` elements have been
parsed, so `querySelector` finds them. Pages without a `preferred` language alternate
simply have no matching link, so no redirect happens.

- [ ] **Step 3: Add lang-click handler in body JS**

In `base.html`, at the end of the last `<script>` block (the theme toggle script, just
before `</script>` on the theme script's closing line), add:

```javascript
document.querySelectorAll(".lang-option").forEach(function(a) {
    a.addEventListener("click", function() {
        sessionStorage.setItem("preferredLang", this.dataset.lang);
    });
});
```

Actually, add it as a separate small `<script>` block just before `</body>` to keep
scripts organized:

```html
<script>
document.querySelectorAll(".lang-option").forEach(function(a) {
    a.addEventListener("click", function() {
        sessionStorage.setItem("preferredLang", this.dataset.lang);
    });
});
</script>
```

- [ ] **Step 4: Manual smoke test**

1. Open `http://localhost:8000/` in a fresh tab (no sessionStorage).
2. Click RU in the lang toggle → redirects to `/ru`. Check DevTools > Application >
   Session Storage — should show `preferredLang = ru`.
3. Manually navigate to `http://localhost:8000/blog` — should auto-redirect to
   `/blog/ru` (because hreflang for `ru` points to `/blog/ru`).
4. Navigate to `http://localhost:8000/blog/the-philosophy-of-semicolons` (EN-only post,
   no hreflang for `ru`) — should stay on EN page, no redirect.
5. Click EN in the lang toggle → sessionStorage `preferredLang = en`. Navigate to
   `/blog/ru` — should auto-redirect to `/blog` (hreflang for `en` is `/blog`).

- [ ] **Step 5: Commit**

```bash
git add frontend/templates/base.html
git commit -m "feat: session language persistence via sessionStorage redirect"
```

---

## Task 7: Add system theme option to TODO.md

**Files:**
- Modify: `TODO.md` (Ideas section)

- [ ] **Step 1: Add to Ideas section**

In `TODO.md`, add to the **Ideas** section:

```markdown
- **System theme option** — add a third theme selector state "System" that follows the
  OS/browser `prefers-color-scheme` setting (dark or light). Currently the toggle is a
  binary dark/light switch; System would be the default before the user makes an explicit
  choice. Implementation: read `window.matchMedia("(prefers-color-scheme: light)").matches`
  when no `localStorage.theme` is set; add a third button state; remove the saved
  localStorage entry when "System" is selected to re-enable following OS changes.
```

- [ ] **Step 2: Commit**

```bash
git add TODO.md
git commit -m "docs: add system theme option to Ideas backlog"
```

---

## Task 8: Version bump and docs sync

**Files:**
- Modify: `VERSION`
- Modify: `README.md`
- Modify: `BlogPages/Test Website.md`

- [ ] **Step 1: Bump VERSION to 1.25.0**

```
1.25.0
```

- [ ] **Step 2: Update README.md**

In `README.md`, find the multilingual bullet and update or add a note about the translation
lookup table. Add something like:

```markdown
- **UI string translations** — create a `type: translations` vault note with a `strings:`
  YAML dict to translate fixed UI labels (Tags, Search, search page copy) into any language.
  No template editing required.
```

- [ ] **Step 3: Update BlogPages/Test Website.md features list**

Add a bullet point after the multilingual line:

```markdown
- **UI string translations** — create a `type: translations` note (no `website: true` needed) 
  with `lang:` and a `strings:` dict to translate fixed UI labels (Tags, Search, nav items) 
  into any language without editing templates
```

- [ ] **Step 4: Commit, tag, push**

```bash
git add VERSION README.md BlogPages/Test\ Website.md
git commit -m "chore: bump version to 1.25.0"
git tag v1.25.0
git push && git push origin v1.25.0
```

---

## Self-Review

**Spec coverage check:**

| Requirement | Covered in |
|-------------|-----------|
| Site title changes per language | Task 2 |
| Nav section labels translate (Blog→Блог) | Task 1 |
| Menu post labels translate (About→Обо мне) | Already works — `lang_menu` uses RU page's title |
| Tags→Теги, Search→Поиск in nav | Task 4 |
| Search UI strings (All tags, No results, etc.) | Task 4 |
| User creates translation note in Obsidian | Task 3 |
| Translation note not rendered on website | Task 3 (`continue` after detecting type:translations) |
| Language persists when clicking links within session | Task 5 (server-side) + Task 6 (client-side) |
| NOT persisted across windows/sessions | Task 6 (sessionStorage, not localStorage) |
| Add System theme to TODO | Task 7 |

**Placeholder scan**: No TBD, TODO, or fill-in-later items found.

**Type consistency**: All references to `WEBSITE_NAMES`, `UI_TRANSLATIONS`, `ui_strings`, and nav section tuples are consistent across tasks.

**Edge cases verified in design:**
- EN-only vault (no multilingual): `UI_TRANSLATIONS = {}`, `WEBSITE_NAMES` has only `"en"` key,
  no sessionStorage script fires (hreflang block only renders with `lang_variants|length > 1`).
  Zero impact on single-language sites.
- Translation note without `lang:` or with empty `strings:`: detected and skipped gracefully.
- Page with no hreflang alternates (e.g. `/search`, `/tags`): sessionStorage redirect finds no
  matching `<link>` element, no redirect — correct behavior.
- User clicks EN (default lang) in toggle: saves `preferredLang=en`; subsequent pages with
  `current_lang=en` hit the `cur === pref` early return — no redirects.
