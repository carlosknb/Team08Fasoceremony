"""
FasoCeremonies - Configuration Module
======================================
Central configuration for the ceremony management system.
Contains constants, UI theme definitions, and application settings.
"""

import os

# ──────────────────────────────────────────────
# Application Information
# ──────────────────────────────────────────────
APP_NAME: str = "FasoCeremonies"
APP_SLOGAN: str = "Plan Your Ceremonies with Elegance"
APP_SUBTITLE: str = "Ceremony Management System - Burkina Faso"
APP_VERSION: str = "2.0.0"

# ──────────────────────────────────────────────
# Data File Paths (TXT Format)
# ──────────────────────────────────────────────
DATA_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CEREMONIES_FILE: str = os.path.join(DATA_DIR, "ceremonies.txt")
GUESTS_FILE: str = os.path.join(DATA_DIR, "guests.txt")
INVITATIONS_FILE: str = os.path.join(DATA_DIR, "invitations.txt")

# ──────────────────────────────────────────────
# TXT File Delimiter
# ──────────────────────────────────────────────
FIELD_SEP: str = "|"
ARRAY_SEP: str = ";"
RECORD_SEP: str = "---"

# ──────────────────────────────────────────────
# Ceremony Types
# ──────────────────────────────────────────────
CEREMONY_TYPES: tuple = (
    "marriage",
    "funeral",
    "baptism",
    "seminar",
)

CEREMONY_LABELS: dict = {
    "marriage": "Marriage Ceremony",
    "funeral": "Funeral Ceremony",
    "baptism": "Baptism Ceremony",
    "seminar": "Seminar / Conference",
}

# ──────────────────────────────────────────────
# Ceremony Statuses
# ──────────────────────────────────────────────
CEREMONY_STATUSES: tuple = (
    "planning",
    "confirmed",
    "in_progress",
    "completed",
    "cancelled",
)

CEREMONY_STATUS_ICONS: dict = {
    "planning": "[o]",
    "confirmed": "[O]",
    "in_progress": "[>>]",
    "completed": "[OK]",
    "cancelled": "[X]",
}

# ──────────────────────────────────────────────
# RSVP Statuses
# ──────────────────────────────────────────────
RSVP_STATUSES: tuple = (
    "pending",
    "accepted",
    "declined",
    "tentative",
)

RSVP_ICONS: dict = {
    "pending": "[?]",
    "accepted": "[Y]",
    "declined": "[N]",
    "tentative": "[~]",
}

# ──────────────────────────────────────────────
# Marriage-Specific
# ──────────────────────────────────────────────
MARRIAGE_STAGES: tuple = (
    "traditional",
    "civil",
    "religious",
    "all_stages",
)

INVITATION_SIDES: tuple = (
    "bride",
    "groom",
    "family",
    "friend",
    "colleague",
    "other",
)

# ──────────────────────────────────────────────
# Funeral-Specific
# ──────────────────────────────────────────────
FUNERAL_TYPES: tuple = (
    "traditional",
    "religious",
    "mixed",
)

# ──────────────────────────────────────────────
# Expense Categories
# ──────────────────────────────────────────────
EXPENSE_CATEGORIES: tuple = (
    "venue",
    "catering",
    "decoration",
    "music",
    "photography",
    "clothing",
    "transport",
    "flowers",
    "invitation_cards",
    "religious_officiant",
    "mortuary",
    "casket",
    "refreshments",
    "equipment",
    "speaker_fees",
    "printing",
    "other",
)

# ──────────────────────────────────────────────
# Currency
# ──────────────────────────────────────────────
CURRENCY: str = "FCFA"
CURRENCY_SYMBOL: str = "F"

# ──────────────────────────────────────────────
# ID Prefixes
# ──────────────────────────────────────────────
CEREMONY_ID_PREFIX: str = "CER"
GUEST_ID_PREFIX: str = "GST"

