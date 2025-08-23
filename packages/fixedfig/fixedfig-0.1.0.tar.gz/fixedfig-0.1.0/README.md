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
-------------
Install:
    ```bash
    pip install -e plot_utils_pkg/
