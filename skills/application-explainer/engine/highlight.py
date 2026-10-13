"""Build-time syntax highlighting for code blocks, so guides stay self-contained (no highlighter script or CDN).

Sections write:   <pre class="code" data-lang="js" data-title="optional caption"><code>escaped code</code></pre>
The build turns that into a figure with a language label, an optional title, a copy button, and <span class="tk-…">
tokens. Highlighting is a small regex tokenizer per language: good enough to read, not a parser.
"""
import html, re

# Token classes (styled in styles.css): com comment · str string · kw keyword · num number · lit true/false/null ·
# fn function or command · key object key / header / YAML key · var variable · tag JSX/HTML tag · attr flag/attribute/decorator
_JS_KW = ('async await break case catch class const continue default delete do else export extends finally for from '
          'function if import in instanceof let new of return static super switch this throw try typeof var void while '
          'yield as interface type enum implements readonly')
_PY_KW = ('and as assert async await break class continue def del elif else except finally for from global if import in '
          'is lambda nonlocal not or pass raise return try while with yield match case')
_SQL_KW = ('select from where and or not insert into values update set delete create table alter drop index on join left '
           'right inner outer full group by order having limit offset as distinct union all returning primary key '
           'foreign references default null is in exists between like case when then else end begin commit rollback')
_GQL_KW = 'query mutation subscription fragment on type input enum interface schema extend scalar union directive implements'

_STR = r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\''
_NUM = r'\b\d[\d_]*(?:\.\d+)?(?:e[+-]?\d+)?\b'
_FN = r'\b[A-Za-z_$][\w$]*(?=\s*\()'


def _kw(words, flags=''):
    body = rf'\b(?:{"|".join(words.split())})\b'
    return f'(?{flags}:{body})' if flags else body


_LANGS = {
    'js': [('com', r'//[^\n]*|/\*[\s\S]*?\*/'), ('str', _STR + r'|`(?:\\.|[^`\\])*`'),
           ('tag', r'</?[A-Z][\w.]*(?=[\s/>])|</?(?:div|span|main|h[1-6]|p|ul|li|a|button|form|input|section|header|nav)(?=[\s/>])'),
           ('kw', _kw(_JS_KW)), ('lit', r'\b(?:true|false|null|undefined|NaN)\b'), ('num', _NUM), ('fn', _FN),
           ('key', r'\b[A-Za-z_$][\w$]*(?=\s*:(?!:))')],
    'python': [('com', r'#[^\n]*'), ('str', r'[rbfu]{0,2}(?:"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|' + _STR + ')'),
               ('attr', r'@[\w.]+'), ('kw', _kw(_PY_KW)), ('lit', r'\b(?:True|False|None)\b'), ('num', _NUM), ('fn', _FN)],
    'bash': [('com', r'(?:(?<=\s)|^)#[^\n]*'), ('str', _STR), ('var', r'\$\{?[\w@#?*]+\}?'),
             ('attr', r'(?:(?<=\s)|^)--?[A-Za-z][\w-]*'), ('fn', r'(?:^|(?<=\|\s)|(?<=&&\s)|(?<=^\$\s))[A-Za-z_][\w.-]*'),
             ('num', r'(?<![\w:/.-])\d+(?![\w./:-])')],   # standalone numbers only, not ports or ids inside URLs
    'json': [('key', r'"(?:\\.|[^"\\\n])*"(?=\s*:)'), ('str', _STR), ('lit', r'\b(?:true|false|null)\b'), ('num', r'-?' + _NUM)],
    'sql': [('com', r'--[^\n]*|/\*[\s\S]*?\*/'), ('str', r"'(?:''|[^'])*'"), ('kw', _kw(_SQL_KW, 'i')),
            ('var', r'\$\d+|:\w+'), ('num', _NUM), ('fn', _FN)],
    'yaml': [('com', r'(?:(?<=\s)|^)#[^\n]*'), ('key', r'^[ \t]*-?[ \t]*[\w./-]+(?=:(?:\s|$))'), ('str', _STR),
             ('lit', r'\b(?:true|false|null|yes|no|on|off)\b'), ('num', _NUM)],
    'http': [('kw', r'^(?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b|^HTTP/[\d.]+'), ('key', r'^[\w-]+(?=:\s)'),
             ('str', _STR), ('num', r'\b\d{3}\b'), ('lit', r'\b(?:true|false|null)\b')],
    'graphql': [('com', r'#[^\n]*'), ('str', r'"""[\s\S]*?"""|' + _STR), ('kw', _kw(_GQL_KW)), ('var', r'\$\w+'),
                ('attr', r'@\w+'), ('lit', r'\b(?:true|false|null)\b'), ('tag', r'\b[A-Z]\w*\b'), ('num', _NUM),
                ('key', r'\b\w+(?=\s*:)')],
    'text': [],
}
ALIASES = {'javascript': 'js', 'jsx': 'js', 'ts': 'js', 'tsx': 'js', 'typescript': 'js', 'mjs': 'js', 'node': 'js',
           'py': 'python', 'sh': 'bash', 'shell': 'bash', 'zsh': 'bash', 'console': 'bash', 'yml': 'yaml',
           'gql': 'graphql', 'plain': 'text', 'txt': 'text', 'psql': 'sql', 'postgres': 'sql'}
