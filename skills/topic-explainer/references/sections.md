# Topic section catalog

The **core** sections ship as skeletons in `starter/sections/`. Drop any that don't apply (for example, recipes for a technology nobody changes day to day). Write the **optional** ones from scratch with the patterns in `AE_DIR/references/authoring.md` and add them to `PARTS`. In a deep dive, every id starts with the topic slug (`graphql-usage`), and so do links between them.

| id | Core? | Answers | Where to look | Shape |
|---|---|---|---|---|
| `overview` | core | What is it, what problem does it solve, what is it compared with, why does this app use it? | tech-researcher summary; repo README, ADRs, or comments for "why" | 3–4 cards |
| `concepts` | core | The 5–10 ideas needed to read the code, each linked to the versioned docs and to where it shows up here, with a code example each | tech-researcher concepts and examples; repo usages | Grouped table: concept · meaning · in app · docs, then "Concepts in code" blocks |
| `usage` | core | Every place the app uses it, and how much depends on it | Imports, config, codegen, wrappers, tests, CI | Flow diagram + grouped table |
| `walkthrough` | core | One real flow, step by step through the code, matching the diagram numbers | The files along that flow | Numbered `<h3>` steps, each with a repo excerpt + "Try it yourself" |
| `conventions` | core | How this repo's use differs from the docs' defaults, and the mistakes it guards against | Wrappers, lint rules, comments, ADRs, review rules | 2 cards |
| `recipes` | core | The everyday changes and how to test them | Package scripts, codegen commands, tests, recent commits touching it | Table: task · steps · where |
| `versions` | core | Exact versions here vs. latest stable, and what changed in between that matters | Lockfile + manifest; release notes | Table + caption |
| `resources` | core | Where to read next, official first, each with the date checked | tech-researcher resources | Grouped table |
| `glossary` | core (separate guide only) | Every term a reader meets | The guide text + repo + docs | Grouped table |
| `request` | optional | Lifecycle of one request or render inside the technology (phases, hooks, caching) | Official docs; the app's middleware or plugins | Numbered diagram + step table |
| `testing` | optional | How the app tests code that uses it: tools, mocks, fixtures | Test configs and helpers | Table + cards |
| `perf` | optional | Performance and security knobs the app sets, and why | Config, docs' production checklist | Table |
| `alternatives` | optional | What else was considered, or what parts of the app use something else | ADRs, other packages in the manifests | Table |

## Code examples

Readers learn a tool faster from code than from definitions, so topic guides show both kinds:

- **Concept examples** (concepts section): one short block per core concept, showing the idea on its own, e.g. "make an API call", "define a route", "handle an error". Base them on the official docs for the pinned version (the `tech-researcher` report has examples with URLs), simplify freely, and title them "Example (v4 docs)" with the docs link in the text. Prefer the app's own naming and style when it doesn't hide the concept.
- **Repo excerpts** (walkthrough, conventions, recipes): the actual lines, titled `path:start-end`, trimmed to what the step discusses.
- **Commands** (recipes, "Try it yourself"): `bash` blocks with commands that exist in package scripts or the tool's CLI; requests against a local server only (`localhost`), never staging or production.

Use the language of the code (`js`, `python`, `bash`, `json`, `sql`, `http`, …). Keep each block to about 15 lines. Use placeholders (`<your-token>`, `42`) instead of real tokens, hostnames, or data.

## Verification notes

- **Versions** come from the lockfile, not the manifest range. Cite both.
- **Behavior claims** ("X caches by default") need the versioned docs page. Defaults change between majors.
- **Counts** ("about 40 resolvers") come from a command; say "about" and how you counted.
- **"Why we use it"** needs evidence in the repo (README, ADR, comment). Otherwise leave it out rather than guess.
- **Code examples** must use the pinned version's API (an Express 4 guide shouldn't show Express 5-only syntax), and repo excerpts must match the cited lines.
