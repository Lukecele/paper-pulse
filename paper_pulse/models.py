"""
Data models for paper-pulse.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ExtractedMetrics:
    sample_sizes: List[str] = field(default_factory=list)
    hazard_ratios: List[str] = field(default_factory=list)
    odds_ratios: List[str] = field(default_factory=list)
    p_values: List[str] = field(default_factory=list)
    confidence_intervals: List[str] = field(default_factory=list)
    genes_and_targets: List[str] = field(default_factory=list)

    @property
    def has_metrics(self) -> bool:
        return any([
            self.sample_sizes,
            self.hazard_ratios,
            self.odds_ratios,
            self.p_values,
            self.confidence_intervals,
            self.genes_and_targets
        ])


@dataclass
class Paper:
    title: str
    authors: str
    journal: str
    year: str
    doi: Optional[str] = None
    pmid: Optional[str] = None
    url: Optional[str] = None
    abstract: str = ""
    is_preprint: bool = False
    source: str = "PubMed"
    metrics: ExtractedMetrics = field(default_factory=ExtractedMetrics)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "authors": self.authors,
            "journal": self.journal,
            "year": self.year,
            "doi": self.doi,
            "pmid": self.pmid,
            "url": self.url,
            "is_preprint": self.is_preprint,
            "source": self.source,
            "metrics": {
                "sample_sizes": self.metrics.sample_sizes,
                "hazard_ratios": self.metrics.hazard_ratios,
                "odds_ratios": self.metrics.odds_ratios,
                "p_values": self.metrics.p_values,
                "confidence_intervals": self.metrics.confidence_intervals,
                "genes_and_targets": self.metrics.genes_and_targets,
            }
        }
