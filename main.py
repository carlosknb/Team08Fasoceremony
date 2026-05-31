"""
FasoCeremonies - Ceremony management system for Burkina Faso.

Main entry point with banner and navigation.
"""

# Grab our visual settings, helper tools, and the two main portals
from config import Box, Theme, TERMINAL_WIDTH, VERSION
from services import (
    clear_screen,
    colored_text,
    load_all,
    pause,
    print_error,
    print_info,
    seed_database,
)
from organizer import OrganizerPortal
from guest import GuestPortal


def display_banner() -> None:
    clear_screen()
    w = TERMINAL_WIDTH
    inner = w - 2  # leave room for the left and right borders
    
    # Build the box line by line.
    # The ^{inner} trick automatically centers the text in the available space.
    lines = [
        f"{Box.tl}{Box.h * inner}{Box.tr}",
        f"{Box.v}{'FasoCeremonies':^{inner}}{Box.v}",
        f"{Box.v}{'Ceremony Management System':^{inner}}{Box.v}",
        f"{Box.v}{'Burkina Faso':^{inner}}{Box.v}",
        f"{Box.lj}{Box.h * inner}{Box.rj}",
        f"{Box.v}{'v' + VERSION:^{inner}}{Box.v}",
        f"{Box.bl}{Box.h * inner}{Box.br}",
    ]
    
    # Print it all out in the app's primary color
    for line in lines:
        print(colored_text(line, Theme.primary))


def display_main_menu() -> None:
    print()
    print("  1. Organizer Portal")
    print("  2. Guest Portal")
    print("  0. Exit")
    print()


def main() -> None:
    # Load up our data and put some starting examples into the database
    load_all()
    seed_database()

    # Keep the app running until the user chooses to leave
    while True:
        display_banner()
        display_main_menu()
        choice = input("  Choice: ").strip()

        if choice == "1":
            oportal = OrganizerPortal()
            oportal.run()
        elif choice == "2":
            gportal = GuestPortal()
            gportal.run()
        elif choice == "0":
            print_info("Goodbye!")
            break  # exits the while loop and ends the program
        else:
            print_error("Invalid choice.")
            pause()  # give them time to read the error before the screen clears


# This makes sure the app only runs if we launch this file directly,
# not if it gets imported by another script.
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # If the user presses Ctrl+C, exit nicely instead of throwing an ugly error
        print()
        print_info("Interrupted. Goodbye!")
