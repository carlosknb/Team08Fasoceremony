"""
FasoCeremonies - Guest Portal Module
======================================
Provides the complete Guest interface for interacting with ceremonies.

The Guest portal allows:
  - Viewing personal invitations
  - Responding to RSVPs (accept / decline / tentative)
  - Viewing ceremony details
  - Making financial contributions
  - Viewing contribution history
  - Personal dashboard with upcoming events
"""

from __future__ import annotations
from datetime import date
from typing import List, Optional, Tuple

from config import (
    APP_NAME, CURRENCY, TERMINAL_WIDTH,
    CEREMONY_LABELS, CEREMONY_STATUS_ICONS,
    RSVP_STATUSES, RSVP_ICONS, DATE_FORMAT,
    Colors, Theme, Box,
)
from models import (
    Ceremony, Guest, Invitation, Contribution,
)
from services import (
    save_all, load_all,
    find_ceremony_by_id, find_guest_by_id,
    find_invitations_for_guest,
    find_contributions_by_guest, find_expenses_for_ceremony,
    find_contributions_for_ceremony,
    validate_positive_float, validate_positive_int,
    validate_choice, validate_non_empty,
    format_fcfa, format_percentage, days_until, compute_rsvp_stats,
    clear_screen, colored, draw_box, draw_double_box, draw_divider,
    draw_section_header, print_success, print_error, print_info,
    print_warning, print_label_value, prompt_input, prompt_confirm,
    pause, select_from_list, display_table,
)


# ══════════════════════════════════════════════
# GUEST PORTAL CLASS
# ══════════════════════════════════════════════

