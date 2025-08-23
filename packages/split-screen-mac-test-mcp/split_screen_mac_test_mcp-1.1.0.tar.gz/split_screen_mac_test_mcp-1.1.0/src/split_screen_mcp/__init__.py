"""Split Screen macOS MCP Server - Window Management Tools"""

__version__ = "1.1.0"
__author__ = "Beta"

from .window_actions import (
    move_active_window_left_half, move_active_window_right_half,
    move_active_window_top_half, move_active_window_bottom_half,
    move_active_window_top_left_quarter, move_active_window_top_right_quarter,
    move_active_window_bottom_left_quarter, move_active_window_bottom_right_quarter,
    move_active_window_left_third, move_active_window_middle_third, move_active_window_right_third,
    move_active_window_left_two_third, move_active_window_right_two_third,
    move_active_window_maximize, minimize_active_window, fullscreen_active_window,
)

__all__ = [
    "__version__",
    "__author__",
    "move_active_window_left_half", "move_active_window_right_half",
    "move_active_window_top_half", "move_active_window_bottom_half",
    "move_active_window_top_left_quarter", "move_active_window_top_right_quarter",
    "move_active_window_bottom_left_quarter", "move_active_window_bottom_right_quarter",
    "move_active_window_left_third", "move_active_window_middle_third", "move_active_window_right_third",
    "move_active_window_left_two_third", "move_active_window_right_two_third",
    "move_active_window_maximize", "minimize_active_window", "fullscreen_active_window",
]
