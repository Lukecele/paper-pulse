"""
Unit tests for paper_pulse exporters and models.
"""

import sys
import os
import json
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from paper_pulse.models import Paper, ExtractedMetrics
from paper_pulse.exporters import (
    export_bibtex,
    export_markdown,
    export_json,
    export_multi_preset_markdown,
    _sanitize_bibtex_key
)


class TestModelsAndExporters(unittest.TestCase):

    def setUp(self):
        self.sample_metrics = ExtractedMetrics(
            sample_sizes=["N=520"],
            hazard_ratios=["HR=0.45"],
            odds_ratios=["OR=2.1"],
            p_values=["p<0.001"],
            confidence_intervals=["95%CI [0.35-0.58]"],
            genes_and_targets=["EGFR", "KRAS"]
        )
        self.sample_paper_1 = Paper(
            title="Targeting EGFR in Non-Small Cell Lung Cancer",
            authors="Celebrano L, Smith J, Doe A",
            journal="J Clin Oncol",
            year="2025",
            doi="10.1200/JCO.2025.123",
            pmid="39000000",
            url="https://doi.org/10.1200/JCO.2025.123",
            abstract="In N=520 patients, EGFR inhibitors showed HR: 0.45 (95% CI 0.35-0.58, p < 0.001).",
            is_preprint=False,
            source="Peer-Reviewed",
            metrics=self.sample_metrics
        )
        self.sample_paper_2 = Paper(
            title="Biophysical Modeling of Clonal Resistance",
            authors="Celebrano L",
            journal="Preprint (bioRxiv)",
            year="2026",
            doi="10.1101/2026.01.01.000000",
            pmid=None,
            url="https://doi.org/10.1101/2026.01.01.000000",
            abstract="Mathematical oncology model of tumor-immune dynamics.",
            is_preprint=True,
            source="Preprint",
            metrics=ExtractedMetrics()
        )

    def test_sanitize_bibtex_key(self):
        key = _sanitize_bibtex_key("Celebrano L, Smith J", "2025", "Targeting EGFR in NSCLC")
        self.assertEqual(key, "Celebrano_2025_Targeting")

    def test_paper_to_dict(self):
        d = self.sample_paper_1.to_dict()
        self.assertEqual(d["title"], "Targeting EGFR in Non-Small Cell Lung Cancer")
        self.assertEqual(d["doi"], "10.1200/JCO.2025.123")
        self.assertFalse(d["is_preprint"])
        self.assertIn("N=520", d["metrics"]["sample_sizes"])
        self.assertIn("EGFR", d["metrics"]["genes_and_targets"])

    def test_export_bibtex(self):
        with tempfile.NamedTemporaryFile(suffix=".bib", delete=False) as f:
            temp_path = f.name

        try:
            export_bibtex([self.sample_paper_1, self.sample_paper_2], temp_path)
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("@article{Celebrano_2025_Targeting", content)
            self.assertIn("@misc{Celebrano_2026_Biophysical", content)
            self.assertIn("10.1200/JCO.2025.123", content)
            self.assertIn("note = {Preprint}", content)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_export_markdown(self):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            temp_path = f.name

        try:
            export_markdown([self.sample_paper_1, self.sample_paper_2], "EGFR lung cancer", temp_path)
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("# 🛰️ PaperPulse Literature Digest: EGFR lung cancer", content)
            self.assertIn("🟢 `PEER-REVIEWED`", content)
            self.assertIn("🟡 `PREPRINT`", content)
            self.assertIn("📊 **Cohort Size:** `N=520`", content)
            self.assertIn("⚖️ **Hazard Ratio:** `HR=0.45`", content)
            self.assertIn("🧬 **Key Targets:** `EGFR KRAS`", content)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_export_json(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            export_json([self.sample_paper_1, self.sample_paper_2], temp_path)
            with open(temp_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["title"], "Targeting EGFR in Non-Small Cell Lung Cancer")
            self.assertEqual(data[1]["is_preprint"], True)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_export_multi_preset_markdown(self):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            temp_path = f.name

        try:
            sections = [
                {
                    "key": "egfr-resistance",
                    "title": "EGFR TKI Resistance",
                    "description": "Acquired resistance mechanisms.",
                    "query": "osimertinib resistance",
                    "papers": [self.sample_paper_1]
                },
                {
                    "key": "spatial-immunology",
                    "title": "Spatial Immunology",
                    "description": "TME profiling.",
                    "query": "spatial transcriptomics",
                    "papers": [self.sample_paper_2]
                }
            ]
            export_multi_preset_markdown(sections, temp_path)
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("# 🛰️ Executive Biomedical Literature & Preprint Briefing", content)
            self.assertIn("1. [EGFR TKI Resistance](#egfr-tki-resistance)", content)
            self.assertIn("2. [Spatial Immunology](#spatial-immunology)", content)
            self.assertIn("## EGFR TKI Resistance", content)
            self.assertIn("## Spatial Immunology", content)
            self.assertIn("Targeting EGFR in Non-Small Cell Lung Cancer", content)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
