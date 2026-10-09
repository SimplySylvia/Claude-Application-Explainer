# Kickoff prompt: build a Product & Engineering Guide for this app

Copy everything below the line into an agent session opened in the application's repository. In Claude Code with the
application-explainer plugin installed, you can just say "use the application-explainer skill" instead.

---

Build an internal Product & Engineering Guide for the application in this repository, using the application-explainer skill at
`<path-to-clone>/skills/application-explainer` (from the application-explainer plugin repo) (read its SKILL.md and references/ first; use its engine and scripts).

Goal: one self-contained HTML file that takes a new engineer or PM from "what is this app" to "how is it built, run,
shipped, and worked on", organized as Product → Engineering → Operations → Working process → Reference, with diagrams,
a site map with every route, a features table, a glossary with hover definitions, search, and optional screenshots.

Rules:
- Treat this repository as read-only. Create the guide in its own folder outside the repo (default: a sibling
  `<repo>-guide/` folder with its own git repo) via `scripts/new_guide.py`.
- Verify every claim against the code and cite repo paths. Leave out anything you can't verify.
- Never reproduce secrets or personal/health data; report suspected secrets by file and line only.
- The guide is internal-only. Don't publish or share it anywhere public.
- Ask me before capturing screenshots, changing any account settings, granting OAuth permissions, or deploying anything.

Start by confirming with me: the app's name, the audience, where the guide should live, and whether you should capture
screenshots (which environment, and whether its data is synthetic). Then scaffold, map the repo, and show me the proposed
section outline before writing. Work in phases, build and run `scripts/qa_check.py` after each one, and commit the guide
folder as you go.
