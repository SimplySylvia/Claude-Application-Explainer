# Kickoff prompt: build a topic guide for one technology in this app

For agents that don't load Claude Code plugins. Copy everything below the line into a session opened in the application's repository, and replace `<path-to-clone>` and `<Topic>`. In Claude Code with the plugin installed, run `/topic-explainer` instead.

---

Build an internal topic guide about <Topic> and how this repository uses it, with the topic-explainer skill at `<path-to-clone>/skills/topic-explainer`.

Read its `SKILL.md` first and follow it: its rules apply to the whole task, and its checklist is the plan. Wherever it says `TOPIC_DIR`, use that folder; wherever it says `AE_DIR`, use `<path-to-clone>/skills/application-explainer`. Use the scripts and engine there instead of writing your own.

The most important rules: treat this repository as read-only, never put anything from it (names, paths, code, config, data) into a web search or URL, cite the official docs for the version this repo pins, never reproduce secrets or personal data, and keep the guide internal.

Start by confirming scope with me (topic, audience, the version the repo uses, and, if a guide for this repo already exists, whether to add the topic to it or build a separate guide), then follow the checklist.
