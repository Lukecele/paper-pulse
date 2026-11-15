"""
Biomedical and statistical entity extraction from abstracts.
Extracts cohort sizes (N), Hazard Ratios (HR), Odds Ratios (OR),
p-values, 95% Confidence Intervals, and key genomic/oncological targets.
"""

import re
from typing import List, Set
from .models import ExtractedMetrics

COMMON_GENES_TARGETS = [
    "EGFR", "KRAS", "TP53", "BRAF", "ALK", "ROS1", "MET", "PIK3CA",
    "BRCA1", "BRCA2", "HER2", "ERBB2", "RET", "NTRK", "ctDNA", "PD-L1",
    "VEGF", "CDK4", "CDK6", "MYC", "PTEN", "RB1", "STK11", "KEAP1"
]


def clean_text(text: str) -> str:
    """Strip XML/HTML tags and normalize whitespace."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&[a-zA-Z]+;", " ", text)
    return " ".join(text.split())


def extract_clinical_metrics(text: str) -> ExtractedMetrics:
    """Extract clinical and statistical metrics from text."""
    if not text:
        return ExtractedMetrics()

    cleaned = clean_text(text)

    # 1. Sample Sizes (N)
    sample_sizes: Set[str] = set()
    n_matches = re.findall(r"\b[Nn]\s*=\s*([0-9,]+)", cleaned)
    for m in n_matches:
        val = m.replace(",", "").strip()
        if val.isdigit() and int(val) > 1:
            sample_sizes.add(f"N={val}")

    patient_matches = re.findall(r"\b([0-9,]+)\s+(?:patients|cases|samples|individuals|subjects)\b", cleaned, re.IGNORECASE)
    for m in patient_matches:
        val = m.replace(",", "").strip()
        if val.isdigit() and int(val) > 5:
            sample_sizes.add(f"N={val}")

    # 2. Hazard Ratios (HR)
    hazard_ratios: Set[str] = set()
    hr_matches = re.findall(r"\bHR\s*[:=]\s*([0-9\.]+)", cleaned, re.IGNORECASE)
    for m in hr_matches:
        hazard_ratios.add(f"HR={m}")

    # 3. Odds Ratios (OR)
    odds_ratios: Set[str] = set()
    or_matches = re.findall(r"\bOR\s*[:=]\s*([0-9\.]+)", cleaned, re.IGNORECASE)
    for m in or_matches:
        odds_ratios.add(f"OR={m}")

    # 4. Confidence Intervals (95% CI)
    confidence_intervals: Set[str] = set()
    ci_matches = re.findall(r"95%\s*CI[:\s,]*([0-9\.]+\s*(?:-|to|–)\s*[0-9\.]+)", cleaned, re.IGNORECASE)
    for m in ci_matches:
        confidence_intervals.add(f"95%CI [{m.strip()}]")

    # 5. p-values
    p_values: Set[str] = set()
    p_matches = re.findall(r"\b[pP]\s*([<>=]|<=|>=)\s*([0-9\.\-eE]+)", cleaned)
    for op, val in p_matches:
        # validate number
        try:
            fval = float(val)
            if 0.0 <= fval <= 1.0 or "e" in val.lower():
                p_values.add(f"p{op}{val}")
        except ValueError:
            continue

    # 6. Key Genomic / Molecular Targets
    genes_found: Set[str] = set()
    for gene in COMMON_GENES_TARGETS:
        pattern = r"\b" + re.escape(gene) + r"\b"
        if re.search(pattern, cleaned, re.IGNORECASE):
            genes_found.add(gene)

    return ExtractedMetrics(
        sample_sizes=sorted(list(sample_sizes))[:3],
        hazard_ratios=sorted(list(hazard_ratios))[:3],
        odds_ratios=sorted(list(odds_ratios))[:3],
        p_values=sorted(list(p_values))[:4],
        confidence_intervals=sorted(list(confidence_intervals))[:3],
        genes_and_targets=sorted(list(genes_found))[:5],
    )
