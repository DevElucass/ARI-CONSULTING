"""Validação explícita, sem completar dados ausentes."""

from dataclasses import dataclass
from decimal import Decimal

from .models import Briefing, Mode


@dataclass(frozen=True)
class ValidationError:
    field: str
    message: str


class InvalidBriefingError(ValueError):
    def __init__(self, errors: tuple[ValidationError, ...]) -> None:
        self.errors = errors
        super().__init__("; ".join(f"{error.field}: {error.message}" for error in errors))


def _is_example_email(value: str) -> bool:
    domain = value.rsplit("@", 1)[-1].lower() if "@" in value else ""
    return domain == "example" or domain.endswith(".example")


def validate_briefing(briefing: Briefing) -> tuple[ValidationError, ...]:
    errors: list[ValidationError] = []

    required_text = {
        "customer_name": briefing.customer_name,
        "contact_email": briefing.contact_email,
        "proposal_reference": briefing.proposal_reference,
    }
    for field_name, value in required_text.items():
        if value is None or not value.strip():
            errors.append(ValidationError(field_name, "campo obrigatório ausente"))

    if not briefing.services:
        errors.append(ValidationError("services", "ao menos um serviço é obrigatório"))

    if briefing.contact_email and "@" not in briefing.contact_email:
        errors.append(ValidationError("contact_email", "formato de e-mail inválido"))

    if briefing.mode is Mode.REAL:
        if briefing.explicitly_fictitious:
            errors.append(ValidationError("explicitly_fictitious", "dados fictícios não são permitidos no modo real"))
        if briefing.contact_email and _is_example_email(briefing.contact_email):
            errors.append(ValidationError("contact_email", "domínio .example não é permitido no modo real"))

    if briefing.discount_percent < Decimal("0") or briefing.discount_percent > Decimal("100"):
        errors.append(ValidationError("discount_percent", "o desconto deve estar entre 0 e 100"))

    for index, service in enumerate(briefing.services):
        if not service.name.strip():
            errors.append(ValidationError(f"services[{index}].name", "nome obrigatório"))
        if service.quantity <= 0:
            errors.append(ValidationError(f"services[{index}].quantity", "quantidade deve ser positiva"))
        if service.unit_price < Decimal("0"):
            errors.append(ValidationError(f"services[{index}].unit_price", "preço não pode ser negativo"))

    return tuple(errors)


def require_valid_briefing(briefing: Briefing) -> None:
    errors = validate_briefing(briefing)
    if errors:
        raise InvalidBriefingError(errors)

