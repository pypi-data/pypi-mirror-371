# fixedfig.py written by Charlie 8/22/2025
"""
fixedfig.py
-------------
This module provides a replacement for matplotlib plt.show() that allows
global configuration of figure window size and position.

Features:
1. Fixed window size and centered display.
2. Adaptive window size with top-left corner offset.
3. Automatically compatible with TkAgg, Qt, and other common backends.

Usage:
    import fixedfig
    fixedfig.set_show_config([800, 600], fixed_size=True)
    plt.plot(...)
    plt.show()  # Applies the global window configuration
"""

import matplotlib.pyplot as plt
import tkinter as tk
from typing import Optional, List

# Save the original plt.show() function
_ORIGINAL_SHOW = plt.show

# Default window configuration
_width, _height = 800, 600
_fixed_size = False

# Tk instance cache to avoid repeated initialization
_root: Optional[tk.Tk] = None


def set_show_config(size: Optional[List[int]] = None, fixed_size: bool = False):
    """
    Set global figure window configuration.

    :param size: [width, height] in pixels
                 fixed_size=True: specifies window size
                 fixed_size=False: specifies top-left corner offset
    :param fixed_size: True for fixed size and centered display,
                       False for adaptive figure size with offset
    """
    global _width, _height, _fixed_size
    if size is not None and len(size) == 2:
        _width, _height = int(size[0]), int(size[1])
    _fixed_size = fixed_size


def _init_screen() -> (int, int):
    """
    Initialize Tk and return the screen width and height.

    :return: (screen_width, screen_height)
    """
    global _root
    if _root is None:
        _root = tk.Tk()
        _root.withdraw()  # Hide the Tk main window
    return int(_root.winfo_screenwidth()), int(_root.winfo_screenheight())


def _show_window():
    """
    Internal function: display the figure window according to the global configuration.
    """
    screen_w, screen_h = _init_screen()
    mng = plt.get_current_fig_manager()
    window = getattr(mng, "window", None)  # Safely access backend-specific window
    if mng is None or window is None:
        _ORIGINAL_SHOW()
        return

    # Initialize x, y to avoid potential uninitialized variable usage
    x, y = 0, 0
    try:
        if _fixed_size:
            # Fixed window size, centered display
            x = (screen_w - _width) // 2
            y = (screen_h - _height) // 2
            window.wm_geometry(f"{_width}x{_height}+{x}+{y}")
        else:
            # Adaptive window size, top-left corner offset
            x, y = _width, _height
            window.wm_geometry(f"+{x}+{y}")
    except AttributeError:
        # Qt backend may not have wm_geometry, use move() if available
        move_method = getattr(window, "move", None)
        if move_method is not None:
            move_method(x, y)

    _ORIGINAL_SHOW()


def show_window():
    """Replacement for plt.show() that applies the global window configuration."""
    _show_window()


# Override matplotlib show function to apply global window settings
plt.show = show_window
