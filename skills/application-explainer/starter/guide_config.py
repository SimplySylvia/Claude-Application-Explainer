"""Guide settings. The build reads this file; sections live in sections/<id>.html."""

TITLE = '__APP__ — Product & Engineering Guide'   # browser tab and header tooltip
SHORT_TITLE = '__APP__ Guide'                     # shown in the header
OUTPUT_NAME = '__SLUG__-guide'                    # writes __SLUG__-guide.html (+ -no-screenshots.html)
BRAND_COLOR = '#1f6feb'                           # logo tile, part badges; use the app's primary brand color
LOGO_SVG = ('<svg viewBox="0 0 24 24"><path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"/></svg>')  # white glyph on the brand tile

GUIDE_KIND = 'app'                               # 'app' (whole-app guide) or 'topic'; the hub lists them separately

# Guide hub (scripts/new_hub.py): one page linking every guide for this repo. new_guide.py and new_hub.py --connect
# fill these in; None leaves the guide standalone.
HUB_URL = None       # path to the hub's index.html; adds the breadcrumb root, Guides menu, and cross-guide search
HUB_TITLE = None     # breadcrumb label: the hub's TITLE
THEME_KEY = None     # localStorage key for light/dark, shared with the hub so all guides match
DEPTH_CSS = True     # build/depth.css surfaces and shadows; False keeps a custom TOKENS_CSS's own backgrounds

# Design tokens. Default: build/tokens.css. Point at the app's own token CSS (copied into this folder) if it has one;
# it must define the variables the styles use (see "Styling and branding" in the skill's references/authoring.md).
TOKENS_CSS = None
# Embedded fonts: [(family, weight, path-relative-to-this-folder), ...]. Fonts must be referenced by the tokens' font-family.
FONTS = []

# Where the guide's facts come from. scripts/changed_since.py diffs SOURCE_REPO from SOURCE_COMMIT to find sections
# that may be stale; `changed_since.py <guide> --mark` records the new commit after an update. A relative
# SOURCE_REPO is resolved from this folder.
SOURCE_REPO = '__REPO_PATH__'
SOURCE_COMMIT = '__COMMIT_FULL__'

FOOTER = 'Generated from the <code>__REPO_NAME__</code> repository on __DATE__ (branch <code>__BRANCH__</code> @ __COMMIT__). Internal use only.'

# Parts become pages (tabs in the header). Each item is (section id, sidebar label); the file is sections/<id>.html.
PARTS = [
    ('product', 'Product', 'What the app is, who uses it, and what it does.', [
        ('overview', 'What is __APP__?'),
        ('features', 'Features'),
        ('sitemap', 'Site map & navigation'),
    ]),
    ('engineering', 'Engineering', 'How it is built: architecture, stack, data, and code layout.', [
        ('arch', 'Architecture'),
        ('stack', 'Tech stack'),
    ]),
    ('operations', 'Operations', 'Where it runs, how changes ship, and how we watch it.', [
        ('envs', 'Environments & deployments'),
    ]),
    ('process', 'Working process', 'How engineers work in the repo, from setup to a merged PR.', [
        ('localdev', 'Local development'),
        ('testing', 'Testing strategy'),
    ]),
    ('reference', 'Reference', 'Quick lookups: commands and terms.', [
        ('cheatsheet', 'Cheat sheet'),
        ('glossary', 'Glossary'),
    ]),
]

# Progressive disclosure: deep dives and reference material start collapsed.
COLLAPSED_SECTIONS = {'glossary'}
COLLAPSED_SUBSECTIONS = set()          # {('section-id', 'Exact h3 title'), ...}
COLLAPSED_GROUP_SECTIONS = {'stack', 'features', 'glossary'}   # table group rows start collapsed in these sections
OPEN_TABLE_GROUPS = set()              # group labels that stay open anyway
COLLAPSED_TABLE_GROUPS = set()
