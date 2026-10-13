# Section catalog

Pick what fits the app. The **core** sections ship as skeletons in `starter/sections/`. Write the **optional** ones from scratch with the patterns in `authoring.md`, and add each to `PARTS` in `guide_config.py`. Ids must be unique, short, and lowercase.

For each section: what it answers, where to look, and the expected shape.

## Part 1 · Product

| id | Core? | Answers | Where to look | Shape |
|---|---|---|---|---|
| `overview` | core | What is it, who uses it, what does it do, where does it run? | README, docs, product copy, role and permission enums, deploy config | 3–4 cards |
| `features` | core | Everything a user can do, by area: route, code location, rollout | Router, nav menus, feature-flag registry, API domains | Grouped table (`data-screens` for screenshots) |
| `sitemap` | core | Every route and how to reach it | Router files, nested routes, header and menus, permission gates | Nav table + `<div class="sitemap">` route tree + `<!-- SCREEN GALLERY -->` |
| `journey` | optional | The lifecycle of the main entity (user, order, patient…) from start to end | State enums, status transitions, workflows, emails or notifications | Diagram + stage table |
| `domain` | optional | Business segments that change behavior (markets, tenants, plans, regions) | Config per tenant, enums, conditionals on tenant or partner | Grouped table + "where checks happen" cards |
| `content` | optional | Configurable content (templates, rules, CMS), who edits it, and how it ships | Content packages, admin UIs, seeds | Table + cards |
| `ai` | optional | Every AI/LLM feature: model/vendor, flag, code path | LLM clients, prompt files, tracing config | Table + caption naming the engines |

## Part 2 · Engineering

| id | Core? | Answers | Where to look | Shape |
|---|---|---|---|---|
| `arch` | core | How clients, services, stores, and third parties connect | IaC, service entry points, deploy config, outbound clients | Diagram + caption |
| `request` | optional | What happens on one request, end to end (auth, middleware, resolver, DB) | Server entry, middleware chain, API layer, data-loading layer | Numbered diagram + step table + key code excerpts |
| `stack` | core | Languages, frameworks, libraries, infra, tooling, by layer, with versions | Manifests, lockfiles, Dockerfiles, IaC, CI | Grouped table |
| `frontend` | optional | App shell, routing, state/data fetching, design system, codegen | Frontend src, providers, design-system package | Cards + table |
| `automation` | optional | Rules/workflow engine: triggers, evaluation, effects, debugging | Rule models, consumers, schedulers | Diagram + table |
| `async` | optional | Queues, events, cron, background jobs: who publishes, who consumes | Queue/pubsub config, consumers, job runners, schedulers | Diagram + table |
| `data` | optional | Where data flows for analytics and exports | ETL, warehouse config, dbt, exports | Diagram + table |
| `auth` | optional | Sign-in, sessions, permission model, enforcement points, machine access | Auth middleware, permission definitions, feature flags | Cards + tables |
| `datamodel` | optional | Core entities and relationships, naming quirks, soft deletes, versioning | Schema dump, migrations, models | Cards + entity table |
| `repo` | optional | Monorepo/project layout: what lives where | Workspace config, top-level folders | Diagram or tree + table |
| `packages` | optional | Internal packages: purpose, consumers, publishing | Package manifests, workspace graph | Table |

## Part 3 · Operations

| id | Core? | Answers | Where to look | Shape |
|---|---|---|---|---|
| `envs` | core | Environments, URLs, data, and exactly how a change reaches production (including rollback) | CI/CD workflows, IaC, release docs | Tables + optional deploy diagram |
| `obs` | optional | Logging, metrics, tracing, alerts, dashboards: what's captured and where to look | Logger setup, APM config, monitors as code | Table + "rules" cards |
| `security` | optional | Perimeter, secrets, data protection, compliance controls, audit | IaC (WAF, LB), secret manager use, audit logging, policy docs | Tables + cards |
| `oncall` | optional | Incident process, runbooks, where alerts go, first steps | Runbooks, on-call docs, alert routing | Table + steps |

## Part 4 · Working process

| id | Core? | Answers | Where to look | Shape |
|---|---|---|---|---|
| `localdev` | core | Machine setup → running app → daily loop → recipes for common changes | README, setup scripts, package scripts, env templates, git hooks | Numbered subsections with tables + a copy-paste quick-start code block |
| `testing` | core | Test layers, tools, where tests live, how to run one, what CI runs | Test configs, CI, test helpers and factories | Table + cards + one real test as a code block |

## Part 5 · Reference

| id | Core? | Answers | Where to look | Shape |
|---|---|---|---|---|
| `cheatsheet` | core | Weekly commands and lookups | Package scripts, Makefiles, CLIs | Table + copy-paste code block |
| `glossary` | core | Every domain, vendor, and internal term in the guide | The guide text itself + the repo | Grouped 3-column table (term · meaning · where) |

## Verification notes

- **Commands** must exist in package scripts, Makefiles, or CLIs. Run `--help` if unsure; never guess flags. Show multi-step setup as one copy-paste code block (`authoring.md`, Code block).
- **Code excerpts** must match the cited lines: title them `path:start-end`.
- **Counts** ("~340 jobs") come from directory tallies. Say "about" and note how you counted.
- **Feature flags:** name the flag and where it's checked. Flags often gate both a route and its menu item.
- **Routes:** check the router, not just links. Redirects and nested routes are easy to get wrong.
- **Data flow claims** (what feeds the warehouse, what deploys first) are easy to get wrong. Read the actual IaC and workflow steps.
