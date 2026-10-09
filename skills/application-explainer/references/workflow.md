# Workflow: building a guide for an application

Work in phases. Each phase ends with a build (`python3 build/build.py`), a QA run (`scripts/qa_check.py`), and a short update to the user. Commit the guide folder after each phase.

## Phase 0 — Agree on scope (ask the user)

Confirm before doing any work:

- **App name and repo path.** The repo is **read-only**: never edit, commit to, or run mutating commands in it. Only read files and run read-only git commands.
- **Audience.** New engineers, product, ops, or all of them? This decides how deep the engineering parts go.
- **Where the guide lives.** Default: a sibling folder `<repo>-guide/`, its own git repo. Never inside the app repo.
- **Screenshots.** Is there a running environment (staging or local) the user is signed into in Chrome? Is its data synthetic? If it may hold real personal or health data, don't capture without explicit confirmation, and scrub anyway.
- **Sensitivity.** The guide documents internal architecture and security controls, so treat it as internal-only (see `sharing.md`).

Then scaffold:

```bash
python3 <skill>/scripts/new_guide.py --repo /path/to/repo --app "Name" [--dest /path/to/name-guide]
```

## Phase 1 — Discover the app

Map the repo before writing anything:

- Read the README, docs, contributing guide, agent rules (`CLAUDE.md`, `.cursor/rules`, `.claude/rules`), and package manifests.
- Map the top-level layout and the monorepo or project config. Find the router, the API layer (REST, GraphQL, RPC), the models or schema, IaC, CI workflows, and test configs.
- List the user-facing surfaces (web, mobile, extensions, CLIs) and the deployable services.

For big repos, fan out read-only research agents, one per area, using the prompts in `agent-prompts.md`. Each agent returns findings with repo paths; nothing is written yet.

Pick the parts and sections from `sections.md` that fit this app, and drop the ones that don't apply. Write `PARTS` in `guide_config.py` in narrative order: **Product → Engineering → Operations → Working process → Reference**. Show the user the section list before writing.

## Phase 2 — Write the sections

- Work section by section, or one agent per section, following `authoring.md`.
- Every claim is verified in the repo: cite paths in a Where/Code column or the `Sources:` line. If you can't verify something, leave it out or mark it as unverified.
- Prefer tables and short bullets. Each section should be scannable in about 2 minutes.
- Draw diagrams in `diagrams.py` and fix every geometry warning the build prints.
- Set collapse defaults in `guide_config.py`: overviews open; deep dives, long reference tables, and the glossary collapsed.

## Phase 3 — Review and verify

Run review agents (prompts in `agent-prompts.md`):

1. **Structure review:** order, gaps, duplication, what a newcomer would miss.
2. **Per-section verification:** check each claim against the repo and report wrong, stale, or missing items with evidence.

Apply the fixes. For claims an agent flags, spot-check the key ones yourself before changing text. Agents can be wrong too.

Report repo problems you notice (stale docs, suspicious config, possible secrets) to the user instead of fixing them. **Never quote secret values.**

## Phase 4 — Screenshots (optional)

Follow `screenshots.md`:

1. Capture each screen.
2. Map the screenshots to features in `shots.py`.
3. Add the `<!-- SCREEN GALLERY -->` placeholder to the site map section.
4. Mark the features table with `data-screens`.

List what couldn't be captured, and why, in `NOT_CAPTURED`. Tell the user what would unblock each one: roles, flags, or test data.

## Phase 5 — Glossary

1. Run `scripts/extract_text.py <guide>.html qa/glossary-work/` to get the guide text and candidate terms.
2. Fan out glossary agents by area (`agent-prompts.md`). Each one writes rows to a draft file.
3. Run `scripts/merge_glossary.py sections/glossary.html drafts/*.html` and review the duplicates and names it prints.
4. Rename aliases that are everyday words, or that collide with other meanings (e.g. "MA" = Massachusetts vs Medicare Advantage). The first mention of every term in each section is auto-linked.
5. Re-run with `--write`, rebuild, then check the most-linked terms for false matches.

## Phase 6 — Ship

- Run `scripts/qa_check.py` on both outputs, the full guide and `-no-screenshots`.
- Share internally only (`sharing.md`). Record how it was shared in the guide README.

## Updating later

Re-run discovery for whatever changed, edit the sections, rebuild, run QA, and re-upload the file. To pick up engine fixes, re-copy `<skill>/engine/` over `build/`. Keep a custom `tokens.css` or `icons.py` registrations if the guide has them.
