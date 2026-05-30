"""
FasoCeremonies - Data Models Module

Defines the complete OOP hierarchy for ceremony management.

Classes:
    Ceremony : Abstract parent class for all ceremony types
    MarriageCeremony : Marriage-specific ceremony (dot, stages, families)
    FuneralCeremony : Funeral-specific ceremony (deceased, mourning, days)
    BaptismCeremony : Baptism-specific ceremony (godparents, church)
    SeminarCeremony : Seminar/conference (speakers, topics, venue)
    Guest : Guest entity with contact info and RSVP tracking
    Invitation : Links a Guest to a Ceremony with RSVP status
    Expense : Financial expense record for a ceremony
    Contribution : Financial contribution from a guest to a ceremony
"""

from __future__ import annotations
import uuid
from datetime import datetime, date
from typing import List, Dict, Optional

from config import (
    CURRENCY, CEREMONY_ID_PREFIX, GUEST_ID_PREFIX,
    CEREMONY_TYPES, CEREMONY_STATUSES, RSVP_STATUSES,
    EXPENSE_CATEGORIES, MARRIAGE_STAGES, FUNERAL_TYPES,
    INVITATION_SIDES, FIELD_SEP, ARRAY_SEP,
)


def _generate_id(prefix: str) -> str:
    short = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-{short}"


# EXPENSE MODEL

class Expense:
    """Represents a single expense record for a ceremony.

    Attributes:
        expense_id : Unique identifier
        ceremony_id : ID of the parent ceremony
        category : Expense category (e.g. 'catering', 'venue')
        description : Human-readable description
        amount : Amount in FCFA
        paid : Whether the expense has been paid
        date_recorded : Date when the expense was recorded
    """

    def __init__(
        self,
        ceremony_id: str,
        category: str,
        description: str,
        amount: float,
        paid: bool = False,
        expense_id: Optional[str] = None,
        date_recorded: Optional[str] = None,
    ) -> None:
        self.expense_id: str = expense_id or _generate_id("EXP")
        self.ceremony_id: str = ceremony_id
        self.category: str = category
        self.description: str = description
        self.amount: float = amount
        self.paid: bool = paid
        self.date_recorded: str = date_recorded or date.today().isoformat()

    def mark_paid(self) -> None:
        """Mark this expense as paid."""
        self.paid = True

    def to_text_line(self) -> str:
        """Serialize expense fields to a single FIELD_SEP-delimited TXT line."""
        parts = [
            self.expense_id,
            self.ceremony_id,
            self.category,
            self.description,
            str(self.amount),
            "1" if self.paid else "0",
            self.date_recorded,
        ]
        return FIELD_SEP.join(parts)

    @classmethod
    def from_text_line(cls, line: str) -> "Expense":
        """Rebuild an Expense object from a serialized TXT line."""
        parts = line.strip().split(FIELD_SEP)
        return cls(
            expense_id=parts[0],
            ceremony_id=parts[1],
            category=parts[2],
            description=parts[3],
            amount=float(parts[4]),
            paid=parts[5] == "1",
            date_recorded=parts[6],
        )

# CONTRIBUTION MODEL

