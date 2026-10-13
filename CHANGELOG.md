# Changelog

All notable changes to this plugin. Versions match `version` in `.claude-plugin/plugin.json`; update an installed
copy with `/plugin marketplace update`.

## 1.3.0 (2026-10-13)

### Skill

- New **topic-explainer** skill: a smaller guide to one technology and how the app uses it. It covers what the
  technology is, core concepts, a usage map and flow diagram, a guided walkthrough of one real flow, patterns and
  gotchas, common changes, the pinned version compared with the latest release, and official docs. It runs only
  when asked for by name (`/topic-explainer`, "topic explainer") or after the user accepts an offer; a plain "what is
  X and how do we use it" question gets a direct answer.
- Topic guides can be **separate** (`<app>-<topic>-guide/`, the default) or a **deep dive** inside an existing
  application-explainer guide. When a guide for the repo exists, Claude asks which.
- New agents `tech-researcher` (web search and fetch only, never sees the repo; prompts carry only the technology,
  version, and generic questions) and `source-verifier` (checks web claims against the cited pages).
- `new_guide.py --topic "<Topic>"` scaffolds a topic guide; `--into <guide>` adds the topic as one part before
  Reference, with `<topic>-` prefixed sections, a `TOPICS` entry, a diagram, and a checklist in `PROGRESS.md`.
- `changed_since.py` reports `DOCS STALE` for topics whose docs were never checked or were checked more than 90 days
  ago; `--mark-docs <slug>` records a re-check.
- The build opens outside links in a new tab (marked ↗) and counts them as citations. Section ids may contain
  hyphens.
- **Code blocks with syntax highlighting** in any guide: `<pre class="code" data-lang="js" data-title="…">`,
  highlighted at build time by the new `engine/highlight.py` (JavaScript/TypeScript/JSX, Python, shell, JSON, SQL,
  YAML, HTTP, GraphQL), with a language label, title, Copy button, and colors for both themes. Nothing is loaded
  from outside the file. The build warns on unknown languages and on a bare `<pre>`.
- Topic guides show concepts in code: the concepts section has a "Concepts in code" example per idea, and the
  walkthrough and recipes quote the repo lines they discuss.
- `tech-researcher` returns a fixed-shape report of about 1,000 words, with code examples for the pinned version.
  Claude saves it to `GUIDE/research/<topic>.md` and spot-checks key claims by opening the cited pages (the rule is
  that nothing from the repo goes to the web, not that only agents may fetch).
- Walkthroughs say where a flow stops when the code doesn't run end to end, and "Try it yourself" lists only steps
  that work as the repo stands.
- The application-explainer starter uses code blocks too: a copy-paste quick start in Local development, one real
  test in Testing strategy, and the weekly commands in the Cheat sheet.

### Repo

- Evals: `trigger-topic-explainer`, `nearmiss-topic-question` (answers and offers, doesn't start a guide),
  `topic-asks-guide-mode` (asks separate guide vs deep dive when a guide exists), and `safety-topic-web-queries`
  (no repo details in web searches, fetches, or the researcher's prompt; the pinned version is documented).
- Unit tests for topic scaffolding, deep dives, external links, docs freshness, and syntax highlighting.
- The live demo has an **Express deep dive** (part 5) built with the topic explainer, linked from its Tech stack and
  Architecture sections, plus code blocks in Local development, Testing, and the Cheat sheet.
- New README screenshots of the deep dive (`guide-topic.png`, `guide-topic-code.png`, `guide-topic-link.png`),
  captured by `docs/demo/capture.py`.

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
