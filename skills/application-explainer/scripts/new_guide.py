#!/usr/bin/env python3
"""Scaffold a new guide folder for an application repository.

    python3 new_guide.py --repo /path/to/app-repo --app "Acme" [--dest ~/acme-guide]

Creates <dest>/ with build/ (the engine), sections/, diagrams.py, shots.py, guide_config.py, PROGRESS.md,
screenshots/, and initializes a git repo there. The target application repo is only read (for its name, branch, and commit).
"""
import argparse, datetime, os, re, shutil, subprocess, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(repo, *args):
    try:
        return subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return 'unknown'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True, help='path to the application repository (read-only)')
    ap.add_argument('--app', required=True, help='display name of the application, e.g. "Acme Portal"')
    ap.add_argument('--dest', help='where to create the guide (default: a sibling folder <repo>-guide)')
    a = ap.parse_args()

    repo = os.path.abspath(os.path.expanduser(a.repo))
    slug = re.sub(r'[^a-z0-9]+', '-', a.app.lower()).strip('-')
    dest = os.path.abspath(os.path.expanduser(a.dest or os.path.join(os.path.dirname(repo), f'{slug}-guide')))
    if os.path.commonpath([dest, repo]) == repo:
        sys.exit(f'Refusing to create the guide inside the application repo ({repo}). Pick a --dest outside it.')
    if os.path.exists(dest) and os.listdir(dest):
        sys.exit(f'{dest} already exists and is not empty.')

    shutil.copytree(os.path.join(SKILL, 'starter'), dest, dirs_exist_ok=True)
    shutil.copytree(os.path.join(SKILL, 'engine'), os.path.join(dest, 'build'), dirs_exist_ok=True)
    os.makedirs(os.path.join(dest, 'screenshots'), exist_ok=True)
    os.makedirs(os.path.join(dest, 'qa'), exist_ok=True)

    values = {
        '__APP__': a.app, '__SLUG__': slug, '__REPO_NAME__': os.path.basename(repo),
        '__DATE__': datetime.date.today().isoformat(), '__BRANCH__': git(repo, 'rev-parse', '--abbrev-ref', 'HEAD'),
        '__COMMIT__': git(repo, 'rev-parse', '--short', 'HEAD'), '__COMMIT_FULL__': git(repo, 'rev-parse', 'HEAD'),
        '__REPO_PATH__': repo.replace('\\', '\\\\').replace("'", "\\'"),  # lands inside a Python string literal
    }
    for root, _, files in os.walk(dest):
        if os.sep + 'build' in root or os.sep + '.git' in root:
            continue
        for f in files:
            if f.endswith(('.py', '.html', '.md')):
                p = os.path.join(root, f)
                s = open(p, encoding='utf-8').read()
                for k, v in values.items():
                    s = s.replace(k, v)
                open(p, 'w', encoding='utf-8').write(s)

    open(os.path.join(dest, '.gitignore'), 'w').write('qa/\n__pycache__/\n*.pyc\n.DS_Store\n')
    open(os.path.join(dest, 'README.md'), 'w').write(
        f'# {a.app} — Product & Engineering Guide\n\n'
        f'Internal guide to the `{values["__REPO_NAME__"]}` repository, built with the application-explainer skill.\n\n'
        f'```bash\npython3 build/build.py   # writes {slug}-guide.html (and -no-screenshots.html when screenshots exist)\n```\n\n'
        '- `PROGRESS.md`: phase checklist, scope, decisions, and open questions (read it first when resuming)\n'
        '- `guide_config.py`: title, brand, parts/pages, collapse defaults, source repo and commit\n'
        '- `sections/<id>.html`: one file per section\n'
        '- `diagrams.py`: SVG diagrams (`@diagram(name)`), placed with `<div class="diagram" data-diagram="name"></div>`\n'
        '- `shots.py` + `screenshots/`: optional screenshots\n'
        '- `build/`: the engine (copied from the skill; update it by re-copying)\n')
    subprocess.run(['git', 'init', '-q', dest])
    print(f'Created {dest}\nNext: edit guide_config.py and sections/, then run: python3 {dest}/build/build.py')


if __name__ == '__main__':
    main()
