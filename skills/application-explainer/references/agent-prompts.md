# Agent prompt templates

Fill in the `{placeholders}`. Run independent agents in parallel. Every agent gets the same ground rules:

> **Ground rules:**
> - The repo at `{REPO}` is read-only. Don't edit, commit, or run mutating commands, and don't connect to deployed databases or services.
> - Verify every claim in repo sources and cite relative paths. If you can't verify something, leave it out and say so.
> - Never reproduce secret values; if you see one, report only its file and line.
> - No personal or health data.
> - Write only to the output path given.

## 1. Discovery / research (one per area)

```
Research the {AREA} of the application in {REPO} for an internal product & engineering guide.
Questions to answer: {QUESTIONS from sections.md for the relevant sections}.
Start from: {LIKELY PATHS, e.g. router files, IaC, CI workflows}. Explore beyond them as needed.
{GROUND RULES}
Return: a findings list (claim → evidence path), a proposed table/card outline for the section(s), open questions,
and anything surprising or inconsistent (stale docs, dead code paths, config that contradicts docs).
```

## 2. Section writer

```
Write sections/{ID}.html for the guide at {GUIDE}. Read {SKILL}/references/authoring.md first and follow it exactly
(skeleton, indentation of <h3>, building blocks, escaping). Existing section ids you may link to: {IDS}.
Use these findings: {FINDINGS or path to them}. Re-verify anything you state against {REPO}.
{GROUND RULES}
Aim for something a new engineer can scan in ~2 minutes: tables and short bullets, paths in a Where/Code column.
When done, run: python3 {GUIDE}/build/build.py and fix any warnings that mention your section.
```

## 3. Structure review

```
Review the overall structure of the guide {GUIDE}/{OUTPUT}.html (text dump: {TEXT_DUMP}).
Judge: narrative order (product → engineering → operations → process → reference), gaps a new engineer or PM would hit,
duplication between sections, sections that are too long or should be split, and missing cross-links.
Return a prioritized list (P1 wrong/misleading, P2 missing, P3 polish) with concrete proposals. Don't edit files.
```

## 4. Section verification (one per section or small group)

```
Verify every factual claim in section(s) {IDS} of the guide (text dump: {TEXT_DUMP}; source: {GUIDE}/sections/).
Check each against {REPO}. For each problem give: the claim, verdict (wrong / stale / unverifiable / incomplete),
evidence (path:line), and a corrected wording. Also list important things the section is missing.
{GROUND RULES} Don't edit files.
```

## 5. Glossary drafting (one per area: domain, product, engineering, internal/process)

```
Draft new glossary rows for the guide at {GUIDE}. Area: {AREA}.
Inputs: guide text {WORK}/guide-text.txt, current glossary {GUIDE}/sections/glossary.html, candidates {WORK}/candidates.txt.
Find every term in your area a reader meets in the guide that the glossary doesn't cover. Define each as used in this app
(1–2 sentences, present tense), verified in {REPO}, with 1–2 real repo paths in the third column.
Naming: "Main name / Other name (expansion)"; parentheses starting with "as " are context. Use the guide's casing.
Avoid names that are everyday words or ambiguous acronyms (they get auto-linked everywhere).
{GROUND RULES}
Write ONLY rows to {WORK}/gl-{AREA_SLUG}.html, grouped with comments:
  <!-- GROUP: Existing group name -->   or   <!-- NEW GROUP: Name | icon-key | var(--c-run) -->
Final reply: row count per group, terms you dropped and why, and existing glossary rows you found inaccurate (with evidence).
```

Merge the drafts with `scripts/merge_glossary.py`.

## 6. Applying review findings (you, not an agent)

- Spot-check every P1 claim yourself before editing. Agents can misread code.
- Fix the guide text. Never "fix" the app repo; list repo problems for the user instead.
- Rebuild, re-run QA, and summarize what changed and what was rejected.
