"""new_hub.py, hub builds, and the engine's hub hooks, on the eval fixture app."""
import json, os, re, sys, unittest

from helpers import SCRIPTS, TempDirCase, read, run, write


class HubTest(TempDirCase):
    def new_hub(self, *extra):
        return run(sys.executable, os.path.join(SCRIPTS, 'new_hub.py'), '--repo', self.app, '--app', 'Shopfront', *extra,
                   cwd=self.tmp, check=False)

    def path(self, *parts):
        return os.path.join(self.tmp, *parts)

    def two_guides_and_hub(self):
        self.assertEqual(self.scaffold().returncode, 0)
        self.assertEqual(self.scaffold('Shopfront', '--topic', 'GraphQL').returncode, 0)
        r = self.new_hub()
        self.assertEqual(r.returncode, 0, r.stderr)
        return r

    def test_new_hub_connects_existing_guides(self):
        r = self.two_guides_and_hub()
        self.assertIn('Connected 2 guide(s)', r.stdout)
        hub = self.path('shopfront-guides')
        for p in ['hub_config.py', 'README.md', '.gitignore', '.git', 'build/build.py', 'build/nav.src.js',
                  'build/tokens.css', 'build/depth.css', 'index.html', 'nav.js']:
            self.assertTrue(os.path.exists(os.path.join(hub, p)), p)
        self.assertIsNone(re.search(r'__[A-Z_]+__', read(os.path.join(hub, 'hub_config.py'))))
        for g in ['shopfront-guide', 'shopfront-graphql-guide']:
            config = read(self.path(g, 'guide_config.py'))
            self.assertIn("HUB_URL = '../shopfront-guides/index.html'", config)
            self.assertIn("HUB_TITLE = 'Shopfront guides'", config)
            self.assertIn("THEME_KEY = 'shopfront-guides-theme'", config)
        self.assertNotIn("BRAND_COLOR = '#1f6feb'", read(self.path('shopfront-graphql-guide', 'guide_config.py')),
                         'a topic guide gets its own marker color')
        self.assertIn("BRAND_COLOR = '#1f6feb'", read(self.path('shopfront-guide', 'guide_config.py')),
                      "the app guide keeps the app's brand")
        self.assertEqual(run('git', '-C', self.app, 'status', '--porcelain').stdout, '')

    def test_guide_build_refreshes_hub_and_links_resolve(self):
        self.two_guides_and_hub()
        for g in ['shopfront-guide', 'shopfront-graphql-guide']:
            r = self.build(self.path(g))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn('hub: OK', r.stdout)
        hub = self.path('shopfront-guides')
        html = read(os.path.join(hub, 'index.html'))
        self.assertIn('Learn the Shopfront codebase', html)
        self.assertNotRegex(html, r'<(script|link)[^>]+(src|href)="https?://', 'hub must be self-contained')
        index = json.loads(re.search(r'id="search-index">(.*?)</script>', html, re.S).group(1))
        self.assertTrue(any(e['k'] == 'Heading' for e in index), 'headings inside sections are searchable')
        hrefs = set(re.findall(r'href="(\.\./[^"]+)"', html)) | {e['h'] for e in index}
        for href in hrefs:
            target, _, frag = href.partition('#')
            page = os.path.normpath(os.path.join(hub, target))
            self.assertTrue(os.path.exists(page), href)
            if frag:
                self.assertIn(f'id="{frag}"', read(page), href)
        manifest = json.loads(re.search(r'var MANIFEST = (\{.*?\});', read(os.path.join(hub, 'nav.js'))).group(1))
        self.assertEqual(sorted(g['kind'] for g in manifest['guides']), ['app', 'topic'])
        self.assertEqual(manifest['themeKey'], 'shopfront-guides-theme')

        guide = read(self.path('shopfront-graphql-guide', 'shopfront-graphql-guide.html'))
        self.assertIn('<script src="../shopfront-guides/nav.js" defer></script>', guide)
        self.assertIn('class="hub-crumb" href="../shopfront-guides/index.html">Shopfront guides</a>', guide)
        self.assertIn("localStorage.getItem('shopfront-guides-theme')", guide)
        self.assertIn('--surface-2', guide, 'depth.css is built in')

    def test_new_guide_connects_to_existing_hub(self):
        self.two_guides_and_hub()
        r = self.scaffold('Shopfront', '--topic', 'Redis')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('Connected to the guide hub', r.stdout)
        config = read(self.path('shopfront-redis-guide', 'guide_config.py'))
        self.assertIn("HUB_URL = '../shopfront-guides/index.html'", config)
        graphql = read(self.path('shopfront-graphql-guide', 'guide_config.py'))
        color = lambda src: re.search(r"^BRAND_COLOR = '([^']+)'", src, re.M).group(1)
        self.assertNotEqual(color(config), color(graphql), 'each topic guide gets a different color')

    def test_no_hub_flag_and_standalone_guides(self):
        self.two_guides_and_hub()
        self.assertEqual(self.scaffold('Shopfront', '--topic', 'Redis', '--no-hub').returncode, 0)
        guide = self.path('shopfront-redis-guide')
        self.assertIn('HUB_URL = None', read(os.path.join(guide, 'guide_config.py')))
        r = self.build(guide)
        self.assertEqual(r.returncode, 0, r.stderr)
        html = read(os.path.join(guide, 'shopfront-redis-guide.html'))
        self.assertNotIn('nav.js', html)
        self.assertNotIn('hub-crumb', html.split('</style>', 1)[1])
        hub = run(sys.executable, self.path('shopfront-guides', 'build', 'build.py'))
        self.assertIn('WARNING shopfront-redis-guide is listed here but not connected', hub.stdout)

    def test_suggests_a_hub_for_the_second_guide(self):
        self.scaffold()
        r = self.scaffold('Shopfront', '--topic', 'GraphQL')
        self.assertIn('new_hub.py --repo', r.stdout)

    def test_connect_refuses_other_repo_and_old_engine(self):
        self.two_guides_and_hub()
        other = self.path('other')
        os.makedirs(other)
        run('git', 'init', '-q', other)
        run('git', '-C', other, '-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-q', '--allow-empty', '-m', 'x')
        run(sys.executable, os.path.join(SCRIPTS, 'new_guide.py'), '--repo', other, '--app', 'Other', '--no-hub', cwd=self.tmp)
        r = run(sys.executable, os.path.join(SCRIPTS, 'new_hub.py'), '--connect', self.path('other-guide'),
                '--hub', self.path('shopfront-guides'), check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('but the hub at', r.stderr)

        guide = self.path('shopfront-graphql-guide')
        layout = os.path.join(guide, 'build', 'layout.py')
        write(layout, read(layout).replace('hub_url', 'old_name'))
        r = run(sys.executable, os.path.join(SCRIPTS, 'new_hub.py'), '--connect', guide, check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('--update-engine', r.stderr)
        r = run(sys.executable, os.path.join(SCRIPTS, 'new_hub.py'), '--connect', guide, '--update-engine', check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('hub_url', read(layout))


if __name__ == '__main__':
    unittest.main()
