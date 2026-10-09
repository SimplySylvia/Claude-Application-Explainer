"""Screenshots (optional). Put JPEGs in screenshots/<name>.jpg (1080 px wide, quality ~72).

Without any screenshots the guide builds without the Screen column and gallery.
"""

GALLERY_CAPTION = 'Captured from TODO-environment at 1440×900. Any personal data is synthetic or blurred.'

# Gallery areas in display order: (area, icon key, color family, one-line description)
# Color families: blue, purple, teal, orange, pink, gray
AREAS = [
    # ('Dashboard', 'dash', 'blue', 'The landing page after sign-in'),
]

# name -> (area, title, route, note)
SHOTS = {
    # 'dashboard': ('Dashboard', 'Home dashboard', '/home', ''),
}

# Rows of a table marked data-screens, by the row's first bold text -> [shot names] or a reason string
FEATURE_SHOTS = {
    # 'Dashboard': ['dashboard'],
    # 'Billing': 'Restricted: needs the billing-admin role',
}

# (route, what the app showed, why) for screens that couldn't be captured
NOT_CAPTURED = []
