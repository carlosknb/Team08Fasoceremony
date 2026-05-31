"""
Organizer portal for FasoCeremonies.

Full management of ceremonies, guests, invitations, and finances.
"""

from __future__ import annotations

from datetime import date
from typing import Callable, Optional, Tuple

from config import (
    CEREMONY_STATUSES,
    CEREMONY_TYPES,
    CITIES,
    DATE_FORMAT,
    EXPENSE_CATEGORIES,
    RSVP_OPTIONS,
    Theme,
)
from models import (
    Ceremony,
    Contribution,
    CEREMONY_CLASS_MAP,
    Expense,
    Guest,
)
from services import (
    add_guest_to_ceremony,
    ceremonies,
    clear_screen,
    colored_text,
    compute_budget_status,
    compute_rsvp_stats,
    contributions,
    days_until,
    display_paginated_list,
    display_table,
    draw_section_header,
    expenses,
    find_ceremony_by_id,
    find_contributions_for_ceremony,
    find_expenses_for_ceremony,
    find_guest_by_id,
    find_invitations_for_ceremony,
    guests,
    invitations,
    format_fcfa,
    format_percentage,
    pause,
    print_error,
    print_info,
    print_label_value,
    print_success,
    prompt_confirm,
    prompt_input,
    remove_expense_completely,
    remove_guest_completely,
    remove_invitation_completely,
    save_all,
    select_from_list,
    select_multiple_from_list,
    validate_date,
    validate_email,
    validate_name,
    validate_non_empty,
    validate_phone,
    validate_positive_float,
    _rebuild_relations,
)


