"""MDLA Android Theme"""
from kivy.utils import get_color_from_hex
from ..config.settings import COLORS


def apply_theme(widget):
    """Apply MDLA theme to widget"""
    # Set background color
    if hasattr(widget, 'canvas'):
        with widget.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*get_color_from_hex(COLORS["bg_primary"]))
            widget.bg_rect = Rectangle(size=widget.size, pos=widget.pos)
            widget.bind(size=_update_rect, pos=_update_rect)


def _update_rect(instance, value):
    """Update background rectangle"""
    if hasattr(instance, 'bg_rect'):
        instance.bg_rect.pos = instance.pos
        instance.bg_rect.size = instance.size


def get_theme_color(color_name: str):
    """Get theme color as Kivy color tuple"""
    hex_color = COLORS.get(color_name, "#FFFFFF")
    return get_color_from_hex(hex_color)