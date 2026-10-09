#!/usr/bin/env python3
"""Add MUI Rounded icons to a guide's engine.

    python3 fetch_icons.py <guide>/build key=MuiName [key=MuiName ...]
    e.g. python3 fetch_icons.py ~/acme-guide/build cart=ShoppingCart invoice=ReceiptLong

Downloads <MuiName>Rounded.js from unpkg (@mui/icons-material@6.4.1) into build/icons/<MuiName>.js and
registers key=MuiName in build/icons.py. Browse names at https://mui.com/material-ui/material-icons/.
"""
import os, re, sys, urllib.request

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    build = os.path.abspath(os.path.expanduser(sys.argv[1]))
    reg = os.path.join(build, 'icons.py')
    src = open(reg).read()
    for pair in sys.argv[2:]:
        key, name = pair.split('=', 1)
        url = f'https://unpkg.com/@mui/icons-material@6.4.1/{name}Rounded.js'
        body = urllib.request.urlopen(url, timeout=30).read().decode()
        if not re.search(r'd: "', body):
            sys.exit(f'{url} has no path data')
        open(os.path.join(build, 'icons', name + '.js'), 'w').write(body)
        if re.search(rf'\b{key}=', src):
            print(f'{key} already registered; file updated')
            continue
        src = src.replace('\n)\nICONS = {}', f'\n    {key}={name!r},\n)\nICONS = {{}}', 1)
        print(f'added {key} -> {name}')
    open(reg, 'w').write(src)

if __name__ == '__main__':
    main()