class Contribution:
    """Represents a financial contribution from a guest to a ceremony.

    Attributes:
        contribution_id : Unique identifier
        ceremony_id : ID of the ceremony
        guest_id : ID of the contributing guest
        amount : Amount in FCFA
        message : Optional message from the contributor
        date_contributed : Date of contribution
    """

    def __init__(
        self,
        ceremony_id: str,
        guest_id: str,
        amount: float,
        message: str = "",
        contribution_id: Optional[str] = None,
        date_contributed: Optional[str] = None,
    ) -> None:
        self.contribution_id: str = contribution_id or _generate_id("CON")
        self.ceremony_id: str = ceremony_id
        self.guest_id: str = guest_id
        self.amount: float = amount
        self.message: str = message
        self.date_contributed: str = date_contributed or date.today().isoformat()

    def to_text_line(self) -> str:
        """Serialize contribution fields to a single FIELD_SEP-delimited TXT line."""
        parts = [
            self.contribution_id,
            self.ceremony_id,
            self.guest_id,
            str(self.amount),
            self.message,
            self.date_contributed,
        ]
        return FIELD_SEP.join(parts)

    @classmethod
    def from_text_line(cls, line: str) -> "Contribution":
        """Rebuild a Contribution object from a serialized TXT line."""
        parts = line.strip().split(FIELD_SEP)
        return cls(
            contribution_id=parts[0],
            ceremony_id=parts[1],
            guest_id=parts[2],
            amount=float(parts[3]),
            message=parts[4] if len(parts) > 4 else "",
            date_contributed=parts[5] if len(parts) > 5 else date.today().isoformat(),
        )

# GUEST MODEL

class Guest:
    """Represents a guest in the system.

    Attributes:
        guest_id : Unique identifier
        first_name :Guest's first name
        last_name : Guest's last name
        phone: Phone number
        email: Email address
        address : Physical address / locality
        notes : Additional notes
    """

    def __init__(
        self,
        first_name: str,
        last_name: str,
        phone: str = "",
        email: str = "",
        address: str = "",
        notes: str = "",
        guest_id: Optional[str] = None,
    ) -> None:
        self.guest_id: str = guest_id or _generate_id(GUEST_ID_PREFIX)
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.phone: str = phone
        self.email: str = email
        self.address: str = address
        self.notes: str = notes

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_text_line(self) -> str:
        """Serialize guest fields to a single FIELD_SEP-delimited TXT line."""
        parts = [
            self.guest_id,
            self.first_name,
            self.last_name,
            self.phone,
            self.email,
            self.address,
            self.notes,
        ]
        return FIELD_SEP.join(parts)

    @classmethod
    def from_text_line(cls, line: str) -> "Guest":
        """Rebuild a Guest object from a serialized TXT line."""
        parts = line.strip().split(FIELD_SEP)
        return cls(
            guest_id=parts[0],
            first_name=parts[1],
            last_name=parts[2],
            phone=parts[3] if len(parts) > 3 else "",
            email=parts[4] if len(parts) > 4 else "",
            address=parts[5] if len(parts) > 5 else "",
            notes=parts[6] if len(parts) > 6 else "",
        )
        
# INVITATION MODEL

class Invitation:
    
    """Links a Guest to a Ceremony with RSVP and side information.

    Attributes:
        invitation_id - Unique identifier
        ceremony_id   - ID of the ceremony
        guest_id      - ID of the invited guest
        rsvp_status   - One of: pending, accepted, declined, tentative
        side          - Invitation side (bride/groom/family/friend/colleague/other)
        table_number  - Assigned table number (optional)
        plus_one      - Whether the guest has a plus-one
        sent          - Whether the invitation has been sent
        message       - Personal message to the guest
    """

    def __init__(
        self,
        ceremony_id: str,
        guest_id: str,
        side: str = "other",
        rsvp_status: str = "pending",
        table_number: int = 0,
        plus_one: bool = False,
        sent: bool = False,
        message: str = "",
        invitation_id: Optional[str] = None,
    ) -> None:
        self.invitation_id: str = invitation_id or _generate_id("INV")
        self.ceremony_id: str = ceremony_id
        self.guest_id: str = guest_id
        self.side: str = side
        self.rsvp_status: str = rsvp_status
        self.table_number: int = table_number
        self.plus_one: bool = plus_one
        self.sent: bool = sent
        self.message: str = message

    def respond(self, status: str) -> None:
        """Update the RSVP status.Does nothing if status is not in RSVP_STATUSES."""
        if status in RSVP_STATUSES:
            self.rsvp_status = status

    def mark_sent(self) -> None:
        self.sent = True

    def to_text_line(self) -> str:
        """Serialize to a single TXT line."""
        parts = [
            self.invitation_id,
            self.ceremony_id,
            self.guest_id,
            self.side,
            self.rsvp_status,
            str(self.table_number),
            "1" if self.plus_one else "0",
            "1" if self.sent else "0",
            self.message,
        ]
        return FIELD_SEP.join(parts)

    @classmethod
    def from_text_line(cls, line: str) -> "Invitation":
        """Rebuild an Invitation object from a serialized TXT line."""
        parts = line.strip().split(FIELD_SEP)
        return cls(
            invitation_id=parts[0],
            ceremony_id=parts[1],
            guest_id=parts[2],
            side=parts[3] if len(parts) > 3 else "other",
            rsvp_status=parts[4] if len(parts) > 4 else "pending",
            table_number=int(parts[5]) if len(parts) > 5 else 0,
            plus_one=parts[6] == "1" if len(parts) > 6 else False,
            sent=parts[7] == "1" if len(parts) > 7 else False,
            message=parts[8] if len(parts) > 8 else "",
        )

