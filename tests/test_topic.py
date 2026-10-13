"""Topic guides: new_guide.py --topic / --into, external links in the build, and docs freshness in changed_since.py."""
import datetime, os, re, sys

from helpers import SCRIPTS, TempDirCase, read, run, write


class TopicCase(TempDirCase):
    def new_guide(self, *args):
        return run(sys.executable, os.path.join(SCRIPTS, 'new_guide.py'), *args, cwd=self.tmp, check=False)

    def changed(self, guide, *extra):
        return run(sys.executable, os.path.join(SCRIPTS, 'changed_since.py'), guide, *extra, check=False)


class SeparateTopicGuideTest(TopicCase):
    def setUp(self):
        super().setUp()
        r = self.new_guide('--repo', self.app, '--app', 'Shopfront', '--topic', 'React Router')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.guide = os.path.join(self.tmp, 'shopfront-react-router-guide')

    def test_scaffold_and_build(self):
        for p in ['guide_config.py', 'diagrams.py', 'PROGRESS.md', 'README.md', '.git', 'build/build.py',
                  'sections/overview.html', 'sections/walkthrough.html', 'sections/glossary.html']:
            self.assertTrue(os.path.exists(os.path.join(self.guide, p)), p)
        self.assertFalse(os.path.exists(os.path.join(self.guide, 'screenshots')))
        config = read(os.path.join(self.guide, 'guide_config.py'))
        self.assertIn("OUTPUT_NAME = 'shopfront-react-router-guide'", config)
        self.assertIn("TOPICS = {'react-router': {'name': 'React Router', 'docs_checked': ''}}", config)
        for root, _, files in os.walk(self.guide):
            if os.sep + 'build' in root or os.sep + '.git' in root:
                continue
            for f in files:
                if f.endswith(('.py', '.html', '.md')):
                    self.assertIsNone(re.search(r'__[A-Z_]+__', read(os.path.join(root, f))), f'placeholder left in {f}')
        r = self.build(self.guide)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn('WARNING', r.stdout)

    def test_external_links_open_in_new_tab_and_count_as_citations(self):
        write(os.path.join(self.guide, 'sections', 'overview.html'),
              '<section id="overview">\n  <h2>What is React Router?</h2>\n'
              '  <p class="sub">A router. See <a href="https://reactrouter.com/6.23.0">the v6 docs</a>.</p>\n</section>\n')
        r = self.build(self.guide)
        self.assertNotIn("section 'overview' cites no repo paths", r.stdout)
        html = read(os.path.join(self.guide, 'shopfront-react-router-guide.html'))
        self.assertIn('<a href="https://reactrouter.com/6.23.0" target="_blank" rel="noopener noreferrer">', html)

    def test_docs_freshness(self):
        out = self.changed(self.guide).stdout
        self.assertIn('DOCS STALE react-router', out)
        self.assertIn('never checked', out)
        r = self.changed(self.guide, '--mark-docs', 'react-router')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('docs ok react-router', self.changed(self.guide).stdout)

        cfg = os.path.join(self.guide, 'guide_config.py')
        old = (datetime.date.today() - datetime.timedelta(days=120)).isoformat()
        write(cfg, re.sub(r"'docs_checked': '[^']*'", f"'docs_checked': '{old}'", read(cfg)))
        self.assertIn('120 days ago', self.changed(self.guide).stdout)

        r = self.changed(self.guide, '--mark-docs', 'nope')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('unknown: nope', r.stderr)


class DeepDiveTest(TopicCase):
    def setUp(self):
        super().setUp()
        self.scaffold()
        self.guide = os.path.join(self.tmp, 'shopfront-guide')

    def add(self, topic='React Router'):
        return self.new_guide('--app', 'Shopfront', '--topic', topic, '--into', self.guide)

    def test_adds_part_before_reference_and_builds(self):
        r = self.add()
        self.assertEqual(r.returncode, 0, r.stderr)
        sections = os.listdir(os.path.join(self.guide, 'sections'))
        self.assertIn('react-router-walkthrough.html', sections)
        self.assertNotIn('react-router-glossary.html', sections)
        self.assertIn('<section id="react-router-usage">', read(os.path.join(self.guide, 'sections', 'react-router-usage.html')))
        config = read(os.path.join(self.guide, 'guide_config.py'))
        self.assertLess(config.index("('react-router', 'React Router deep dive'"), config.index("('reference', 'Reference'"))
        self.assertIn("TOPICS = {'react-router': {'name': 'React Router', 'docs_checked': ''}}", config)
        self.assertIn("@diagram('react-router-flow')", read(os.path.join(self.guide, 'diagrams.py')))
        self.assertIn('## Deep dive: React Router', read(os.path.join(self.guide, 'PROGRESS.md')))
        b = self.build(self.guide)
        self.assertEqual(b.returncode, 0, b.stderr)
        self.assertNotIn('WARNING', b.stdout)
        self.assertEqual(run('git', '-C', self.app, 'status', '--porcelain').stdout, '')

    def test_second_topic_and_duplicate(self):
        self.assertEqual(self.add().returncode, 0)
        r = self.add('Express')
        self.assertEqual(r.returncode, 0, r.stderr)
        config = read(os.path.join(self.guide, 'guide_config.py'))
        self.assertIn("'express': {'name': 'Express', 'docs_checked': ''}", config)
        self.assertEqual(self.build(self.guide).returncode, 0)
        r = self.add()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('already has', r.stderr)

    def test_refuses_to_overwrite_sections(self):
        write(os.path.join(self.guide, 'sections', 'react-router-usage.html'), 'mine')
        before = read(os.path.join(self.guide, 'guide_config.py'))
        r = self.add()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('Refusing to overwrite', r.stderr)
        self.assertEqual(read(os.path.join(self.guide, 'sections', 'react-router-usage.html')), 'mine')
        self.assertEqual(read(os.path.join(self.guide, 'guide_config.py')), before)
