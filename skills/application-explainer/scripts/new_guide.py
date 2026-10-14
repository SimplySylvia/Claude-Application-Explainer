#!/usr/bin/env python3
"""Scaffold a new guide folder for an application repository, or add a technology deep dive to one.

    python3 new_guide.py --repo /path/to/app-repo --app "Acme" [--dest ~/acme-guide]
    python3 new_guide.py --repo /path/to/app-repo --app "Acme" --topic "GraphQL" [--dest ~/acme-graphql-guide]
    python3 new_guide.py --app "Acme" --topic "GraphQL" --into ~/acme-guide

The first form creates <dest>/ with build/ (the engine), sections/, diagrams.py, shots.py, guide_config.py,
PROGRESS.md, screenshots/, and initializes a git repo there. --topic uses the topic-explainer starter instead: a
smaller guide about one technology and how the app uses it. --into adds that topic as a deep dive in an existing
guide instead: a group on its Topics page (created before Reference on first use), with sections prefixed by the
topic slug and glossary rows merged into the guide's own glossary. The target application repo is only read (for its name, branch, and commit).
"""
import argparse, ast, datetime, os, re, shutil, subprocess, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPIC_STARTER = os.path.join(os.path.dirname(SKILL), 'topic-explainer', 'starter')
TEXT_FILES = ('.py', '.html', '.md')


def git(repo, *args):
    try:
        return subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return 'unknown'


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def fill(text, values):
    for k, v in values.items():
        text = text.replace(k, v)
    return text


def fill_tree(dest, values):
    for root, _, files in os.walk(dest):
        if os.sep + 'build' in root or os.sep + '.git' in root:
            continue
        for f in files:
            if f.endswith(TEXT_FILES):
                p = os.path.join(root, f)
                s = open(p, encoding='utf-8').read()
                open(p, 'w', encoding='utf-8').write(fill(s, values))


def config_value(src, key):
    m = re.search(rf'^{key} = (.+)$', src, re.M)
    return ast.literal_eval(m.group(1).split('  #')[0].strip()) if m else None


def set_topics(src, topics):
    """Rewrite (or append) the one-line TOPICS registry that changed_since.py reads."""
    line = f'TOPICS = {topics!r}'
    if re.search(r'^TOPICS = ', src, re.M):
        return re.sub(r'^TOPICS = .*$', lambda _: line, src, flags=re.M)
    return src.rstrip('\n') + ('\n\n# Technology deep dives: {slug: {"name": ..., "docs_checked": "YYYY-MM-DD"}}. '
                               'changed_since.py flags docs\n# checked more than 90 days ago; '
                               '`changed_since.py <guide> --mark-docs <slug>` records a re-check.\n') + line + '\n'


def repo_values(repo):
    return {
        '__REPO_NAME__': os.path.basename(repo), '__DATE__': datetime.date.today().isoformat(),
        '__BRANCH__': git(repo, 'rev-parse', '--abbrev-ref', 'HEAD'),
        '__COMMIT__': git(repo, 'rev-parse', '--short', 'HEAD'), '__COMMIT_FULL__': git(repo, 'rev-parse', 'HEAD'),
        '__REPO_PATH__': repo.replace('\\', '\\\\').replace("'", "\\'"),  # lands inside a Python string literal
    }


def topic_values(topic, prefix):
    tslug = slugify(topic)
    return {'__TOPIC__': topic, '__TOPIC_SLUG__': tslug,
            # Section ids and diagram names get a prefix only when added to an existing guide; function names too.
            '__T__': prefix, '__TFN__': ('t_' + tslug.replace('-', '_') + '_') if prefix else ''}


