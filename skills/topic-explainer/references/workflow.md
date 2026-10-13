# Workflow details, phase by phase

The phase numbers match the checklist in `SKILL.md`, which also gives each phase's **Done when** criteria. Each phase ends with a build (`python3 GUIDE/build/build.py`), an update to `GUIDE/PROGRESS.md`, a commit of the guide folder, and a short update to the user.

## 0 · Scope (ask the user)

- **Topic and repo.** Name the technology precisely: "Apollo Client" and "GraphQL" are different guides. If the user's topic spans several packages (for example `graphql`, `@apollo/server`, `@graphql-codegen/cli`), list them and confirm.
- **Version.** Find each package in the manifests and read the resolved version from the lockfile. If the repo has several versions (a monorepo with two apps on different majors), say so and agree which one the guide follows.
- **Audience.** New engineers who've never used it, or experienced engineers new to this repo? This decides how long the concept part is.
- **Separate guide or deep dive.** Look for an existing guide: sibling folders matching `*-guide/` whose `guide_config.py` has `SOURCE_REPO` pointing at this repo, or one the user names. If you find one, ask which they want:
  - *Separate topic guide (default):* `<app>-<topic>-guide/`, own git repo, shared on its own. Best for a quick learning aid or when the main guide is owned by someone else.
  - *Deep dive in `<existing guide>`:* adds one part to it. Best when the team keeps that guide as its main internal doc, so the topic stays current alongside everything else, and updates and sharing happen once.
- **Location** for a separate guide: default sibling `<app>-<topic>-guide/`. Never inside the app repo; `new_guide.py` refuses that.

## 1 · Scaffold

`new_guide.py --topic` copies the topic starter and the engine, fills in the app, topic, repo, branch, and commit, adds the topic to `TOPICS` in `guide_config.py`, writes `PROGRESS.md`, and runs `git init`.

`new_guide.py --topic --into <guide>` instead:
- writes `sections/<topic-slug>-*.html` (the starter sections minus the glossary),
- inserts one part named "<Topic> deep dive" into `PARTS`, before the Reference part,
- adds the topic to `TOPICS`, appends its flow diagram to `diagrams.py`, and appends the topic checklist to `PROGRESS.md`.

It refuses to overwrite existing sections or add a topic that's already in `TOPICS`. Commit the existing guide before running it, and tell the user which files it changed.

## 2 · Discover

**Repo track** (you, or `repo-researcher` agents for big repos):
- Manifests and lockfiles for the packages and versions.
- Imports and entry points (`git -C <repo> grep -l "<package>"`), config files, code generation, wrappers or internal helpers built on top of it, lint rules, tests, and CI steps that involve it.
- Local conventions that differ from the docs' defaults. Comments and ADRs often explain why.
- One real, representative flow for the walkthrough: common enough that readers will meet it, small enough to follow in 4–7 steps.

**Web track** (`tech-researcher`, launched in the same message as any repo agents):

```
Research {TECHNOLOGY} version {VERSION} for an internal guide aimed at {AUDIENCE, e.g. "engineers who have never used it"}.
Also find the latest stable release and what changed between {VERSION} and it.
Specific questions: {GENERIC QUESTIONS, e.g. "how does request batching work", "what replaced the deprecated X API"}.
Concepts to show in code: {GENERIC TASKS, e.g. "define a route", "make a POST request with a JSON body", "handle an error"}.
```

The prompt contains only the technology, version, audience, and generic questions: no app name, paths, code, or config (`web-research.md`). Describe the code examples you need as generic tasks, never by pasting the app's code.

Save the report to `GUIDE/research/<topic-slug>.md` (it's committed with the guide, so the next update can see what was checked). Spot-check its key claims, at least the version facts and anything security-related, by opening the cited pages yourself: they're public docs, and the URLs carry nothing from the repo. Record the date and what you checked under Sources checked in `PROGRESS.md`, then `changed_since.py GUIDE --mark-docs <topic-slug>`.

Show the user the outline: the sections you'll keep, the flow the walkthrough follows, and the version gap.

## 3 · Write

- Follow `AE_DIR/references/authoring.md` for the skeleton, building blocks, and diagrams, and `sections.md` here for each section's shape.
- Concept sections (overview, concepts) explain the technology in general, then tie each idea to where it shows up in the repo. Cite official URLs inline; the "In <app>" column cites repo paths.
- In-app sections (usage, walkthrough, conventions, recipes) cite repo paths like any application-explainer section. Quote at most a few lines of code; point to the file instead.
- The walkthrough's steps match the numbers on the flow diagram, and each step quotes the few repo lines it's about in a code block titled with `path:lines`.
- **When the flow doesn't run end to end** (code that's stubbed, never wired up, or needs services you can't run locally): walk through what the code does today, and say plainly where it stops and what's missing, linking to the gotcha. Don't write the missing code into the walkthrough as if it existed. In "Try it yourself", give only steps that work as the repo stands (a test, a request against the local API, a dev-server URL), and name what would have to change for the rest. If nothing in the flow runs, say so and drop "Try it yourself".
- Versions and resources say the date you checked.

## 4 · Review

Launch in the same message:

- `section-verifier` on the usage, walkthrough, conventions, recipes, and versions sections (`AE_DIR/references/agent-prompts.md` §4).
- `source-verifier` on the overview, concepts, versions, and resources sections:

```
Verify the web-sourced claims in sections {IDS} of the guide (text dump: {TEXT_DUMP}; source: {GUIDE}/sections/).
The app runs {TECHNOLOGY} {VERSION}. Check every cited URL supports its claim for that version, and that the
"latest stable" facts are still current.
```

Make the text dump with `python3 AE_DIR/scripts/extract_text.py GUIDE/<output>.html GUIDE/qa/text/`. Apply findings as in application-explainer phase 4: spot-check every P1 yourself, fix the guide text, and log rejected findings in `PROGRESS.md`.

## 5–7 · Glossary, QA, share

Same as application-explainer phases 6–8 (`AE_DIR/references/workflow.md`). Glossary rows for topic terms cite either a repo path or the docs page. For a deep dive, the topic's terms go into the existing glossary in their own group, and sharing reuses the guide's recorded channel.
