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
