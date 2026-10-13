#!/usr/bin/env python3
"""List guide sections that may be stale because the app repo changed since the guide was last verified.

    python3 changed_since.py <guide>            # report: changed files, affected sections, uncovered changes
    python3 changed_since.py <guide> --mark     # after updating: record the repo's current HEAD as SOURCE_COMMIT

Reads SOURCE_REPO and SOURCE_COMMIT from <guide>/guide_config.py, diffs the repo from that commit to HEAD
(read-only git commands), and matches changed files against the repo paths each section cites in <code> spans.
A section is affected when it cites a changed file or a folder containing one. Changed files that no section cites
are listed separately: they may need new content. --mark also updates the commit in FOOTER.
"""
import ast, os, re, subprocess, sys

CODE = re.compile(r'<code>([^<]+)</code>')


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
    head = git(repo, 'rev-parse', 'HEAD')

    if '--mark' in args:
        short_old, short_new = git(repo, 'rev-parse', '--short', since), git(repo, 'rev-parse', '--short', 'HEAD')
        src = re.sub(r"^SOURCE_COMMIT = .*$", f"SOURCE_COMMIT = '{head}'", src, flags=re.M)
        src = re.sub(r"^(FOOTER = .*)$", lambda m: m.group(1).replace(short_old, short_new), src, flags=re.M)
        open(path, 'w', encoding='utf-8').write(src)
        print(f'SOURCE_COMMIT {short_old} -> {short_new}')
        return

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
