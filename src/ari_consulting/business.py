"""Regras financeiras determinísticas do fluxo comercial."""

from decimal import Decimal, ROUND_HALF_UP

from .models import Briefing, CommercialResult


MONEY = Decimal("0.01")


def calculate_commercial_result(briefing: Briefing) -> CommercialResult:
    subtotal = sum(
        (service.unit_price * service.quantity for service in briefing.services),
        start=Decimal("0"),
    ).quantize(MONEY, rounding=ROUND_HALF_UP)
    discount_amount = (
        subtotal * briefing.discount_percent / Decimal("100")
    ).quantize(MONEY, rounding=ROUND_HALF_UP)
    total = (subtotal - discount_amount).quantize(MONEY, rounding=ROUND_HALF_UP)
    return CommercialResult(subtotal, discount_amount, total)

