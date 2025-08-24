def get_theme(name="mono"):
    """
    Return a dict of theme characters and colors.
    Themes: mono, bright, hud
    """
    base = {
        "bar": "█",
        "line": "•",
        "hbar": "─",
        "up": "╱",
        "down": "╲",
        "color": "cyan"
    }

    themes = {
        "mono": {
            **base,
            "color": "",   # no ANSI color
        },
        "bright": {
            **base,
            "color": "yellow",
            "bar": "▓",
            "line": "●",
        },
        "hud": {
            **base,
            "color": "green",
            "bar": "⚡",
            "line": "◆",
        }
    }

    return themes.get(name, base)
