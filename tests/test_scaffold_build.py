"""new_guide.py scaffolding and build.py output, on the eval fixture app."""
import os, re, shutil, sys, unittest

from helpers import ROOT, SCRIPTS, TempDirCase, read, run, write


class ScaffoldTest(TempDirCase):
    def test_creates_sibling_guide_with_git_repo(self):
        r = self.scaffold('Shop Front')
        self.assertEqual(r.returncode, 0, r.stderr)
        guide = os.path.join(self.tmp, 'shop-front-guide')
        for p in ['guide_config.py', 'diagrams.py', 'shots.py', 'README.md', 'PROGRESS.md', '.gitignore', '.git',
                  'build/build.py', 'sections/overview.html', 'screenshots', 'qa']:
            self.assertTrue(os.path.exists(os.path.join(guide, p)), p)

    def test_fills_placeholders(self):
        self.scaffold()
        guide = os.path.join(self.tmp, 'shopfront-guide')
        commit = run('git', '-C', self.app, 'rev-parse', '--short', 'HEAD').stdout.strip()
        config = read(os.path.join(guide, 'guide_config.py'))
        self.assertIn("OUTPUT_NAME = 'shopfront-guide'", config)
        self.assertIn(commit, config)
        full = run('git', '-C', self.app, 'rev-parse', 'HEAD').stdout.strip()
        self.assertIn(f"SOURCE_COMMIT = '{full}'", config)
        self.assertIn(f"SOURCE_REPO = '{os.path.realpath(self.app)}'", config.replace(self.app, os.path.realpath(self.app)))
        self.assertIn('# Shopfront guide: progress', read(os.path.join(guide, 'PROGRESS.md')))
        for root, _, files in os.walk(guide):
            if os.sep + 'build' in root or os.sep + '.git' in root:
                continue
            for f in files:
                if f.endswith(('.py', '.html', '.md')):
                    text = read(os.path.join(root, f))
                    self.assertIsNone(re.search(r'__[A-Z_]+__', text), f'placeholder left in {f}')

    def test_refuses_dest_inside_app_repo(self):
        r = self.scaffold('Shopfront', '--dest', os.path.join(self.app, 'docs', 'guide'))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('Refusing', r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.app, 'docs')))
        self.assertEqual(run('git', '-C', self.app, 'status', '--porcelain').stdout, '')

    def test_refuses_non_empty_dest(self):
        dest = os.path.join(self.tmp, 'taken')
        os.makedirs(dest)
        write(os.path.join(dest, 'keep.txt'), 'x')
        r = self.scaffold('Shopfront', '--dest', dest)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(os.listdir(dest), ['keep.txt'])