class OrganizerPortal:
    """Main organizer interface with all management features."""

    def run(self) -> None:
        while True:
            self._show_menu()
            choice = input("\n  Choice: ").strip()
            actions = {
                "1": self._create_ceremony,
                "2": self._manage_ceremonies,
                "3": self._manage_guests,
                "4": self._manage_invitations,
                "5": self._financial_management,
                "6": self._view_reports,
                "7": self._search_ceremonies,
                "8": self._upcoming_ceremonies,
                "9": self._budget_alerts,
                "0": self._logout,
            }
            action = actions.get(choice)
            if action:
                action()
                if choice == "0":
                    return
            else:
                print_error("Invalid choice.")

    def _show_menu(self) -> None:
        clear_screen()
        print(colored_text(draw_section_header("ORGANIZER PORTAL"), Theme.primary))
        print()
        print("  1. Create Ceremony")
        print("  2. Manage Ceremonies")
        print("  3. Manage Guest Directory")
        print("  4. Manage Invitations & RSVPs")
        print("  5. Financial Management")
        print("  6. View Reports")
        print("  7. Search Ceremonies")
        print("  8. Upcoming Ceremonies")
        print("  9. Budget Alerts")
        print("  0. Logout")

    # ------------------------------------------------------------------
    # 1. Create Ceremony
    # ------------------------------------------------------------------

    def _create_ceremony(self) -> None:
        clear_screen()
        print(colored_text(draw_section_header("CREATE CEREMONY"), Theme.primary))
        print()

        # choose type
        type_items = [t.capitalize() for t in CEREMONY_TYPES]
        idx = select_from_list(type_items, "Ceremony type")
        if idx is None:
            return
        ctype = CEREMONY_TYPES[idx]

        # common fields
        name = self._prompt_validated("Name", validate_non_empty)
        if not name:
            return
        date_str = self._prompt_validated(f"Date ({DATE_FORMAT})", validate_date)
        if not date_str:
            return

        city_idx = select_from_list(CITIES, "City")
        city = CITIES[city_idx] if city_idx is not None else ""

        venue = prompt_input("Venue")
        budget_str = self._prompt_validated("Budget", validate_positive_float)
        budget = float(budget_str) if budget_str else 0.0
        organizer = self._prompt_validated("Organizer name", validate_name)
        if not organizer:
            organizer = "Admin"
        desc = prompt_input("Description (optional)")

        # create the right subclass
        cls = CEREMONY_CLASS_MAP.get(ctype, Ceremony)
        c = cls(
            name=name,
            date_str=date_str,
            city=city,
            venue=venue,
            budget=budget,
            organizer=organizer,
            description=desc,
        )
        ceremonies.append(c)
        save_all()
        print_success(f"Ceremony '{name}' created ({ctype}).")
        pause()

    # ------------------------------------------------------------------
    # 2. Manage Ceremonies
    # ------------------------------------------------------------------

    def _manage_ceremonies(self) -> None:
        if not ceremonies:
            print_info("No ceremonies yet. Create one first.")
            pause()
            return

        items = [f"{c.name} ({c.date_str}) - {c.ceremony_type}" for c in ceremonies]
        idx = select_from_list(items, "Select ceremony")
        if idx is None:
            return
        c = ceremonies[idx]
        self._ceremony_detail(c)

    def _ceremony_detail(self, c: Ceremony) -> None:
        while True:
            clear_screen()
            print(
                colored_text(draw_section_header(f"CEREMONY: {c.name}"), Theme.primary)
            )
            print()
            print_label_value("Type:", c.ceremony_type.capitalize())
            print_label_value("Date:", c.date_str)
            print_label_value("City:", c.city)
            print_label_value("Venue:", c.venue)
            print_label_value("Budget:", format_fcfa(c.budget))
            print_label_value("Status:", c.status)
            print_label_value("Organizer:", c.organizer)
            print_label_value("Description:", c.description or "N/A")
            print_label_value("Guests:", str(c.guest_count))
            print_label_value("Expenses:", format_fcfa(c.total_expenses))
            print_label_value("Contributions:", format_fcfa(c.total_contributions))
            print_label_value("Balance:", format_fcfa(c.balance))
            print()
            print("  a. Edit details")
            print("  b. Change status")
            print("  c. View full report")
            print("  d. Add expense")
            print("  e. Record contribution")
            print("  f. Invite guests")
            print("  g. View guest list")
            print("  h. Delete ceremony")
            print("  0. Back")

            choice = input("\n  Choice: ").strip().lower()
            if choice == "a":
                self._edit_ceremony(c)
            elif choice == "b":
                self._change_ceremony_status(c)
            elif choice == "c":
                print("\n" + c.generate_report())
                pause()
            elif choice == "d":
                self._add_expense(c)
            elif choice == "e":
                self._record_contribution(c)
            elif choice == "f":
                self._invite_guests(c)
            elif choice == "g":
                self._view_guest_list(c)
            elif choice == "h":
                if prompt_confirm("Delete this ceremony?"):
                    ceremonies.remove(c)
                    # also remove related expenses, contributions, invitations
                    exp_ids = set(c.expense_ids)
                    cont_ids = set(c.contribution_ids)
                    inv_ids = set(c.invitation_ids)
                    expenses[:] = [e for e in expenses if e.expense_id not in exp_ids]
                    contributions[:] = [
                        co for co in contributions if co.contribution_id not in cont_ids
                    ]
                    invitations[:] = [
                        i for i in invitations if i.invitation_id not in inv_ids
                    ]
                    save_all()
                    _rebuild_relations()
                    print_success("Ceremony deleted.")
                    pause()
                    return
            elif choice == "0":
                return

    def _edit_ceremony(self, c: Ceremony) -> None:
        print_info("Leave blank to keep current value.\n")
        new_name = prompt_input("Name", c.name)
        new_date = prompt_input(f"Date ({DATE_FORMAT})", c.date_str)
        new_venue = prompt_input("Venue", c.venue)
        new_budget = prompt_input("Budget", str(c.budget))

        c.name = new_name
        if new_date:
            ok, _ = validate_date(new_date)
            if ok:
                c.date_str = new_date
        c.venue = new_venue
        try:
            c.budget = float(new_budget)
        except ValueError:
            pass
        save_all()
        print_success("Ceremony updated.")
        pause()

    def _change_ceremony_status(self, c: Ceremony) -> None:
        idx = select_from_list(CEREMONY_STATUSES, "New status")
        if idx is not None:
            c.status = CEREMONY_STATUSES[idx]
            save_all()
            print_success(f"Status changed to {c.status}.")
            pause()

    def _add_expense(self, c: Ceremony) -> None:
        print()
        cat_idx = select_from_list(EXPENSE_CATEGORIES, "Category")
        if cat_idx is None:
            return
        category = EXPENSE_CATEGORIES[cat_idx]
        desc = prompt_input("Description")
        amount_str = self._prompt_validated("Amount", validate_positive_float)
        if not amount_str:
            return
        paid = prompt_confirm("Already paid?", False)

        exp = Expense(
            ceremony_id=c.ceremony_id,
            category=category,
            description=desc,
            amount=float(amount_str),
            paid=paid,
        )
        expenses.append(exp)
        c.expense_ids.append(exp.expense_id)
        save_all()
        _rebuild_relations()
        print_success("Expense added.")
        pause()

    def _record_contribution(self, c: Ceremony) -> None:
        # select guest
        g_items = [g.full_name for g in guests]
        idx = select_from_list(g_items, "Contributing guest")
        if idx is None:
            return
        g = guests[idx]
        amount_str = self._prompt_validated("Amount", validate_positive_float)
        if not amount_str:
            return
        note = prompt_input("Note (optional)")

        cont = Contribution(
            ceremony_id=c.ceremony_id,
            guest_id=g.guest_id,
            amount=float(amount_str),
            note=note,
        )
        contributions.append(cont)
        c.contribution_ids.append(cont.contribution_id)
        save_all()
        _rebuild_relations()
        print_success(f"Contribution of {format_fcfa(cont.amount)} recorded.")
        pause()

    def _invite_guests(self, c: Ceremony) -> None:
        """Invite multiple guests at once."""
        # show guests not already invited
        invited_gids = set()
        for inv in find_invitations_for_ceremony(c.ceremony_id):
            invited_gids.add(inv.guest_id)
        available = [g for g in guests if g.guest_id not in invited_gids]
        if not available:
            print_info("All guests are already invited.")
            pause()
            return

        items = [f"{g.full_name} ({g.city})" for g in available]
        indices = select_multiple_from_list(items, "Select guests to invite")
        if not indices:
            print_info("No guests selected.")
            pause()
            return

        count = 0
        for i in indices:
            add_guest_to_ceremony(c.ceremony_id, available[i].guest_id)
            count += 1
        print_success(f"{count} guest(s) invited.")
        pause()

    def _view_guest_list(self, c: Ceremony) -> None:
        inv_list = find_invitations_for_ceremony(c.ceremony_id)
        if not inv_list:
            print_info("No guests invited yet.")
            pause()
            return
        print()
        for inv in inv_list:
            g = find_guest_by_id(inv.guest_id)
            if g:
                rsvp_color = {
                    "accepted": Theme.success,
                    "declined": Theme.error,
                    "tentative": Theme.warning,
                    "pending": Theme.muted,
                }.get(inv.rsvp, Theme.muted)
                name = g.full_name.ljust(25)
                rsvp = colored_text(f"[{inv.rsvp.upper()}]", rsvp_color)
                print(f"  {name} {rsvp}")
        print()
        stats = compute_rsvp_stats(inv_list)
        print(
            f"  Accepted: {stats['accepted']}  Declined: {stats['declined']}  "
            f"Tentative: {stats['tentative']}  Pending: {stats['pending']}"
        )
        pause()

    # ------------------------------------------------------------------
    # 3. Manage Guest Directory
    # ------------------------------------------------------------------

    def _manage_guests(self) -> None:
        while True:
            clear_screen()
            print(colored_text(draw_section_header("GUEST DIRECTORY"), Theme.primary))
            print()
            print("  1. Add guest")
            print("  2. Edit guest")
            print("  3. Delete guest")
            print("  4. Search guests")
            print("  5. List all guests")
            print("  0. Back")

            choice = input("\n  Choice: ").strip()
            if choice == "1":
                self._add_guest()
            elif choice == "2":
                self._edit_guest()
            elif choice == "3":
                self._delete_guest()
            elif choice == "4":
                self._search_guests()
            elif choice == "5":
                self._list_all_guests()
            elif choice == "0":
                return

    def _add_guest(self) -> None:
        print()
        first = self._prompt_validated("First name", validate_name)
        if not first:
            return
        last = self._prompt_validated("Last name", validate_name)
        if not last:
            return
        phone = prompt_input("Phone (optional)")
        if phone:
            ok, msg = validate_phone(phone)
            if not ok:
                print_error(msg)
                return
        email = prompt_input("Email (optional)")
        if email:
            ok, msg = validate_email(email)
            if not ok:
                print_error(msg)
                return
        city_idx = select_from_list(CITIES, "City")
        city = CITIES[city_idx] if city_idx is not None else ""
        neighborhood = prompt_input("Neighborhood (optional)")

        g = Guest(
            first_name=first,
            last_name=last,
            phone=phone,
            email=email,
            city=city,
            neighborhood=neighborhood,
        )
        guests.append(g)
        save_all()
        print_success(f"Guest '{g.full_name}' added.")
        pause()

    def _edit_guest(self) -> None:
        g = self._pick_guest()
        if not g:
            return
        print_info("Leave blank to keep current value.\n")
        first = prompt_input("First name", g.first_name)
        last = prompt_input("Last name", g.last_name)
        phone = prompt_input("Phone", g.phone)
        email = prompt_input("Email", g.email)
        city = prompt_input("City", g.city)
        hood = prompt_input("Neighborhood", g.neighborhood)

        g.first_name = first
        g.last_name = last
        g.phone = phone
        g.email = email
        g.city = city
        g.neighborhood = hood
        save_all()
        print_success("Guest updated.")
        pause()

    def _delete_guest(self) -> None:
        g = self._pick_guest()
        if not g:
            return
        if not prompt_confirm(f"Delete {g.full_name} and all their data?"):
            return
        remove_guest_completely(g.guest_id)
        print_success(f"Guest '{g.full_name}' deleted.")
        pause()

    def _search_guests(self) -> None:
        term = prompt_input("Search term").lower()
        if not term:
            return
        results = [
            g for g in guests if term in g.full_name.lower() or term in g.city.lower()
        ]
        if not results:
            print_info("No matches found.")
        else:
            for g in results:
                print(f"  {g.full_name} - {g.city} ({g.phone or 'no phone'})")
        pause()

    def _list_all_guests(self) -> None:
        if not guests:
            print_info("No guests in directory.")
            pause()
            return
        items = [f"{g.full_name} - {g.city}" for g in guests]
        display_paginated_list(items, "All Guests")
        pause()

    def _pick_guest(self) -> Optional[Guest]:
        if not guests:
            print_info("No guests available.")
            pause()
            return None
        items = [f"{g.full_name} ({g.city})" for g in guests]
        idx = select_from_list(items, "Select guest")
        if idx is None:
            return None
        return guests[idx]

    # ------------------------------------------------------------------
    # 4. Manage Invitations & RSVPs
    # ------------------------------------------------------------------

    def _manage_invitations(self) -> None:
        while True:
            clear_screen()
            print(
                colored_text(draw_section_header("INVITATIONS & RSVPS"), Theme.primary)
            )
            print()
            print("  1. View all invitations")
            print("  2. View by ceremony")
            print("  3. Send pending invitations")
            print("  4. Update RSVP manually")
            print("  5. Remove invitation")
            print("  0. Back")

            choice = input("\n  Choice: ").strip()
            if choice == "1":
                self._view_all_invitations()
            elif choice == "2":
                self._view_invitations_by_ceremony()
            elif choice == "3":
                self._send_pending()
            elif choice == "4":
                self._update_rsvp()
            elif choice == "5":
                self._remove_invitation()
            elif choice == "0":
                return

    def _view_all_invitations(self) -> None:
        if not invitations:
            print_info("No invitations.")
            pause()
            return
        headers = ["Guest", "Ceremony", "RSVP", "Sent"]
        rows = []
        for inv in invitations:
            g = find_guest_by_id(inv.guest_id)
            c = find_ceremony_by_id(inv.ceremony_id)
            gname = g.full_name[:15] if g else "?"
            cname = c.name[:20] if c else "?"
            rows.append([gname, cname, inv.rsvp, "Yes" if inv.sent else "No"])
        display_table(headers, rows)
        pause()

    def _view_invitations_by_ceremony(self) -> None:
        c = self._pick_ceremony()
        if not c:
            return
        inv_list = find_invitations_for_ceremony(c.ceremony_id)
        if not inv_list:
            print_info("No invitations for this ceremony.")
            pause()
            return
        for inv in inv_list:
            g = find_guest_by_id(inv.guest_id)
            name = g.full_name if g else "Unknown"
            print(
                f"  {name:25} [{inv.rsvp.upper()}]  "
                f"{'Sent' if inv.sent else 'Pending'}"
            )
        pause()

    def _send_pending(self) -> None:
        pending = [inv for inv in invitations if not inv.sent]
        if not pending:
            print_info("No pending invitations to send.")
            pause()
            return
        count = 0
        for inv in pending:
            g = find_guest_by_id(inv.guest_id)
            c = find_ceremony_by_id(inv.ceremony_id)
            if prompt_confirm(
                f"Send invitation to {g.full_name if g else '?'} "
                f"for {c.name if c else '?'}?"
            ):
                inv.sent = True
                inv.date_sent = date.today().strftime(DATE_FORMAT)
                count += 1
        save_all()
        print_success(f"{count} invitation(s) sent.")
        pause()

    def _update_rsvp(self) -> None:
        c = self._pick_ceremony()
        if not c:
            return
        inv_list = find_invitations_for_ceremony(c.ceremony_id)
        if not inv_list:
            print_info("No invitations for this ceremony.")
            pause()
            return
        items = []
        for inv in inv_list:
            g = find_guest_by_id(inv.guest_id)
            items.append(f"{g.full_name if g else '?'} [{inv.rsvp}]")
        idx = select_from_list(items, "Select invitation")
        if idx is None:
            return
        rsvp_idx = select_from_list(RSVP_OPTIONS, "New RSVP status")
        if rsvp_idx is None:
            return
        inv_list[idx].rsvp = RSVP_OPTIONS[rsvp_idx]
        save_all()
        _rebuild_relations()
        print_success("RSVP updated.")
        pause()

    def _remove_invitation(self) -> None:
        c = self._pick_ceremony()
        if not c:
            return
        inv_list = find_invitations_for_ceremony(c.ceremony_id)
        if not inv_list:
            print_info("No invitations for this ceremony.")
            pause()
            return
        items = []
        for inv in inv_list:
            g = find_guest_by_id(inv.guest_id)
            items.append(f"{g.full_name if g else '?'} [{inv.rsvp}]")
        idx = select_from_list(items, "Select invitation to remove")
        if idx is None:
            return
        if prompt_confirm("Remove this invitation?"):
            remove_invitation_completely(inv_list[idx].invitation_id)
            print_success("Invitation removed.")
        pause()

    # ------------------------------------------------------------------
    # 5. Financial Management
    # ------------------------------------------------------------------

    def _financial_management(self) -> None:
        while True:
            clear_screen()
            print(
                colored_text(draw_section_header("FINANCIAL MANAGEMENT"), Theme.primary)
            )
            print()
            print("  1. Overview dashboard")
            print("  2. Expenses by ceremony")
            print("  3. Contributions by ceremony")
            print("  4. Expense category summary")
            print("  5. Mark expense as paid")
            print("  6. Delete expense")
            print("  0. Back")

            choice = input("\n  Choice: ").strip()
            if choice == "1":
                self._financial_dashboard()
            elif choice == "2":
                self._expenses_by_ceremony()
            elif choice == "3":
                self._contributions_by_ceremony()
            elif choice == "4":
                self._expense_category_summary()
            elif choice == "5":
                self._mark_expense_paid()
            elif choice == "6":
                self._delete_expense()
            elif choice == "0":
                return

    def _financial_dashboard(self) -> None:
        total_budget = sum(c.budget for c in ceremonies)
        total_exp = sum(e.amount for e in expenses)
        total_cont = sum(co.amount for co in contributions)
        total_paid = sum(e.amount for e in expenses if e.paid)
        total_unpaid = total_exp - total_paid

        print()
        print_label_value("Total Budget:", format_fcfa(total_budget))
        print_label_value("Total Expenses:", format_fcfa(total_exp))
        print_label_value("Total Contributions:", format_fcfa(total_cont))
        print_label_value("Overall Balance:", format_fcfa(total_cont - total_exp))
        print_label_value("Paid:", format_fcfa(total_paid))
        print_label_value("Unpaid:", format_fcfa(total_unpaid))
        print()
        print_label_value("Ceremonies:", str(len(ceremonies)))
        print_label_value("Guests:", str(len(guests)))
        pause()

    def _expenses_by_ceremony(self) -> None:
        c = self._pick_ceremony()
        if not c:
            return
        exp_list = find_expenses_for_ceremony(c.ceremony_id)
        if not exp_list:
            print_info("No expenses recorded.")
            pause()
            return
        headers = ["Category", "Description", "Amount", "Paid"]
        rows = []
        for e in exp_list:
            rows.append(
                [
                    e.category,
                    e.description[:18],
                    format_fcfa(e.amount),
                    "Yes" if e.paid else "No",
                ]
            )
        print(f"\n  Expenses for: {c.name}")
        display_table(headers, rows)
        pause()

    def _contributions_by_ceremony(self) -> None:
        c = self._pick_ceremony()
        if not c:
            return
        cont_list = find_contributions_for_ceremony(c.ceremony_id)
        if not cont_list:
            print_info("No contributions recorded.")
            pause()
            return
        headers = ["Guest", "Amount", "Date", "Note"]
        rows = []
        for co in cont_list:
            g = find_guest_by_id(co.guest_id)
            gname = g.full_name[:15] if g else "?"
            rows.append(
                [gname, format_fcfa(co.amount), co.date_contributed, co.note[:15]]
            )
        print(f"\n  Contributions for: {c.name}")
        display_table(headers, rows)
        pause()

    def _expense_category_summary(self) -> None:
        cat_totals: dict[str, float] = {}
        for e in expenses:
            cat_totals[e.category] = cat_totals.get(e.category, 0.0) + e.amount
        if not cat_totals:
            print_info("No expenses to summarize.")
            pause()
            return
        headers = ["Category", "Total"]
        rows = [[cat, format_fcfa(amt)] for cat, amt in sorted(cat_totals.items())]
        display_table(headers, rows)
        pause()

    def _mark_expense_paid(self) -> None:
        c = self._pick_ceremony()
        if not c:
            return
        exp_list = find_expenses_for_ceremony(c.ceremony_id)
        unpaid = [e for e in exp_list if not e.paid]
        if not unpaid:
            print_info("All expenses are already paid.")
            pause()
            return
        items = [f"{e.description} - {format_fcfa(e.amount)}" for e in unpaid]
        idx = select_from_list(items, "Mark as paid")
        if idx is not None:
            unpaid[idx].paid = True
            save_all()
            print_success("Expense marked as paid.")
            pause()

    def _delete_expense(self) -> None:
        c = self._pick_ceremony()
        if not c:
            return
        exp_list = find_expenses_for_ceremony(c.ceremony_id)
        if not exp_list:
            print_info("No expenses to delete.")
            pause()
            return
        items = [f"{e.description} - {format_fcfa(e.amount)}" for e in exp_list]
        idx = select_from_list(items, "Delete expense")
        if idx is None:
            return
        if prompt_confirm("Delete this expense?"):
            remove_expense_completely(exp_list[idx].expense_id)
            print_success("Expense deleted.")
        pause()

    # ------------------------------------------------------------------
    # 6. View Reports
    # ------------------------------------------------------------------

    def _view_reports(self) -> None:
        while True:
            clear_screen()
            print(colored_text(draw_section_header("REPORTS"), Theme.primary))
            print()
            print("  1. Ceremony summary")
            print("  2. Financial overview")
            print("  3. Guest attendance")
            print("  4. Budget status")
            print("  0. Back")

            choice = input("\n  Choice: ").strip()
            if choice == "1":
                self._report_ceremony_summary()
            elif choice == "2":
                self._report_financial()
            elif choice == "3":
                self._report_attendance()
            elif choice == "4":
                self._report_budget()
            elif choice == "0":
                return

    def _report_ceremony_summary(self) -> None:
        if not ceremonies:
            print_info("No ceremonies.")
            pause()
            return
        headers = ["Name", "Type", "Date", "Status", "Guests"]
        rows = []
        for c in ceremonies:
            rows.append(
                [
                    c.name[:20],
                    c.ceremony_type[:10],
                    c.date_str,
                    c.status[:10],
                    str(c.guest_count),
                ]
            )
        display_table(headers, rows)
        pause()

    def _report_financial(self) -> None:
        if not ceremonies:
            print_info("No data.")
            pause()
            return
        headers = ["Ceremony", "Budget", "Expenses", "Contribs", "Balance"]
        rows = []
        for c in ceremonies:
            rows.append(
                [
                    c.name[:16],
                    format_fcfa(c.budget),
                    format_fcfa(c.total_expenses),
                    format_fcfa(c.total_contributions),
                    format_fcfa(c.balance),
                ]
            )
        display_table(headers, rows)
        pause()

    def _report_attendance(self) -> None:
        if not ceremonies:
            print_info("No data.")
            pause()
            return
        for c in ceremonies:
            stats = compute_rsvp_stats(c._loaded_invitations)
            print(f"\n  {c.name}")
            print(
                f"    Accepted: {stats['accepted']}  "
                f"Declined: {stats['declined']}  "
                f"Tentative: {stats['tentative']}  "
                f"Pending: {stats['pending']}"
            )
        pause()

    def _report_budget(self) -> None:
        if not ceremonies:
            print_info("No data.")
            pause()
            return
        for c in ceremonies:
            bar = compute_budget_status(c)
            print(f"\n  {c.name}")
            print(
                f"    Budget: {format_fcfa(c.budget)}  "
                f"Spent: {format_fcfa(c.total_expenses)}  "
                f"Remaining: {format_fcfa(c.budget_remaining)}"
            )
            print(f"    {bar}")
        pause()

    # ------------------------------------------------------------------
    # 7. Search
    # ------------------------------------------------------------------

    def _search_ceremonies(self) -> None:
        term = prompt_input("Search term").lower()
        if not term:
            return
        results = [
            c
            for c in ceremonies
            if term in c.name.lower()
            or term in c.city.lower()
            or term in c.ceremony_type.lower()
            or term in c.organizer.lower()
        ]
        if not results:
            print_info("No matches.")
        else:
            for c in results:
                d = days_until(c.date_str)
                when = (
                    f"in {d} days" if d > 0 else f"{-d} days ago" if d < 0 else "today"
                )
                print(f"  {c.name} ({c.ceremony_type}) - {c.date_str} ({when})")
        pause()

    # ------------------------------------------------------------------
    # 8. Upcoming
    # ------------------------------------------------------------------

    def _upcoming_ceremonies(self) -> None:
        upcoming = sorted(
            [c for c in ceremonies if days_until(c.date_str) >= 0],
            key=lambda x: x.date_str,
        )
        if not upcoming:
            print_info("No upcoming ceremonies.")
            pause()
            return
        for c in upcoming:
            d = days_until(c.date_str)
            print(f"  {c.name} - {c.date_str} (in {d} days) [{c.status}]")
        pause()

    # ------------------------------------------------------------------
    # 9. Budget Alerts
    # ------------------------------------------------------------------

    def _budget_alerts(self) -> None:
        alerts = []
        for c in ceremonies:
            pct = c.budget_usage_percent
            if pct > 90:
                alerts.append((c, "CRITICAL", Theme.error))
            elif pct > 70:
                alerts.append((c, "WARNING", Theme.warning))
        if not alerts:
            print_success("No budget alerts. All ceremonies within budget.")
            pause()
            return
        for c, level, color in alerts:
            print(
                colored_text(
                    f"  [{level}] {c.name}: "
                    f"{format_percentage(c.budget_usage_percent)} "
                    f"spent, {format_fcfa(c.budget_remaining)} remaining",
                    color,
                )
            )
        pause()

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------

    def _logout(self) -> None:
        print_info("Logging out...")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _pick_ceremony(self) -> Optional[Ceremony]:
        if not ceremonies:
            print_info("No ceremonies available.")
            pause()
            return None
        items = [f"{c.name} ({c.date_str})" for c in ceremonies]
        idx = select_from_list(items, "Select ceremony")
        if idx is None:
            return None
        return ceremonies[idx]

    def _prompt_validated(
        self, label: str, validator: Callable[[str], Tuple[bool, str]]
    ) -> str:
        """Prompt with validation. Returns empty on failure after retries."""
        for _ in range(3):
            raw = prompt_input(label)
            if not raw:
                return ""
            ok, msg = validator(raw)
            if ok:
                return raw
            print_error(msg)
        print_error("Too many attempts.")
        return ""
