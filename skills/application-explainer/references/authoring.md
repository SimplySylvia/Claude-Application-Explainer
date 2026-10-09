# Authoring: sections, diagrams, styling

## Section files

Write one file per section: `sections/<id>.html`. The build depends on this skeleton:

```html
<!-- ============ TITLE IN CAPS ============ -->
<section id="<id>">
  <h2>Section title</h2>
  <p class="sub">One- or two-sentence summary. Sources: <code>path</code>, <code>path</code>.</p>

  <h3>First subsection title</h3>
  ...content...

  <h3 style="margin-top:24px">Second subsection title</h3>
  ...content...
</section>
```

- **Collapsible subsections:** subsection `<h3>` tags must be indented exactly 2 spaces, on their own line, and be direct children of `<section>`. Those become collapsible. An `<h3>` inside a card is indented deeper and stays a card title.
- **Headings and scripts:** use one `<h2>` only, the first line. No inline `<script>` and no external assets. Everything must be self-contained.
- **Escaping:** write `&` as `&amp;`, `<` as `&lt;`, and `>` as `&gt;` in text.
- **Cross-links:** link to other sections with `<a href="#<id>">Title</a>`. Any element id works, and the page switches automatically.

## Building blocks

**Grouped reference table.** Preferred for lists. Group rows are collapsible and show a preview of their items.

```html
<table class="stack">
  <colgroup><col style="width:22%"><col><col style="width:26%"></colgroup>
  <tr><th>Thing</th><th>What it is / does</th><th>Where (repo path)</th></tr>
  <tr class="group" style="--accent: var(--c-run)"><td colspan="3"><span class="row-icon" data-icon="server"></span>Group name</td></tr>
  <tr><td><b>Item</b></td><td>Description</td><td><code>path/to/file</code></td></tr>
</table>
```

`colspan` must equal the column count. Add `data-screens` to the `<table>` tag to get a Screen column fed by `FEATURE_SHOTS`, keyed by each row's first `<b>` text.

**Plain table:**

```html
<table><tr><th>…</th></tr><tr><td>…</td></tr></table>
```

**Cards grid.** At most two per row. An odd last card spans the full row and its list flows into two columns.

```html
<div class="grid">
  <div class="card" style="--accent: var(--c-edge)">
    <h3 class="card-title"><span class="card-icon"><svg viewBox="0 0 24 24" data-card-icon="shield"></svg></span>Card title</h3>
    <ul><li>…</li></ul>
  </div>
</div>
```

**Smaller pieces:**

- Chips: `<span class="chip">Vendor</span>`
- Pills: `<span class="pill p-purple">featureFlag</span>` (`p-green`, `p-gray`, `p-blue`, `p-teal`, `p-purple`)
- Caption: `<p class="caption">…</p>`
- Inline code: `<code>…</code>`

**Route tree** (site map):

```html
<div class="sitemap">
  <details open><summary><code>/path</code> <span>What it is</span></summary>
    <ul><li><code>child</code> <span>note</span></li></ul>
    <details><summary><code>/nested</code> <span>…</span></summary>…</details>
  </details>
</div>
```

**Placeholders:**

- Screenshot gallery: `<!-- SCREEN GALLERY -->` on its own line inside a section, usually `sitemap`. It's replaced by the gallery and the "Not captured" table, and removed when there are no screenshots.
- Diagram: `<div class="diagram" data-diagram="name"></div>`.

**Accent and icon variables:**

- **Accents:** `--c-client` (blue), `--c-edge` (purple), `--c-run` (teal), `--c-data` (orange), `--c-ext` (pink), `--c-ci` (gray).
- **Icon keys** for `data-icon`, `data-card-icon`, diagram nodes, and gallery areas: admin ai apps book build calendar chart chat check clock cloud code cog dash db eye filter fn folder globe hospital hub inbox key layers link list lock member merge monitor package person play pulse puzzle radio rocket search server shield sync table terminal tree upload users zap. Add more with `scripts/fetch_icons.py`.