class BuildTest(TempDirCase):
    def test_starter_builds_without_warnings(self):
        self.scaffold()
        guide = os.path.join(self.tmp, 'shopfront-guide')
        r = self.build(guide)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn('WARNING', r.stdout)
        self.assertTrue(r.stdout.startswith('OK '), r.stdout)
        html = read(os.path.join(guide, 'shopfront-guide.html'))
        self.assertNotRegex(html, r'<(script|link)[^>]+(src|href)="https?://', 'guide must be self-contained')
        self.assertFalse(os.path.exists(os.path.join(guide, 'shopfront-guide-no-screenshots.html')))

    def test_demo_source_builds_without_warnings_or_todos(self):
        # The same steps as docs/demo/make-demo.sh: two guides and the hub that links them.
        demo = os.path.join(ROOT, 'docs', 'demo')
        self.scaffold('Shopfront', '--no-hub')
        self.scaffold('Shopfront', '--topic', 'PostgreSQL', '--no-hub')
        run(sys.executable, os.path.join(SCRIPTS, 'new_hub.py'), '--repo', self.app, '--app', 'Shopfront', cwd=self.tmp)
        guide = os.path.join(self.tmp, 'shopfront-guide')
        topic = os.path.join(self.tmp, 'shopfront-postgresql-guide')
        hub = os.path.join(self.tmp, 'shopfront-guides')
        shutil.copytree(os.path.join(demo, 'source'), guide, dirs_exist_ok=True)
        shutil.rmtree(os.path.join(topic, 'sections'))
        shutil.copytree(os.path.join(demo, 'source-postgresql'), topic, dirs_exist_ok=True)
        shutil.copy(os.path.join(demo, 'source-hub', 'hub_config.py'), hub)
        for g in (guide, topic):
            r = run(sys.executable, os.path.join(g, 'build', 'build.py'), '--no-hub', check=False)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn('WARNING', r.stdout)
        r = run(sys.executable, os.path.join(hub, 'build', 'build.py'), check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn('WARNING', r.stdout)
        self.assertIn('2 guides', r.stdout)
        for page in (os.path.join(guide, 'shopfront-guide.html'), os.path.join(topic, 'shopfront-postgresql-guide.html')):
            html = read(page)
            self.assertNotRegex(re.sub(r'<script.*?</script>', '', html, flags=re.S), r'\bTODO\b')
            for href in set(re.findall(r'href="(\.\./[^"#]+)#([^"]+)"', html)):
                target = os.path.normpath(os.path.join(os.path.dirname(page), href[0]))
                self.assertIn(f'id="{href[1]}"', read(target), f'{os.path.basename(page)} links to {href}')
        html = read(os.path.join(guide, 'shopfront-guide.html'))

        out = os.path.join(self.tmp, 'text')
        r = run(sys.executable, os.path.join(SCRIPTS, 'extract_text.py'), os.path.join(guide, 'shopfront-guide.html'), out)
        terms = read(os.path.join(out, 'glossary-terms.txt')).splitlines()
        self.assertIn('requireStaff', terms)
        text = read(os.path.join(out, 'guide-text.txt'))
        self.assertIn('===== #arch =====', text)
        self.assertIn('Guided walkthrough', text)                     # section titles survive chrome stripping
        self.assertNotRegex(text, r'(?m)^\s*(Copy|Collapsed)\s*$')    # page chrome doesn't
        usage = {line.split('\t')[1]: line.split('\t') for line in read(os.path.join(out, 'glossary-usage.txt')).splitlines()}
        count, _, sections = usage['requireStaff']
        self.assertGreater(int(count), 0)
        self.assertIn('express-conventions', sections.split(','))
        cands = [line.split('\t') for line in read(os.path.join(out, 'candidates.txt')).splitlines()]
        self.assertTrue(all(len(c) == 3 for c in cands))
        names = [c[1] for c in cands]
        self.assertIn('Shopfront', names)
        self.assertNotIn('Express', names)                           # already a glossary term
        self.assertNotIn('The', names)                               # sentence-initial ordinary words are dropped

    def test_section_without_sources_warns(self):
        self.scaffold()
        guide = os.path.join(self.tmp, 'shopfront-guide')
        shutil.copytree(os.path.join(ROOT, 'docs', 'demo', 'source'), guide, dirs_exist_ok=True)
        write(os.path.join(guide, 'sections', 'cheatsheet.html'),
              '<section id="cheatsheet">\n  <h2>Cheat sheet</h2>\n  <p class="sub">Run <code>npm test</code>.</p>\n</section>\n')
        r = self.build(guide, '--no-hub')
        self.assertIn("section 'cheatsheet' cites no repo paths", r.stdout)
        write(os.path.join(guide, 'sections', 'cheatsheet.html'),
              '<section id="cheatsheet">\n  <h2>Cheat sheet</h2>\n  <p class="sub">From <code>package.json</code>.</p>\n</section>\n')
        self.assertNotIn('WARNING', self.build(guide, '--no-hub').stdout)

    def test_unplaced_diagram_warns(self):
        self.scaffold()
        guide = os.path.join(self.tmp, 'shopfront-guide')
        arch = os.path.join(guide, 'sections', 'arch.html')
        s = read(arch).replace('<div class="diagram" data-diagram="arch"></div>', '')
        write(arch, s)
        r = self.build(guide)
        self.assertIn("diagram 'arch' is defined but not placed", r.stdout)


if __name__ == '__main__':
    unittest.main()
