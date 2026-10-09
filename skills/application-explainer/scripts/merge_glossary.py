#!/usr/bin/env python3
"""Merge agent-drafted glossary rows into sections/glossary.html, dropping duplicates.

    python3 merge_glossary.py <guide>/sections/glossary.html drafts/*.html [--write] [--order "Group A" "Group B" ...]

Draft files contain only rows, grouped by comments:
    <!-- GROUP: Existing group name -->
    <!-- NEW GROUP: New group name | icon-key | var(--c-run) -->
    <tr><td><b>Term / Other name (expansion)</b></td><td>Meaning.</td><td><code>path</code></td></tr>

A draft row is skipped when any of its names (split on " / " and the parenthetical) matches an existing name.
Rows are sorted A–Z inside each group. Without --write it only prints what it would do.
Review the printed list: rename aliases that are everyday words or would mislead the auto-linker.
"""
import collections, html, re, sys

def aliases(term):
    t = html.unescape(re.sub(r'<[^>]+>', '', term))
    paren = re.search(r'\(([^)]*)\)', t)
    out = [a for a in re.split(r'\s+/\s+', re.sub(r'\s*\([^)]*\)', '', t)) if a]
    if paren and not re.match(r'as ', paren.group(1), re.I):
        out += [a.strip() for a in re.split(r'\s*[,/]\s*', re.sub('["“”…]', '', paren.group(1))) if a.strip()]
    return [a.lower() for a in out if len(a) > 1]

def main():
    args = sys.argv[1:]
    write = '--write' in args
    order = args[args.index('--order') + 1:] if '--order' in args else None
    files = [a for a in (args[:args.index('--order')] if order else args) if a != '--write']
    if len(files) < 2:
        sys.exit(__doc__)
    gpath, drafts = files[0], files[1:]
    src = open(gpath, encoding='utf-8').read()
    head, rest = src.split('<tr class="group"', 1)
    body, tail = ('<tr class="group"' + rest).split('  </table>', 1)
    groups, meta, cur = collections.OrderedDict(), {}, None
    for line in body.splitlines():
        m = re.match(r'\s*<tr class="group" style="--accent: ([^"]+)"><td colspan="3"><span class="row-icon" data-icon="([\w-]+)"></span>(.*?)</td></tr>', line)
        if m:
            cur = m.group(3); groups[cur] = []; meta[cur] = (m.group(2), m.group(1)); continue
        if line.strip().startswith('<tr><td><b>'):
            groups[cur].append(line.strip())
    known = {a: re.match(r'<tr><td><b>(.*?)</b>', r).group(1) for g in groups.values() for r in g for a in aliases(re.match(r'<tr><td><b>(.*?)</b>', r).group(1))}
    added = collections.Counter()
    for f in drafts:
        cur = None
        for line in open(f, encoding='utf-8'):
            line = line.strip()
            m = re.match(r'<!-- NEW GROUP: (.*?) \| ([\w-]+) \| (.*?) -->', line)
            if m:
                cur = m.group(1); groups.setdefault(cur, []); meta.setdefault(cur, (m.group(2), m.group(3) if m.group(3).startswith('var(') else f'var({m.group(3)})')); continue
            m = re.match(r'<!-- GROUP: (.*?) -->', line)
            if m:
                cur = m.group(1); groups.setdefault(cur, []); continue
            m = re.match(r'<tr><td><b>(.*?)</b></td>', line)
            if not m:
                continue
            term = m.group(1)
            if line.count('<td>') != 3:
                print(f'BAD  {f}: {term} (needs exactly 3 cells)'); continue
            if cur not in meta:
                print(f'BAD  {f}: {term} (group {cur!r} has no icon/accent; use NEW GROUP)'); continue
            clash = [a for a in aliases(term) if a in known]
            if clash:
                print(f'dup  {f}: {term!r} <-> {known[clash[0]]!r} [{", ".join(clash)}]'); continue
            for a in aliases(term):
                known[a] = term
            groups[cur].append(line); added[cur] += 1
    key = lambda r: html.unescape(re.sub(r'<[^>]+>', '', re.match(r'<tr><td><b>(.*?)</b>', r).group(1))).lstrip('@.').lower()
    names = order or list(groups)
    assert set(names) == set(groups), f'--order must list exactly these groups: {list(groups)}'
    out = []
    for g in names:
        icon, accent = meta[g]
        out.append(f'    <tr class="group" style="--accent: {accent}"><td colspan="3"><span class="row-icon" data-icon="{icon}"></span>{g}</td></tr>')
        out += ['    ' + r for r in sorted(groups[g], key=key)]
        out.append('')
    for g in names:
        print(f'{len(groups[g]):4} rows (+{added[g]})  {html.unescape(g)}')
    print('total', sum(len(v) for v in groups.values()))
    if write:
        open(gpath, 'w', encoding='utf-8').write(head + '\n'.join(out).lstrip() + '\n  </table>' + tail)
        print('written', gpath)

if __name__ == '__main__':
    main()
