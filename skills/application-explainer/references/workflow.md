# Workflow details, phase by phase

The phase numbers match the checklist in `SKILL.md`, which also gives each phase's **Done when** criteria. Each phase ends with a build (`python3 GUIDE/build/build.py`), an update to `GUIDE/PROGRESS.md`, a commit of the guide folder, and a short update to the user.

`GUIDE/PROGRESS.md` is the guide's memory across sessions: the ticked checklist, the scope answers, decisions (outline approved, sections dropped, review findings rejected and why), open questions, and repo problems to report. A resumed session reads it first.

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

It copies the engine to `GUIDE/build/`, the starter sections to `GUIDE/sections/`, fills in the app name, repo, branch, and commit (also recorded as `SOURCE_REPO` and `SOURCE_COMMIT` in `guide_config.py` for later updates), writes `PROGRESS.md`, and runs `git init`. Record the phase 0 answers under Scope in `PROGRESS.md`.

## 2 · Discover

Map the repo before writing anything:

- Read the README, docs, contributing guide, agent rules (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules`, `.claude/rules`), and package manifests.
- Map the top-level layout and any monorepo or project config. Find the router, the API layer (REST, GraphQL, RPC), the models or schema, IaC, CI workflows, and test configs.
- List the user-facing surfaces (web, mobile, extensions, CLIs) and the deployable services.

If the repo has more than about 1,000 tracked files (`git -C <repo> ls-files | wc -l`) or more than 3 deployable apps or services, run `repo-researcher` agents in parallel, one per area (`agent-prompts.md` §1). They return findings with paths and write nothing. Smaller repos are faster to research yourself.

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

1. `python3 SKILL_DIR/scripts/extract_text.py GUIDE/<name>-guide.html GUIDE/qa/glossary-work/` writes the guide text, the current terms with how often each is used (`glossary-usage.txt`), and regex candidates.
2. Run one `glossary-scout` (`agent-prompts.md` §5). It reads the guide as the audience would and writes `scout.md`: terms to **ADD**, terms that need an **EXPLAINER**, terms to **SKIP**, and existing rows to **FIX**.
3. Review the report yourself before drafting:
   - Spot-check the P1 ADD terms in the guide text: is each one really unclear to this audience?
   - Apply the FIX items to `sections/glossary.html` (remove unused rows, add missing names, rename risky aliases), or log why not.
   - **EXPLAINER terms:** show the user the list. For kind **topic** (a technology), offer a topic explainer, as a deep dive in this guide or a separate guide, and don't start one unless they say yes (the topic-explainer skill takes it from there). For kind **section** (an app concept), propose the new or expanded section. Log their answers in `PROGRESS.md`.
4. Run `glossary-drafter` agents, one per area that has ADD rows (§6). Each writes rows to its own draft file.
5. `python3 SKILL_DIR/scripts/merge_glossary.py GUIDE/sections/glossary.html GUIDE/qa/glossary-work/gl-*.html` and review the duplicates and names it prints.
6. Rename aliases that are everyday words or collide with other meanings (e.g. "PR" = pull request vs public relations). The first mention of every term in each section is auto-linked.
7. Re-run with `--write`, rebuild, then check the most-linked terms for false matches.

## 7 · QA

Run `scripts/qa_check.py` on both outputs, the full guide and `-no-screenshots`. It must print PASS, and the TODO count must be zero.

## 8 · Share

Share internally only (`sharing.md`). Record how it was shared (link, file ID, access level) in the guide README.

## Updating a guide later

Follow "Updating an existing guide" in `SKILL.md`: `scripts/changed_since.py GUIDE` lists the sections that cite files changed since `SOURCE_COMMIT`, plus changed files no section cites. Re-verify those, rebuild, run QA, then `changed_since.py GUIDE --mark` to record the new commit. Guides scaffolded before `SOURCE_COMMIT` existed can add `SOURCE_REPO` and `SOURCE_COMMIT` to `guide_config.py` by hand (the commit in the footer is where they were built from).
