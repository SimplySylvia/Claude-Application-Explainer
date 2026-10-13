"""Alias parsing and merging in scripts/merge_glossary.py."""
import os, shutil, sys, tempfile, unittest

from helpers import SCRIPTS, read, run, write

sys.path.insert(0, SCRIPTS)
from merge_glossary import aliases  # noqa: E402

GLOSSARY = '''<section id="glossary">
  <h2>Glossary</h2>
  <table class="stack">
    <tr><th>Term</th><th>Meaning</th><th>Where</th></tr>
    <tr class="group" style="--accent: var(--c-run)"><td colspan="3"><span class="row-icon" data-icon="book"></span>Domain</td></tr>
    <tr><td><b>Order / Purchase</b></td><td>A placed cart.</td><td><code>server/routes/orders.js</code></td></tr>
  </table>
</section>
'''

DRAFT = '''<!-- GROUP: Domain -->
<tr><td><b>Cart</b></td><td>Items before checkout.</td><td><code>server/routes/orders.js</code></td></tr>
<tr><td><b>Purchase order (PO)</b></td><td>Duplicate by alias? No: different name.</td><td><code>x</code></td></tr>
<tr><td><b>purchase</b></td><td>Duplicate of Order / Purchase.</td><td><code>x</code></td></tr>
<tr><td><b>Broken</b></td><td>Only two cells.</td></tr>
<!-- NEW GROUP: Code | code | --c-edge -->
<tr><td><b>requireStaff</b></td><td>Staff-only middleware.</td><td><code>server/auth.js</code></td></tr>
'''


class AliasTest(unittest.TestCase):
    def test_splits_names_and_expansion(self):
        self.assertEqual(aliases('Main name / Other name (MN)'), ['main name', 'other name', 'mn'])

    def test_as_context_is_not_a_name(self):
        self.assertEqual(aliases('Services layer (as in src/services)'), ['services layer'])

    def test_bare_slash_does_not_split(self):
        self.assertEqual(aliases('CI/CD'), ['ci/cd'])

    def test_html_is_stripped(self):
        self.assertEqual(aliases('<code>DATABASE_URL</code>'), ['database_url'])


class MergeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='ae-gloss-')
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.gpath = os.path.join(self.tmp, 'glossary.html')
        self.draft = os.path.join(self.tmp, 'draft.html')
        write(self.gpath, GLOSSARY)
        write(self.draft, DRAFT)

    def merge(self, *extra):
        return run(sys.executable, os.path.join(SCRIPTS, 'merge_glossary.py'), self.gpath, self.draft, *extra)

    def test_dry_run_reports_without_writing(self):
        r = self.merge()
        self.assertIn("dup  ", r.stdout)
        self.assertIn('BAD ', r.stdout)
        self.assertEqual(read(self.gpath), GLOSSARY)

    def test_write_merges_sorts_and_skips(self):
        self.merge('--write')
        out = read(self.gpath)
        self.assertIn('<b>Cart</b>', out)
        self.assertIn('<b>Purchase order (PO)</b>', out)
        self.assertNotIn('<b>purchase</b>', out)
        self.assertNotIn('<b>Broken</b>', out)
        self.assertLess(out.index('<b>Cart</b>'), out.index('<b>Order / Purchase</b>'))
        self.assertIn('data-icon="code"></span>Code</td></tr>', out)
        self.assertIn('--accent: var(--c-edge)', out)
        self.assertTrue(out.rstrip().endswith('</section>'))

    def test_order_flag(self):
        self.merge('--write', '--order', 'Code', 'Domain')
        out = read(self.gpath)
        self.assertLess(out.index('</span>Code<'), out.index('</span>Domain<'))


if __name__ == '__main__':
    unittest.main()