# CEREMONY MODEL (Parent Class)

class Ceremony:
    
    """Base class for all ceremony types.

    Handles common logic: budget tracking, guest invitations,
    expenses, contributions, and report generation.

    Subclasses (MarriageCeremony, FuneralCeremony, etc.) override
    calculate_cost() and generate_report() for type-specific behavior.
    """

    def __init__(
        self,
        name: str,
        ceremony_date: str,
        location: str,
        budget: float = 0.0,
        organizer_name: str = "",
        description: str = "",
        status: str = "planning",
        ceremony_id: Optional[str] = None,
    ) -> None:
        self.ceremony_id: str = ceremony_id or _generate_id(CEREMONY_ID_PREFIX)
        self.name: str = name
        self.ceremony_type: str = "generic"
        self.ceremony_date: str = ceremony_date
        self.location: str = location
        self.budget: float = budget
        self.organizer_name: str = organizer_name
        self.description: str = description
        self.status: str = status
        self.created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Associated collections (IDs only; resolved at runtime)
        self.invitation_ids: List[str] = []
        self.expense_ids: List[str] = []
        self.contribution_ids: List[str] = []

    # Properties

    @property
    def total_expenses(self) -> float:
        return sum(e.amount for e in self._loaded_expenses)

    @property
    def total_contributions(self) -> float:
        return sum(c.amount for c in self._loaded_contributions)

    @property
    def balance(self) -> float:
        return self.total_contributions - self.total_expenses

    @property
    def budget_remaining(self) -> float:
        return self.budget - self.total_expenses

    @property
    def budget_usage_percent(self) -> float:
        if self.budget <= 0:
            return 0.0
        return min((self.total_expenses / self.budget) * 100, 999.9)

    # Runtime-loaded associations

    _loaded_expenses: List[Expense] = []
    _loaded_contributions: List[Contribution] = []
    _loaded_invitations: List[Invitation] = []

    def load_associations(
        self,
        expenses: Optional[List[Expense]] = None,
        contributions: Optional[List[Contribution]] = None,
        invitations: Optional[List[Invitation]] = None,
    ) -> None:
        """Load associated objects for computed properties."""
        self._loaded_expenses = expenses or []
        self._loaded_contributions = contributions or []
        self._loaded_invitations = invitations or []

    # Polymorphic Methods

    def calculate_cost(self) -> float:
        """Calculate the estimated total cost for this ceremony.
        Override in subclasses for type-specific calculation.
        """
        return self.total_expenses

    def generate_report(self) -> str:
        """Generate a detailed report for this ceremony.
        Override in subclasses for type-specific reporting.
        """
        lines = []
        lines.append(f"  Ceremony Report: {self.name}")
        lines.append(f"  Type:            {self.ceremony_type.title()}")
        lines.append(f"  Date:            {self.ceremony_date}")
        lines.append(f"  Location:        {self.location}")
        lines.append(f"  Status:          {self.status.title()}")
        lines.append(f"  Organizer:       {self.organizer_name}")
        lines.append(f"  Budget:          {self.budget:,.0f} {CURRENCY}")
        lines.append(f"  Total Expenses:  {self.total_expenses:,.0f} {CURRENCY}")
        lines.append(f"  Contributions:   {self.total_contributions:,.0f} {CURRENCY}")
        lines.append(f"  Balance:         {self.balance:,.0f} {CURRENCY}")
        lines.append(f"  Budget Used:     {self.budget_usage_percent:.1f}%")
        lines.append(f"  Guests Invited:  {len(self._loaded_invitations)}")
        accepted = sum(1 for i in self._loaded_invitations if i.rsvp_status == "accepted")
        lines.append(f"  RSVP Accepted:   {accepted}")
        return "\n".join(lines)

    def display_summary(self) -> str:
        """Return a one-line summary: ID | name | type | date | status."""
        return (
            f"{self.ceremony_id} | {self.name} | "
            f"{self.ceremony_type.title()} | {self.ceremony_date} | "
            f"{self.status.title()}"
        )

    # Serialization 

    def _base_to_parts(self) -> list:
        """Return the 13 base fields as a list. Subclasses append their own fields after."""
        return [
            self.ceremony_id,
            self.ceremony_type,
            self.name,
            self.ceremony_date,
            self.location,
            str(self.budget),
            self.organizer_name,
            self.description,
            self.status,
            self.created_at,
            ARRAY_SEP.join(self.invitation_ids),
            ARRAY_SEP.join(self.expense_ids),
            ARRAY_SEP.join(self.contribution_ids),
        ]

    def _base_from_parts(self, parts: list) -> None:
        """Restore the 13 base ceremony fields from a parts list."""
        self.ceremony_id = parts[0]
        self.ceremony_type = parts[1]
        self.name = parts[2]
        self.ceremony_date = parts[3]
        self.location = parts[4]
        self.budget = float(parts[5])
        self.organizer_name = parts[6]
        self.description = parts[7]
        self.status = parts[8]
        self.created_at = parts[9]
        self.invitation_ids = parts[10].split(ARRAY_SEP) if parts[10] else []
        self.expense_ids = parts[11].split(ARRAY_SEP) if parts[11] else []
        self.contribution_ids = parts[12].split(ARRAY_SEP) if parts[12] else []

    def to_text_line(self) -> str:
        """Serialize to a single TXT line. Override in subclasses for extra fields."""
        return FIELD_SEP.join(self._base_to_parts())

    @classmethod
    def from_text_line(cls, line: str) -> "Ceremony":
        """Deserialize from a single TXT line. Dispatches to correct subclass."""
        parts = line.strip().split(FIELD_SEP)
        ctype = parts[1] if len(parts) > 1 else "generic"

        subclass_map = {
            "marriage": MarriageCeremony,
            "funeral": FuneralCeremony,
            "baptism": BaptismCeremony,
            "seminar": SeminarCeremony,
        }

        target_cls = subclass_map.get(ctype, Ceremony)
        obj = target_cls.__new__(target_cls)
        obj._base_from_parts(parts[:13])

        # Let subclass handle extra fields
        if hasattr(obj, "_from_extra_parts"):
            obj._from_extra_parts(parts[13:])

        # Initialize runtime-loaded associations
        obj._loaded_expenses = []
        obj._loaded_contributions = []
        obj._loaded_invitations = []

        return obj


