"""Construção estruturada do resumo executivo."""

from .models import Briefing, CommercialResult, ExecutiveSummary, Mode


TEST_LABEL = "MODO TESTE — DEMONSTRAÇÃO; DADOS PODEM SER FICTÍCIOS"
REAL_LABEL = "MODO REAL"


def build_executive_summary(
    briefing: Briefing,
    commercial: CommercialResult,
) -> ExecutiveSummary:
    # A validação anterior garante os tipos concretos; nenhum valor é inventado aqui.
    assert briefing.customer_name is not None
    assert briefing.contact_email is not None
    assert briefing.proposal_reference is not None
    return ExecutiveSummary(
        mode=briefing.mode,
        label=TEST_LABEL if briefing.mode is Mode.TEST else REAL_LABEL,
        customer_name=briefing.customer_name,
        contact_email=briefing.contact_email,
        proposal_reference=briefing.proposal_reference,
        service_count=len(briefing.services),
        subtotal=commercial.subtotal,
        discount_percent=briefing.discount_percent,
        discount_amount=commercial.discount_amount,
        total=commercial.total,
    )

