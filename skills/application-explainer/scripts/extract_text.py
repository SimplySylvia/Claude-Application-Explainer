#!/usr/bin/env python3
"""Dump a built guide's text (per section) and candidate glossary terms, for research/review agents.

    python3 extract_text.py guide.html out-dir/

Writes, for the glossary-scout and glossary-drafter agents:
  guide-text.txt       all sections except the glossary, headed "===== #section-id ====="
  glossary-terms.txt   the glossary's current terms
  glossary-usage.txt   each glossary term, how often its names appear in the guide text, and in which sections
                       (0 means nothing links to it)
  candidates.txt       acronyms and capitalized phrases used 2+ times that the glossary doesn't cover, with the
                       sections they appear in: "count<TAB>term<TAB>section-ids". A starting point only; lowercase
                       jargon isn't detected, which is what glossary-scout is for.
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
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    s = open(src, encoding='utf-8').read()
    s = re.sub(r'<script.*?</script>|<style.*?</style>|<svg.*?</svg>', '', s, flags=re.S)
    # Page chrome isn't guide text: Copy buttons, collapse-state badges, group previews, code-block language labels.
    # (Section titles live inside their toggle buttons, so other buttons stay.)
    s = re.sub(r'<button type="button" class="code-copy"[^>]*>.*?</button>|'
               r'<span class="(?:sec-state|group-preview|code-lang)[^"]*"[^>]*>.*?</span>', '', s, flags=re.S)
    parts, alltext, gloss, by_section = [], '', '', {}
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
        by_section[sid] = t
    open(os.path.join(out, 'guide-text.txt'), 'w').write(''.join(parts))
    terms = [html.unescape(re.sub(r'<[^>]+>', '', t)) for t in re.findall(r'<tr[^>]*><td><b>(.*?)</b>', gloss)]
    open(os.path.join(out, 'glossary-terms.txt'), 'w').write('\n'.join(terms))
    known = {a for t in terms for a in aliases(t)}
    usage = []
    for t in terms:
        hits = {sid: sum(len(re.findall(r'(?<![\w-])' + re.escape(a) + r's?(?![\w-])', text, re.I)) for a in aliases(t))
                for sid, text in by_section.items()}
        hits = {k: v for k, v in hits.items() if v}
        usage.append(f'{sum(hits.values())}\t{t}\t{",".join(hits)}')
    open(os.path.join(out, 'glossary-usage.txt'), 'w').write('\n'.join(usage))
    c, where = collections.Counter(), collections.defaultdict(list)
    for sid, text in by_section.items():
        for rx in (r'\b([A-Z][A-Z0-9+&-]{1,}[a-z]?)\b', r'\b([A-Z][a-z]+(?: [A-Z][a-z]+){0,2})\b'):
            for m in re.finditer(rx, text):
                c[m.group(1)] += 1
                if sid not in where[m.group(1)]:
                    where[m.group(1)].append(sid)
    lower = collections.Counter(re.findall(r'\b[a-z][a-z]+\b', alltext))
    # A capitalized single word that mostly appears in lowercase is an ordinary word starting a sentence ("The").
    ordinary = {k for k in c if ' ' not in k and k[1:].islower() and lower[k.lower()] >= c[k]}
    cand = sorted(((v, k) for k, v in c.items() if k.lower() not in known and k not in ordinary and v >= 2), reverse=True)
    open(os.path.join(out, 'candidates.txt'), 'w').write('\n'.join(f'{v}\t{k}\t{",".join(where[k])}' for v, k in cand))
    print(f'{len(alltext.split())} words, {len(terms)} glossary terms, {len(cand)} candidates -> {out}')

if __name__ == '__main__':
    main()
