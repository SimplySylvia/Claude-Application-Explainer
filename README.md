# application-explainer

A Claude Code plugin that builds an internal, self-contained HTML **Product & Engineering Guide** for whatever
application repo you're in: product overview, features, site map, architecture diagrams, tech stack, environments,
local dev, testing, a glossary with hover definitions, search, and optional screenshots. Every claim is verified
against the code.

## Install

This repo is both the plugin and a single-plugin marketplace. In Claude Code:

```
/plugin marketplace add SimplySylvia/Claude-Application-Explainer
/plugin install application-explainer@application-explainer
```

Or from a local clone:

```
/plugin marketplace add /path/to/application-explainer
/plugin install application-explainer@application-explainer
```

To try it without installing: `claude --plugin-dir /path/to/application-explainer`.

## Use

Open Claude Code in the app repo you want documented and ask for an explainer, onboarding guide, or system overview
(or say "use the application-explainer skill"). The skill confirms scope with you, scaffolds a guide folder *outside*
the app repo, and works in phases.

Requirements: Python 3 and Google Chrome (for `qa_check.py` and screenshots).

For agents that don't load plugins, see [`skills/application-explainer/PROMPT.md`](skills/application-explainer/PROMPT.md).

## What it generates

The skill writes to a **guide folder** outside the app repo (default: a sibling `<app>-guide/`) and gives it its
own git repo, with one commit per phase. The app repo is only read, never modified.

```
<app>-guide/
├── <app>-guide.html                  # the guide: one self-contained HTML file
├── <app>-guide-no-screenshots.html   # share version without screenshots (only built when screenshots exist)
├── guide_config.py                   # title, brand color, logo, parts/pages, collapse defaults
├── sections/<id>.html                # one source file per section
├── diagrams.py                       # SVG architecture/flow diagrams
├── shots.py, screenshots/            # optional screenshot gallery
├── build/                            # build engine copied from the skill (python3 build/build.py)
├── qa/                               # qa_check.py output (git-ignored)
└── README.md                         # how to rebuild, and how the guide is shared internally
```

**The HTML guide** needs no server or network access; CSS, JS, icons, fonts, and images are all inlined. It has:

- **Five part pages** shown as header tabs, each with a sidebar:
  - **Product:** overview, features (grouped by area, with route, code location, and rollout flag), site map and route tree
  - **Engineering:** architecture diagram, tech stack by layer with versions
  - **Operations:** environments, URLs, and how a change reaches production (including rollback)
  - **Working process:** local dev setup and daily loop, testing strategy
  - **Reference:** cheat sheet of commands, glossary
- **Optional sections** chosen to fit the app, such as request lifecycle, auth, data model, async jobs, data
  pipeline, observability, security, and AI features. See the full catalog in
  [`references/sections.md`](skills/application-explainer/references/sections.md).
- **SVG diagrams** with a pan/zoom viewer.
- **A glossary** of domain, vendor, and internal terms. Every mention of a term in the guide links to it and shows
  its definition on hover.
- **⌘K search** across all pages.
- **Dark and light themes.**
- **An optional screenshot gallery**, captured only from an environment with synthetic data that you've approved.
- **A footer** recording the source repo, branch, commit, and build date.

Claims in the guide cite file paths in the app repo. Anything that couldn't be verified is left out. Before the
skill hands the guide over, `qa_check.py` must pass on both HTML files with zero TODOs.

### Example

These screenshots come from a guide for **Shopfront**, the small fictional app used by the evals
(`evals/_fixture/make-app.sh`). A real app produces more sections and longer tables.

**Engineering page:** architecture diagram with a legend and a pan/zoom viewer (light theme). The caption flags a
mismatch between a code comment and what the code actually does.

![Engineering page with the architecture diagram](docs/images/guide-engineering.png)

**Glossary hover cards:** underlined terms show their definition and repo path on hover (dark theme).

![Product overview with a glossary hover card](docs/images/guide-glossary.png)

**⌘K search** across every page; each result shows the page and section it's in.

![Search results for "order"](docs/images/guide-search.png)

## Layout

| Path | What |
|---|---|
| `.claude-plugin/plugin.json` | Plugin manifest |
| `.claude-plugin/marketplace.json` | Marketplace manifest (lists this repo as its only plugin) |
| `skills/application-explainer/` | The skill: `SKILL.md`, build `engine/`, `starter/` template, `scripts/`, `references/` |
| `agents/` | Read-only subagents the skill fans out to: `repo-researcher`, `structure-reviewer`, `section-verifier`, `glossary-drafter` |
| `docs/images/` | README screenshots of an example guide |
| `evals/` | `claude plugin eval` suite: trigger, near-miss, and end-to-end cases on a small fixture app |

## Testing the skill

The suite in `evals/` runs against a small fictional app that `evals/_fixture/make-app.sh` creates.

```bash
# Trigger and near-miss cases: does the skill fire when it should, and stay out of the way when it shouldn't?
claude plugin eval . --tag trigger nearmiss --scaffold

# End to end: builds a whole guide and runs QA (slow; grants the tools the build needs)
claude plugin eval . --tag e2e --scaffold --runs 1 --allow-tools Bash Write Edit
```

Run the trigger and near-miss cases after any change to the skill's `description`.

## Releasing

Bump `version` in `.claude-plugin/plugin.json` when you change the skill; users pick it up with
`/plugin marketplace update`.

Internal only — the guides it produces must not be shared publicly (see `skills/application-explainer/references/sharing.md`).
