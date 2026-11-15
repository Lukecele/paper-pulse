"""
Unit tests for paper_pulse entity and metric extractor.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from paper_pulse.extractor import clean_text, extract_clinical_metrics


class TestExtractor(unittest.TestCase):

    def test_clean_text_removes_xml_and_extra_whitespace(self):
        raw = "<p>This is   a <b>bold</b> study &amp; analysis.</p>"
        cleaned = clean_text(raw)
        self.assertEqual(cleaned, "This is a bold study analysis.")

    def test_clean_text_handles_empty_or_none(self):
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text(None), "")

    def test_extract_sample_sizes(self):
        text = "A total of n = 450 patients were enrolled. Subgroup N=120 showed benefit. 1,250 cases reviewed."
        metrics = extract_clinical_metrics(text)
        self.assertIn("N=450", metrics.sample_sizes)
        self.assertIn("N=120", metrics.sample_sizes)
        self.assertIn("N=1250", metrics.sample_sizes)

    def test_extract_hazard_ratios(self):
        text = "Progression-free survival was improved with osimertinib (HR: 0.46; 95% CI 0.37-0.57)."
        metrics = extract_clinical_metrics(text)
        self.assertIn("HR=0.46", metrics.hazard_ratios)

    def test_extract_odds_ratios(self):
        text = "Response was significantly higher in EGFR group (OR: 2.85; p < 0.001)."
        metrics = extract_clinical_metrics(text)
        self.assertIn("OR=2.85", metrics.odds_ratios)

    def test_extract_confidence_intervals(self):
        text = "Overall survival benefit was observed (95% CI 0.62-0.89, p = 0.002)."
        metrics = extract_clinical_metrics(text)
        self.assertTrue(any("0.62" in ci and "0.89" in ci for ci in metrics.confidence_intervals))

    def test_extract_p_values(self):
        text = "Statistical significance was reached (p < 0.001, P = 0.042, p <= 0.05, p=1.2e-4)."
        metrics = extract_clinical_metrics(text)
        self.assertIn("p<0.001", metrics.p_values)
        self.assertIn("p=0.042", metrics.p_values)

    def test_extract_genomic_targets(self):
        text = "Patients harboring EGFR L858R or KRAS G12C mutations along with TP53 alterations and PD-L1 expression."
        metrics = extract_clinical_metrics(text)
        self.assertIn("EGFR", metrics.genes_and_targets)
        self.assertIn("KRAS", metrics.genes_and_targets)
        self.assertIn("TP53", metrics.genes_and_targets)
        self.assertIn("PD-L1", metrics.genes_and_targets)

    def test_has_metrics_flag(self):
        empty_metrics = extract_clinical_metrics("A retrospective review of historical institutional records.")
        self.assertFalse(empty_metrics.has_metrics)

        rich_metrics = extract_clinical_metrics("EGFR mutant lung cancer cohort with N=350 patients (HR: 0.55).")
        self.assertTrue(rich_metrics.has_metrics)


if __name__ == "__main__":
    unittest.main()
