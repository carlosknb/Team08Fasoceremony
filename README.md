# FasoCeremonies v2.0.0

**Ceremony Management System — Burkina Faso**

A professional command-line application for planning and managing ceremonies in Burkina Faso, featuring a dual-portal architecture for organizers and guests.

---

## Features

### Organizer Portal
- **Create Ceremonies** — Marriage, Funeral, Baptism, Seminar with type-specific fields
- **Guest Directory** — Add, edit, search, and delete guests
- **Invitations & RSVPs** — Invite guests, track responses, send reminders
- **Financial Management** — Budget tracking, expenses, contributions, category reports
- **Reports** — Ceremony summaries, financial overviews, attendance stats, budget status
- **Search & Alerts** — Find ceremonies by name/type/location, budget warnings

### Guest Portal
- **View Invitations** — See all ceremonies you are invited to
- **RSVP** — Accept, decline, or mark as tentative
- **View Details** — See full ceremony information including location and schedule
- **Contribute** — Make financial contributions to ceremonies
- **Upcoming Events** — Personal calendar of accepted events
- **Edit Profile** — Update your contact information

### Architecture
- **OOP Inheritance** — `Ceremony` parent class with 4 specialized subclasses
- **Polymorphism** — `calculate_cost()` and `generate_report()` overridden per type
- **Encapsulation** — Private attributes with property accessors
- **TXT Persistence** — All data stored in pipe-delimited text files
- **Professional Terminal UI** — ANSI colors, Unicode box-drawing, structured layouts

---

## Ceremony Types

| Type | Specific Fields |
|------|----------------|
| Marriage | Bride/Groom names, Dot amount, Marriage stage, Families |
| Funeral | Deceased name/age, Village of origin, Funeral type, Duration |
| Baptism | Child name/age, Godfather/Godmother, Church, Priest |
| Seminar | Topic, Speakers, Attendees, Venue type, Meals |

---

## Installation

```bash
# No external dependencies required — uses Python standard library only
cd FasoCeremonies
python main.py
```

---

## Data Storage

All data is stored in the `data/` directory as plain text files:

| File | Contents |
|------|----------|
| `ceremonies.txt` | Ceremony records (pipe-delimited) |
| `guests.txt` | Guest records (pipe-delimited) |
| `invitations.txt` | Invitations, Expenses, Contributions (section-based) |

### TXT Format Example

```
# FasoCeremonies - Ceremonies Data
CER-A1B2C3D4|marriage|Kouda Wedding|2025-12-15|Ouagadougou|500000|Amadou Kouda|...|planning|...

# FasoCeremonies - Guests Data
GST-E5F6G7H8|Fatou|Ouedraogo|+226 70 00 00|fatou@email.com|Ouagadougou|VIP guest

[INVITATIONS]
INV-XXXX|CER-A1B2C3D4|GST-E5F6G7H8|bride|pending|0|0|0|Welcome!

[EXPENSES]
EXP-YYYY|CER-A1B2C3D4|catering|Food service|150000|0|2025-06-01

[CONTRIBUTIONS]
CON-ZZZZ|CER-A1B2C3D4|GST-E5F6G7H8|25000|Best wishes|2025-06-05
```

---

## Usage

1. Run `python main.py`
2. Choose **Organizer Portal** to manage ceremonies or **Guest Portal** to view invitations
3. All data is automatically saved to TXT files after each operation

---

## Project Structure

```
FasoCeremonies/
  main.py          — Entry point and main menu
  config.py        — Constants, UI theme, application settings
  models.py        — Data models (Ceremony hierarchy, Guest, Invitation, etc.)
  services.py      — TXT persistence, validation, UI utilities
  organizer.py     — Organizer portal (full management)
  guest.py         — Guest portal (view, RSVP, contribute)
  data/            — TXT data files (auto-created)
  README.md        — This file
  .gitignore       — Git ignore rules
  requirements.txt — Python dependencies (stdlib only)
```

---

## License

MIT License — Free for personal and commercial use.
