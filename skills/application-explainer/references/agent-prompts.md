# Agent prompts

The plugin ships four agents whose rules (read-only, cite paths, no secrets) are built in, and whose tools are limited so they can't edit the app repo:

| Agent | Tools | Used in |
|---|---|---|
| `repo-researcher` | Read, Grep, Glob | 2 · Discover |
| `structure-reviewer` | Read, Grep, Glob | 4 · Review |
| `section-verifier` | Read, Grep, Glob | 4 · Review |
| `glossary-drafter` | Read, Grep, Glob, Write (its draft file only) | 6 · Glossary |

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

## 5. Glossary drafting (`glossary-drafter`, one per area: domain, product, engineering, internal/process)

```
Draft glossary rows for the guide at {GUIDE}, area: {AREA}. Repo: {REPO}.
Inputs: {WORK}/guide-text.txt, current glossary {GUIDE}/sections/glossary.html, candidates {WORK}/candidates.txt.
Cover every term in your area a reader meets in the guide that the glossary doesn't.
Write ONLY to {WORK}/gl-{AREA_SLUG}.html.
```

Merge the drafts with `scripts/merge_glossary.py`.

## 6. Applying review findings (you, not an agent)

- Spot-check every P1 claim yourself before editing. Agents can misread code.
- Fix the guide text. Never "fix" the app repo; list repo problems for the user instead.
- Rebuild, re-run QA, and summarize what changed and what was rejected.
