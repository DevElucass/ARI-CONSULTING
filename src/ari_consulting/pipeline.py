"""Orquestração do fluxo briefing → validação → regras → resumo."""

from .business import calculate_commercial_result
from .models import Briefing, ExecutiveSummary
from .summary import build_executive_summary
from .validation import require_valid_briefing


def process_briefing(briefing: Briefing) -> ExecutiveSummary:
    require_valid_briefing(briefing)
    commercial = calculate_commercial_result(briefing)
    return build_executive_summary(briefing, commercial)