## Diagrams (`diagrams.py`)

```python
from diagram import Diagram, diagram, mid

@diagram('request')
def request():
    d = Diagram('request', 1200, 360)                 # canvas in SVG units; renders responsive
    d.zone(16, 20, 400, 320, 'BROWSER')               # dashed group box with a label pill
    a = d.node('ui', 32, 70, 200, 'client', 'monitor', 'Web app', ['React', 'Apollo'], num=1)
    b = d.node('api', 460, 70, 220, 'run', 'server', 'API', ['Express'], num=2)
    d.edge([mid(a, 'r'), mid(b, 'l')], 'sync', label='POST /graphql')   # 'sync' solid, 'async' dashed
    d.edge([(570, 150), (570, 220), (760, 220)], 'async')              # orthogonal segments only
    return d, 'Request lifecycle'                     # aria label
```

- **Node size and text:** node height is `50` with no lines, otherwise `46 + 16 × lines`. Keep each line short; the build warns on overflow.
- **Categories:** `client`, `edge`, `run`, `data`, `ext`, `ci`. They set the node color and build the legend automatically.
- **Connecting nodes:** `mid(rect, 'l'|'r'|'t'|'b', offset)` gives a node's edge midpoint. Edges must be horizontal or vertical segments. A connection between nodes of different heights produces a diagonal, so align them.
- **Fix every warning the build prints:** overlaps, labels on nodes, edges through nodes, text overflow. Each diagram gets a fullscreen viewer with pan and zoom for free.

## Styling and branding

- **Brand:** `BRAND_COLOR` and `LOGO_SVG` in `guide_config.py`. The logo is a white glyph on a brand-colored tile.
- **Design tokens:** `build/tokens.css` by default. To match the app's look, copy its token CSS into the guide and set `TOKENS_CSS`. It must define the variables the styles use; map missing ones to the app's equivalents:
  - color families: blue, purple, teal, orange, pink, gray (`-bg`, `-fg`, `-fg-alt`)
  - text, link, border, background, button, input, and nav colors
  - spacing, radius, shadow, font, and z-index scales
  - the same names under `[data-theme="dark"]`

  To list them, diff `var(--…)` uses in `build/styles.css` and `build/layout.py` against the tokens file.
- **Fonts:** `FONTS = [('Family', 400, 'fonts/x.woff2'), …]` embeds them. The tokens' `--font-family` must name the family.

## Collapse defaults (`guide_config.py`)

- `COLLAPSED_SECTIONS`: section ids that start collapsed (deep dives, reference).
- `COLLAPSED_SUBSECTIONS`: `{('section-id', 'Exact h3 title')}`.
- `COLLAPSED_GROUP_SECTIONS`: sections whose table group rows start collapsed, showing a preview. Good for long tables (stack, features, glossary). `OPEN_TABLE_GROUPS` keeps specific groups open.
- Readers' own choices are remembered per browser; the **Reset** button restores these defaults.

## Glossary naming (auto-linking)

- **One row per concept:** `<tr><td><b>Main name / Other name (expansion)</b></td><td>Meaning.</td><td><code>path</code></td></tr>`
- **How names are matched:**
  - Names are split on ` / ` (with spaces); a bare `/` inside a name doesn't split it.
  - Parenthetical text is another name unless it starts with "as " (context).
  - Acronyms and mixed-case identifiers match exactly; plain words ignore case and match plurals.
- **What gets linked:** the first mention per section and per glossary definition, so definitions link to each other and hover cards stack.
- **Avoid broad names:** don't use everyday words or ambiguous acronyms as names (e.g. "service", "model", "IP" vs IP address). Rename them, e.g. "Services layer (as in src/services)".

## Writing style

- Plain, direct, present tense. Lead with what the reader needs.
- Tables and short bullets over prose. Specifics (paths, flags, commands) over adjectives.
- Every claim verifiable in the repo. Say "about" for counts.
- No personal data, health data, or credential values. Schema and table names are fine.
