# FasoCeremonies

**Ceremony Management System for Burkina Faso**

FasoCeremonies is a command-line application designed to manage the full lifecycle of traditional and modern ceremonies in Burkina Faso. It supports marriages, funerals, baptisms, and seminars — allowing organizers to plan events, track guests and RSVPs, manage budgets, record expenses and financial contributions, and generate detailed reports. Guests also have their own self-service portal where they can view invitations, respond to RSVPs, make contributions, and see other contributors.

The system is built entirely with Python and its standard library, storing all data in pipe-delimited text files under a `data/` directory. On first launch, the application automatically seeds itself with realistic Burkinabe sample data including guests, ceremonies, invitations, expenses, and contributions — so it is immediately usable out of the box.

---

## Table of Contents

- [How to Run the Project](#how-to-run-the-project)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [OOP Structure](#oop-structure)
- [Team](#team)
- [Acknowledgements](#acknowledgements)

---

## How to Run the Project

### Prerequisites

- **Python 3.8 or higher** — the project uses f-strings, `dataclass`-style constructors, and type annotations that require Python 3.8+.
- **No external packages are needed** — FasoCeremonies uses only the Python standard library (`os`, `re`, `uuid`, `datetime`, `typing`).

### Step-by-Step Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/carlosknb/FasoCeremonies.git
   cd FasoCeremonies
   ```

2. **Run the application**

   ```bash
   python main.py
   ```

3. **Navigate the main menu**

   On launch, the application displays a banner and a menu with two portals:

   ```
   1. Organizer Portal
   2. Guest Portal
   0. Exit
   ```

   - Select **1** to enter the Organizer Portal (full management capabilities).
   - Select **2** to enter the Guest Portal (view invitations, RSVP, contribute).
   - Select **0** to quit.

4. **First run note**: If no data files exist in the `data/` directory, the application automatically generates seed data with 16 guests, 6 ceremonies (2 marriages, 1 funeral, 1 baptism, 1 seminar, and 1 additional marriage), along with sample invitations, expenses, and contributions.

### Data Storage

All data is persisted in the `data/` directory using plain text files:

| File | Purpose |
|---|---|
| `data/ceremonies.txt` | One ceremony per line, fields separated by `|` |
| `data/guests.txt` | One guest per line, fields separated by `|` |
| `data/invitations.txt` | Three sections (`[INVITATIONS]`, `[EXPENSES]`, `[CONTRIBUTIONS]`), each line pipe-delimited |

---

## Features

### Organizer Portal

The Organizer Portal provides full ceremony lifecycle management with the following capabilities:

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Create Ceremony** | Create a new ceremony by selecting its type (marriage, funeral, baptism, seminar), entering the name, date, city, venue, budget, organizer, and an optional description. The system automatically instantiates the correct subclass. |
| 2 | **Manage Ceremonies** | Select any existing ceremony to view its full details, edit fields, change status (planned / ongoing / completed / cancelled), generate a type-specific report, add expenses, record contributions, invite guests, view the guest list with RSVP summary, or delete the ceremony and all its associated data. |
| 3 | **Manage Guest Directory** | Add, edit, delete, search, and list all guests. Deleting a guest also removes all their invitations and contributions. Name validation supports accented characters, apostrophes, and hyphens common in Burkinabe names (e.g. N'gourma, Ouedraogo). |
| 4 | **Manage Invitations & RSVPs** | View all invitations in a tabular format, filter by ceremony, send pending invitations (marks them as sent with a date), manually update RSVP statuses, and remove invitations. |
| 5 | **Financial Management** | Dashboard showing total budget, expenses, contributions, balance, paid/unpaid breakdown. View expenses and contributions per ceremony. Expense category summary across all ceremonies. Mark expenses as paid. Delete expenses. |
| 6 | **View Reports** | Ceremony summary table, financial overview table, guest attendance breakdown by RSVP status per ceremony, and budget status with visual progress bars and alert levels (OK / WARNING / CRITICAL). |
| 7 | **Search Ceremonies** | Search across ceremony name, city, type, and organizer with a single keyword. |
| 8 | **Upcoming Ceremonies** | List all ceremonies whose date is today or in the future, sorted chronologically, showing days remaining. |
| 9 | **Budget Alerts** | Automatically flags ceremonies that have exceeded 70% (WARNING) or 90% (CRITICAL) of their budget. |

### Guest Portal

The Guest Portal is a self-service interface where guests can interact with the system without organizer privileges:

| # | Feature | Description |
|---|---------|-------------|
| 1 | **View My Invitations** | Displays all invitations for the logged-in guest with ceremony name, type, date, city, venue, and color-coded RSVP status. |
| 2 | **Respond to Invitation** | Allows the guest to change their RSVP on pending or tentative invitations to any of the four statuses (pending, accepted, declined, tentative). |
| 3 | **View Ceremony Details** | Shows full details of a ceremony the guest is invited to: name, type, date, city, venue, organizer, description, status, and guest count. |
| 4 | **Make a Contribution** | Contribute money to a ceremony the guest has accepted the invitation for. The amount is validated and recorded with an optional note. |
| 5 | **Contribution History** | Lists all past contributions by the guest, including ceremony name, amount, date, and note, with a running total. |
| 6 | **Upcoming Events** | Shows all future ceremonies the guest is invited to, sorted by date, with days remaining. |
| 7 | **Edit My Profile** | Update first name, last name, phone, and email with validation. Leave fields blank to keep existing values. |
| 8 | **View Other Contributors** | See who else has contributed to a ceremony the guest is invited to, with amounts shown (the guest's own contributions are marked). |

---

## Technologies Used

| Technology | Version | Purpose |
|---|---------|---------|
| Python | 3.8+ | Primary programming language |
| `os` | stdlib | File system operations, screen clearing |
| `re` | stdlib | Regular expressions for name, phone, and email validation |
| `uuid` | stdlib | Unique ID generation for all entities |
| `datetime` | stdlib | Date parsing, formatting, and day calculations |
| `typing` | stdlib | Type annotations (`List`, `Dict`, `Optional`, `Tuple`, `Callable`) |

No external libraries or third-party packages are required. The entire application runs on the Python standard library alone.

---

## Project Structure

```
FasoCeremonies/
├── main.py              # Entry point: displays banner, main menu, launches portals
├── config.py            # Application constants, ANSI colors, box-drawing characters,
│                        #   validation regex patterns, ceremony types, cities, etc.
├── models.py            # Data model classes: Guest, Expense, Contribution,
│                        #   Invitation, Ceremony (base), and subclasses
│                        #   (MarriageCeremony, FuneralCeremony, BaptismCeremony,
│                        #   SeminarCeremony). Handles serialization/deserialization.
├── services.py          # Persistence layer (load/save to text files), validation
│                        #   functions, terminal UI helpers (colors, boxes, tables,
│                        #   pagination, prompts), lookup helpers, and seed data.
├── organizer.py         # OrganizerPortal class: full ceremony, guest, invitation,
│                        #   and financial management interface for organizers.
├── guest.py             # GuestPortal class: self-service portal for guests to
│                        #   view invitations, RSVP, contribute, and manage profile.
├── requirements.txt     # Empty — no external dependencies required.
├── .gitignore           # Standard Python gitignore rules.
└── data/                # Auto-created data directory.
    ├── ceremonies.txt   # Pipe-delimited ceremony records.
    ├── guests.txt       # Pipe-delimited guest records.
    └── invitations.txt  # Three-section file: invitations, expenses, contributions.
```

### File Descriptions

- **`main.py`** — The application entry point. On startup, it loads all data from disk and seeds the database if empty. It then presents a banner and main menu loop that routes the user to either the Organizer Portal or the Guest Portal. Handles `KeyboardInterrupt` gracefully.

- **`config.py`** — Central configuration hub. Defines application metadata (name, version, currency), file paths, delimiters (`|` for fields, `;` for arrays), date format, ceremony types and statuses, RSVP options, expense categories, Burkina Faso cities and neighborhoods, validation regex patterns, and UI theming (ANSI `Colors`, `Theme`, and `Box` drawing characters).

- **`models.py`** — Contains all data model classes with full serialization support. Each model has `to_text_line()` and `from_text_line()` class methods for pipe-delimited text file persistence. The `Ceremony` base class defines polymorphic methods `calculate_cost()` and `generate_report()` that are overridden by each subclass. A `CEREMONY_CLASS_MAP` dictionary maps type strings to their corresponding classes for correct deserialization.

- **`services.py`** — The service and persistence layer. Manages global data stores, file I/O (`load_all()`, `save_all()`), all validation functions (name, email, phone, date, positive numbers), terminal UI utilities (colored output, box drawing, tables, pagination, prompts), formatting helpers (FCFA currency, percentages, days until), lookup helpers (find by ID, find related entities), cascade deletion functions, and the comprehensive seed data generator.

- **`organizer.py`** — The `OrganizerPortal` class implementing the organizer-facing menu system. Provides 9 top-level actions covering ceremony CRUD, guest directory management, invitation and RSVP management, financial dashboards and expense tracking, reports, search, upcoming events, and budget alerts.

- **`guest.py`** — The `GuestPortal` class implementing the guest-facing menu system. Guests identify themselves from a list, then can view and respond to invitations, view ceremony details, make contributions, see their contribution history, check upcoming events, edit their profile, and view other contributors for ceremonies they are invited to.

---

## OOP Structure

The project demonstrates all four Object-Oriented Programming principles: Encapsulation, Abstraction, Inheritance, and Polymorphism.

### Class Hierarchy

```
Ceremony (base class)
├── MarriageCeremony
├── FuneralCeremony
├── BaptismCeremony
└── SeminarCeremony

Guest
Expense
Contribution
Invitation
OrganizerPortal
GuestPortal
```

### Class Details

| Class | File | Parent | Key Attributes | Key Methods | OOP Principle |
|-------|------|--------|----------------|-------------|---------------|
| **Ceremony** | `models.py` | — | `ceremony_id`, `name`, `date_str`, `city`, `venue`, `budget`, `status`, `organizer`, `description`, `expense_ids`, `contribution_ids`, `invitation_ids` | `calculate_cost()`, `generate_report()`, `load_relations()`, `to_text_line()`, `from_text_line()`, properties: `total_expenses`, `total_contributions`, `balance`, `budget_remaining`, `budget_usage_percent`, `guest_count`, `accepted_count`, `declined_count`, `pending_count` | **Encapsulation** — manages its own data, caches loaded relations privately (`_loaded_expenses`, `_loaded_contributions`, `_loaded_invitations`), exposes computed values via properties. **Abstraction** — hides internal relation loading and computation behind clean property interfaces. |
| **MarriageCeremony** | `models.py` | `Ceremony` | *(inherits all from Ceremony)* | `calculate_cost()` — overrides base: `budget * 0.9 + guest_count * 5000`. `generate_report()` — adds marriage-specific cost estimate and type note. | **Inheritance** — extends Ceremony. **Polymorphism** — same method names, different behavior. |
| **FuneralCeremony** | `models.py` | `Ceremony` | *(inherits all from Ceremony)* | `calculate_cost()` — overrides base: `budget * 0.7 + guest_count * 3000`. `generate_report()` — adds funeral-specific cost estimate and type note. | **Inheritance** — extends Ceremony. **Polymorphism** — same method names, different behavior. |
| **BaptismCeremony** | `models.py` | `Ceremony` | *(inherits all from Ceremony)* | `calculate_cost()` — overrides base: `budget * 0.5 + guest_count * 4000`. `generate_report()` — adds baptism-specific cost estimate and type note. | **Inheritance** — extends Ceremony. **Polymorphism** — same method names, different behavior. |
| **SeminarCeremony** | `models.py` | `Ceremony` | *(inherits all from Ceremony)* | `calculate_cost()` — overrides base: `budget * 0.6 + guest_count * 2000`. `generate_report()` — adds seminar-specific cost estimate and type note. | **Inheritance** — extends Ceremony. **Polymorphism** — same method names, different behavior. |
| **Guest** | `models.py` | — | `guest_id`, `first_name`, `last_name`, `phone`, `email`, `city`, `neighborhood` | `full_name` (property), `to_text_line()`, `from_text_line()` | **Encapsulation** — manages its own data and serialization. |
| **Expense** | `models.py` | — | `expense_id`, `ceremony_id`, `category`, `description`, `amount`, `paid`, `date_incurred` | `to_text_line()`, `from_text_line()` | **Encapsulation** — self-contained record with serialization. |
| **Contribution** | `models.py` | — | `contribution_id`, `ceremony_id`, `guest_id`, `amount`, `date_contributed`, `note` | `to_text_line()`, `from_text_line()` | **Encapsulation** — self-contained record with serialization. |
| **Invitation** | `models.py` | — | `invitation_id`, `ceremony_id`, `guest_id`, `rsvp`, `sent`, `date_sent` | `to_text_line()`, `from_text_line()` | **Encapsulation** — self-contained record with serialization. |
| **OrganizerPortal** | `organizer.py` | — | *(no instance state beyond method local vars)* | `run()`, `_create_ceremony()`, `_manage_ceremonies()`, `_manage_guests()`, `_manage_invitations()`, `_financial_management()`, `_view_reports()`, `_search_ceremonies()`, `_upcoming_ceremonies()`, `_budget_alerts()` | **Abstraction** — hides complex ceremony/guest/financial management behind a simple menu-driven interface. |
| **GuestPortal** | `guest.py` | — | `current_guest` | `run()`, `_view_invitations()`, `_respond_invitation()`, `_view_ceremony_details()`, `_make_contribution()`, `_contribution_history()`, `_upcoming_events()`, `_edit_profile()`, `_view_other_contributors()` | **Abstraction** — presents a simplified self-service interface. **Encapsulation** — encapsulates the current guest session state. |

### OOP Principles Demonstrated

- **Encapsulation**: Each class manages its own data through well-defined attributes and methods. The `Ceremony` class caches loaded relations in private attributes (`_loaded_expenses`, `_loaded_contributions`, `_loaded_invitations`) and exposes computed values through read-only properties (`total_expenses`, `balance`, `budget_usage_percent`, etc.). Guest, Expense, Contribution, and Invitation each encapsulate their own serialization logic.

- **Abstraction**: Internal complexity is hidden behind clean interfaces. For example, `services.py` provides high-level functions like `save_all()`, `load_all()`, and `seed_database()` that hide the details of multi-file I/O and section parsing. The portal classes present simple numbered menus that hide complex data manipulation behind single actions.

- **Inheritance**: `MarriageCeremony`, `FuneralCeremony`, `BaptismCeremony`, and `SeminarCeremony` all extend the `Ceremony` base class, inheriting all its attributes, properties, and methods while adding ceremony-type-specific behavior.

- **Polymorphism**: The `calculate_cost()` and `generate_report()` methods are defined in the `Ceremony` base class and overridden in each subclass with type-specific logic (different cost formulas and report annotations). The `CEREMONY_CLASS_MAP` enables runtime polymorphic deserialization — when reading from file, the correct subclass is instantiated based on the ceremony type string, and calling `calculate_cost()` or `generate_report()` automatically dispatches to the appropriate overridden implementation.

---

## Team

| Role | Name | GitHub Profile | Contribution |
|------|------|----------------|--------------|
| Lecturer | Kweyakie Afi Blebo | — | — |
| Group Member | KONOMBO Pendg-wende Stephane Carlos | [carlosknb](https://github.com/carlosknb) | `main.py` — application entry point, banner, and navigation |
| Group Member | KOURAOGO Oceane Rihanata Nebnonma | [oceane2006-g](https://github.com/oceane2006-g) | `config.py` — configuration, constants, and UI theming |
| Group Member | KYELEM Shekina Orelie | [KYEL-cmyk](https://github.com/KYEL-cmyk) | `organizer.py` — Organizer Portal with full management features |
| Group Member | KPIELLE Some Kadidia Augustine | [Kadidia-debug](https://github.com/Kadidia-debug) | `README.md` — documentation |
| Group Member | KONDOMBO Wendtoin Doriane Arlenne | [Doriane2007](https://github.com/Doriane2007) | `services.py` — persistence, validation, UI utilities, and seed data |
| Group Member | MILLOGO Dorcax Albertine | [Dorcx](https://github.com/Dorcx) | `guest.py` and `models.py` — Guest Portal and data model classes |

---

## Acknowledgements

- **Course**: Programming I with Python (3PRG1205) — Burkina Institute of Technology
- **Lecturer**: Kweyakie Afi Blebo (blebo.kweyakie@bit.bf)
- **Python Documentation**: [docs.python.org](https://docs.python.org/3/) — referred to for standard library modules (`os`, `re`, `uuid`, `datetime`, `typing`), string formatting with f-strings, and OOP patterns.
- **PEP 8 Style Guide**: [peps.python.org/pep-0008](https://peps.python.org/pep-0008/) — followed for naming conventions, indentation, and code organization throughout the project.
