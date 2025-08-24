import shutil, os

def get_terminal_size():
    """Return terminal width, height"""
    size = shutil.get_terminal_size((80, 20))
    return size.columns, size.lines

def scale_values(values, height=10):
    """Scale values into a fixed height"""
    max_val = max(values) if values else 1
    return [int((v / max_val) * height) for v in values]

def colorize(text, color=None):
    """Add ANSI colors if available"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "end": "\033[0m"
    }
    if not color or "NO_COLOR" in os.environ:
        return text
    return colors.get(color, "") + text + colors["end"]