def new_guide(a):
    repo = os.path.abspath(os.path.expanduser(a.repo))
    slug = slugify(a.app)
    tslug = slugify(a.topic) if a.topic else ''
    default = f'{slug}-{tslug}-guide' if a.topic else f'{slug}-guide'
    dest = os.path.abspath(os.path.expanduser(a.dest or os.path.join(os.path.dirname(repo), default)))
    if os.path.commonpath([dest, repo]) == repo:
        sys.exit(f'Refusing to create the guide inside the application repo ({repo}). Pick a --dest outside it.')
    if os.path.exists(dest) and os.listdir(dest):
        sys.exit(f'{dest} already exists and is not empty.')

    shutil.copytree(TOPIC_STARTER if a.topic else os.path.join(SKILL, 'starter'), dest, dirs_exist_ok=True)
    shutil.copytree(os.path.join(SKILL, 'engine'), os.path.join(dest, 'build'), dirs_exist_ok=True)
    if not a.topic:
        os.makedirs(os.path.join(dest, 'screenshots'), exist_ok=True)
    os.makedirs(os.path.join(dest, 'qa'), exist_ok=True)

    name = f'{slug}-{tslug}-guide' if a.topic else f'{slug}-guide'
    values = {'__APP__': a.app, '__SLUG__': slug, **repo_values(repo), **(topic_values(a.topic, '') if a.topic else {})}
    fill_tree(dest, values)

    open(os.path.join(dest, '.gitignore'), 'w').write('qa/\n__pycache__/\n*.pyc\n.DS_Store\n')
    if a.topic:
        readme = (f'# {a.topic} in {a.app} — Topic Guide\n\n'
                  f'Internal guide to {a.topic} and how the `{values["__REPO_NAME__"]}` repository uses it, built with the '
                  'topic-explainer skill.\n\n'
                  f'```bash\npython3 build/build.py   # writes {name}.html\n```\n\n'
                  '- `PROGRESS.md`: phase checklist, scope, decisions, and open questions (read it first when resuming)\n'
                  '- `guide_config.py`: title, parts/pages, source repo and commit, and when the docs were last checked\n'
                  '- `sections/<id>.html`: one file per section\n'
                  '- `diagrams.py`: SVG diagrams (`@diagram(name)`), placed with `<div class="diagram" data-diagram="name"></div>`\n'
                  '- `build/`: the engine (copied from the skill; update it by re-copying)\n')
    else:
        readme = (f'# {a.app} — Product & Engineering Guide\n\n'
                  f'Internal guide to the `{values["__REPO_NAME__"]}` repository, built with the application-explainer skill.\n\n'
                  f'```bash\npython3 build/build.py   # writes {name}.html (and -no-screenshots.html when screenshots exist)\n```\n\n'
                  '- `PROGRESS.md`: phase checklist, scope, decisions, and open questions (read it first when resuming)\n'
                  '- `guide_config.py`: title, brand, parts/pages, collapse defaults, source repo and commit\n'
                  '- `sections/<id>.html`: one file per section\n'
                  '- `diagrams.py`: SVG diagrams (`@diagram(name)`), placed with `<div class="diagram" data-diagram="name"></div>`\n'
                  '- `shots.py` + `screenshots/`: optional screenshots\n'
                  '- `build/`: the engine (copied from the skill; update it by re-copying)\n')
    open(os.path.join(dest, 'README.md'), 'w').write(readme)
    subprocess.run(['git', 'init', '-q', dest])
    print(f'Created {dest}\nNext: edit guide_config.py and sections/, then run: python3 {dest}/build/build.py')