LABELS = {'js': 'JavaScript', 'jsx': 'JSX', 'ts': 'TypeScript', 'tsx': 'TSX', 'python': 'Python', 'bash': 'Shell',
          'json': 'JSON', 'sql': 'SQL', 'yaml': 'YAML', 'http': 'HTTP', 'graphql': 'GraphQL', 'text': 'Text'}
_COMPILED = {lang: re.compile('|'.join(f'(?P<{name}>{rx})' for name, rx in rules), re.M) if rules else None
             for lang, rules in _LANGS.items()}

BLOCK = re.compile(r'<pre class="code" data-lang="([\w+-]*)"(?: data-title="([^"]*)")?><code>(.*?)</code></pre>', re.S)


def known(lang):
    return (ALIASES.get(lang, lang)) in _LANGS


def highlight(code, lang):
    """Escaped HTML for code (plain text) with token spans for lang."""
    rx = _COMPILED.get(ALIASES.get(lang, lang))
    if rx is None:
        return html.escape(code, quote=False)
    out, pos = [], 0
    for m in rx.finditer(code):
        if m.start() == m.end():
            continue
        out.append(html.escape(code[pos:m.start()], quote=False))
        out.append(f'<span class="tk-{m.lastgroup}">{html.escape(m.group(), quote=False)}</span>')
        pos = m.end()
    out.append(html.escape(code[pos:], quote=False))
    return ''.join(out)


def render_blocks(section_html, warn):
    """Replace every <pre class="code"> block in a section with its highlighted figure."""
    def one(m):
        lang, title, body = m.group(1).lower(), m.group(2), m.group(3)
        if not known(lang):
            warn(f'unknown code language {lang!r}: use one of {", ".join(sorted(set(_LANGS) | set(ALIASES)))}')
        code = html.unescape(body).strip('\n')
        code = re.sub(r'(?m)^' + re.escape(min(re.findall(r'(?m)^[ \t]*(?=\S)', code) or [''], key=len)), '', code)
        label = LABELS.get(lang) or LABELS.get(ALIASES.get(lang, lang), lang or 'Code')
        title_html = f'<span class="code-title">{title}</span>' if title else ''
        return (f'<figure class="code-block"><figcaption><span class="code-lang">{label}</span>{title_html}'
                f'<button type="button" class="code-copy" aria-label="Copy code">Copy</button></figcaption>'
                f'<pre><code class="lang-{ALIASES.get(lang, lang)}">{highlight(code, lang)}</code></pre></figure>')
    return BLOCK.sub(one, section_html)
