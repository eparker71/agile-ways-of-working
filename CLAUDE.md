# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static site of printable agile facilitation tools: A3 landscape boards (each as `.html` + `.svg`), A4 facilitator guides, two cheat sheets, a home page and a role guide. No build system, dependencies or tests; Python 3 standard library only. Published with GitHub Pages (legacy build from `main`, repo root, `.nojekyll`) at https://eparker71.github.io/agile-ways-of-working/. Pushing to `main` deploys.

## Commands

```sh
python3 _generator/build_boards.py   # every generated board → <slug>.svg + <slug>.html
python3 _generator/build_guides.py   # every generated guide → facilitator-guide-<slug>.html + .docx
python3 _generator/build_roles.py    # start-here-by-role.html + role tags/filter in index.html
python3 _generator/build_glossary.py # glossary.html (imports TOOLS from build_roles.py)
python3 _generator/build_antipatterns.py # anti-patterns.html (ANTIPATTERNS list; build_boards.py reads it for the Spotter board)
```

Each script regenerates everything it owns (there's no per-file target). They're idempotent.

## Generated vs hand-written

Never edit generated files directly; edit the script and re-run.

- **Generated:** every board except Marginal Gains, every `facilitator-guide-*.html` except Marginal Gains, `start-here-by-role.html`, `glossary.html`, `anti-patterns.html`.
- **Hand-written:** `marginal-gains-workshop-board.{svg,html}`, `facilitator-guide-marginal-gains.html`, `scrum-master-agile-coach-cheat-sheet.html`, `jira-cheat-sheet.html`, `make-it-yours.html`, `index.html`, `LICENSE.md`.
- **Brand:** colours, fonts and the credit line (© author · CC BY 4.0 · site) live in `_generator/brand.py` and are imported by all four generators. The hand-written pages carry the same values by hand, so update them too when rebranding.
- `index.html` is hand-written **except** the regions `build_roles.py` maintains: the `<!-- roles:… -->` / `/* roles:css */` blocks and each card's `data-roles` attribute.
- `build_guides.py` copies its CSS from `facilitator-guide-marginal-gains.html` at run time, so editing that file's `<style>` restyles every guide.
- `jira-cheat-sheet.html` was assembled from the main cheat sheet's CSS; the two share styles by copy, not by reference.

## Architecture

**`build_boards.py`** draws SVG by string-building on a fixed 1680×1190 canvas (A3 at print). Layers:
- Primitives: `T` (text), `R`, `L`, `field` (label + write-on line), `lines`, `checkbox`, `sticky`, `para`.
- Components: `header` (navy band to y≈138; right side takes `legend(...)` or `header_fields([...])`), `panel(x, y, w, h, num, title, color, note)`, `sticky_zone`, `table`, `quad_grid`, `kanban_cols`, `step_cards`, `footer`.
- Colour pairs are `(dark, light)` tuples (`BLUE`, `EMERALD`, `PURPLE`, `ORANGE`, `RED`, `AMBER`, `FOREST`, `SKY`, `SLATE`); `ACCENT` is the orange brand colour.
- Each tool is a `build_<name>()` function ending in `write_board(slug, title, desc, body)`, and is called from `__main__`. Boards are cadence-neutral: one board per tool, with a write-in blank (`strip_blank`) where the period matters. `write_redirects()` turns the old `retro-board-*-{sprint,quarter}.html` and `marginal-gains-workshop-board-{sprint,quarter}.html` names into redirect pages; it overwrites those files, so never reuse those names. Prefer "iteration" to "sprint" except on Scrum-named tools (Sprint Planning, Sprint Review).
- Usual layout: content from y=148 to y=1060, 24px outer margin, 14px gaps; rows often split 808 / 397 / 397 or 1082 / 536 wide.
- `write_board` adds a fixed "Facilitator guide →" link from `guide_for(slug)`. That function strips `-board`/`-poster` (`retro-board-X-{sprint,quarter}` → `facilitator-guide-retro-X.html`), so a guide's `slug` must match.

**Licensing:** content is CC BY 4.0 and `_generator/` code is MIT (`LICENSE.md`). Every page and board shows the credit line; keep it on new pages.

**`build_guides.py`** holds guide content as dicts (in `GUIDES` and lists appended to it). Required keys: `slug, title, subtitle, tag, boards, lede, intro, glance, before, agenda_heads, agenda, sections_title, sections_intro, sections, tips, pitfalls, after, toolkit, foot`. `render()` turns each one into a fixed page layout, and `render_docx()` writes the matching Word file through `docx_writer.py`, a small zipfile-based WordprocessingML writer (headings, bullets, tables, bold/italic runs from simple HTML). Validate `.docx` output by parsing each XML part and with `textutil -convert txt`. `intro`, `before` and `toolkit` may contain HTML; most other fields are escaped. Shared "how it fits the toolkit" paragraphs are constants such as `LIFECYCLE_TOOLKIT`, `PROJECT_TOOLKIT`, `PROGRAM_TOOLKIT` and `FLOW_TOOLKIT`.

**`board_spec.py`** builds each guide's "Recreate it in your whiteboard" AI prompt by parsing the board's SVG: rects with `filter="url(#fc)"` are sections (the white text in their header is the title and note), dashed rects inside a headerless panel are zones (e.g. Sailboat), and boards with no panels fall back to rows grouped by vertical gaps. It merges wrapped lines and list numbers. If you add a new layout primitive, check its spec with `python3 _generator/board_spec.py <board>.svg`. The Marginal Gains guide's prompt block is pasted in by hand, so regenerate it if that board changes.

**`build_roles.py`** holds two tables, which are the single source of truth for the role feature:
- `TOOLS`: key → (title, board, guide, href-prefix for matching index cards).
- `ROLES`: id, name, description, three start-with tools, also-useful tools.

It writes the role page, tags each index card by matching the card's `class="primary"` link against the prefixes, and generates the home page's sticky section menu (from `<h2 id="…">` headings, with short labels in `SHORT`) and search box. One script handles role filtering (`#role=<id>` hash) and search together, hiding empty sections and their menu links.

**Home page structure:** `index.html` is grouped into task-based `<h2 id>` sections (set up the team, decide what to build, break down work, …, facilitate & coach). Reference pages (role guide, glossary, cheat sheets, Make It Yours) sit in the header's "Start here" strip, not as cards. A new section needs an `id` on its `<h2>` and, ideally, an entry in `SHORT`.

**Adding a tool** touches five places:
1. A `build_*` function, plus its call in `__main__`.
2. A guide dict.
3. A card in the right `<h2>` section of `index.html`.
4. Entries in `TOOLS` and `ROLES` in `build_roles.py`, then re-run it.
5. Rows in `README.md`'s tool table and lifecycle sections.

If the tool introduces new terms, add them to `TERMS` in `build_glossary.py`. Optionally, add a link in the cheat sheet's "Your Toolkit" panel.

## Verifying changes

There are no tests; verify by rendering with headless Chrome (`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`):
- **Screenshot a board:** `--headless=new --hide-scrollbars --window-size=1728,1238 --virtual-time-budget=4000 --screenshot=<png> file://<path>`. Look for text overlapping panel edges, legends or other text. `text_w()` is only a rough width estimate.
- **Page count:** `--print-to-pdf`, then count `/Type /Page` objects. Guides should print to 3–4 A4 pages; the main cheat sheet to exactly 2 A3 pages; the Jira sheet to 1.
- **Cheat sheet overflow:** inject a script that compares `scrollHeight` with `clientHeight` on `.panel`/`.pb` at a 1660px-wide window, and dump the DOM with `--dump-dom`. The main cheat sheet is nearly full. Adding a line to one panel can overflow a different panel in the same grid row, often Team Development on side 2. Rebalancing the `.s2` grid columns has worked better than shrinking text.
- **Links:** after edits, check that every relative `href` in `*.html` exists on disk.
- Headless Chrome won't render narrower than 500px. The `.tbl` tables scrolling sideways inside their panel on phones is intentional.

## Conventions and gotchas

- **Writing style:** British spelling (prioritisation, visualise, colour). Framework-neutral: don't brand the toolkit with any methodology. Name a framework only as the source of a practice (e.g. "big-room planning (SAFe: PI Planning)"). Credit originators in board taglines and guide intros. Trademarked models carry a notice (ADKAR® → Prosci, Inc.).
- **`÷` glyph:** in Geist / Geist Mono at board sizes it reads as `+`. Use `/` instead.
- **`header_fields` labels:** the write-on line starts 96px after the label start, so keep labels to about 15 characters.
- **`panel(num=...)`:** accepts letters too (the RAID board uses `"R"`, `"A"`, …). Pass `None` for no badge.
- **Fonts and libraries:** Instrument Serif, Geist and Geist Mono. Boards' `.html` load them from Google Fonts; standalone `.svg` files `@import` them. No other external assets.
