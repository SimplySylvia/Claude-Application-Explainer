# Agent prompts

The plugin ships these agents. Their rules (read-only, cite paths, no secrets) are built in, and their tools are limited so they can't edit the app repo:

| Agent | Tools | Used in |
|---|---|---|
| `repo-researcher` | Read, Grep, Glob | 2 · Discover |
| `structure-reviewer` | Read, Grep, Glob | 4 · Review |
| `section-verifier` | Read, Grep, Glob | 4 · Review |
| `glossary-scout` | Read, Grep, Glob, Write (its report file only) | 6 · Glossary |
| `glossary-drafter` | Read, Grep, Glob, Write (its draft file only) | 6 · Glossary |
| `tech-researcher`, `source-verifier` | Web search and fetch; never the repo | topic-explainer only |

Section writers (§2) need to edit and build, so they run as general-purpose agents with the ground rules pasted in.

Fill in the `{placeholders}`. Launch independent agents in the same message so they run in parallel. Subagents don't see this conversation, so every prompt must name the paths it needs.

Outside Claude Code (no plugin agents), use general-purpose agents and paste the matching agent file's body from the plugin's `agents/` folder into each prompt.

## Ground rules (for general-purpose agents only)

> - The repo at `{REPO}` is read-only. Don't edit, commit, or run mutating commands, and don't connect to deployed databases or services.
> - Verify every claim in repo sources and cite relative paths. If you can't verify something, leave it out and say so.
> - Never reproduce secret values; if you see one, report only its file and line. No personal data.
> - Write only to the output paths given.

## 1. Discovery (`repo-researcher`, one per area)

```
Research the {AREA} of the application in {REPO}.
Questions to answer: {QUESTIONS from sections.md for the relevant sections}.
Start from: {LIKELY PATHS, e.g. router files, IaC, CI workflows}. Explore beyond them as needed.
```

## 2. Section writer (general-purpose)

```
Write sections/{ID}.html for the guide at {GUIDE}. Read {SKILL_DIR}/references/authoring.md first and follow it exactly
(skeleton, indentation of <h3>, building blocks, escaping). Existing section ids you may link to: {IDS}.
Use these findings: {FINDINGS or path to them}. Re-verify anything you state against {REPO}.
{GROUND RULES}
Aim for something a new engineer can scan in ~2 minutes: tables and short bullets, paths in a Where/Code column.
When done, run: python3 {GUIDE}/build/build.py and fix any warnings that mention your section.
```

## 3. Structure review (`structure-reviewer`)

```
Review the guide built at {GUIDE}/{OUTPUT}.html. Text dump: {TEXT_DUMP}. Section files: {GUIDE}/sections/.
```

## 4. Section verification (`section-verifier`, one per section or small group)

```
Verify sections {IDS} of the guide (text dump: {TEXT_DUMP}; source: {GUIDE}/sections/) against the repo at {REPO}.
```

## 5. Glossary scouting (`glossary-scout`, one for the whole guide)

```
Scout the glossary for the guide at {GUIDE}. Audience: {AUDIENCE from PROGRESS.md}. Repo: {REPO}.
Inputs: {WORK}/guide-text.txt, {WORK}/glossary-terms.txt, {WORK}/glossary-usage.txt, {WORK}/candidates.txt,
and the glossary section {GUIDE}/sections/glossary.html.
{For a deep dive: "Focus on sections {TOPIC_SLUG}-*; the rest of the guide's glossary is already reviewed."}
Write ONLY to {WORK}/scout.md.
```

For a very large guide (more than about 15,000 words in `guide-text.txt`), run one scout per part, each given its section ids and its own report path (`scout-{PART}.md`).

## 6. Glossary drafting (`glossary-drafter`, one per area: domain, product, engineering, internal, vendor)

```
Draft glossary rows for the guide at {GUIDE}, area: {AREA}. Repo: {REPO}.
Terms to draft: the ADD rows for area "{AREA}" in {WORK}/scout.md (use the proposed names unless the repo shows a
better one), plus the short ADD rows for its EXPLAINER terms, linking to the explainer once it exists.
Context: {WORK}/guide-text.txt, current glossary {GUIDE}/sections/glossary.html.
Write ONLY to {WORK}/gl-{AREA_SLUG}.html.
```

Skip areas with no ADD rows. Merge the drafts with `scripts/merge_glossary.py`.

## 7. Applying review findings (you, not an agent)

- Spot-check every P1 claim yourself before editing. Agents can misread code.
- Fix the guide text. Never "fix" the app repo; list repo problems for the user instead.
- Rebuild, re-run QA, and summarize what changed and what was rejected.
