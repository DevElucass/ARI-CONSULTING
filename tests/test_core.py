"""Testes unitários do núcleo público, sem I/O e sem rede."""

import sys
import unittest
from decimal import Decimal
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ari_consulting import (  # noqa: E402
    Briefing,
    InvalidBriefingError,
    Mode,
    ServiceItem,
    process_briefing,
    validate_briefing,
)
from ari_consulting.business import calculate_commercial_result  # noqa: E402


def make_briefing(**changes: object) -> Briefing:
    values: dict[str, object] = {
        "mode": Mode.TEST,
        "customer_name": "Empresa Fictícia",
        "contact_email": "contato@empresa.example",
        "proposal_reference": "DEMO-001",
        "services": (
            ServiceItem("Diagnóstico demonstrativo", 2, Decimal("150.00")),
            ServiceItem("Oficina demonstrativa", 1, Decimal("200.00")),
        ),
        "discount_percent": Decimal("10"),
        "explicitly_fictitious": True,
    }
    values.update(changes)
    return Briefing(**values)  # type: ignore[arg-type]


class ValidationTests(unittest.TestCase):
    def test_valid_test_mode_briefing(self) -> None:
        self.assertEqual(validate_briefing(make_briefing()), ())

    def test_example_email_is_accepted_in_test_mode(self) -> None:
        errors = validate_briefing(make_briefing(contact_email="pessoa@demo.example"))
        self.assertFalse(any(error.field == "contact_email" for error in errors))

    def test_example_email_is_rejected_in_real_mode(self) -> None:
        errors = validate_briefing(
            make_briefing(mode=Mode.REAL, explicitly_fictitious=False)
        )
        self.assertTrue(any(".example" in error.message for error in errors))

    def test_missing_required_field_is_rejected_in_real_mode(self) -> None:
        errors = validate_briefing(
            make_briefing(
                mode=Mode.REAL,
                customer_name=None,
                contact_email="contato@empresa.test",
                explicitly_fictitious=False,
            )
        )
        self.assertTrue(any(error.field == "customer_name" for error in errors))

    def test_explicitly_fictitious_data_is_rejected_in_real_mode(self) -> None:
        errors = validate_briefing(
            make_briefing(mode=Mode.REAL, contact_email="contato@empresa.test")
        )
        self.assertTrue(any(error.field == "explicitly_fictitious" for error in errors))


class BusinessRuleTests(unittest.TestCase):
    def test_subtotal_calculation(self) -> None:
        result = calculate_commercial_result(make_briefing())
        self.assertEqual(result.subtotal, Decimal("500.00"))

    def test_discount_calculation(self) -> None:
        result = calculate_commercial_result(make_briefing())
        self.assertEqual(result.discount_amount, Decimal("50.00"))

    def test_total_calculation(self) -> None:
        result = calculate_commercial_result(make_briefing())
        self.assertEqual(result.total, Decimal("450.00"))


class PipelineTests(unittest.TestCase):
    def test_test_mode_is_explicit_in_result(self) -> None:
        summary = process_briefing(make_briefing())
        self.assertEqual(summary.mode, Mode.TEST)
        self.assertIn("MODO TESTE", summary.label)
        self.assertIn("DEMONSTRAÇÃO", summary.label)

    def test_executive_summary_is_built_from_valid_data(self) -> None:
        briefing = make_briefing()
        summary = process_briefing(briefing)
        self.assertEqual(summary.customer_name, briefing.customer_name)
        self.assertEqual(summary.proposal_reference, briefing.proposal_reference)
        self.assertEqual(summary.service_count, 2)
        self.assertEqual(summary.total, Decimal("450.00"))

    def test_missing_commercial_data_is_never_invented(self) -> None:
        briefing = make_briefing(
            mode=Mode.REAL,
            proposal_reference=None,
            contact_email="contato@empresa.test",
            explicitly_fictitious=False,
        )
        with self.assertRaises(InvalidBriefingError) as context:
            process_briefing(briefing)
        self.assertTrue(any(error.field == "proposal_reference" for error in context.exception.errors))
        self.assertIsNone(briefing.proposal_reference)


if __name__ == "__main__":
    unittest.main()
