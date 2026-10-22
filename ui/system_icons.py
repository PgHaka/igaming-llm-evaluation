"""Original SVG icon family for Control Room system cards."""

from html import escape

SYSTEM_ICON_PATHS = {
    'AI Support Bot': '<path d="M32 12V8"/>\n        <circle cx="32" cy="5" r="3"/>\n        <rect x="12" y="16" width="40" height="34" rx="11"/>\n        <path d="M12 25H8a4 4 0 0 0-4 4v8a4 4 0 0 0 4 4h4"/>\n        <path d="M52 25h4a4 4 0 0 1 4 4v8a4 4 0 0 1-4 4h-4"/>\n        <path d="M24 29v5M40 29v5"/>\n        <path d="M25 41c4 4 10 4 14 0"/>\n        <path d="M26 50c-1 4-4 7-7 9 8 0 13-3 17-9"/>',
    'Payment Automation': '<rect x="7" y="15" width="50" height="34" rx="6"/>\n        <path d="M7 26h50M16 39h13"/>\n        <path d="M39 37l5 5 9-10"/>',
    'KYC Decision Engine': '<rect x="7" y="19" width="50" height="35" rx="5"/>\n        <circle cx="21" cy="33" r="5"/>\n        <path d="M12 46c1-6 5-9 9-9s8 3 9 9"/>\n        <path d="M36 33h13M36 40h10"/>\n        <circle cx="45" cy="15" r="10" fill="#101B2D"/>\n        <path d="M40 15l4 4 7-8"/>',
    'Knowledge Retrieval': '<ellipse cx="32" cy="15" rx="22" ry="8"/>\n        <path d="M10 15v15c0 5 10 8 22 8s22-3 22-8V15"/>\n        <path d="M10 30v15c0 5 10 8 22 8s22-3 22-8V30"/>\n        <path d="M10 30c0 5 10 8 22 8s22-3 22-8"/>',
    'Bonus Automation': '<rect x="12" y="27" width="40" height="29" rx="3"/>\n        <path d="M8 20h48v9H8zM32 20v36"/>\n        <path d="M32 20c-12 0-17-3-17-9 0-4 3-6 7-6 6 0 10 8 10 15z"/>\n        <path d="M32 20c12 0 17-3 17-9 0-4-3-6-7-6-6 0-10 8-10 15z"/>',
    'Model Regression Lab': '<rect x="5" y="12" width="21" height="32" rx="4"/>\n        <rect x="38" y="20" width="21" height="32" rx="4"/>\n        <path d="M11 22h9M11 29h9M44 30h9M44 37h9"/>\n        <path d="M29 17h7l-4-4m4 4-4 4"/>\n        <path d="M35 47h-7l4-4m-4 4 4 4"/>',
}


def system_icon(name, implemented=True):
    """Return a consistent decorative SVG for a known system."""
    if name not in SYSTEM_ICON_PATHS:
        raise ValueError(f"Unknown system icon: {name}")

    color = "#5EEAD4" if implemented else "#71869F"
    label = escape(name, quote=True)

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'width="48" height="48" viewBox="0 0 64 64" '
        'fill="none" '
        f'stroke="{color}" stroke-width="3.5" '
        'stroke-linecap="round" stroke-linejoin="round" '
        f'role="img" aria-label="{label}">'
        + SYSTEM_ICON_PATHS[name]
        + '</svg>'
    )
