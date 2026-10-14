---
name: application-explainer
description: Builds a self-contained HTML "Product & Engineering Guide" for the application repo you're in — product overview, features, site map, architecture diagrams, tech stack, environments, local dev, testing, glossary with hover definitions, search, optional screenshots — with every claim verified against the code. Use when someone asks for an explainer, onboarding guide or docs, system or architecture overview, tech-stack breakdown, "explain this codebase/app", or a documentation site for a whole app or repo, and to update a guide it built earlier after the code changed. Not for single-file questions, README edits, API reference docs, or a guide to one technology and how the app uses it (that's topic-explainer).
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
- After every phase: build, update `GUIDE/PROGRESS.md`, commit the guide folder, and give the user a short update.
- **Resuming or updating?** If `GUIDE/PROGRESS.md` exists, read it first and continue from the first unticked phase. To refresh a finished guide after the code changed, follow [Updating an existing guide](#updating-an-existing-guide).

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
               extract_text → glossary-scout ──◆ explainers offered
               → ⫴ glossary-drafter → merge_glossary ↻ aliases
 7 QA ─────────↻ qa_check.py on both builds: PASS, 0 TODOs
 8 SHARE ──────◆ internal channel chosen → recorded in GUIDE/README.md
```

Show this checklist in your first reply. The scaffold writes the same list to `GUIDE/PROGRESS.md`: tick phases there as you go, and log scope answers, decisions, rejected review findings, open questions, and repo problems in its sections.

```
- [ ] 0 Scope agreed with the user
- [ ] 1 Guide scaffolded
- [ ] 2 Repo mapped; section outline approved by the user
- [ ] 3 Sections and diagrams written; build has 0 warnings
- [ ] 4 Structure review and per-section verification applied
- [ ] 5 Screenshots captured, or skipped by agreement
- [ ] 6 Glossary scouted, drafted, merged, aliases checked; explainers offered
- [ ] 7 qa_check.py PASS on both outputs, 0 TODOs
- [ ] 8 Shared internally; method recorded in the guide README
```

## Steps

Details for each phase are in `references/workflow.md`. Don't tick a phase until its **Done when** holds.

0. **Scope.** Confirm the app name and repo path, the audience (it sets how deep engineering goes), where the guide lives (default: sibling `<repo>-guide/`), and whether to capture screenshots (which environment, and is its data synthetic?). Don't start until the user answers, unless they already gave all of these.
   **Done when:** all four are answered, and you've written them under Scope in `PROGRESS.md` (right after phase 1 creates it).
1. **Scaffold:**
   ```bash
   python3 SKILL_DIR/scripts/new_guide.py --repo <repo> --app "<App>" [--dest <folder>]
   ```
   If a guide hub for the repo sits next to the new guide, the scaffold connects it, and every build refreshes the hub. If the scaffold reports other guides for the repo but no hub, offer one (`references/hub.md`).
   **Done when:** `python3 GUIDE/build/build.py` prints `OK` and the guide folder has its first commit.
2. **Discover.** Read the README, docs, agent rules, and manifests. Find the router, API layer, models, IaC, CI, and test configs. Size the repo with `git -C <repo> ls-files | wc -l` and count its deployable apps and services. If it has more than about 1,000 tracked files or more than 3 deployables, run one `repo-researcher` agent per area, in parallel (prompt in `references/agent-prompts.md` §1); otherwise research it yourself. Pick sections from `references/sections.md`, set `PARTS` in `GUIDE/guide_config.py`, and show the user the outline.
   **Done when:** every chosen section has findings with repo paths, unanswered questions are in `PROGRESS.md`, and the user has approved the outline.
3. **Write** `sections/<id>.html` and `diagrams.py` following `references/authoring.md`. Build often and fix every warning:
   ```bash
   python3 GUIDE/build/build.py
   ```
   Commonly wrong: how data reaches the warehouse, deploy order, auth-proxy details, counts (say "about" and say how you counted), redirect-only routes, and pages hidden behind a feature flag or role (read the gate in code).
   **Done when:** no section contains `TODO`, every section cites repo paths (the build warns when one doesn't), and the build prints `OK` with 0 warnings.
4. **Review.** Run one `structure-reviewer` and a `section-verifier` per section or small group (§3–4), in parallel.
   **Done when:** you've checked every P1 finding against the cited code yourself and either fixed it or logged why you rejected it in `PROGRESS.md`, you've spot-checked at least 3 P2 findings (all of them if there are fewer), and the rebuild has 0 warnings.
5. **Screenshots** (optional): `references/screenshots.md`.
   **Done when:** every screen in the site map is captured and scrubbed, or listed in `NOT_CAPTURED` with what would unblock it; or the user agreed to skip screenshots.
6. **Glossary:** `scripts/extract_text.py`, then one `glossary-scout` (§5) that decides which terms the audience needs defined, which need a fuller explainer, and which existing rows to fix. Review its report, offer the explainers to the user, then run `glossary-drafter` agents for the areas with terms to add (§6), and `scripts/merge_glossary.py`. Rename aliases that are everyday words or ambiguous acronyms; they get auto-linked everywhere.
   **Done when:** every P1 ADD term from the scout is in the glossary or logged as rejected, every FIX is applied or logged, the user has seen the EXPLAINER list and their answer is in `PROGRESS.md`, the merge prints no `BAD` rows, you've reviewed every `dup` it reported, and you've checked the 10 most-linked terms (count `class="gl-term"` links per term in the built HTML) and confirmed each links only real mentions, not everyday words.
7. **QA** on both the full guide and `-no-screenshots`. Fix and re-run until it passes with zero TODOs:
   ```bash
   python3 SKILL_DIR/scripts/qa_check.py GUIDE/<name>-guide.html
   ```
   **Done when:** both files print `PASS` with `todos 0`.
8. **Share internally** (`references/sharing.md`).
   **Done when:** the user has chosen the channel, and the link, file ID, and access level are recorded in the guide README.

## Updating an existing guide

When the code has moved on since a guide was built, update only what changed:

1. Read `GUIDE/PROGRESS.md` and run:
   ```bash
   python3 SKILL_DIR/scripts/changed_since.py GUIDE
   ```
   It diffs the repo from `SOURCE_COMMIT` in `guide_config.py` and lists the **affected** sections (they cite a changed file or folder) and changed files that **no section cites**. If the guide has technology deep dives (`TOPICS`), it also flags their docs as `DOCS STALE` after 90 days: refresh those with the topic-explainer skill's Updating steps.
2. Tell the user what changed and which sections you plan to re-check. Don't rebuild sections nobody asked about.
3. Run a `section-verifier` on each affected section, and a `repo-researcher` on any area with significant uncited changes (a new service, routes, jobs, or infra). Apply findings as in phase 4.
4. To pick up engine fixes, re-copy `SKILL_DIR/engine/` over `GUIDE/build/`, keeping any custom `tokens.css` or `icons.py` registrations (`new_hub.py --connect GUIDE --update-engine` does this for a guide that isn't on a hub yet).
5. Rebuild, run QA on both outputs, then record the new commit and commit the guide:
   ```bash
   python3 SKILL_DIR/scripts/changed_since.py GUIDE --mark
   ```
6. Re-share through the same channel recorded in the guide README. If the guide is on a hub, the build already refreshed it; re-share the hub with it.

## Guide hubs

When a repo has more than one guide, a hub links them: one page that features the whole-app guide, lists topic guides in a sortable table, and searches all of them, plus a Guides menu, breadcrumb, shared theme setting and "Continue reading" in every connected guide. Create one with `python3 SKILL_DIR/scripts/new_hub.py --repo <repo> --app "<App>"`. Connect an existing guide with `new_hub.py --connect GUIDE`. Details: `references/hub.md`.

## Files

| Path | What |
|---|---|
| `engine/` | Build engine, copied into each guide as `build/`: `build.py`, `layout.py`, `diagram.py`, `icons.py` (+ `icons/`), `styles.css`, `tokens.css`, `depth.css`, and the page scripts |
| `hub/` | Guide hub engine, copied into each hub as `build/`: `build.py`, `nav.src.js` (the Guides menu and reading position, written out as `nav.js`), and the `hub_config.py` template |
| `starter/` | New-guide template: `guide_config.py`, `diagrams.py`, `shots.py`, `PROGRESS.md`, skeleton `sections/` |
| `scripts/` | `new_guide.py` scaffold (also `--topic` / `--into` for topic-explainer) · `new_hub.py` guide hub (and `--connect`) · `qa_check.py` headless Chrome checks · `extract_text.py` text + glossary candidates · `merge_glossary.py` · `changed_since.py` stale sections · `fetch_icons.py` |
| `references/` | `workflow.md` phase details · `sections.md` catalog · `authoring.md` HTML/diagram/styling · `agent-prompts.md` · `screenshots.md` · `sharing.md` · `hub.md` guide hubs · `lessons.md` tooling gotchas |
| `apps-script/Code.gs` | Optional: serve the guide from Google Drive to signed-in company accounts |
| `PROMPT.md` | Kickoff prompt for agents that don't load skills |

Requirements: Python 3.9+ and Google Chrome or Chromium (for `qa_check.py` and screenshots).