# MARRIAGE CEREMONY

class MarriageCeremony(Ceremony):
    """Marriage ceremony with cultural specifics for Burkina Faso.

    Extra Attributes:
        bride_name : Full name of the bride
        groom_name : Full name of the groom
        dot_amount : Traditional bride price (dot) in FCFA
        marriage_stage : Stage of marriage (traditional/civil/religious/all_stages)
        bride_family : Bride's family name
        groom_family : Groom's family name
    """

    def __init__(
        self,
        name: str,
        ceremony_date: str,
        location: str,
        bride_name: str = "",
        groom_name: str = "",
        dot_amount: float = 0.0,
        marriage_stage: str = "all_stages",
        bride_family: str = "",
        groom_family: str = "",
        budget: float = 0.0,
        organizer_name: str = "",
        description: str = "",
        status: str = "planning",
        ceremony_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            name=name,
            ceremony_date=ceremony_date,
            location=location,
            budget=budget,
            organizer_name=organizer_name,
            description=description,
            status=status,
            ceremony_id=ceremony_id,
        )
        self.ceremony_type = "marriage"
        self.bride_name = bride_name
        self.groom_name = groom_name
        self.dot_amount = dot_amount
        self.marriage_stage = marriage_stage
        self.bride_family = bride_family
        self.groom_family = groom_family

    def calculate_cost(self) -> float:
        """Marriage cost includes all expenses plus the dot."""
        return self.total_expenses + self.dot_amount

    def generate_report(self) -> str:
        """Generate a marriage-specific report."""
        base = super().generate_report()
        lines = [
            base,
            "",
            "  -- Marriage Details --",
            f"  Bride:           {self.bride_name}",
            f"  Groom:           {self.groom_name}",
            f"  Bride's Family:  {self.bride_family}",
            f"  Groom's Family:  {self.groom_family}",
            f"  Marriage Stage:  {self.marriage_stage.replace('_', ' ').title()}",
            f"  Dot Amount:      {self.dot_amount:,.0f} {CURRENCY}",
            f"  Total w/ Dot:    {self.calculate_cost():,.0f} {CURRENCY}",
        ]
        return "\n".join(lines)

    def _from_extra_parts(self, parts: list) -> None:
        """Restore marriage-specific fields from extra parts."""
        self.bride_name = parts[0] if len(parts) > 0 else ""
        self.groom_name = parts[1] if len(parts) > 1 else ""
        self.dot_amount = float(parts[2]) if len(parts) > 2 else 0.0
        self.marriage_stage = parts[3] if len(parts) > 3 else "all_stages"
        self.bride_family = parts[4] if len(parts) > 4 else ""
        self.groom_family = parts[5] if len(parts) > 5 else ""

    def to_text_line(self) -> str:
        """Serialize marriage ceremony including extra fields."""
        base_parts = self._base_to_parts()
        extra = [
            self.bride_name,
            self.groom_name,
            str(self.dot_amount),
            self.marriage_stage,
            self.bride_family,
            self.groom_family,
        ]
        return FIELD_SEP.join(base_parts + extra)

