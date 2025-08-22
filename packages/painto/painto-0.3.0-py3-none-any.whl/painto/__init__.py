from .color import (
    Color,
    color_lists,
    color_range,
    dynamic_name_lookup,
    dynamic_name_lookup_enabled,
    random_color,
    sort_by_hue,
    sort_by_luminosity,
    sorting_by,
    transparent,
)
from .list_base import base_colors
from .list_pride import pride
from .list_w3c import w3c
from .list_xkcd import xkcd

# TODO: Add X11 colors
color_lists.append(w3c)
color_lists.append(xkcd)
color_lists.append(pride)
color_lists.append(base_colors)


def __getattr__(name: str) -> Color:
    for color_list in color_lists:
        if name in color_list:
            return color_list[name]
    raise AttributeError(f"Color '{name}' not found in predefined w3c/CSS colors.")


__all__ = ["Color", "__getattr__", "sort_by_hue", "sort_by_luminosity", "sorting_by", "random_color", "color_range"]
__all__ += ["dynamic_name_lookup", "dynamic_name_lookup_enabled"]
__all__ += ["xkcd", "pride", "base_colors", "w3c", "transparent"]
