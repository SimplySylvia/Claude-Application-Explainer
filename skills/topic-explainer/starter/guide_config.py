"""Guide settings. The build reads this file; sections live in sections/<id>.html."""

TITLE = '__TOPIC__ in __APP__ — Topic Guide'       # browser tab and header tooltip
SHORT_TITLE = '__TOPIC__ in __APP__'               # shown in the header
OUTPUT_NAME = '__SLUG__-__TOPIC_SLUG__-guide'      # writes __SLUG__-__TOPIC_SLUG__-guide.html
BRAND_COLOR = '#1f6feb'                           # logo tile, part badges; use the app's primary brand color
LOGO_SVG = ('<svg viewBox="0 0 24 24"><path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"/></svg>')  # white glyph on the brand tile

# Design tokens. Default: build/tokens.css. Point at the app's own token CSS (copied into this folder) if it has one;
# it must define the variables the styles use (see "Styling and branding" in application-explainer's references/authoring.md).
TOKENS_CSS = None
# Embedded fonts: [(family, weight, path-relative-to-this-folder), ...]. Fonts must be referenced by the tokens' font-family.
FONTS = []

# Where the guide's facts come from. scripts/changed_since.py diffs SOURCE_REPO from SOURCE_COMMIT to find sections
# that may be stale; `changed_since.py <guide> --mark` records the new commit after an update. A relative
# SOURCE_REPO is resolved from this folder.
SOURCE_REPO = '__REPO_PATH__'
SOURCE_COMMIT = '__COMMIT_FULL__'

# Technology deep dives: {slug: {"name": ..., "docs_checked": "YYYY-MM-DD"}}. changed_since.py flags docs
# checked more than 90 days ago; `changed_since.py <guide> --mark-docs <slug>` records a re-check.
TOPICS = {'__TOPIC_SLUG__': {'name': '__TOPIC__', 'docs_checked': ''}}

FOOTER = ('Generated from the <code>__REPO_NAME__</code> repository on __DATE__ (branch <code>__BRANCH__</code> @ __COMMIT__) '
          'and the official __TOPIC__ documentation linked in each section. Internal use only.')

# Parts become pages (tabs in the header). Each item is (section id, sidebar label); the file is sections/<id>.html.
# When this topic is added to an existing guide (new_guide.py --into), these items become one part, minus the glossary.
PARTS = [
    ('concept', 'The concept', 'What __TOPIC__ is and the ideas you need before reading the code.', [
        ('__T__overview', 'What is __TOPIC__?'),
        ('__T__concepts', 'Core concepts'),
    ]),
    ('in-app', 'In __APP__', 'Where __APP__ uses __TOPIC__, one flow end to end, and how to change it.', [
        ('__T__usage', 'Where __APP__ uses it'),
        ('__T__walkthrough', 'Guided walkthrough'),
        ('__T__conventions', 'Patterns & gotchas'),
        ('__T__recipes', 'Common changes'),
    ]),
    ('reference', 'Reference', 'Versions, official docs, and terms.', [
        ('__T__versions', 'Versions & what changed'),
        ('__T__resources', 'Official docs & further reading'),
        ('glossary', 'Glossary'),
    ]),
]

# Progressive disclosure: deep dives and reference material start collapsed.
COLLAPSED_SECTIONS = {'glossary'}
COLLAPSED_SUBSECTIONS = set()          # {('section-id', 'Exact h3 title'), ...}
COLLAPSED_GROUP_SECTIONS = {'glossary'}   # table group rows start collapsed in these sections
OPEN_TABLE_GROUPS = set()              # group labels that stay open anyway
COLLAPSED_TABLE_GROUPS = set()