# FUNERAL CEREMONY

class FuneralCeremony(Ceremony):
    """Funeral ceremony with cultural specifics for Burkina Faso.

    Extra Attributes:
        deceased_name : Full name of the deceased
        deceased_age : Age of the deceased
        village_of_origin : Village of origin for burial
        funeral_type : Type (traditional/religious/mixed)
        duration_days : Number of days the funeral lasts
        mourning_period : Mourning period description
    """

    def __init__(
        self,
        name: str,
        ceremony_date: str,
        location: str,
        deceased_name: str = "",
        deceased_age: int = 0,
        village_of_origin: str = "",
        funeral_type: str = "traditional",
        duration_days: int = 3,
        mourning_period: str = "",
        budget: float = 0.0,
        organizer_name: str = "",
        description: str = "",
        status: str = "planning",
        ceremony_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            name=name,
            ceremony_date=ceremony_date,
            location=location,
            budget=budget,
            organizer_name=organizer_name,
            description=description,
            status=status,
            ceremony_id=ceremony_id,
        )
        self.ceremony_type = "funeral"
        self.deceased_name = deceased_name
        self.deceased_age = deceased_age
        self.village_of_origin = village_of_origin
        self.funeral_type = funeral_type
        self.duration_days = duration_days
        self.mourning_period = mourning_period

    def calculate_cost(self) -> float:
        """Funeral cost includes all expenses plus per-day overhead."""
        daily_overhead = 15000 
        # estimated daily cost: meals + logistics for extended family in francs CFa
        return self.total_expenses + (daily_overhead * self.duration_days)

    def generate_report(self) -> str:
        """Generate a funeral-specific report."""
        base = super().generate_report()
        lines = [
            base,
            "",
            "  -- Funeral Details --",
            f"  Deceased:        {self.deceased_name}",
            f"  Age:             {self.deceased_age}",
            f"  Village of Origin: {self.village_of_origin}",
            f"  Funeral Type:    {self.funeral_type.title()}",
            f"  Duration:        {self.duration_days} day(s)",
            f"  Mourning Period: {self.mourning_period}",
            f"  Total w/ Overhead: {self.calculate_cost():,.0f} {CURRENCY}",
        ]
        return "\n".join(lines)

    def _from_extra_parts(self, parts: list) -> None:
        """Restore funeral-specific fields from extra parts."""
        self.deceased_name = parts[0] if len(parts) > 0 else ""
        self.deceased_age = int(parts[1]) if len(parts) > 1 else 0
        self.village_of_origin = parts[2] if len(parts) > 2 else ""
        self.funeral_type = parts[3] if len(parts) > 3 else "traditional"
        self.duration_days = int(parts[4]) if len(parts) > 4 else 3
        self.mourning_period = parts[5] if len(parts) > 5 else ""

    def to_text_line(self) -> str:
        """Serialize funeral ceremony including extra fields."""
        base_parts = self._base_to_parts()
        extra = [
            self.deceased_name,
            str(self.deceased_age),
            self.village_of_origin,
            self.funeral_type,
            str(self.duration_days),
            self.mourning_period,
        ]
        return FIELD_SEP.join(base_parts + extra)

