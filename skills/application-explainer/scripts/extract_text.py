#!/usr/bin/env python3
"""Dump a built guide's text (per section) and candidate glossary terms, for research/review agents.

    python3 extract_text.py guide.html out-dir/

Writes out-dir/guide-text.txt (all sections except the glossary), out-dir/glossary-terms.txt, and
out-dir/candidates.txt (acronyms and capitalized phrases used 2+ times that the glossary doesn't cover).
"""
import collections, html, os, re, sys

def aliases(term):
    t = html.unescape(re.sub(r'<[^>]+>', '', term))
    paren = re.search(r'\(([^)]*)\)', t)
    out = [a for a in re.split(r'\s+/\s+', re.sub(r'\s*\([^)]*\)', '', t)) if a]
    if paren and not re.match(r'as ', paren.group(1), re.I):
        out += [a.strip() for a in re.split(r'\s*[,/]\s*', re.sub('["“”…]', '', paren.group(1))) if a.strip()]
    return [a.lower() for a in out]

def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    s = open(src, encoding='utf-8').read()
    s = re.sub(r'<script.*?</script>|<style.*?</style>|<svg.*?</svg>', '', s, flags=re.S)
    parts, alltext, gloss = [], '', ''
    for sid, body in re.findall(r'<section id="([\w-]+)"[^>]*>(.*?)</section>', s, flags=re.S):
        if sid == 'glossary':
            gloss = body
            continue
        t = re.sub(r'<(br|/p|/li|/tr|/h\d|/td)[^>]*>', '\n', body)
        t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
        t = re.sub(r'[ \t]+', ' ', t)
        t = re.sub(r'\n\s*\n+', '\n', t)
        parts.append(f'\n===== #{sid} =====\n{t}')
        alltext += t + '\n'
    open(os.path.join(out, 'guide-text.txt'), 'w').write(''.join(parts))
    terms = [html.unescape(re.sub(r'<[^>]+>', '', t)) for t in re.findall(r'<tr[^>]*><td><b>(.*?)</b>', gloss)]
    open(os.path.join(out, 'glossary-terms.txt'), 'w').write('\n'.join(terms))
    known = {a for t in terms for a in aliases(t)}
    c = collections.Counter()
    for m in re.finditer(r'\b([A-Z][A-Z0-9+&-]{1,}[a-z]?)\b', alltext):
        c[m.group(1)] += 1
    for m in re.finditer(r'\b([A-Z][a-z]+(?: [A-Z][a-z]+){0,2})\b', alltext):
        c[m.group(1)] += 1
    cand = sorted(((v, k) for k, v in c.items() if k.lower() not in known and v >= 2), reverse=True)
    open(os.path.join(out, 'candidates.txt'), 'w').write('\n'.join(f'{v}\t{k}' for v, k in cand))
    print(f'{len(alltext.split())} words, {len(terms)} glossary terms, {len(cand)} candidates -> {out}')

if __name__ == '__main__':
    main()
