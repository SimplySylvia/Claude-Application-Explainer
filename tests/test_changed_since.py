"""scripts/changed_since.py: which sections cite files changed since SOURCE_COMMIT."""
import os, shutil, sys

from helpers import ROOT, SCRIPTS, TempDirCase, read, run, write

GIT = ['-c', 'user.name=t', '-c', 'user.email=t@example.com']


class ChangedSinceTest(TempDirCase):
    def setUp(self):
        super().setUp()
        self.scaffold()
        self.guide = os.path.join(self.tmp, 'shopfront-guide')
        shutil.copytree(os.path.join(ROOT, 'docs', 'demo', 'source', 'sections'), os.path.join(self.guide, 'sections'),
                        dirs_exist_ok=True)

    def changed(self, *extra):
        return run(sys.executable, os.path.join(SCRIPTS, 'changed_since.py'), self.guide, *extra, check=False)

    def commit(self, files):
        for rel, text in files.items():
            path = os.path.join(self.app, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            write(path, text)
        run('git', '-C', self.app, *GIT, 'add', '-A')
        run('git', '-C', self.app, *GIT, 'commit', '-q', '-m', 'change')

    def test_no_changes(self):
        r = self.changed()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('0 file(s) changed', r.stdout)

    def test_file_and_folder_citations(self):
        self.commit({'server/auth.js': 'changed', 'server/jobs/nightly.js': 'new', 'docs/notes.txt': 'new'})
        out = self.changed().stdout
        self.assertIn('3 file(s) changed', out)
        self.assertIn('AFFECTED arch', out)        # cites server/auth.js
        self.assertIn('AFFECTED stack', out)       # cites the server/ folder
        not_cited = out.split('NOT CITED')[1]
        self.assertIn('docs/notes.txt', not_cited)
        self.assertNotIn('server/auth.js', not_cited)

    def test_mark_records_head(self):
        self.commit({'server/auth.js': 'changed'})
        head = run('git', '-C', self.app, 'rev-parse', 'HEAD').stdout.strip()
        r = self.changed('--mark')
        self.assertEqual(r.returncode, 0, r.stderr)
        config = read(os.path.join(self.guide, 'guide_config.py'))
        self.assertIn(f"SOURCE_COMMIT = '{head}'", config)
        self.assertIn(head[:7], config.split('FOOTER = ')[1])
        self.assertIn('0 file(s) changed', self.changed().stdout)

    def test_relative_source_repo(self):
        path = os.path.join(self.guide, 'guide_config.py')
        config = read(path)
        start = config.index("SOURCE_REPO = '")
        end = config.index("'\n", start + len("SOURCE_REPO = '"))
        write(path, config[:start] + "SOURCE_REPO = '../app" + config[end:])
        self.assertIn('0 file(s) changed', self.changed().stdout)

    def test_missing_config_explains(self):
        path = os.path.join(self.guide, 'guide_config.py')
        write(path, '\n'.join(l for l in read(path).splitlines() if not l.startswith('SOURCE_COMMIT')))
        r = self.changed()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('has no SOURCE_COMMIT', r.stderr)
