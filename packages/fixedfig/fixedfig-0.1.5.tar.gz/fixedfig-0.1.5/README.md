fixedfig 0.1.5

written by Charlie and his friends (8/22/2025)

-------------

This module provides an enhanced version of matplotlib's plt.show(), enabling global configuration of figure window size, position, and target screen.

·Dependencies:

    pip install matplotlib
    pip install pyglet==1.5.27  # required for multiscreen support

·Features:

1. Fixed window size and centered display.
2. Adaptive window size with top-left corner offset.
3. Supports choosing which screen to display on (primary or secondary).
4. Compatible with TkAgg. Switch to the TkAgg backend by default on macOS to ensure window control.

·Usage:

    import fixedfig
    
    # Figure window fixed at 800x600 pixels and centered on the primary screen
    fixedfig.set_show_config([800, 600], fixed_size=True, screen_index=0)
    plt.plot(...)
    plt.show()

    # Figure window with adaptive size, positioned with an offset of 100x50 pixels on the secondary screen
    fixedfig.set_show_config([100, 50], fixed_size=False, screen_index=1)
    plt.plot(...)
    plt.show()

-------------

