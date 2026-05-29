"""
FasoCeremonies - Services Module
=================================
Provides data persistence (TXT format), input validation,
formatting utilities, and UI helper functions.
"""

from __future__ import annotations
import os
import re
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple, Any

from config import (
    DATA_DIR, CEREMONIES_FILE, GUESTS_FILE, INVITATIONS_FILE,
    FIELD_SEP, RECORD_SEP, CURRENCY, TERMINAL_WIDTH,
    DATE_FORMAT, CEREMONY_TYPES, CEREMONY_STATUSES, RSVP_STATUSES,
    EXPENSE_CATEGORIES, MARRIAGE_STAGES, FUNERAL_TYPES, INVITATION_SIDES,
    Colors, Theme, Box,
)
from models import (
    Ceremony, MarriageCeremony, FuneralCeremony,
    BaptismCeremony, SeminarCeremony,
    Guest, Invitation, Expense, Contribution,
)


# ══════════════════════════════════════════════
# DATA PERSISTENCE - TXT FILE OPERATIONS
# ══════════════════════════════════════════════

def ensure_data_dir() -> None:
    """Ensure the data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)


def save_ceremonies(ceremonies: List[Ceremony]) -> None:
    """Save all ceremonies to the TXT data file.

    Each ceremony is serialized to a single line using pipe delimiters.
    Records are separated by a record separator line.
    """
    ensure_data_dir()
    lines = []
    for c in ceremonies:
        lines.append(c.to_text_line())
    with open(CEREMONIES_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        if lines:
            f.write("\n")


def load_ceremonies() -> List[Ceremony]:
    """Load all ceremonies from the TXT data file.

    Returns an empty list if the file does not exist or is empty.
    Skips blank lines and comment lines (starting with #).
    """
    if not os.path.exists(CEREMONIES_FILE):
        return []
    ceremonies = []
    with open(CEREMONIES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                c = Ceremony.from_text_line(line)
                ceremonies.append(c)
            except (IndexError, ValueError, TypeError):
                continue  # Skip malformed lines
    return ceremonies


def save_guests(guests: List[Guest]) -> None:
    """Save all guests to the TXT data file."""
    ensure_data_dir()
    lines = []
    for g in guests:
        lines.append(g.to_text_line())
    with open(GUESTS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        if lines:
            f.write("\n")


def load_guests() -> List[Guest]:
    """Load all guests from the TXT data file."""
    if not os.path.exists(GUESTS_FILE):
        return []
    guests = []
    with open(GUESTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                g = Guest.from_text_line(line)
                guests.append(g)
            except (IndexError, ValueError, TypeError):
                continue
    return guests


def save_invitations(invitations: List[Invitation]) -> None:
    """Save all invitations to the TXT data file.

    Also stores embedded Expense and Contribution records.
    Format:
        - Blank line as section separator
        - INV lines for invitations
        - EXP lines for expenses
        - CON lines for contributions
    """
    ensure_data_dir()
    inv_lines = []
    exp_lines = []
    con_lines = []

    for inv in invitations:
        inv_lines.append(inv.to_text_line())

    # We also need to save expenses and contributions
    # They are stored inline via the ceremony objects
    ceremonies = load_ceremonies()
    for c in ceremonies:
        for e in c._loaded_expenses:
            exp_lines.append(e.to_text_line())
        for con in c._loaded_contributions:
            con_lines.append(con.to_text_line())

    with open(INVITATIONS_FILE, "w", encoding="utf-8") as f:
        f.write("# FasoCeremonies Data File - Invitations, Expenses, Contributions\n")
        f.write("# Do not edit manually unless you know the format\n\n")
        if inv_lines:
            f.write("[INVITATIONS]\n")
            f.write("\n".join(inv_lines) + "\n\n")
        if exp_lines:
            f.write("[EXPENSES]\n")
            f.write("\n".join(exp_lines) + "\n\n")
        if con_lines:
            f.write("[CONTRIBUTIONS]\n")
            f.write("\n".join(con_lines) + "\n\n")


def save_all(
    ceremonies: List[Ceremony],
    guests: List[Guest],
    invitations: List[Invitation],
    expenses: List[Expense],
    contributions: List[Contribution],
) -> None:
    """Save all data to TXT files using the unified format."""
    ensure_data_dir()

    # Save ceremonies
    cer_lines = [c.to_text_line() for c in ceremonies]
    with open(CEREMONIES_FILE, "w", encoding="utf-8") as f:
        f.write("# FasoCeremonies - Ceremonies Data\n")
        f.write("\n".join(cer_lines))
        if cer_lines:
            f.write("\n")

    # Save guests
    gst_lines = [g.to_text_line() for g in guests]
    with open(GUESTS_FILE, "w", encoding="utf-8") as f:
        f.write("# FasoCeremonies - Guests Data\n")
        f.write("\n".join(gst_lines))
        if gst_lines:
            f.write("\n")

    # Save invitations, expenses, contributions in one file
    with open(INVITATIONS_FILE, "w", encoding="utf-8") as f:
        f.write("# FasoCeremonies - Invitations, Expenses, Contributions\n\n")
        f.write("[INVITATIONS]\n")
        for inv in invitations:
            f.write(inv.to_text_line() + "\n")
        f.write("\n[EXPENSES]\n")
        for exp in expenses:
            f.write(exp.to_text_line() + "\n")
        f.write("\n[CONTRIBUTIONS]\n")
        for con in contributions:
            f.write(con.to_text_line() + "\n")
        f.write("\n")


def load_all() -> Tuple[List[Ceremony], List[Guest], List[Invitation], List[Expense], List[Contribution]]:
    """Load all data from TXT files.

    Returns a tuple of (ceremonies, guests, invitations, expenses, contributions).
    """
    ceremonies = load_ceremonies()
    guests = load_guests()
    invitations = []
    expenses = []
    contributions = []

    if os.path.exists(INVITATIONS_FILE):
        current_section = ""
        with open(INVITATIONS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("["):
                    current_section = line.strip("[]").upper()
                    continue
                try:
                    if current_section == "INVITATIONS":
                        invitations.append(Invitation.from_text_line(line))
                    elif current_section == "EXPENSES":
                        expenses.append(Expense.from_text_line(line))
                    elif current_section == "CONTRIBUTIONS":
                        contributions.append(Contribution.from_text_line(line))
                except (IndexError, ValueError, TypeError):
                    continue

    # Link associations to ceremonies
    for c in ceremonies:
        c_inv = [i for i in invitations if i.ceremony_id == c.ceremony_id]
        c_exp = [e for e in expenses if e.ceremony_id == c.ceremony_id]
        c_con = [co for co in contributions if co.ceremony_id == c.ceremony_id]
        c.load_associations(expenses=c_exp, contributions=c_con, invitations=c_inv)

    return ceremonies, guests, invitations, expenses, contributions


# ══════════════════════════════════════════════
# LOOKUP HELPERS
# ══════════════════════════════════════════════

def find_ceremony_by_id(ceremonies: List[Ceremony], cid: str) -> Optional[Ceremony]:
    """Find a ceremony by its ID."""
    for c in ceremonies:
        if c.ceremony_id == cid:
            return c
    return None


def find_guest_by_id(guests: List[Guest], gid: str) -> Optional[Guest]:
    """Find a guest by their ID."""
    for g in guests:
        if g.guest_id == gid:
            return g
    return None


def find_guests_for_ceremony(
    guests: List[Guest], invitations: List[Invitation], ceremony_id: str
) -> List[Tuple[Guest, Invitation]]:
    """Find all guests invited to a specific ceremony with their invitation info."""
    result = []
    for inv in invitations:
        if inv.ceremony_id == ceremony_id:
            guest = find_guest_by_id(guests, inv.guest_id)
            if guest:
                result.append((guest, inv))
    return result


def find_invitations_for_guest(
    invitations: List[Invitation], guest_id: str
) -> List[Invitation]:
    """Find all invitations for a specific guest."""
    return [i for i in invitations if i.guest_id == guest_id]


def find_expenses_for_ceremony(
    expenses: List[Expense], ceremony_id: str
) -> List[Expense]:
    """Find all expenses for a specific ceremony."""
    return [e for e in expenses if e.ceremony_id == ceremony_id]


def find_contributions_for_ceremony(
    contributions: List[Contribution], ceremony_id: str
) -> List[Contribution]:
    """Find all contributions for a specific ceremony."""
    return [c for c in contributions if c.ceremony_id == ceremony_id]


def find_contributions_by_guest(
    contributions: List[Contribution], guest_id: str
) -> List[Contribution]:
    """Find all contributions made by a specific guest."""
    return [c for c in contributions if c.guest_id == guest_id]


# ══════════════════════════════════════════════
# INPUT VALIDATION
# ══════════════════════════════════════════════

def validate_positive_float(value: str, field_name: str = "Value") -> Tuple[bool, float, str]:
    """Validate that a string can be parsed as a positive float.

    Returns (is_valid, parsed_value, error_message).
    """
    try:
        num = float(value)
        if num < 0:
            return False, 0.0, f"{field_name} must be zero or positive."
        return True, num, ""
    except ValueError:
        return False, 0.0, f"Invalid number for {field_name}."


def validate_positive_int(value: str, field_name: str = "Value") -> Tuple[bool, int, str]:
    """Validate that a string can be parsed as a positive integer.

    Returns (is_valid, parsed_value, error_message).
    """
    try:
        num = int(value)
        if num < 0:
            return False, 0, f"{field_name} must be zero or positive."
        return True, num, ""
    except ValueError:
        return False, 0, f"Invalid integer for {field_name}."


def validate_date(value: str) -> Tuple[bool, str, str]:
    """Validate that a string matches the expected date format (YYYY-MM-DD).

    Returns (is_valid, formatted_date, error_message).
    """
    try:
        parsed = datetime.strptime(value.strip(), DATE_FORMAT)
        return True, parsed.strftime(DATE_FORMAT), ""
    except ValueError:
        return False, "", f"Invalid date format. Use {DATE_FORMAT}."


def validate_choice(value: str, min_val: int, max_val: int) -> Tuple[bool, int, str]:
    """Validate that a string is an integer within the given range.

    Returns (is_valid, parsed_value, error_message).
    """
    try:
        num = int(value)
        if min_val <= num <= max_val:
            return True, num, ""
        return False, 0, f"Choose a number between {min_val} and {max_val}."
    except ValueError:
        return False, 0, "Please enter a valid number."


def validate_non_empty(value: str, field_name: str = "Field") -> Tuple[bool, str, str]:
    """Validate that a string is not empty after stripping whitespace.

    Returns (is_valid, cleaned_value, error_message).
    """
    cleaned = value.strip()
    if not cleaned:
        return False, "", f"{field_name} cannot be empty."
    return True, cleaned, ""


# ══════════════════════════════════════════════
# FORMATTING UTILITIES
# ══════════════════════════════════════════════

def format_fcfa(amount: float) -> str:
    """Format an amount as FCFA currency string."""
    return f"{amount:,.0f} {CURRENCY}"


def format_percentage(value: float) -> str:
    """Format a float as a percentage string."""
    return f"{value:.1f}%"


def days_until(date_str: str) -> int:
    """Calculate the number of days from today until the given date.

    Returns a negative number if the date is in the past.
    """
    try:
        target = datetime.strptime(date_str, DATE_FORMAT).date()
        today = date.today()
        return (target - today).days
    except ValueError:
        return 0


def compute_rsvp_stats(invitations: List[Invitation]) -> Dict[str, int]:
    """Compute RSVP statistics from a list of invitations.

    Returns a dict like {'pending': 3, 'accepted': 5, 'declined': 1, 'tentative': 2}
    """
    stats = {s: 0 for s in RSVP_STATUSES}
    for inv in invitations:
        if inv.rsvp_status in stats:
            stats[inv.rsvp_status] += 1
    return stats


def compute_budget_status(ceremony: Ceremony) -> str:
    """Return a human-readable budget status string for a ceremony."""
    if ceremony.budget <= 0:
        return "No budget set"
    pct = ceremony.budget_usage_percent
    if pct <= 50:
        return f"On track ({pct:.0f}% used)"
    elif pct <= 80:
        return f"Caution ({pct:.0f}% used)"
    elif pct <= 100:
        return f"Near limit ({pct:.0f}% used)"
    else:
        return f"OVER BUDGET ({pct:.0f}% used)"


# ══════════════════════════════════════════════
# UI HELPER FUNCTIONS
# ══════════════════════════════════════════════

def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def colored(text: str, color: str) -> str:
    """Apply an ANSI color to text and reset afterward."""
    return f"{color}{text}{Colors.RESET}"


def draw_box(title: str, content_lines: List[str], width: int = TERMINAL_WIDTH) -> str:
    """Draw a framed box with a title and content lines.

    Uses single-line box-drawing characters.
    """
    inner_w = width - 4
    lines = []
    # Top border
    lines.append(f"{Box.TL}{Box.H * (inner_w + 2)}{Box.TR}")
    # Title line
    title_padded = title.center(inner_w)
    lines.append(f"{Box.V} {colored(title_padded, Theme.HEADING)} {Box.V}")
    # Separator
    lines.append(f"{Box.T_RIGHT}{Box.H * (inner_w + 2)}{Box.T_LEFT}")
    # Content
    for line in content_lines:
        padded = line.ljust(inner_w)
        lines.append(f"{Box.V} {padded} {Box.V}")
    # Bottom border
    lines.append(f"{Box.BL}{Box.H * (inner_w + 2)}{Box.BR}")
    return "\n".join(lines)


def draw_double_box(title: str, content_lines: List[str], width: int = TERMINAL_WIDTH) -> str:
    """Draw a double-line framed box with a title and content lines."""
    inner_w = width - 4
    lines = []
    lines.append(f"{Box.DTL}{Box.DH * (inner_w + 2)}{Box.DTR}")
    title_padded = title.center(inner_w)
    lines.append(f"{Box.DV} {colored(title_padded, Theme.BANNER)} {Box.DV}")
    lines.append(f"{Box.DV}{' ' * (inner_w + 2)}{Box.DV}")
    for line in content_lines:
        padded = line.ljust(inner_w)
        lines.append(f"{Box.DV} {padded} {Box.DV}")
    lines.append(f"{Box.DBL}{Box.DH * (inner_w + 2)}{Box.DBR}")
    return "\n".join(lines)


def draw_divider(char: str = Box.H, width: int = TERMINAL_WIDTH) -> str:
    """Draw a horizontal divider line."""
    return colored(char * width, Theme.DIVIDER)


def draw_section_header(title: str, width: int = TERMINAL_WIDTH) -> str:
    """Draw a section header with decorative framing."""
    padded = f"  {title}  "
    side_w = (width - len(padded)) // 2
    left = Box.H * side_w
    right = Box.H * (width - len(padded) - side_w)
    return colored(f"{left}{padded}{right}", Theme.SECONDARY)


def print_success(message: str) -> None:
    """Print a success message in green."""
    print(colored(f"  [+] {message}", Theme.SUCCESS))


def print_error(message: str) -> None:
    """Print an error message in red."""
    print(colored(f"  [x] {message}", Theme.ERROR))


def print_info(message: str) -> None:
    """Print an info message in blue."""
    print(colored(f"  [i] {message}", Theme.INFO))


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    print(colored(f"  [!] {message}", Theme.WARNING))


def print_label_value(label: str, value: str, indent: int = 4) -> None:
    """Print a label-value pair with consistent formatting."""
    lbl = colored(f"{' ' * indent}{label}:", Theme.LABEL)
    val = colored(str(value), Theme.VALUE)
    print(f"{lbl} {val}")


def prompt_input(prompt_text: str, color: str = Theme.PRIMARY) -> str:
    """Display a colored prompt and return the user's input."""
    prompt = colored(f"  > {prompt_text}: ", color)
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def prompt_confirm(prompt_text: str) -> bool:
    """Ask for a yes/no confirmation. Returns True for yes."""
    response = prompt_input(f"{prompt_text} (y/n)")
    return response.lower() in ("y", "yes", "oui", "o")


def pause() -> None:
    """Pause and wait for the user to press Enter."""
    prompt_input("Press Enter to continue", Theme.MUTED)


def select_from_list(
    items: List[str],
    title: str = "Select an option",
    allow_back: bool = True,
) -> Tuple[bool, int]:
    """Display a numbered list and get the user's selection.

    Returns (was_successful, selected_index).
    If the user chooses to go back, returns (False, -1).
    """
    print()
    print(colored(f"  {title}", Theme.SUBHEADING))
    print(draw_divider())

    for i, item in enumerate(items, 1):
        num = colored(f"  {i}.", Theme.MENU_NUM)
        text = colored(item, Theme.MENU_TEXT)
        print(f"{num} {text}")

    if allow_back:
        num = colored("  0.", Theme.MENU_NUM)
        text = colored("Back", Theme.MUTED)
        print(f"{num} {text}")

    max_val = len(items)
    choice = prompt_input("Your choice")
    if not choice:
        return False, -1
    valid, val, err = validate_choice(choice, 0, max_val)
    if not valid:
        print_error(err)
        return False, -1
    if val == 0:
        return False, -1
    return True, val - 1


def display_table(headers: List[str], rows: List[List[str]], col_widths: Optional[List[int]] = None) -> None:
    """Display a formatted table in the terminal.

    If col_widths is not provided, they are calculated from headers and data.
    """
    if not rows:
        print_info("No data to display.")
        return

    num_cols = len(headers)
    if col_widths is None:
        col_widths = []
        for i in range(num_cols):
            max_w = len(headers[i])
            for row in rows:
                if i < len(row):
                    max_w = max(max_w, len(row[i]))
            col_widths.append(min(max_w + 2, 30))

    # Header
    header_parts = []
    for i, h in enumerate(headers):
        w = col_widths[i] if i < len(col_widths) else 15
        header_parts.append(colored(h.ljust(w), Theme.HEADING))
    print("  " + "".join(header_parts))

    # Separator
    sep_parts = [Box.H * w for w in col_widths]
    print("  " + colored("".join(sep_parts), Theme.DIVIDER))

    # Rows
    for row in rows:
        row_parts = []
        for i in range(num_cols):
            val = row[i] if i < len(row) else ""
            w = col_widths[i] if i < len(col_widths) else 15
            row_parts.append(val.ljust(w))
        print("  " + "".join(row_parts))


def display_paginated_list(
    items: List[str],
    title: str = "",
    page_size: int = 10,
) -> None:
    """Display a list of items with pagination."""
    if not items:
        print_info("No items to display.")
        return

    if title:
        print(colored(f"\n  {title}", Theme.SUBHEADING))
        print(draw_divider())

    total = len(items)
    page = 0
    while page * page_size < total:
        start = page * page_size
        end = min(start + page_size, total)
        for i in range(start, end):
            num = colored(f"  {i + 1}.", Theme.MENU_NUM)
            print(f"{num} {items[i]}")
        if end < total:
            print(colored(f"  ... showing {start + 1}-{end} of {total}", Theme.MUTED))
            if not prompt_confirm("Show more?"):
                break
        page += 1