# BAPTISM CEREMONY

class BaptismCeremony(Ceremony):
    """Baptism ceremony with cultural specifics.

    Extra Attributes:
        child_name : Full name of the child being baptized
        child_age_months : Age of the child in months
        godfather_name : Name of the godfather (parrain)
        godmother_name : Name of the godmother (marraine)
        church_name : Name of the church
        priest_name : Name of the officiating priest/pastor
    """

    def __init__(
        self,
        name: str,
        ceremony_date: str,
        location: str,
        child_name: str = "",
        child_age_months: int = 0,
        godfather_name: str = "",
        godmother_name: str = "",
        church_name: str = "",
        priest_name: str = "",
        budget: float = 0.0,
        organizer_name: str = "",
        description: str = "",
        status: str = "planning",
        ceremony_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            name=name,
            ceremony_date=ceremony_date,
            location=location,
            budget=budget,
            organizer_name=organizer_name,
            description=description,
            status=status,
            ceremony_id=ceremony_id,
        )
        self.ceremony_type = "baptism"
        self.child_name = child_name
        self.child_age_months = child_age_months
        self.godfather_name = godfather_name
        self.godmother_name = godmother_name
        self.church_name = church_name
        self.priest_name = priest_name

    def calculate_cost(self) -> float:
        """Baptism cost includes all expenses plus church offering."""
        church_offering = 10000  # FCFA standard offering
        return self.total_expenses + church_offering

    def generate_report(self) -> str:
        """Generate a baptism-specific report."""
        base = super().generate_report()
        lines = [
            base,
            "",
            "  -- Baptism Details --",
            f"  Child:           {self.child_name}",
            f"  Age:             {self.child_age_months} month(s)",
            f"  Godfather:       {self.godfather_name}",
            f"  Godmother:       {self.godmother_name}",
            f"  Church:          {self.church_name}",
            f"  Priest/Pastor:   {self.priest_name}",
            f"  Total w/ Offering: {self.calculate_cost():,.0f} {CURRENCY}",
        ]
        return "\n".join(lines)

    def _from_extra_parts(self, parts: list) -> None:
        """Restore baptism-specific fields from extra parts."""
        self.child_name = parts[0] if len(parts) > 0 else ""
        self.child_age_months = int(parts[1]) if len(parts) > 1 else 0
        self.godfather_name = parts[2] if len(parts) > 2 else ""
        self.godmother_name = parts[3] if len(parts) > 3 else ""
        self.church_name = parts[4] if len(parts) > 4 else ""
        self.priest_name = parts[5] if len(parts) > 5 else ""

    def to_text_line(self) -> str:
        """Serialize baptism ceremony including extra fields."""
        base_parts = self._base_to_parts()
        extra = [
            self.child_name,
            str(self.child_age_months),
            self.godfather_name,
            self.godmother_name,
            self.church_name,
            self.priest_name,
        ]
        return FIELD_SEP.join(base_parts + extra)

