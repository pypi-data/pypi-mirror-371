# fixedfig.py written by Charlie 8/22/2025
"""
fixedfig.py
-------------
This module provides a replacement for matplotlib plt.show() that allows
global configuration of figure window size, position, and target screen.

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
-------------
Install:
    ```bash
    pip install -e plot_utils_pkg/
