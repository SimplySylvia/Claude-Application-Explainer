"""Shared paths and helpers for the tests. Run everything with: python3 -m unittest discover tests"""
import os, shutil, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, 'skills', 'application-explainer')
SCRIPTS = os.path.join(SKILL, 'scripts')
ENGINE = os.path.join(SKILL, 'engine')
FIXTURE = os.path.join(ROOT, 'evals', '_fixture', 'make-app.sh')


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def write(path, text):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def run(*args, cwd=None, check=True):
    return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, check=check)


class TempDirCase(unittest.TestCase):
    """Gives each test a fresh temp dir containing the Shopfront fixture app at ./app."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='ae-test-')
        self.addCleanup(shutil.rmtree, self.tmp, True)
        run('bash', FIXTURE, cwd=self.tmp)
        self.app = os.path.join(self.tmp, 'app')

    def scaffold(self, app='Shopfront', *extra):
        return run(sys.executable, os.path.join(SCRIPTS, 'new_guide.py'), '--repo', self.app, '--app', app, *extra,
                   cwd=self.tmp, check=False)

    def build(self, guide, *extra):
        return run(sys.executable, os.path.join(guide, 'build', 'build.py'), *extra, check=False)
