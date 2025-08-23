# fixedfig.py written by Charlie 8/22/2025
"""
fixedfig.py
-------------
This module provides a replacement for matplotlib plt.show() that allows
global configuration of figure window size, position, and target screen.

Dependencies:
    pip install matplotlib
    pip install pyglet==1.5.27  # required for multiscreen support

Features:
1. Fixed window size and centered display.
2. Adaptive window size with top-left corner offset.
3. Supports choosing which screen to display on (primary or secondary).
4. Compatible with TkAgg, Qt, and other common backends.

Usage:
    import fixedfig
    # Fixed size 800x600, centered on primary screen
    fixedfig.set_show_config([800, 600], fixed_size=True, screen_index=0)
    plt.plot(...)
    plt.show()

    # Adaptive size, offset on secondary screen
    fixedfig.set_show_config([100, 50], fixed_size=False, screen_index=1)
    plt.plot(...)
    plt.show()
"""

import matplotlib

# Force TkAgg backend on macOS
if matplotlib.get_backend().lower() != "TkAgg":
    matplotlib.use("TkAgg", force=True)

import matplotlib.pyplot as plt
import tkinter as tk
from typing import Optional, List
import pyglet

# Save the original plt.show() function
_ORIGINAL_SHOW = plt.show

# Default window configuration
_width, _height = 800, 600
_fixed_size = False
_screen_index = 0  # 0=primary, 1=secondary, etc.

# Tk instance cache
_root: Optional[tk.Tk] = None


def set_show_config(
        size: Optional[List[int]] = None,
        fixed_size: bool = False,
        screen_index: int = 0
):
    """Set global figure window configuration."""
    global _width, _height, _fixed_size, _screen_index
    if size is not None and len(size) == 2:
        _width, _height = int(size[0]), int(size[1])
    _fixed_size = fixed_size
    _screen_index = screen_index


def _init_screen() -> (int, int, int, int):
    """Return geometry of the chosen screen: (screen_x, screen_y, screen_width, screen_height)"""
    global _root
    display = pyglet.canvas.get_display()
    screens = display.get_screens()
    index = min(_screen_index, len(screens) - 1)
    m = screens[index]
    return m.x, m.y, m.width, m.height


def _show_window():
    """Internal function: display the figure window according to the global configuration."""
    screen_x, screen_y, screen_w, screen_h = _init_screen()
    mng = plt.get_current_fig_manager()
    window = getattr(mng, "window", None)
    if mng is None or window is None:
        _ORIGINAL_SHOW()
        return

    x, y = 0, 0
    try:
        if _fixed_size:
            x = screen_x + (screen_w - _width) // 2
            y = screen_y + (screen_h - _height) // 2
            window.wm_geometry(f"{_width}x{_height}+{x}+{y}")
        else:
            x = screen_x + _width
            y = screen_y + _height
            window.wm_geometry(f"+{x}+{y}")
    except AttributeError:
        move_method = getattr(window, "move", None)
        if move_method is not None:
            move_method(x, y)

    _ORIGINAL_SHOW()


def show_window():
    """Replacement for plt.show() that applies the global window configuration."""
    _show_window()


# Override matplotlib show function
plt.show = show_window
