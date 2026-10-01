"""Teste de integração local do fluxo completo até o DOCX físico."""

import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile, is_zipfile


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ari_consulting import Briefing, Mode, ServiceItem  # noqa: E402
from ari_consulting.docx_generator import generate_demo_docx  # noqa: E402


class DocxIntegrationTests(unittest.TestCase):
    def test_fictitious_data_to_temporary_valid_docx_and_cleanup(self) -> None:
        temporary_file: Path
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_file = Path(temporary_directory) / "demonstracao.docx"
            briefing = Briefing(
                mode=Mode.TEST,
                customer_name="Cliente Exemplo Fictício",
                contact_email="contato@cliente.example",
                proposal_reference="DEMO-INTEGRACAO-001",
                services=(
                    ServiceItem("Análise demonstrativa", 2, Decimal("125.00")),
                    ServiceItem("Sessão demonstrativa", 1, Decimal("300.00")),
                ),
                discount_percent=Decimal("10"),
                explicitly_fictitious=True,
            )

            generated = generate_demo_docx(briefing, temporary_file)

            self.assertEqual(generated, temporary_file)
            self.assertTrue(temporary_file.is_file())
            self.assertGreater(temporary_file.stat().st_size, 0)
            self.assertTrue(is_zipfile(temporary_file))

            with ZipFile(temporary_file) as package:
                self.assertIsNone(package.testzip())
                self.assertTrue(
                    {"[Content_Types].xml", "_rels/.rels", "word/document.xml", "word/styles.xml"}
                    <= set(package.namelist())
                )
                document_xml = package.read("word/document.xml")
                ElementTree.fromstring(document_xml)
                document_text = document_xml.decode("utf-8")

            self.assertIn("MODO TESTE", document_text)
            self.assertIn("DEMONSTRAÇÃO", document_text)
            self.assertIn("contato@cliente.example", document_text)
            self.assertIn("R$ 550,00", document_text)
            self.assertIn("R$ 55,00", document_text)
            self.assertIn("R$ 495,00", document_text)
            self.assertIn("exclusivamente demonstrativos", document_text)

        self.assertFalse(temporary_file.exists())


if __name__ == "__main__":
    unittest.main()
