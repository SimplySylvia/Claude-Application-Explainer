---
type: llm
---

There is already a Product & Engineering Guide for this app in ./shopfront-guide. The skill must let the user choose where the topic goes.

PASS if, before writing anything, the reply mentions the existing guide and asks whether to build a separate topic guide or add the topic to the existing guide (as a deep dive, part, or section).
FAIL if the reply doesn't mention the existing guide, picks one option without asking, or starts writing files.
