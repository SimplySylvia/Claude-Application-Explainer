"""new_guide.py scaffolding and build.py output, on the eval fixture app."""
import os, re, shutil, sys, unittest

from helpers import ROOT, SCRIPTS, TempDirCase, read, run, write


class ScaffoldTest(TempDirCase):
    def test_creates_sibling_guide_with_git_repo(self):
        r = self.scaffold('Shop Front')
        self.assertEqual(r.returncode, 0, r.stderr)
        guide = os.path.join(self.tmp, 'shop-front-guide')
        for p in ['guide_config.py', 'diagrams.py', 'shots.py', 'README.md', '.gitignore', '.git',
                  'build/build.py', 'sections/overview.html', 'screenshots', 'qa']:
            self.assertTrue(os.path.exists(os.path.join(guide, p)), p)

    def test_fills_placeholders(self):
        self.scaffold()
        guide = os.path.join(self.tmp, 'shopfront-guide')
        commit = run('git', '-C', self.app, 'rev-parse', '--short', 'HEAD').stdout.strip()
        config = read(os.path.join(guide, 'guide_config.py'))
        self.assertIn("OUTPUT_NAME = 'shopfront-guide'", config)
        self.assertIn(commit, config)
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
        self.scaffold()
        guide = os.path.join(self.tmp, 'shopfront-guide')
        shutil.copytree(os.path.join(ROOT, 'docs', 'demo', 'source'), guide, dirs_exist_ok=True)
        r = self.build(guide)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn('WARNING', r.stdout)
        html = read(os.path.join(guide, 'shopfront-guide.html'))
        main = re.sub(r'<script.*?</script>', '', html, flags=re.S)
        self.assertNotRegex(main, r'\bTODO\b')

        out = os.path.join(self.tmp, 'text')
        r = run(sys.executable, os.path.join(SCRIPTS, 'extract_text.py'), os.path.join(guide, 'shopfront-guide.html'), out)
        terms = read(os.path.join(out, 'glossary-terms.txt')).splitlines()
        self.assertIn('requireStaff', terms)
        self.assertIn('===== #arch =====', read(os.path.join(out, 'guide-text.txt')))

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
