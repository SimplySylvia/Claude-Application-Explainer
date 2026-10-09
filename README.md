# application-explainer

A Claude Code plugin that builds an internal, self-contained HTML **Product & Engineering Guide** for whatever
application repo you're in: product overview, features, site map, architecture diagrams, tech stack, environments,
local dev, testing, a glossary with hover definitions, search, and optional screenshots. Every claim is verified
against the code.

## Install

This repo is both the plugin and a single-plugin marketplace. In Claude Code:

```
/plugin marketplace add SimplySylvia/Claude-Application-Explainer
/plugin install application-explainer@application-explainer
```

Or from a local clone:

```
/plugin marketplace add /path/to/application-explainer
/plugin install application-explainer@application-explainer
```

To try it without installing: `claude --plugin-dir /path/to/application-explainer`.

## Use

Open Claude Code in the app repo you want documented and ask for an explainer, onboarding guide, or system overview
(or say "use the application-explainer skill"). The skill confirms scope with you, scaffolds a guide folder *outside*
the app repo, and works in phases.

Requirements: Python 3 and Google Chrome (for `qa_check.py` and screenshots).

For agents that don't load plugins, see [`skills/application-explainer/PROMPT.md`](skills/application-explainer/PROMPT.md).

## Layout

| Path | What |
|---|---|
| `.claude-plugin/plugin.json` | Plugin manifest |
| `.claude-plugin/marketplace.json` | Marketplace manifest (lists this repo as its only plugin) |
| `skills/application-explainer/` | The skill: `SKILL.md`, build `engine/`, `starter/` template, `scripts/`, `references/` |
| `agents/` | Read-only subagents the skill fans out to: `repo-researcher`, `structure-reviewer`, `section-verifier`, `glossary-drafter` |
| `evals/` | `claude plugin eval` suite: trigger, near-miss, and end-to-end cases on a small fixture app |

## Testing the skill

The suite in `evals/` runs against a small fictional app that `evals/_fixture/make-app.sh` creates.

```bash
# Trigger and near-miss cases: does the skill fire when it should, and stay out of the way when it shouldn't?
claude plugin eval . --tag trigger nearmiss --scaffold

# End to end: builds a whole guide and runs QA (slow; grants the tools the build needs)
claude plugin eval . --tag e2e --scaffold --runs 1 --allow-tools Bash Write Edit
```

Run the trigger and near-miss cases after any change to the skill's `description`.

## Releasing

Bump `version` in `.claude-plugin/plugin.json` when you change the skill; users pick it up with
`/plugin marketplace update`.

Internal only — the guides it produces must not be shared publicly (see `skills/application-explainer/references/sharing.md`).
