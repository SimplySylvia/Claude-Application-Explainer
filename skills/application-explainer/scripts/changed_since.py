#!/usr/bin/env python3
"""List guide sections that may be stale because the app repo changed since the guide was last verified.

    python3 changed_since.py <guide>            # report: changed files, affected sections, uncovered changes
    python3 changed_since.py <guide> --mark     # after updating: record the repo's current HEAD as SOURCE_COMMIT
    python3 changed_since.py <guide> --mark-docs <slug> [...]   # after re-checking a topic's web docs: record today

Reads SOURCE_REPO and SOURCE_COMMIT from <guide>/guide_config.py, diffs the repo from that commit to HEAD
(read-only git commands), and matches changed files against the repo paths each section cites in <code> spans.
A section is affected when it cites a changed file or a folder containing one. Changed files that no section cites
are listed separately: they may need new content. --mark also updates the commit in FOOTER.

Guides with technology deep dives (TOPICS in guide_config.py) also get a docs check: a topic whose official docs
were never checked, or were checked more than DOCS_MAX_AGE days ago, is listed as DOCS STALE.
"""
import ast, datetime, os, re, subprocess, sys

CODE = re.compile(r'<code>([^<]+)</code>')
DOCS_MAX_AGE = 90


def git(repo, *args):
    r = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f'git {" ".join(args)} failed in {repo}: {r.stderr.strip()}')
    return r.stdout.strip()


def config(guide):
    path = os.path.join(guide, 'guide_config.py')
    src = open(path, encoding='utf-8').read()
    vals = {}
    for key in ('SOURCE_REPO', 'SOURCE_COMMIT'):
        m = re.search(rf"^{key} = (.+)$", src, re.M)
        val = ast.literal_eval(m.group(1).split('  #')[0].strip()) if m else ''
        if not val or val.startswith('__'):
            sys.exit(f'{path} has no {key}. Add it (see the starter guide_config.py) to track the source commit.')
        vals[key] = val
    repo = vals['SOURCE_REPO']
    if not os.path.isabs(repo):
        repo = os.path.normpath(os.path.join(guide, repo))
    return path, src, repo, vals['SOURCE_COMMIT']


def topics(src):
    m = re.search(r'^TOPICS = (.+)$', src, re.M)
    return ast.literal_eval(m.group(1)) if m else {}


def docs_report(src, today):
    for slug, t in sorted(topics(src).items()):
        checked = t.get('docs_checked') or ''
        if not checked:
            print(f'DOCS STALE {slug}: {t.get("name", slug)} docs never checked; run tech-researcher, then --mark-docs {slug}')
            continue
        age = (today - datetime.date.fromisoformat(checked)).days
        if age > DOCS_MAX_AGE:
            print(f'DOCS STALE {slug}: {t.get("name", slug)} docs last checked {checked} ({age} days ago); '
                  f're-run tech-researcher, then --mark-docs {slug}')
        else:
            print(f'docs ok {slug}: checked {checked} ({age} days ago)')


def mark_docs(path, src, slugs, today):
    ts = topics(src)
    unknown = [x for x in slugs if x not in ts]
    if not slugs or unknown:
        sys.exit(f'--mark-docs needs topic slug(s) from TOPICS: {", ".join(sorted(ts)) or "(none)"}'
                 + (f'; unknown: {", ".join(unknown)}' if unknown else ''))
    for x in slugs:
        ts[x]['docs_checked'] = today.isoformat()
    src = re.sub(r'^TOPICS = .*$', lambda _: f'TOPICS = {ts!r}', src, flags=re.M)
    open(path, 'w', encoding='utf-8').write(src)
    print(f'docs_checked = {today.isoformat()} for {", ".join(slugs)}')


def cited_paths(html):
    """Repo-looking paths in <code> spans: anything with a slash or a file extension, minus URLs and routes."""
    out = set()
    for raw in CODE.findall(html):
        for tok in re.split(r'[\s,]+', raw):
            tok = tok.strip('`\'"()').removeprefix('./')
            if not tok or '://' in tok or tok.startswith('/') or ':' in tok:
                continue
            if '/' in tok or re.search(r'\.[A-Za-z]{1,6}$', tok) or tok in ('Makefile', 'Dockerfile'):
                out.add(tok.rstrip('/'))
    return out


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith('-'):
        sys.exit(__doc__)
    guide = os.path.abspath(args[0])
    path, src, repo, since = config(guide)
    today = datetime.date.today()
    if '--mark-docs' in args:
        mark_docs(path, src, [x for x in args[args.index('--mark-docs') + 1:] if not x.startswith('-')], today)
        return
    head = git(repo, 'rev-parse', 'HEAD')

    if '--mark' in args:
        short_old, short_new = git(repo, 'rev-parse', '--short', since), git(repo, 'rev-parse', '--short', 'HEAD')
        src = re.sub(r"^SOURCE_COMMIT = .*$", f"SOURCE_COMMIT = '{head}'", src, flags=re.M)
        src = re.sub(r"^(FOOTER = .*)$", lambda m: m.group(1).replace(short_old, short_new), src, flags=re.M)
        open(path, 'w', encoding='utf-8').write(src)
        print(f'SOURCE_COMMIT {short_old} -> {short_new}')
        return

    docs_report(src, today)
    changed = [f for f in git(repo, 'diff', '--name-only', f'{since}..HEAD').splitlines() if f]
    print(f'{len(changed)} file(s) changed in {repo} since {since[:10]} (HEAD {head[:10]})')
    if not changed:
        return
    sections_dir = os.path.join(guide, 'sections')
    covered = set()
    for name in sorted(os.listdir(sections_dir)):
        if not name.endswith('.html'):
            continue
        cited = cited_paths(open(os.path.join(sections_dir, name), encoding='utf-8').read())
        hits = sorted({f for f in changed for c in cited if f == c or f.startswith(c + '/')})
        if hits:
            covered.update(hits)
            print(f'\nAFFECTED {name[:-5]}  ({len(hits)} changed file(s) it cites)')
            for f in hits[:12]:
                print(f'  {f}')
            if len(hits) > 12:
                print(f'  ... and {len(hits) - 12} more')
    uncovered = [f for f in changed if f not in covered]
    if uncovered:
        print(f'\nNOT CITED by any section ({len(uncovered)}): check whether they need new content')
        for f in uncovered[:30]:
            print(f'  {f}')
        if len(uncovered) > 30:
            print(f'  ... and {len(uncovered) - 30} more')


if __name__ == '__main__':
    main()