# SEMINAR CEREMONY

class SeminarCeremony(Ceremony):
    """Seminar / Conference ceremony.

    Extra Attributes:
        topic : Main topic or theme
        speaker_names : List of speaker names (semicolon-separated)
        num_attendees : Expected number of attendees
        venue_type : Type of venue (hotel/conference_hall/outdoor/other)
        includes_meals : Whether meals are included
    """

    def __init__(
        self,
        name: str,
        ceremony_date: str,
        location: str,
        topic: str = "",
        speaker_names: str = "",
        num_attendees: int = 0,
        venue_type: str = "conference_hall",
        includes_meals: bool = True,
        budget: float = 0.0,
        organizer_name: str = "",
        description: str = "",
        status: str = "planning",
        ceremony_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            name=name,
            ceremony_date=ceremony_date,
            location=location,
            budget=budget,
            organizer_name=organizer_name,
            description=description,
            status=status,
            ceremony_id=ceremony_id,
        )
        self.ceremony_type = "seminar"
        self.topic = topic
        self.speaker_names = speaker_names
        self.num_attendees = num_attendees
        self.venue_type = venue_type
        self.includes_meals = includes_meals

    def calculate_cost(self) -> float:
        """Seminar cost includes all expenses plus per-attendee meal cost."""
        meal_cost_per_person = 3500  
        meal_total = 0
        if self.includes_meals:
            meal_total = meal_cost_per_person * self.num_attendees
        return self.total_expenses + meal_total

    def generate_report(self) -> str:
        """Generate a seminar-specific report."""
        base = super().generate_report()
        speakers = self.speaker_names.replace(";", ", ") if self.speaker_names else "N/A"
        lines = [
            base,
            "",
            "  -- Seminar Details --",
            f"  Topic:           {self.topic}",
            f"  Speakers:        {speakers}",
            f"  Expected Attendees: {self.num_attendees}",
            f"  Venue Type:      {self.venue_type.replace('_', ' ').title()}",
            f"  Meals Included:  {'Yes' if self.includes_meals else 'No'}",
            f"  Total w/ Meals:  {self.calculate_cost():,.0f} {CURRENCY}",
        ]
        return "\n".join(lines)

    def _from_extra_parts(self, parts: list) -> None:
        """Restore seminar-specific fields from extra parts."""
        self.topic = parts[0] if len(parts) > 0 else ""
        self.speaker_names = parts[1] if len(parts) > 1 else ""
        self.num_attendees = int(parts[2]) if len(parts) > 2 else 0
        self.venue_type = parts[3] if len(parts) > 3 else "conference_hall"
        self.includes_meals = parts[4] == "1" if len(parts) > 4 else True

    def to_text_line(self) -> str:
        """Serialize seminar ceremony including extra fields."""
        base_parts = self._base_to_parts()
        extra = [
            self.topic,
            self.speaker_names,
            str(self.num_attendees),
            self.venue_type,
            "1" if self.includes_meals else "0",
        ]
        return FIELD_SEP.join(base_parts + extra)
