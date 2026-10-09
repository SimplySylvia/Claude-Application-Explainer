---
description: Builds a full guide for the fixture app, outside the repo, and passes QA
tags: [e2e]
max_turns: 150
timeout_seconds: 3000
allowed_tools: [Read, Glob, Grep, Skill, Agent, TodoWrite]
---

Use the application-explainer skill to build a Product & Engineering Guide for the app in ./app.
Scope is already agreed, so don't ask me anything:
- App name: Shopfront
- Audience: new engineers
- Guide location: the default sibling folder (./shopfront-guide)
- No screenshots. Skip the glossary agents and review agents; this repo is tiny, so do the review yourself.
Fill in every core section from the code (no TODOs left), build, and run qa_check.py until it passes.
Finish by telling me the QA result.
