"""Modelos de dados do núcleo público do ARI-CONSULTING."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


class Mode(str, Enum):
    TEST = "test"
    REAL = "real"


@dataclass(frozen=True)
class ServiceItem:
    name: str
    quantity: int
    unit_price: Decimal


@dataclass(frozen=True)
class Briefing:
    mode: Mode
    customer_name: str | None
    contact_email: str | None
    proposal_reference: str | None
    services: tuple[ServiceItem, ...] = field(default_factory=tuple)
    discount_percent: Decimal = Decimal("0")
    explicitly_fictitious: bool = False


@dataclass(frozen=True)
class CommercialResult:
    subtotal: Decimal
    discount_amount: Decimal
    total: Decimal


@dataclass(frozen=True)
class ExecutiveSummary:
    mode: Mode
    label: str
    customer_name: str
    contact_email: str
    proposal_reference: str
    service_count: int
    subtotal: Decimal
    discount_percent: Decimal
    discount_amount: Decimal
    total: Decimal

