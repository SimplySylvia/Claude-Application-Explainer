"""Guide settings. The build reads this file; sections live in sections/<id>.html."""

TITLE = '__APP__ — Product & Engineering Guide'   # browser tab and header tooltip
SHORT_TITLE = '__APP__ Guide'                     # shown in the header
OUTPUT_NAME = '__SLUG__-guide'                    # writes __SLUG__-guide.html (+ -no-screenshots.html)
BRAND_COLOR = '#1f6feb'                           # logo tile, part badges; use the app's primary brand color
LOGO_SVG = ('<svg viewBox="0 0 24 24"><path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"/></svg>')  # white glyph on the brand tile

# Design tokens. Default: build/tokens.css. Point at the app's own token CSS (copied into this folder) if it has one;
# the variable names used by the styles are listed in references/design-tokens.md of the skill.
TOKENS_CSS = None
# Embedded fonts: [(family, weight, path-relative-to-this-folder), ...]. Fonts must be referenced by the tokens' font-family.
FONTS = []

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
