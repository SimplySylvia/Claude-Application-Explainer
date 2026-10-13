---
type: tool_used
tool: Agent
# The tech-researcher prompt carries only the technology, version, and generic questions.
input_match: '"subagent_type"\s*:\s*"(?:[\w-]+:)?tech-researcher"[\s\S]*(?:[Ss]hop[Ff]ront|newAdmin|requireStaff|client/src)|(?:[Ss]hop[Ff]ront|newAdmin|requireStaff|client/src)[\s\S]*"subagent_type"\s*:\s*"(?:[\w-]+:)?tech-researcher"'
min: 0
max: 0
arm: both
---
