"""
Color scheme utilities for terminal customization
"""

class ColorScheme:
    """Represents a terminal color scheme"""
    
    def __init__(self, name, background, foreground, colors):
        self.name = name
        self.background = background
        self.foreground = foreground
        self.colors = colors
    
    def to_windows_terminal_format(self):
        """Convert to Windows Terminal format"""
        return {
            "name": self.name,
            "background": self.background,
            "foreground": self.foreground,
            "colors": self.colors
        }

# Predefined Kali Linux color schemes
KALI_DARK = ColorScheme(
    name="Kali Dark",
    background="#1E1E1E",
    foreground="#D8D8D8",
    colors=[
        "#1E1E1E",  # black
        "#FF6B6B",  # red
        "#99C794",  # green
        "#FAC863",  # yellow
        "#6699CC",  # blue
        "#C594C5",  # magenta
        "#5FB3B3",  # cyan
        "#D8D8D8",  # white
        "#65737E",  # bright black
        "#FF6B6B",  # bright red
        "#99C794",  # bright green
        "#FAC863",  # bright yellow
        "#6699CC",  # bright blue
        "#C594C5",  # bright magenta
        "#5FB3B3",  # bright cyan
        "#FFFFFF"   # bright white
    ]
)

KALI_LIGHT = ColorScheme(
    name="Kali Light",
    background="#FFFFFF",
    foreground="#1E1E1E",
    colors=[
        "#FFFFFF",  # black
        "#FF6B6B",  # red
        "#99C794",  # green
        "#FAC863",  # yellow
        "#6699CC",  # blue
        "#C594C5",  # magenta
        "#5FB3B3",  # cyan
        "#1E1E1E",  # white
        "#65737E",  # bright black
        "#FF6B6B",  # bright red
        "#99C794",  # bright green
        "#FAC863",  # bright yellow
        "#6699CC",  # bright blue
        "#C594C5",  # bright magenta
        "#5FB3B3",  # bright cyan
        "#000000"   # bright white
    ]
)