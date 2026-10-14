#!/usr/bin/env python3
"""Create a guide hub for an application repo, or connect a guide to one.

    python3 new_hub.py --repo /path/to/app-repo --app "Acme" [--dest ~/acme-guides]
    python3 new_hub.py --connect ~/acme-graphql-guide [--hub ~/acme-guides] [--update-engine]

A hub is one page (index.html) that lists every guide built for the same repo: the whole-app guide first, then topic
guides in a sortable table, with search across all of them and a "Continue reading" list. It also writes nav.js,
which connected guides load to get a Guides menu, a breadcrumb back to the hub, a shared light/dark setting, and a
"Search all guides" handoff from their own search.

The first form creates <dest>/ (default: a sibling <app>-guides/ folder) with build/ (the hub engine), hub_config.py,
README.md and a git repo, connects every guide already sitting next to it for that repo, and builds the hub.
--connect points one guide at a hub: it sets HUB_URL, HUB_TITLE and THEME_KEY in its guide_config.py and gives a topic
guide still on the default brand color a color of its own. Guides then refresh the hub whenever they build.
The application repo is only read.
"""
import argparse, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from new_guide import SKILL, config_value, fill, git, slugify  # noqa: E402

HUB = os.path.join(SKILL, 'hub')
ENGINE = os.path.join(SKILL, 'engine')
DEFAULT_BRAND = '#1f6feb'
# Same order as the hub's PALETTE: one per topic guide, so each is easy to tell apart in the hub and Guides menu.
PALETTE = ['#905d9a', '#49786d', '#ad5900', '#a9527c', '#437e00', '#0064fa']
HUB_ENGINE_FILES = [(HUB, 'build.py'), (HUB, 'nav.src.js'), (ENGINE, 'tokens.css'), (ENGINE, 'depth.css')]


def resolve(path, base):
    return os.path.realpath(os.path.join(base, os.path.expanduser(path)))


def read_config(folder, name):
    path = os.path.join(folder, name)
    if not os.path.exists(path):
        sys.exit(f'{folder} has no {name}.')
    return path, open(path, encoding='utf-8').read()


def set_value(src, key, value, before='\n# Design tokens.'):
    """Set a one-line `KEY = value` in a config, keeping its trailing comment; insert it if the key is missing."""
    line = f'{key} = {value!r}'
    m = re.search(rf'^{key} = .*?(\s+#.*)?$', src, re.M)
    if m:
        return src[:m.start()] + line + (m.group(1) or '') + src[m.end():]
    if before in src:
        return src.replace(before, f'\n{line}{before}', 1)
    return src.rstrip('\n') + f'\n{line}\n'


def guides_beside(hub_dir, repo):
    """Sibling folders of the hub holding a guide for repo."""
    parent = os.path.dirname(hub_dir)
    found = []
    for name in sorted(os.listdir(parent)):
        folder = os.path.join(parent, name)
        cfg = os.path.join(folder, 'guide_config.py')
        if folder == hub_dir or not os.path.isfile(cfg):
            continue
        src_repo = config_value(open(cfg, encoding='utf-8').read(), 'SOURCE_REPO')
        if src_repo and resolve(src_repo, folder) == repo:
            found.append(folder)
    return found


def hubs_beside(folder, repo):
    """Hub folders next to folder whose SOURCE_REPO is repo."""
    parent = os.path.dirname(os.path.abspath(folder))
    out = []
    for name in sorted(os.listdir(parent)):
        hub = os.path.join(parent, name)
        cfg = os.path.join(hub, 'hub_config.py')
        if os.path.isfile(cfg):
            src_repo = config_value(open(cfg, encoding='utf-8').read(), 'SOURCE_REPO')
            if src_repo and resolve(src_repo, hub) == repo:
                out.append(hub)
    return out


def engine_supports_hub(guide):
    layout = os.path.join(guide, 'build', 'layout.py')
    return os.path.exists(layout) and 'hub_url' in open(layout, encoding='utf-8').read()


def update_engine(guide):
    """Re-copy the engine into guide/build, keeping a customized tokens.css and icons.py."""
    dest = os.path.join(guide, 'build')
    for name in os.listdir(ENGINE):
        src, target = os.path.join(ENGINE, name), os.path.join(dest, name)
        if name in ('tokens.css', 'icons.py') and os.path.exists(target):
            continue
        if os.path.isdir(src):
            shutil.copytree(src, target, dirs_exist_ok=True)
        elif not name.endswith('.pyc'):
            shutil.copy2(src, target)


