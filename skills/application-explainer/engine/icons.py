"""MUI icon paths (Rounded style, @mui/icons-material 6.4.1). Add icons with scripts/fetch_icons.py."""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
# short key -> MUI file name in icons/
ICON_FILES = dict(
    monitor='Computer', puzzle='Extension', users='Groups', zap='Bolt', shield='Security', server='Dns',
    cog='Settings', radio='Sensors', clock='Schedule', key='VpnKey', db='Storage', folder='Folder',
    chart='BarChart', layers='Layers', fn='Functions', globe='Public', chat='Chat', ai='AutoAwesome',
    pulse='MonitorHeart', hospital='LocalHospital', tree='AccountTree', code='Code', check='CheckCircle',
    package='Inventory2', terminal='Terminal', eye='Visibility', rocket='RocketLaunch', merge='CallMerge',
    book='MenuBook', link='Link', hub='Hub', dash='Dashboard', filter='FilterAlt', list='ListAlt',
    table='TableChart', sync='Sync', play='PlayCircle', upload='CloudUpload', lock='Lock', person='Person', cloud='Cloud', build='Build',
    expand='Fullscreen', zoomIn='ZoomIn', zoomOut='ZoomOut', fit='FitScreen', close='Close',
    search='Search', inbox='Inbox', calendar='CalendarMonth', member='AccountCircle', apps='Apps', admin='AdminPanelSettings',
)
ICONS = {}
for _key, _name in ICON_FILES.items():
    with open(os.path.join(HERE, 'icons', _name + '.js'), encoding='utf-8') as _f:
        _src = _f.read()
    _ds = re.findall(r'd: "([^"]+)"', _src)
    assert _ds, _name
    ICONS[_key] = ''.join(f'<path d="{d}"/>' for d in _ds)
