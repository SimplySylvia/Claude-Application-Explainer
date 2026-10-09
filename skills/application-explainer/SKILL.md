---
name: application-explainer
description: Build an internal, self-contained HTML "Product & Engineering Guide" for the application repo you're in — product overview, features, site map, architecture diagrams, tech stack, environments, local dev, testing, glossary with hover definitions, search, optional screenshots — verified against the code. Use when someone asks for an explainer, onboarding guide, system overview, tech-stack breakdown, or documentation site for an app/repo.
---

# Application explainer

Produces one self-contained HTML file per app. It has:

- **Pages:** five part pages (Product, Engineering, Operations, Working process, Reference) with sticky header tabs, plus a sidebar tree, collapsible sections, and a live breadcrumb.
- **Search:** ⌘K search with find-on-page highlighting across all pages.
- **Diagrams:** SVG diagrams with a fullscreen pan/zoom viewer.
- **Glossary:** auto-linked terms with stacked hover cards.
- **Themes:** dark and light.
- **Screenshots (optional):** a gallery. A `-no-screenshots` share build is produced automatically.

Everything in it is verified against the repo.

## Non-negotiables

- **The app repo is read-only.** Read files and run read-only git/CLI commands only. The guide lives in its own folder and git repo, outside the app repo.
- **Verify every claim** in the code and cite paths. Leave out what you can't verify.
- **Never reproduce secrets or personal/health data.** Report suspected secrets by file:line only.
- **Internal only.** No public sharing (see `references/sharing.md`).
- **Ask before:** account changes (flags/roles), OAuth consent, deploying or publishing anything, and capturing screens that may show real personal data.

## Steps

`<this-skill>` below means this skill's base directory (the folder containing this `SKILL.md`).

1. **Scope:** confirm the app, repo path, audience, guide location, and whether screenshots are wanted. See Phase 0 in `references/workflow.md`.
2. **Scaffold:**
   ```bash
   python3 <this-skill>/scripts/new_guide.py --repo <repo> --app "<App>" [--dest <folder>]
   ```
3. **Discover:** map the repo, using parallel read-only research agents for big repos (`references/agent-prompts.md` §1). Pick sections from `references/sections.md` and set `PARTS` in `guide_config.py`. Show the user the outline.
4. **Write:** fill `sections/<id>.html` and `diagrams.py` following `references/authoring.md`. Build often:
   ```bash
   python3 <guide>/build/build.py
   ```
   Fix every warning it prints.
5. **Review:** run a structure review plus per-section verification agents (§3-4). Spot-check findings yourself before applying them.
6. **Screenshots** (optional): `references/screenshots.md`.
7. **Glossary:** run `scripts/extract_text.py`, then glossary agents (§5), then `scripts/merge_glossary.py`. Remove aliases that are too broad.
8. **QA:** run this on both outputs. It must PASS, and any TODO count should be zero before sharing:
   ```bash
   python3 <this-skill>/scripts/qa_check.py <guide>/<name>-guide.html
   ```
9. **Share internally:** Drive, or the Apps Script web app (`references/sharing.md`, `apps-script/Code.gs`).

Commit the guide folder after each step and keep the user posted with short updates.

## Files

| Path                        | What                                                                                                                                                                                                                                                                            |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `engine/`                   | The build engine, copied into each guide as `build/`. `build.py`, `layout.py`, `diagram.py`, `icons.py` (+ `icons/`), `styles.css`, `tokens.css`, and the page scripts (`layout.js` pages/collapse/sidebar, `search.js`, `glossary.js`, `diagram-viewer.js`, `shots-viewer.js`) |
| `starter/`                  | The new-guide template: `guide_config.py`, `diagrams.py`, `shots.py`, and skeleton `sections/`                                                                                                                                                                                  |
| `scripts/new_guide.py`      | Scaffold a guide for a repo                                                                                                                                                                                                                                                     |
| `scripts/qa_check.py`       | Headless Chrome checks: JS errors, broken links, images, navigation, search, glossary, TODO count                                                                                                                                                                               |
| `scripts/extract_text.py`   | Guide text + glossary candidates for agents                                                                                                                                                                                                                                     |
| `scripts/merge_glossary.py` | Merge drafted glossary rows, dropping duplicates, sorted by group                                                                                                                                                                                                               |
| `scripts/fetch_icons.py`    | Add MUI Rounded icons                                                                                                                                                                                                                                                           |
| `references/`               | `workflow.md`, `sections.md`, `authoring.md`, `agent-prompts.md`, `screenshots.md`, `sharing.md`, `lessons.md`                                                                                                                                                                  |
| `apps-script/Code.gs`       | Serves the guide to signed-in company accounts                                                                                                                                                                                                                                  |
| `PROMPT.md`                 | A copy-paste kickoff prompt for agents that don't load skills                                                                                                                                                                                                                   |

Read `references/lessons.md` before starting. It lists the mistakes that cost the most time last time.
