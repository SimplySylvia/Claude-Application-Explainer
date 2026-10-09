# Workflow details, phase by phase

The phase numbers match the checklist in `SKILL.md`. Each phase ends with a build (`python3 GUIDE/build/build.py`), a commit of the guide folder, and a short update to the user.

## 0 · Scope (ask the user)

Confirm before doing any work:

- **App name and repo path.** The repo is read-only: never edit, commit to, or run mutating commands in it.
- **Audience.** New engineers, product, ops, or all of them? This decides how deep the engineering parts go.
- **Where the guide lives.** Default: a sibling folder `<repo>-guide/`, its own git repo. Never inside the app repo; `new_guide.py` refuses that.
- **Screenshots.** Is there a running environment (staging or local) the user is signed into in Chrome? Is its data synthetic? If it may hold real personal data, don't capture without explicit confirmation, and scrub anyway.

## 1 · Scaffold

```bash
python3 SKILL_DIR/scripts/new_guide.py --repo /path/to/repo --app "Name" [--dest /path/to/name-guide]
```

It copies the engine to `GUIDE/build/`, the starter sections to `GUIDE/sections/`, fills in the app name, repo, branch, and commit, and runs `git init`.

## 2 · Discover

Map the repo before writing anything:

- Read the README, docs, contributing guide, agent rules (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules`, `.claude/rules`), and package manifests.
- Map the top-level layout and any monorepo or project config. Find the router, the API layer (REST, GraphQL, RPC), the models or schema, IaC, CI workflows, and test configs.
- List the user-facing surfaces (web, mobile, extensions, CLIs) and the deployable services.

For big repos, run `repo-researcher` agents in parallel, one per area (`agent-prompts.md` §1). They return findings with paths and write nothing.

Pick the sections from `sections.md` that fit this app and drop the ones that don't apply. Write `PARTS` in `guide_config.py` in narrative order: Product → Engineering → Operations → Working process → Reference. Show the user the section list before writing.

## 3 · Write

- Work section by section, or one general-purpose agent per section (`agent-prompts.md` §2), following `authoring.md`.
- Cite paths in a Where/Code column or the `Sources:` line. If you can't verify something, leave it out or mark it unverified.
- Prefer tables and short bullets. Each section should be scannable in about 2 minutes.
- Draw diagrams in `diagrams.py` and fix every geometry warning the build prints.
- Set collapse defaults in `guide_config.py`: overviews open; deep dives, long reference tables, and the glossary collapsed.

## 4 · Review

1. **Structure review** (`structure-reviewer`, §3): order, gaps, duplication, what a newcomer would miss.
2. **Per-section verification** (`section-verifier`, §4): each claim checked against the repo; wrong, stale, or missing items with evidence.

Spot-check the key flagged claims yourself before changing text. Report repo problems (stale docs, suspicious config, possible secrets) to the user instead of fixing them. Never quote secret values.

## 5 · Screenshots (optional)

Follow `screenshots.md`: capture each screen, map them in `shots.py`, add the `<!-- SCREEN GALLERY -->` placeholder to the site map, and mark the features table with `data-screens`. List what couldn't be captured in `NOT_CAPTURED`, and tell the user what would unblock each one (role, flag, or test data).

## 6 · Glossary

1. `python3 SKILL_DIR/scripts/extract_text.py GUIDE/<name>-guide.html GUIDE/qa/glossary-work/` writes the guide text and candidate terms.
2. Run `glossary-drafter` agents by area (§5). Each writes rows to its own draft file.
3. `python3 SKILL_DIR/scripts/merge_glossary.py GUIDE/sections/glossary.html GUIDE/qa/glossary-work/gl-*.html` and review the duplicates and names it prints.
4. Rename aliases that are everyday words or collide with other meanings (e.g. "PR" = pull request vs public relations). The first mention of every term in each section is auto-linked.
5. Re-run with `--write`, rebuild, then check the most-linked terms for false matches.

## 7 · QA

Run `scripts/qa_check.py` on both outputs, the full guide and `-no-screenshots`. It must print PASS, and the TODO count must be zero.

## 8 · Share

Share internally only (`sharing.md`). Record how it was shared (link, file ID, access level) in the guide README.

## Updating a guide later

Re-run discovery for whatever changed, edit the sections, rebuild, run QA, and re-upload. To pick up engine fixes, re-copy `SKILL_DIR/engine/` over `GUIDE/build/`, keeping any custom `tokens.css` or `icons.py` registrations.