def add_topic(a):
    """Add the topic starter to an existing guide as a group on its Topics page, creating the page if needed."""
    guide = os.path.abspath(os.path.expanduser(a.into))
    cfg_path = os.path.join(guide, 'guide_config.py')
    if not os.path.exists(cfg_path):
        sys.exit(f'{guide} has no guide_config.py: --into needs a guide built by this skill.')
    src = open(cfg_path, encoding='utf-8').read()
    repo = config_value(src, 'SOURCE_REPO')
    if a.repo:
        repo = os.path.abspath(os.path.expanduser(a.repo))
    elif repo and not os.path.isabs(repo):
        repo = os.path.normpath(os.path.join(guide, repo))
    if not repo or repo.startswith('__'):
        sys.exit(f'{cfg_path} has no SOURCE_REPO. Pass --repo.')

    tslug = slugify(a.topic)
    registry = config_value(src, 'TOPICS') or {}
    if tslug in registry:
        sys.exit(f'{guide} already has a {a.topic!r} deep dive (TOPICS[{tslug!r}]). Update it instead.')
    prefix = tslug + '-'
    values = {'__APP__': a.app, '__SLUG__': slugify(a.app), **repo_values(repo), **topic_values(a.topic, prefix)}

    # The starter's own config lists the topic sections; reuse it so the two modes can't drift apart.
    ns = {}
    exec(fill(open(os.path.join(TOPIC_STARTER, 'guide_config.py'), encoding='utf-8').read(), values), ns)
    items = [(sid, label) for _, _, _, its in ns['PARTS'] for sid, label in its if sid != 'glossary']

    starter_sections = os.path.join(TOPIC_STARTER, 'sections')
    files = [f for f in sorted(os.listdir(starter_sections)) if f.endswith('.html') and f != 'glossary.html']
    targets = {f: os.path.join(guide, 'sections', prefix + f) for f in files}
    taken = [t for t in targets.values() if os.path.exists(t)]
    if taken:
        sys.exit(f'Refusing to overwrite existing sections: {", ".join(map(os.path.basename, taken))}')

    lines = src.split('\n')
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith('PARTS = ['))
        end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith(']'))
    except StopIteration:
        sys.exit(f'Could not find a "PARTS = [ ... ]" block in {cfg_path}. Add the topic by hand:\n{items}')
    # Every deep dive is a group on one Topics page: (id, title, blurb, [sections]), the same shape as a part.
    group = ([f'        ({tslug!r}, {a.topic!r}, {f"What {a.topic} is and how {a.app} uses it."!r}, ['] +
             [f'            ({sid!r}, {label!r}),' for sid, label in items] + ['        ]),'])
    topics = next((i for i in range(start, end) if lines[i].startswith("    ('topics',")), None)
    if topics is not None:
        close = next(i for i in range(topics + 1, end + 1) if lines[i] == '    ]),' or lines[i].startswith(']'))
        lines[close:close] = group
    else:
        at = next((i for i in range(start, end) if lines[i].startswith("    ('reference',")), end)
        lines[at:at] = ([f"    ('topics', 'Topics', {f'Deep dives into the technologies {a.app} is built on.'!r}, ["] +
                        group + ['    ]),'])
    src = '\n'.join(lines)
    registry[tslug] = {'name': a.topic, 'docs_checked': ''}
    open(cfg_path, 'w', encoding='utf-8').write(set_topics(src, registry))

    for f, target in targets.items():
        text = open(os.path.join(starter_sections, f), encoding='utf-8').read()
        open(target, 'w', encoding='utf-8').write(fill(text, values))

    starter_diagrams = fill(open(os.path.join(TOPIC_STARTER, 'diagrams.py'), encoding='utf-8').read(), values)
    body = starter_diagrams.split('from diagram import Diagram, diagram, mid\n', 1)[-1].strip('\n')
    diagrams_path = os.path.join(guide, 'diagrams.py')
    existing = open(diagrams_path, encoding='utf-8').read() if os.path.exists(diagrams_path) else (
        'from diagram import Diagram, diagram, mid\n')
    open(diagrams_path, 'w', encoding='utf-8').write(existing.rstrip('\n') + f'\n\n\n# ---- {a.topic} deep dive\n{body}\n')

    progress = os.path.join(guide, 'PROGRESS.md')
    checklist = fill(open(os.path.join(TOPIC_STARTER, 'PROGRESS.md'), encoding='utf-8').read(), values)
    checklist = checklist.split('## Checklist', 1)[1].split('## Decisions', 1)[0].strip('\n').replace('\n## ', '\n### ')
    with open(progress, 'a', encoding='utf-8') as fh:
        fh.write(f'\n## Deep dive: {a.topic} (added {values["__DATE__"]}, sections `{prefix}*`)\n\n{checklist}\n')

    print(f'Added a {a.topic} deep dive to {guide}: {len(files)} section(s) prefixed {prefix!r}, a group on the Topics page, '
          f'TOPICS[{tslug!r}], a diagram in diagrams.py, and a checklist in PROGRESS.md.\n'
          f'Next: fill in sections/{prefix}*.html, then run: python3 {guide}/build/build.py')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', help='path to the application repository (read-only); optional with --into')
    ap.add_argument('--app', required=True, help='display name of the application, e.g. "Acme Portal"')
    ap.add_argument('--dest', help='where to create the guide (default: a sibling folder <app>-guide, or <app>-<topic>-guide)')
    ap.add_argument('--topic', help='build a topic guide about one technology, e.g. "GraphQL"')
    ap.add_argument('--into', help='with --topic: add the topic to the Topics page of this existing guide instead of a new folder')
    a = ap.parse_args()
    if a.into:
        if not a.topic or a.dest:
            sys.exit('--into needs --topic and can\'t be combined with --dest.')
        add_topic(a)
    else:
        if not a.repo:
            sys.exit('--repo is required (unless you use --into).')
        new_guide(a)


if __name__ == '__main__':
    main()
