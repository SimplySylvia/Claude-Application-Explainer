"""Hub settings. build/build.py reads this file; it finds the guides on its own (sibling folders whose guide_config.py
has the same SOURCE_REPO) and writes index.html and nav.js here."""

APP = '__APP__'                      # used in the headline and section intros
TITLE = '__APP__ guides'             # header, browser tab, and the breadcrumb root and Guides menu label in every guide
HEADLINE = None                      # hero heading; default "Learn the <APP> codebase"
BRAND_COLOR = '#1f6feb'              # logo tile, buttons, focus rings
LOGO_SVG = None                      # white glyph on the brand tile; default: a 2×2 grid

# Design tokens and fonts, as in guide_config.py. Use the same TOKENS_CSS as the guides so the pages match.
TOKENS_CSS = None
FONTS = []

# Guides whose SOURCE_REPO resolves to this folder are listed. A relative path is resolved from this folder.
SOURCE_REPO = '__REPO_PATH__'

# localStorage prefix: <key>-theme (the light/dark choice; connected guides use it as THEME_KEY) and <key>-recent.
STORAGE_KEY = '__SLUG__-guides'

# {guide folder: one-line blurb} for the hub's cards and table. Default: the guide's first part's blurb.
BLURBS = {}

# Guides that have no guide_config.py, listed by hand with PARTS read from their builder script:
# [{'folder': ..., 'html': ..., 'title': ..., 'blurb': ..., 'kind': 'app' or 'topic', 'parts_from': 'build/build.py',
#   'color': '#hex'}]
OTHER_GUIDES = []

FOOTER = None                        # default: build date, guide count, repo name, "Internal use only."
