# Kickoff prompt: build a Product & Engineering Guide for this app

For agents that don't load Claude Code plugins. Copy everything below the line into a session opened in the application's repository, and replace `<path-to-clone>`. In Claude Code with the plugin installed, just ask for an onboarding guide or explainer instead.

---

Build an internal Product & Engineering Guide for the application in this repository with the application-explainer skill at `<path-to-clone>/skills/application-explainer`.

Read its `SKILL.md` first and follow it: its rules apply to the whole task, and its checklist is the plan. Wherever it says `SKILL_DIR`, use that folder. Read the files under `references/` when a step points to them, and use the skill's `engine/` and `scripts/` instead of writing your own.

The most important rules: treat this repository as read-only, put the guide in its own folder outside it, verify every claim against the code, never reproduce secrets or personal data, keep the guide internal, and ask me before capturing screenshots, changing account settings, granting OAuth permissions, or deploying anything.

Start by confirming scope with me (app name, audience, guide location, screenshots), then follow the checklist.
