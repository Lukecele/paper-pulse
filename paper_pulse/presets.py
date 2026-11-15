"""
Pre-configured research query presets for oncology, liquid biopsy, and spatial biology.
"""

from typing import Dict, Any

RESEARCH_PRESETS: Dict[str, Dict[str, Any]] = {
    "egfr-resistance": {
        "title": "EGFR TKI Resistance & Molecular Evolution",
        "query": '(osimertinib OR "EGFR TKI" OR "EGFR tyrosine kinase") AND (resistance OR C797S OR "MET amplification" OR "histologic transformation")',
        "description": "Mechanisms of acquired resistance to 3rd-generation EGFR TKIs in NSCLC."
    },
    "ctdna-mrd": {
        "title": "ctDNA & Liquid Biopsy for Minimal Residual Disease (MRD)",
        "query": '("circulating tumor DNA" OR ctDNA OR "liquid biopsy") AND ("minimal residual disease" OR MRD OR "molecular recurrence")',
        "description": "Circulating tumor DNA dynamics, early detection, and MRD monitoring."
    },
    "spatial-immunology": {
        "title": "Spatial Transcriptomics & Tumor Microenvironment Architecture",
        "query": '("spatial transcriptomics" OR "spatial proteomics" OR "spatial biology") AND ("tumor microenvironment" OR "immune infiltration" OR immunotherapy)',
        "description": "High-resolution spatial profiling of tumor-immune cell communication."
    }
}