class GuestPortal:
    """Guest portal for viewing invitations, RSVPs, and contributing.

    The guest selects or creates their profile, then interacts
    with their personal dashboard.
    """

    def __init__(self) -> None:
        """Initialize the portal and load data."""
        self.ceremonies: List[Ceremony] = []
        self.guests: List[Guest] = []
        self.invitations: List[Invitation] = []
        self.expenses: list = []
        self.contributions: List[Contribution] = []
        self.current_guest: Optional[Guest] = None
        self._reload_data()

    def _reload_data(self) -> None:
        """Reload all data from TXT files."""
        self.ceremonies, self.guests, self.invitations, \
            self.expenses, self.contributions = load_all()

    def _save(self) -> None:
        """Persist all data to TXT files."""
        save_all(self.ceremonies, self.guests, self.invitations,
                 self.expenses, self.contributions)

    # ──────────────────────────────────────────
    # GUEST IDENTIFICATION
    # ──────────────────────────────────────────

    def identify_guest(self) -> bool:
        """Prompt the guest to identify themselves or register.

        Returns True if a guest was successfully identified.
        """
        clear_screen()
        print(draw_section_header("GUEST IDENTIFICATION"))
        print()

        if not self.guests:
            print_info("No guests registered yet. You need to be added by an organizer first.")
            print_info("Please ask the organizer to add you to the guest directory.")
            pause()
            return False

        print(colored("  Welcome! Please identify yourself.", Theme.SUBHEADING))
        print()
        print(colored("  1.", Theme.MENU_NUM), colored("Select from existing guests", Theme.MENU_TEXT))
        print(colored("  2.", Theme.MENU_NUM), colored("Register as a new guest", Theme.MENU_TEXT))
        print(colored("  0.", Theme.MENU_NUM), colored("Back", Theme.MUTED))
        print()

        choice = prompt_input("Your choice")
        if choice == "1":
            return self._select_existing_guest()
        elif choice == "2":
            return self._register_new_guest()
        else:
            return False

    def _select_existing_guest(self) -> bool:
        """Let the guest select their profile from existing guests."""
        guest_labels = [f"{g.guest_id} - {g.full_name} ({g.address or 'No locality'})" for g in self.guests]
        ok, idx = select_from_list(guest_labels, "Select Your Profile")
        if not ok:
            return False

        self.current_guest = self.guests[idx]
        print_success(f"Welcome, {self.current_guest.full_name}!")
        pause()
        return True

    def _register_new_guest(self) -> bool:
        """Register a new guest profile."""
        print(draw_section_header("NEW GUEST REGISTRATION"))
        print()

        first = prompt_input("First name")
        if not first:
            print_error("First name is required.")
            pause()
            return False

        last = prompt_input("Last name")
        if not last:
            print_error("Last name is required.")
            pause()
            return False

        phone = prompt_input("Phone number (optional)")
        email = prompt_input("Email (optional)")
        address = prompt_input("Address / Locality (optional)")
        notes = prompt_input("Notes (optional)")

        guest = Guest(
            first_name=first, last_name=last,
            phone=phone, email=email,
            address=address, notes=notes,
        )
        self.guests.append(guest)
        self.current_guest = guest
        self._save()

        print_success(f"Welcome, {guest.full_name}! Your ID is {guest.guest_id}")
        print_info("You can now view invitations from organizers.")
        pause()
        return True

    # ──────────────────────────────────────────
    # MAIN MENU
    # ──────────────────────────────────────────

    def run(self) -> None:
        """Main guest portal loop after identification."""
        while True:
            clear_screen()
            self._display_header()
            self._display_guest_summary()
            self._display_main_menu()

            choice = prompt_input("Your choice")
            if not choice:
                continue

            actions = {
                "1": self._view_invitations,
                "2": self._respond_to_invitation,
                "3": self._view_ceremony_details,
                "4": self._make_contribution,
                "5": self._view_contribution_history,
                "6": self._upcoming_events,
                "7": self._edit_profile,
                "0": self._logout,
            }

            action = actions.get(choice)
            if action:
                if choice == "0":
                    return
                action()
            else:
                print_error("Invalid option. Please try again.")
                pause()

    def _display_header(self) -> None:
        """Display the guest portal header."""
        if self.current_guest:
            title = f"  {APP_NAME} - Guest Portal  "
            name_line = f"  Welcome, {self.current_guest.full_name}"
            lines = [colored(name_line, Theme.MUTED)]
        else:
            title = f"  {APP_NAME} - Guest Portal  "
            lines = [colored("  View your invitations and contribute to ceremonies.", Theme.MUTED)]
        print(draw_double_box(title, lines))
        print()

    def _display_guest_summary(self) -> None:
        """Display a brief summary for the current guest."""
        if not self.current_guest:
            return

        my_invs = find_invitations_for_guest(self.invitations, self.current_guest.guest_id)
        pending = sum(1 for i in my_invs if i.rsvp_status == "pending")
        accepted = sum(1 for i in my_invs if i.rsvp_status == "accepted")
        my_cons = find_contributions_by_guest(self.contributions, self.current_guest.guest_id)
        total_contributed = sum(c.amount for c in my_cons)

        items = [
            f"Invitations: {len(my_invs)}",
            f"Pending RSVPs: {pending}",
            f"Accepted: {accepted}",
            f"Total Contributed: {format_fcfa(total_contributed)}",
        ]
        line = "  |  ".join(items)
        print(colored(f"  {line}", Theme.INFO))
        print(draw_divider())
        print()

    def _display_main_menu(self) -> None:
        """Display the guest main menu options."""
        menu_items = [
            ("1", "View My Invitations"),
            ("2", "Respond to an Invitation (RSVP)"),
            ("3", "View Ceremony Details"),
            ("4", "Make a Contribution"),
            ("5", "My Contribution History"),
            ("6", "Upcoming Events"),
            ("7", "Edit My Profile"),
            ("0", "Logout"),
        ]
        for num, text in menu_items:
            n = colored(f"  {num}.", Theme.MENU_NUM)
            t = colored(text, Theme.MENU_TEXT)
            print(f"{n} {t}")
        print()

    # ──────────────────────────────────────────
    # 1. VIEW MY INVITATIONS
    # ──────────────────────────────────────────

    def _view_invitations(self) -> None:
        """Display all invitations for the current guest."""
        if not self.current_guest:
            return

        print(draw_section_header("MY INVITATIONS"))
        print()

        my_invs = find_invitations_for_guest(self.invitations, self.current_guest.guest_id)

        if not my_invs:
            print_info("You have no invitations at this time.")
            print_info("Organizers will add you to ceremonies from their portal.")
            pause()
            return

        headers = ["Ceremony", "Date", "Location", "Side", "RSVP", "Table", "+1"]
        rows = []
        for inv in my_invs:
            ceremony = find_ceremony_by_id(self.ceremonies, inv.ceremony_id)
            rsvp_icon = RSVP_ICONS.get(inv.rsvp_status, "?")
            rows.append([
                ceremony.name if ceremony else inv.ceremony_id,
                ceremony.ceremony_date if ceremony else "N/A",
                ceremony.location if ceremony else "N/A",
                inv.side.title(),
                f"{rsvp_icon} {inv.rsvp_status.title()}",
                str(inv.table_number) if inv.table_number else "-",
                "Yes" if inv.plus_one else "No",
            ])
        display_table(headers, rows, [16, 12, 14, 10, 12, 6, 4])

        if any(inv.message for inv in my_invs):
            print()
            print(colored("  Personal Messages:", Theme.SUBHEADING))
            for inv in my_invs:
                if inv.message:
                    ceremony = find_ceremony_by_id(self.ceremonies, inv.ceremony_id)
                    name = ceremony.name if ceremony else inv.ceremony_id
                    print(colored(f"    {name}: \"{inv.message}\"", Theme.MUTED))

        pause()

    # ──────────────────────────────────────────
    # 2. RESPOND TO INVITATION (RSVP)
    # ──────────────────────────────────────────

    def _respond_to_invitation(self) -> None:
        """Allow the guest to respond to a pending invitation."""
        if not self.current_guest:
            return

        my_invs = find_invitations_for_guest(self.invitations, self.current_guest.guest_id)
        pending_invs = [i for i in my_invs if i.rsvp_status == "pending"]

        if not pending_invs:
            if my_invs:
                print_info("You have already responded to all your invitations.")
            else:
                print_info("You have no invitations to respond to.")
            pause()
            return

        print(draw_section_header("RESPOND TO INVITATION"))
        print()

        inv_labels = []
        for inv in pending_invs:
            ceremony = find_ceremony_by_id(self.ceremonies, inv.ceremony_id)
            name = ceremony.name if ceremony else inv.ceremony_id
            date_str = ceremony.ceremony_date if ceremony else "N/A"
            loc = ceremony.location if ceremony else "N/A"
            inv_labels.append(f"{name} | {date_str} | {loc}")

        ok, idx = select_from_list(inv_labels, "Select an Invitation to Respond To")
        if not ok:
            return

        invitation = pending_invs[idx]

        # Show ceremony details
        ceremony = find_ceremony_by_id(self.ceremonies, invitation.ceremony_id)
        if ceremony:
            print()
            print_label_value("Ceremony", ceremony.name)
            print_label_value("Date", ceremony.ceremony_date)
            print_label_value("Location", ceremony.location)
            print_label_value("Type", ceremony.ceremony_type.title())
            if ceremony.description:
                print_label_value("Description", ceremony.description)
            print()

        # RSVP options
        status_labels = [s.title() for s in RSVP_STATUSES]
        ok, sidx = select_from_list(status_labels, "Your Response")
        if not ok:
            return

        old_status = invitation.rsvp_status
        invitation.rsvp_status = RSVP_STATUSES[sidx]
        self._save()

        if invitation.rsvp_status != old_status:
            print_success(f"Your RSVP has been updated to '{invitation.rsvp_status.title()}'.")
        else:
            print_info(f"Your RSVP remains '{invitation.rsvp_status.title()}'.")

        # Offer contribution if accepted
        if invitation.rsvp_status == "accepted":
            if prompt_confirm("Would you like to make a contribution?"):
                self._make_contribution_to_ceremony(invitation.ceremony_id)

        pause()

    # ──────────────────────────────────────────
    # 3. VIEW CEREMONY DETAILS
    # ──────────────────────────────────────────

    def _view_ceremony_details(self) -> None:
        """View details of ceremonies the guest is invited to."""
        if not self.current_guest:
            return

        my_invs = find_invitations_for_guest(self.invitations, self.current_guest.guest_id)
        if not my_invs:
            print_info("You are not invited to any ceremonies yet.")
            pause()
            return

        inv_labels = []
        for inv in my_invs:
            ceremony = find_ceremony_by_id(self.ceremonies, inv.ceremony_id)
            name = ceremony.name if ceremony else inv.ceremony_id
            inv_labels.append(f"{name} | {inv.rsvp_status.title()}")

        ok, idx = select_from_list(inv_labels, "Select a Ceremony to View")
        if not ok:
            return

        invitation = my_invs[idx]
        ceremony = find_ceremony_by_id(self.ceremonies, invitation.ceremony_id)

        if not ceremony:
            print_error("Ceremony not found.")
            pause()
            return

        # Load associations
        c_exp = find_expenses_for_ceremony(self.expenses, ceremony.ceremony_id)
        c_con = find_contributions_for_ceremony(self.contributions, ceremony.ceremony_id)
        c_inv = [i for i in self.invitations if i.ceremony_id == ceremony.ceremony_id]
        ceremony.load_associations(expenses=c_exp, contributions=c_con, invitations=c_inv)

        clear_screen()
        print(draw_section_header(f"CEREMONY: {ceremony.name}"))
        print()
        print(ceremony.generate_report())
        print()
        print_label_value("Your RSVP", f"{RSVP_ICONS.get(invitation.rsvp_status, '?')} {invitation.rsvp_status.title()}")
        print_label_value("Your Side", invitation.side.title())
        print_label_value("Table", str(invitation.table_number) if invitation.table_number else "Not assigned")
        print_label_value("Plus-one", "Yes" if invitation.plus_one else "No")
        if invitation.message:
            print_label_value("Message", invitation.message)
        print()
        pause()

    # ──────────────────────────────────────────
    # 4. MAKE A CONTRIBUTION
    # ──────────────────────────────────────────

    def _make_contribution(self) -> None:
        """Make a financial contribution to a ceremony."""
        if not self.current_guest:
            return

        my_invs = find_invitations_for_guest(self.invitations, self.current_guest.guest_id)
        accepted_invs = [i for i in my_invs if i.rsvp_status == "accepted"]

        if not accepted_invs:
            if my_invs:
                print_info("You can only contribute to ceremonies you have accepted.")
                print_info("Please respond to your invitations first (Menu 2).")
            else:
                print_info("You have no invitations yet.")
            pause()
            return

        inv_labels = []
        for inv in accepted_invs:
            ceremony = find_ceremony_by_id(self.ceremonies, inv.ceremony_id)
            name = ceremony.name if ceremony else inv.ceremony_id
            inv_labels.append(f"{name}")

        ok, idx = select_from_list(inv_labels, "Select a Ceremony to Contribute To")
        if not ok:
            return

        ceremony_id = accepted_invs[idx].ceremony_id
        self._make_contribution_to_ceremony(ceremony_id)

    def _make_contribution_to_ceremony(self, ceremony_id: str) -> None:
        """Make a contribution to a specific ceremony."""
        if not self.current_guest:
            return

        ceremony = find_ceremony_by_id(self.ceremonies, ceremony_id)
        name = ceremony.name if ceremony else ceremony_id

        print(draw_section_header(f"CONTRIBUTE TO: {name}"))
        print()

        amount_str = prompt_input("Contribution amount (FCFA)")
        ok, amount, err = validate_positive_float(amount_str, "Amount")
        if not ok or amount <= 0:
            print_error(err or "Amount must be greater than zero.")
            pause()
            return

        message = prompt_input("Message (optional)")

        contribution = Contribution(
            ceremony_id=ceremony_id,
            guest_id=self.current_guest.guest_id,
            amount=amount,
            message=message,
        )
        self.contributions.append(contribution)

        # Add to ceremony's contribution IDs
        if ceremony:
            ceremony.contribution_ids.append(contribution.contribution_id)

        self._save()
        print_success(f"Contribution of {format_fcfa(amount)} recorded. Thank you!")
        pause()

    # ──────────────────────────────────────────
    # 5. MY CONTRIBUTION HISTORY
    # ──────────────────────────────────────────

    def _view_contribution_history(self) -> None:
        """View all contributions made by the current guest."""
        if not self.current_guest:
            return

        print(draw_section_header("MY CONTRIBUTION HISTORY"))
        print()

        my_cons = find_contributions_by_guest(self.contributions, self.current_guest.guest_id)

        if not my_cons:
            print_info("You have not made any contributions yet.")
            pause()
            return

        headers = ["Ceremony", "Amount", "Date", "Message"]
        rows = []
        for con in my_cons:
            ceremony = find_ceremony_by_id(self.ceremonies, con.ceremony_id)
            rows.append([
                ceremony.name if ceremony else con.ceremony_id,
                format_fcfa(con.amount),
                con.date_contributed,
                con.message[:20] if con.message else "",
            ])
        display_table(headers, rows, [16, 14, 12, 20])

        total = sum(c.amount for c in my_cons)
        print()
        print(colored(f"  Total Contributions: {format_fcfa(total)}", Theme.VALUE))
        pause()

    # ──────────────────────────────────────────
    # 6. UPCOMING EVENTS
    # ──────────────────────────────────────────

    def _upcoming_events(self) -> None:
        """Display upcoming ceremonies the guest is invited to."""
        if not self.current_guest:
            return

        print(draw_section_header("UPCOMING EVENTS"))
        print()

        my_invs = find_invitations_for_guest(self.invitations, self.current_guest.guest_id)
        accepted = [i for i in my_invs if i.rsvp_status in ("accepted", "tentative")]

        if not accepted:
            print_info("No upcoming events. Accept invitations to see them here.")
            pause()
            return

        # Sort by date
        event_list = []
        for inv in accepted:
            ceremony = find_ceremony_by_id(self.ceremonies, inv.ceremony_id)
            if ceremony and ceremony.status not in ("completed", "cancelled"):
                days = days_until(ceremony.ceremony_date)
                event_list.append((ceremony, inv, days))

        event_list.sort(key=lambda x: x[2])

        if not event_list:
            print_info("No upcoming events.")
            pause()
            return

        for ceremony, inv, days in event_list:
            if days > 0:
                day_str = f"in {days} day(s)"
            elif days == 0:
                day_str = "TODAY!"
            else:
                day_str = f"{abs(days)} day(s) ago"

            print(colored(f"  {ceremony.name}", Theme.VALUE))
            print(colored(f"    {ceremony.ceremony_type.title()} | {ceremony.ceremony_date} | {ceremony.location}", Theme.INFO))
            print(colored(f"    {day_str} | Table: {inv.table_number or 'Not assigned'} | +1: {'Yes' if inv.plus_one else 'No'}", Theme.MUTED))
            print()

        pause()

    # ──────────────────────────────────────────
    # 7. EDIT PROFILE
    # ──────────────────────────────────────────

    def _edit_profile(self) -> None:
        """Edit the current guest's profile."""
        if not self.current_guest:
            return

        print(draw_section_header("EDIT MY PROFILE"))
        print_info("Leave blank to keep current value.")
        print()

        new_first = prompt_input(f"First name [{self.current_guest.first_name}]")
        if new_first:
            self.current_guest.first_name = new_first

        new_last = prompt_input(f"Last name [{self.current_guest.last_name}]")
        if new_last:
            self.current_guest.last_name = new_last

        new_phone = prompt_input(f"Phone [{self.current_guest.phone}]")
        if new_phone:
            self.current_guest.phone = new_phone

        new_email = prompt_input(f"Email [{self.current_guest.email}]")
        if new_email:
            self.current_guest.email = new_email

        new_addr = prompt_input(f"Address [{self.current_guest.address}]")
        if new_addr:
            self.current_guest.address = new_addr

        new_notes = prompt_input(f"Notes [{self.current_guest.notes}]")
        if new_notes:
            self.current_guest.notes = new_notes

        self._save()
        print_success("Profile updated.")
        pause()

    # ──────────────────────────────────────────
    # 0. LOGOUT
    # ──────────────────────────────────────────

    def _logout(self) -> None:
        """Save data and return to main menu."""
        self._save()
        self.current_guest = None
        print_success("Data saved. Logging out...")
