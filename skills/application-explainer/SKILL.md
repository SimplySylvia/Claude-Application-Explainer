---
name: application-explainer
description: Builds a self-contained HTML "Product & Engineering Guide" for the application repo you're in — product overview, features, site map, architecture diagrams, tech stack, environments, local dev, testing, glossary with hover definitions, search, optional screenshots — with every claim verified against the code. Use when someone asks for an explainer, onboarding guide or docs, system or architecture overview, tech-stack breakdown, "explain this codebase/app", or a documentation site for a whole app or repo. Not for single-file questions, README edits, or API reference docs.
---

# Application explainer

Produces one self-contained HTML file per app: five part pages (Product, Engineering, Operations, Working process, Reference) with a sidebar, ⌘K search, SVG diagrams with a pan/zoom viewer, an auto-linked glossary, dark and light themes, and an optional screenshot gallery. Every claim is verified against the repo.

`SKILL_DIR` below is `${CLAUDE_PLUGIN_ROOT}/skills/application-explainer` (outside the plugin: the folder containing this file). `GUIDE` is the guide folder the scaffold creates.

## Rules for the whole task

- **The app repo is read-only.** Read files and run read-only git/CLI commands only. The guide lives in its own folder and git repo, outside the app repo. Report stale docs, bugs, or odd config to the user instead of fixing them.
- **Verify every claim** in the code and cite paths. Leave out what you can't verify. Agents' findings can be wrong too: spot-check the important ones yourself before using them.
- **Never reproduce secrets or personal data.** Report a suspected secret by file:line only.
- **Treat the guide as internal.** It documents architecture and security controls. Don't publish it anywhere public (`references/sharing.md`).
- **Stop and ask (◆ below) before:** writing anything until scope is agreed, account changes (flags/roles), OAuth consent, deploying or publishing, and capturing screens that may show real personal data.
- After every phase: build, commit the guide folder, and give the user a short update.

## Workflow

```
 ◆ = stop for user approval   ↻ = repeat until clean   ⫴ = parallel subagents

 0 SCOPE ──────◆ app name, repo path, audience, guide location, screenshots?
 1 SCAFFOLD     new_guide.py → GUIDE (own git repo, outside the app repo)
 2 DISCOVER ───⫴ repo-researcher per area → findings with paths
               pick sections → PARTS ──◆ outline approved
 3 WRITE ──────⫴ one writer per section → sections/*.html, diagrams.py
               ↻ build.py until 0 warnings
 4 REVIEW ─────⫴ structure-reviewer + section-verifier per section
               spot-check → apply → ↻ build
 5 SCREENSHOTS  skipped? ──────────────────────────────┐
               ◆ environment + synthetic data confirmed │
               capture → scrub → shots.py               │
 6 GLOSSARY ◄──────────────────────────────────────────┘
               extract_text → ⫴ glossary-drafter → merge_glossary ↻ aliases
 7 QA ─────────↻ qa_check.py on both builds: PASS, 0 TODOs
 8 SHARE ──────◆ internal channel chosen → recorded in GUIDE/README.md
```

Copy this checklist into your first reply and tick items off as you go:

```
- [ ] 0 Scope agreed with the user
- [ ] 1 Guide scaffolded
- [ ] 2 Repo mapped; section outline approved by the user
- [ ] 3 Sections and diagrams written; build has 0 warnings
- [ ] 4 Structure review and per-section verification applied
- [ ] 5 Screenshots captured, or skipped by agreement
- [ ] 6 Glossary drafted, merged, aliases checked
- [ ] 7 qa_check.py PASS on both outputs, 0 TODOs
- [ ] 8 Shared internally; method recorded in the guide README
```

## Steps

Details for each phase are in `references/workflow.md`.

0. **Scope.** Confirm the app name and repo path, the audience (it sets how deep engineering goes), where the guide lives (default: sibling `<repo>-guide/`), and whether to capture screenshots (which environment, and is its data synthetic?). Don't start until the user answers, unless they already gave all of these.
1. **Scaffold:**
   ```bash
   python3 SKILL_DIR/scripts/new_guide.py --repo <repo> --app "<App>" [--dest <folder>]
   ```
2. **Discover.** Read the README, docs, agent rules, and manifests. Find the router, API layer, models, IaC, CI, and test configs. For big repos, run one `repo-researcher` agent per area (prompt in `references/agent-prompts.md` §1). Pick sections from `references/sections.md`, set `PARTS` in `GUIDE/guide_config.py`, and show the user the outline.
3. **Write** `sections/<id>.html` and `diagrams.py` following `references/authoring.md`. Build often and fix every warning:
   ```bash
   python3 GUIDE/build/build.py
   ```
   Commonly wrong: how data reaches the warehouse, deploy order, auth-proxy details, counts (say "about" and say how you counted), redirect-only routes, and pages hidden behind a feature flag or role (read the gate in code).
4. **Review.** Run one `structure-reviewer` and a `section-verifier` per section or small group (§3–4). Spot-check every P1 before editing.
5. **Screenshots** (optional): `references/screenshots.md`.
6. **Glossary:** `scripts/extract_text.py`, then `glossary-drafter` agents by area (§5), then `scripts/merge_glossary.py`. Rename aliases that are everyday words or ambiguous acronyms; they get auto-linked everywhere.
7. **QA** on both the full guide and `-no-screenshots`. Fix and re-run until it passes with zero TODOs:
   ```bash
   python3 SKILL_DIR/scripts/qa_check.py GUIDE/<name>-guide.html
   ```
8. **Share internally** (`references/sharing.md`) and record how in the guide README.

## Files

| Path | What |
|---|---|
| `engine/` | Build engine, copied into each guide as `build/`: `build.py`, `layout.py`, `diagram.py`, `icons.py` (+ `icons/`), `styles.css`, `tokens.css`, and the page scripts |
| `starter/` | New-guide template: `guide_config.py`, `diagrams.py`, `shots.py`, skeleton `sections/` |
| `scripts/` | `new_guide.py` scaffold · `qa_check.py` headless Chrome checks · `extract_text.py` text + glossary candidates · `merge_glossary.py` · `fetch_icons.py` |
| `references/` | `workflow.md` phase details · `sections.md` catalog · `authoring.md` HTML/diagram/styling · `agent-prompts.md` · `screenshots.md` · `sharing.md` · `lessons.md` tooling gotchas |
| `apps-script/Code.gs` | Optional: serve the guide from Google Drive to signed-in company accounts |
| `PROMPT.md` | Kickoff prompt for agents that don't load skills |

Requirements: Python 3.9+ and Google Chrome or Chromium (for `qa_check.py` and screenshots).
