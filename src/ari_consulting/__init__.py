"""API pública do núcleo autoral ARI-CONSULTING."""

from .models import Briefing, CommercialResult, ExecutiveSummary, Mode, ServiceItem
from .pipeline import process_briefing
from .validation import InvalidBriefingError, ValidationError, validate_briefing

__all__ = [
    "Briefing",
    "CommercialResult",
    "ExecutiveSummary",
    "InvalidBriefingError",
    "Mode",
    "ServiceItem",
    "ValidationError",
    "process_briefing",
    "validate_briefing",
]

