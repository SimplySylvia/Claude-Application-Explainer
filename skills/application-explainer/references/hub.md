# Guide hubs: one front door for every guide about a repo

Once a repo has more than one guide (say, the Product & Engineering Guide plus a couple of topic guides), a **hub**
ties them together:

- **The hub page** (`<app>-guides/index.html`) features the whole-app guide, with a tile for each page. Below it,
  topic guides sit in a compact table you can sort and filter, with a preview of each guide's sections. Search covers
  every guide, page, section and heading, grouped by guide. A "Continue reading" list shows where you left off in
  each guide.
- **Every connected guide** gets a breadcrumb root (the hub's `TITLE`), a **Guides** menu listing all guides, a
  "Search all guides" link at the end of its own search results, the same light/dark setting as the hub and the
  other guides, and reading-position tracking for "Continue reading".

Guides and the hub use the same surfaces and shadows (`engine/depth.css`). Each topic guide's `BRAND_COLOR` serves
as its marker: a dot and an edge stripe on the hub, its logo tile and part badges inside the guide.

## Create one

```bash
python3 SKILL_DIR/scripts/new_hub.py --repo <repo> --app "<App>" [--dest <folder>]
```

This creates `<app>-guides/` next to the repo (it must sit beside the guides; links between them are relative), with
`build/` (the hub engine), `hub_config.py`, `README.md` and a git repo. It connects every guide already beside it for
the same repo and builds the hub. Rebuild each connected guide once so its header picks up the hub.

Offer a hub when a second guide for the same repo is about to exist, or when the user asks to link or organize
guides. `new_guide.py` prints the command when it notices other guides for the repo next to the new one.

## How guides join and stay current

- **Discovery:** the hub lists every sibling folder whose `guide_config.py` has the same `SOURCE_REPO`. Whole-app
  guides (`GUIDE_KIND = 'app'`) go under "Start here", and topic guides (`'topic'`) go in the table. A deep dive
  added with `new_guide.py --into` shows up inside its guide's row and in the hub's topic buttons.
- **New guides:** `new_guide.py` connects a new guide to the hub next to it for the same repo (`--no-hub` skips
  this).
- **Existing guides:** run `new_hub.py --connect <guide>` to connect one. It sets `HUB_URL`, `HUB_TITLE` and
  `THEME_KEY`, and gives a topic guide still on the default brand color a palette color of its own. If the guide's
  engine predates hub support, add `--update-engine`. That re-copies the engine, keeping a customized `tokens.css`
  and `icons.py`.
- **Refreshing:** a connected guide rebuilds its hub at the end of every `build/build.py` run (lines prefixed
  `hub:`; `--no-hub` skips it). Run the hub's own `build/build.py` after deleting or renaming a guide.
- **Warnings:** the hub warns about guides it lists but that aren't built yet or aren't connected.

## hub_config.py

| Setting | What |
|---|---|
| `APP`, `TITLE`, `HEADLINE` | Names in the headline and intros; `TITLE` is also the breadcrumb root and menu label in every guide |
| `BRAND_COLOR`, `LOGO_SVG` | The hub's own brand tile and buttons |
| `TOKENS_CSS`, `FONTS` | Same as in `guide_config.py`; use the guides' tokens so the pages match |
| `SOURCE_REPO` | Which guides belong here |
| `STORAGE_KEY` | `localStorage` prefix: `<key>-theme` (guides' `THEME_KEY`) and `<key>-recent` |
| `BLURBS` | `{guide folder: one-line blurb}`; keep it to one line, since the table cuts it off |
| `OTHER_GUIDES` | Guides with no `guide_config.py`, listed by hand with `PARTS` read from their builder script |

## Sharing and hosting

The hub and its guides are separate files that link to each other with relative paths. Share or host the folders
together and keep the same layout, through the same internal channels as a single guide (`references/sharing.md`).
Reading history uses `localStorage`. Chrome shares it across local `file://` pages; Firefox and Safari keep each
local file separate, so "Continue reading" only works there once the guides are served from one site.

## Updating the hub engine

Re-copy `SKILL_DIR/hub/build.py`, `hub/nav.src.js`, `engine/tokens.css` and `engine/depth.css` into
`<hub>/build/`, then rebuild one guide. Never edit `nav.js`: the hub regenerates it from `nav.src.js`.
