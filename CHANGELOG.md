# Changelog

All notable changes to this plugin. Versions match `version` in `.claude-plugin/plugin.json`; update an installed
copy with `/plugin marketplace update`.

## 1.2.0 (2026-10-13)

### Skill

- **Done when** criteria for every phase in `SKILL.md`, including when to fan out to `repo-researcher` agents
  (more than about 1,000 tracked files or 3 deployables) and how many review findings to spot-check.
- `GUIDE/PROGRESS.md`: the scaffold writes the phase checklist plus sections for scope, decisions, open questions,
  and repo problems. Claude keeps it current, and a resumed session reads it first.
- Updating an existing guide: `guide_config.py` records `SOURCE_REPO` and `SOURCE_COMMIT`, and the new
  `scripts/changed_since.py` lists the sections that cite files changed since then (`--mark` records the new commit).
- The build warns about finished sections that cite no repo paths.
- Diagrams wider than the page now fade at the cut-off edge and show a "scroll sideways or Expand" hint, instead of
  being silently cut off on laptop-sized windows. `qa_check.py` adds a 1280×800 pass that fails if a hint is missing.
- Fixed an unclosed file handle in `engine/icons.py`.

### Repo

- Evals: `safety-secret-not-reproduced` (a hardcoded credential is reported by file, never copied) and
  `safety-screenshots-ask-first` (asks whether staging data is synthetic before capturing).
- Live demo guide for the fictional Shopfront app on GitHub Pages, rebuilt by `docs/demo/make-demo.sh`, which
  also recaptures the README screenshots.
- Unit tests (`tests/`, standard library `unittest`) for scaffolding, building, diagram geometry warnings, and
  glossary merging.
- GitHub Actions CI: unit tests on Python 3.9 and 3.13, the demo build with `qa_check.py`, a check that the
  committed demo is up to date, and a check that pull requests changing `skills/` or `agents/` bump the version.
- End-to-end eval: a new `repo-untouched-bash` grader fails the run if a shell command modifies the app repo.
- README rewrite with badges, quick start, and guardrails; workflow diagram and agent roles in
  `docs/HOW-IT-WORKS.md`.
- MIT license, issue templates, and a pull request template.

## 1.1.0 (2026-10-09)

- Restructured `SKILL.md` around a nine-phase checklist (scope → share) with approval gates, and aligned
  `references/workflow.md` and `PROMPT.md` with it.
- Added subagents: `repo-researcher`, `structure-reviewer`, and `section-verifier` (read-only), and
  `glossary-drafter`.
- Added the `claude plugin eval` suite: trigger, near-miss, and end-to-end cases on a fixture app.
- Fixed a dead `design-tokens.md` reference, made screenshot compression and email scrubbing portable,
  generalized sharing options and domain-specific wording, and added usage errors to the glossary scripts.

## 1.0.0 (2026-10-09)

- First release: the application-explainer skill (build engine, starter template, scaffold, QA, and glossary
  scripts) packaged as a Claude Code plugin with a single-plugin marketplace.
