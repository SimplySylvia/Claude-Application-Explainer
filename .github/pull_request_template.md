## What and why

<!-- What this changes, and the problem it solves. -->

## Checklist

- [ ] `python3 -m unittest discover -s tests -t tests` passes
- [ ] If `skills/` or `agents/` changed: bumped `version` in `.claude-plugin/plugin.json` and added a `CHANGELOG.md` entry
- [ ] If the skill's `description` changed: ran the trigger and near-miss evals (`claude plugin eval . --tag trigger nearmiss --scaffold`)
- [ ] If the engine or demo source changed: ran `docs/demo/make-demo.sh` and committed `docs/demo/index.html` and `docs/images/`
- [ ] No guide content, secrets, or personal data from a real app