# ──────────────────────────────────────────────
# ANSI Color Codes - UI Theme
# ──────────────────────────────────────────────
class Colors:
    """ANSI escape codes for terminal coloring and styling."""
    RESET: str = "\033[0m"
    BOLD: str = "\033[1m"
    DIM: str = "\033[2m"
    ITALIC: str = "\033[3m"
    UNDERLINE: str = "\033[4m"

    BLACK: str = "\033[30m"
    RED: str = "\033[31m"
    GREEN: str = "\033[32m"
    YELLOW: str = "\033[33m"
    BLUE: str = "\033[34m"
    MAGENTA: str = "\033[35m"
    CYAN: str = "\033[36m"
    WHITE: str = "\033[37m"

    BRIGHT_RED: str = "\033[91m"
    BRIGHT_GREEN: str = "\033[92m"
    BRIGHT_YELLOW: str = "\033[93m"
    BRIGHT_BLUE: str = "\033[94m"
    BRIGHT_MAGENTA: str = "\033[95m"
    BRIGHT_CYAN: str = "\033[96m"
    BRIGHT_WHITE: str = "\033[97m"

    BG_BLACK: str = "\033[40m"
    BG_RED: str = "\033[41m"
    BG_GREEN: str = "\033[42m"
    BG_YELLOW: str = "\033[43m"
    BG_BLUE: str = "\033[44m"
    BG_MAGENTA: str = "\033[45m"
    BG_CYAN: str = "\033[46m"
    BG_WHITE: str = "\033[47m"


# ──────────────────────────────────────────────
# UI Theme - Semantic Color Aliases
# ──────────────────────────────────────────────
class Theme:
    """Semantic color aliases for consistent UI theming."""
    PRIMARY: str = Colors.BRIGHT_CYAN
    SECONDARY: str = Colors.CYAN
    ACCENT: str = Colors.BRIGHT_YELLOW
    SUCCESS: str = Colors.BRIGHT_GREEN
    WARNING: str = Colors.BRIGHT_YELLOW
    ERROR: str = Colors.BRIGHT_RED
    INFO: str = Colors.BRIGHT_BLUE
    MUTED: str = Colors.DIM
    HIGHLIGHT: str = Colors.BRIGHT_MAGENTA
    HEADING: str = Colors.BRIGHT_CYAN + Colors.BOLD
    SUBHEADING: str = Colors.CYAN + Colors.BOLD
    MENU_NUM: str = Colors.BRIGHT_YELLOW + Colors.BOLD
    MENU_TEXT: str = Colors.BRIGHT_WHITE
    VALUE: str = Colors.BRIGHT_GREEN
    LABEL: str = Colors.BRIGHT_CYAN
    BORDER: str = Colors.CYAN
    BANNER: str = Colors.BRIGHT_CYAN + Colors.BOLD
    DIVIDER: str = Colors.DIM


# ──────────────────────────────────────────────
# Box-Drawing Characters
# ──────────────────────────────────────────────
class Box:
    """Unicode box-drawing characters for terminal UI frames."""
    TL: str = "\u250c"
    TR: str = "\u2510"
    BL: str = "\u2514"
    BR: str = "\u2518"
    H: str = "\u2500"
    V: str = "\u2502"
    T_DOWN: str = "\u252c"
    T_UP: str = "\u2534"
    T_RIGHT: str = "\u251c"
    T_LEFT: str = "\u2524"
    CROSS: str = "\u253c"

    DTL: str = "\u2554"
    DTR: str = "\u2557"
    DBL: str = "\u255a"
    DBR: str = "\u255d"
    DH: str = "\u2550"
    DV: str = "\u2551"


# ──────────────────────────────────────────────
# UI Layout Constants
# ──────────────────────────────────────────────
TERMINAL_WIDTH: int = 60
MENU_INDENT: int = 4
SECTION_INDENT: int = 6

# ──────────────────────────────────────────────
# Date Format
# ──────────────────────────────────────────────
DATE_FORMAT: str = "%Y-%m-%d"
DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