def connect(guide, hub, update=False, quiet=False):
    guide, hub = os.path.realpath(guide), os.path.realpath(hub)
    cfg_path, src = read_config(guide, 'guide_config.py')
    _, hub_src = read_config(hub, 'hub_config.py')
    guide_repo = resolve(config_value(src, 'SOURCE_REPO') or '.', guide)
    hub_repo = resolve(config_value(hub_src, 'SOURCE_REPO') or '.', hub)
    if guide_repo != hub_repo:
        sys.exit(f'{guide} documents {guide_repo}, but the hub at {hub} is for {hub_repo}.')
    if os.path.dirname(guide) != os.path.dirname(hub):
        sys.exit(f'Keep the guide and hub side by side: {guide} and {hub} are in different folders.')
    if not engine_supports_hub(guide):
        if not update:
            sys.exit(f'{guide}/build predates hub support. Re-run with --update-engine to re-copy the engine '
                     '(a customized tokens.css and icons.py are kept).')
        update_engine(guide)

    src = set_value(src, 'HUB_URL', os.path.relpath(os.path.join(hub, 'index.html'), guide))
    src = set_value(src, 'HUB_TITLE', config_value(hub_src, 'TITLE'))
    src = set_value(src, 'THEME_KEY', (config_value(hub_src, 'STORAGE_KEY') or slugify(os.path.basename(hub))) + '-theme')
    kind = config_value(src, 'GUIDE_KIND') or ('topic' if 'Topic Guide' in (config_value(src, 'TITLE') or '') else 'app')
    color = config_value(src, 'BRAND_COLOR')
    if kind == 'topic' and (not color or color.lower() == DEFAULT_BRAND):
        taken = {(config_value(open(os.path.join(g, 'guide_config.py'), encoding='utf-8').read(), 'BRAND_COLOR') or '').lower()
                 for g in guides_beside(hub, hub_repo) if g != guide}
        color = next((c for c in PALETTE if c not in taken), PALETTE[len(taken) % len(PALETTE)])
        src = set_value(src, 'BRAND_COLOR', color)
    open(cfg_path, 'w', encoding='utf-8').write(src)
    if not quiet:
        print(f'Connected {guide} to {hub}. Rebuild the guide: python3 {guide}/build/build.py (it refreshes the hub too).')


def build_hub(hub):
    r = subprocess.run([sys.executable, os.path.join(hub, 'build', 'build.py')], capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    return r.returncode


def new_hub(a):
    repo = os.path.realpath(os.path.expanduser(a.repo))
    slug = slugify(a.app)
    dest = os.path.abspath(os.path.expanduser(a.dest or os.path.join(os.path.dirname(repo), f'{slug}-guides')))
    if os.path.commonpath([dest, repo]) == repo:
        sys.exit(f'Refusing to create the hub inside the application repo ({repo}). Pick a --dest outside it.')
    if os.path.exists(dest) and os.listdir(dest):
        sys.exit(f'{dest} already exists and is not empty.')
    os.makedirs(os.path.join(dest, 'build'), exist_ok=True)
    for folder, name in HUB_ENGINE_FILES:
        shutil.copy2(os.path.join(folder, name), os.path.join(dest, 'build', name))
    values = {'__APP__': a.app, '__SLUG__': slug, '__REPO_PATH__': repo.replace('\\', '\\\\').replace("'", "\\'")}
    open(os.path.join(dest, 'hub_config.py'), 'w', encoding='utf-8').write(
        fill(open(os.path.join(HUB, 'hub_config.py'), encoding='utf-8').read(), values))
    open(os.path.join(dest, '.gitignore'), 'w').write('qa/\n__pycache__/\n*.pyc\n.DS_Store\n')
    open(os.path.join(dest, 'README.md'), 'w', encoding='utf-8').write(
        f'# {a.app} guides — hub\n\n'
        f'One page that links every guide built for the `{os.path.basename(repo)}` repository, built with the '
        'application-explainer skill.\n\n'
        '```bash\npython3 build/build.py   # writes index.html and nav.js\n```\n\n'
        '- Guides in sibling folders with the same `SOURCE_REPO` are listed on their own. Each connected guide rebuilds '
        'this hub when it builds, so it rarely needs a manual run.\n'
        '- `hub_config.py`: title, brand, tokens and fonts, one-line blurbs per guide\n'
        '- `build/`: the hub engine (copied from the skill; update it by re-copying `hub/` and `engine/tokens.css`, '
        '`engine/depth.css`)\n'
        '- Links are relative, so keep the hub and its guides side by side, also when you host them.\n')
    subprocess.run(['git', 'init', '-q', dest])
    connected = []
    for guide in guides_beside(dest, repo):
        if engine_supports_hub(guide) or a.update_engine:
            connect(guide, dest, update=a.update_engine, quiet=True)
            connected.append(guide)
        else:
            print(f'Skipped {guide}: its engine predates hub support. Run: new_hub.py --connect {guide} --update-engine')
    print(f'Created {dest} for {repo}. Connected {len(connected)} guide(s)' + (': ' + ', '.join(map(os.path.basename, connected)) if connected else '') + '.')
    build_hub(dest)
    if connected:
        print('Rebuild each connected guide so its header gets the Guides menu: python3 <guide>/build/build.py')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--repo', help='path to the application repository (read-only)')
    ap.add_argument('--app', help='display name of the application, e.g. "Acme Portal"')
    ap.add_argument('--dest', help='where to create the hub (default: a sibling folder <app>-guides)')
    ap.add_argument('--connect', metavar='GUIDE', help='connect this guide to a hub instead of creating one')
    ap.add_argument('--hub', help='with --connect: the hub folder (default: the hub next to the guide for the same repo)')
    ap.add_argument('--update-engine', action='store_true', help="re-copy the engine into guides that predate hub support")
    a = ap.parse_args()
    if a.connect:
        guide = os.path.realpath(os.path.expanduser(a.connect))
        if a.hub:
            hub = a.hub
        else:
            _, src = read_config(guide, 'guide_config.py')
            hubs = hubs_beside(guide, resolve(config_value(src, 'SOURCE_REPO') or '.', guide))
            if len(hubs) != 1:
                sys.exit(f'Found {len(hubs)} hubs next to {guide} for its repo; pass --hub.')
            hub = hubs[0]
        connect(guide, os.path.expanduser(hub), update=a.update_engine)
    else:
        if not (a.repo and a.app):
            sys.exit('--repo and --app are required (unless you use --connect).')
        new_hub(a)


if __name__ == '__main__':
    main()
