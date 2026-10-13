"""Color tokens for light and dark calculator themes."""

THEMES = {
    "dark": {
        "bg": "#121417", "surface": "#1C1F24", "key": "#262A31",
        "key_op": "#323844", "accent": "#4F8CFF", "text": "#F2F4F8",
        "muted": "#A8B0BE", "danger": "#FF6B6B", "hover": "#3A414D",
    },
    "light": {
        "bg": "#F4F6FA", "surface": "#FFFFFF", "key": "#EDEFF4",
        "key_op": "#DDE2EC", "accent": "#2F6BFF", "text": "#14171C",
        "muted": "#596273", "danger": "#D64545", "hover": "#D2D8E3",
    },
}


def get_theme(name):
    return THEMES.get(name, THEMES["dark"])
