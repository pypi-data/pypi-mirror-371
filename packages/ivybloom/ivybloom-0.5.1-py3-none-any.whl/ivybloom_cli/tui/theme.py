from __future__ import annotations

from typing import Dict


def get_tabs_css(colors: Dict[str, str]) -> str:
    """Return CSS styles for clickable tabs using the provided color palette.

    Keep this small and focused so multiple screens can reuse consistent tab styles.
    """
    return f"""
    /* Reusable Tab styles */
    TabbedContent Tab {{
        background: {colors['neutral_cream']};
        color: {colors['sage_dark']};
        border: tall {colors['sage_medium']};
    }}
    TabbedContent Tab:hover {{
        text-style: underline;
        color: {colors['accent']};
    }}
    TabbedContent Tab.-active {{
        background: {colors['sage_medium']};
        color: {colors['neutral_cream']};
    }}
    """


