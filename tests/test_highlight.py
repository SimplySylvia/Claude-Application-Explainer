"""engine/highlight.py: build-time syntax highlighting of <pre class="code"> blocks."""
import os, sys, unittest

from helpers import ENGINE, TempDirCase, read, write

sys.path.insert(0, ENGINE)
import highlight  # noqa: E402


class HighlightTest(unittest.TestCase):
    def test_js_tokens(self):
        out = highlight.highlight("const r = await fetch('/api/x', { method: 'POST' }); // go", 'js')
        for tok in ('<span class="tk-kw">const</span>', '<span class="tk-fn">fetch</span>',
                    '<span class="tk-str">\'/api/x\'</span>', '<span class="tk-key">method</span>',
                    '<span class="tk-com">// go</span>'):
            self.assertIn(tok, out)

    def test_escapes_and_aliases(self):
        out = highlight.highlight('if (a < b && c) return <Order />;', 'jsx')
        self.assertIn('&lt;', out)
        self.assertNotIn('< b', out)
        self.assertIn('<span class="tk-tag">&lt;Order</span>', out)
        self.assertIn('<span class="tk-key">"id"</span>', highlight.highlight('{"id": 1}', 'json'))
        self.assertIn('<span class="tk-var">$PORT</span>', highlight.highlight('PORT=1 node x.js $PORT', 'sh'))
        self.assertIn('<span class="tk-kw">SELECT</span>', highlight.highlight('SELECT 1', 'sql'))
        self.assertEqual(highlight.highlight('a < b', 'text'), 'a &lt; b')

    def test_render_block_dedents_and_labels(self):
        warned = []
        src = ('<pre class="code" data-lang="js" data-title="server/x.js:1-2"><code>\n    const a = 1;\n      a &amp;&amp; b;\n</code></pre>')
        out = highlight.render_blocks(src, warned.append)
        self.assertEqual(warned, [])
        self.assertIn('<span class="code-lang">JavaScript</span><span class="code-title">server/x.js:1-2</span>', out)
        self.assertIn('class="code-copy"', out)
        self.assertIn('<code class="lang-js"><span class="tk-kw">const</span> a', out)
        self.assertIn('\n  a &amp;&amp; b;', out)
        highlight.render_blocks('<pre class="code" data-lang="cobol"><code>x</code></pre>', warned.append)
        self.assertIn('unknown code language', warned[0])


class BuildCodeBlocksTest(TempDirCase):
    def test_build_highlights_and_warns_on_bare_pre(self):
        self.scaffold()
        guide = os.path.join(self.tmp, 'shopfront-guide')
        write(os.path.join(guide, 'sections', 'overview.html'),
              '<section id="overview">\n  <h2>What is Shopfront?</h2>\n  <p class="sub">Sources: <code>README.md</code>.</p>\n'
              '  <pre class="code" data-lang="bash"><code>npm run dev</code></pre>\n  <pre>raw</pre>\n</section>\n')
        r = self.build(guide)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("section 'overview' has a <pre> without class=\"code\"", r.stdout)
        html = read(os.path.join(guide, 'shopfront-guide.html'))
        self.assertIn('<span class="tk-fn">npm</span> run dev', html)
        self.assertIn('Copy buttons on code blocks', html)
