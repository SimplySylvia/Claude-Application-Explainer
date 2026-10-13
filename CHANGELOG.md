# Changelog

All notable changes to this plugin. Versions match `version` in `.claude-plugin/plugin.json`; update an installed
copy with `/plugin marketplace update`.

## Unreleased

No changes to the skill or agents, so no version bump.

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
