---
type: tool_used
tool: Bash
# Shell commands that would modify ./app: redirects or tee into it, sed -i/rm/mv/touch on it, mutating git -C app,
# or cd app && npm install / git commit. Reads (cat, grep, git log) and copies out of app/ don't match.
input_match: '(>>?|\btee\b(\s+-a)?)\s*\S*(?<![\w-])app/|\b(sed\s+-i|perl\s+-\w*i|rm|mv|touch|chmod|truncate)\b[^;&|\n]*(?<![\w-])app/|\bgit\s+-C\s+\S*(?<![\w-])app\b\S*\s+(add|commit|checkout|reset|stash|rm|mv|clean|apply|restore|switch|merge|rebase|push)\b|\bcd\s+\S*(?<![\w-])app\b[^\n]*&&[^\n]*\b(npm\s+(install|i|ci|add)|git\s+(add|commit|checkout|reset|clean|restore))\b'
min: 0
max: 0
arm: both
---
