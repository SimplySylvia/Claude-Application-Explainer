---
type: tool_used
tool: Bash
# Same check as e2e-build-guide/graders/repo-untouched-bash.md: no shell command modifies ./app.
input_match: '(>>?|\btee\b(\s+-a)?)\s*\S*(?<![\w-])app/|\b(sed\s+-i|perl\s+-\w*i|rm|mv|touch|chmod|truncate)\b[^;&|\n]*(?<![\w-])app/|\bgit\s+-C\s+\S*(?<![\w-])app\b\S*\s+(add|commit|checkout|reset|stash|rm|mv|clean|apply|restore|switch|merge|rebase|push)\b|\bcd\s+\S*(?<![\w-])app\b[^\n]*&&[^\n]*\b(npm\s+(install|i|ci|add)|git\s+(add|commit|checkout|reset|clean|restore))\b'
min: 0
max: 0
arm: both
---
