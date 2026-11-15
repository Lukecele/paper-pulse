"""
Exporters for literature digests: Markdown, BibTeX, and JSON.
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any
from .models import Paper


def _sanitize_bibtex_key(author: str, year: str, title: str) -> str:
    first_author = author.split(",")[0].split()[0] if author else "Unknown"
    first_author = re.sub(r"[^a-zA-Z]", "", first_author)
    first_word = re.sub(r"[^a-zA-Z]", "", title.split()[0]) if title else "Paper"
    return f"{first_author}_{year}_{first_word}".strip("_")


def export_bibtex(papers: List[Paper], output_path: str) -> None:
    """Generate BibTeX entries for literature collection."""
    entries = []
    for p in papers:
        key = _sanitize_bibtex_key(p.authors, p.year, p.title)
        entry_type = "article" if not p.is_preprint else "misc"
        
        fields = [
            f"  author = {{{p.authors}}}",
            f"  title = {{{{{p.title}}}}}",
            f"  year = {{{p.year}}}",
            f"  journal = {{{p.journal}}}",
        ]
        if p.doi:
            fields.append(f"  doi = {{{p.doi}}}")
        if p.url:
            fields.append(f"  url = {{{p.url}}}")
        if p.is_preprint:
            fields.append("  note = {Preprint}")

        entry_str = f"@{entry_type}{{{key},\n" + ",\n".join(fields) + "\n}"
        entries.append(entry_str)

    content = "\n\n".join(entries) + "\n"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def _render_paper_markdown_lines(idx: int, p: Paper) -> List[str]:
    lines = []
    badge = "🟡 `PREPRINT`" if p.is_preprint else "🟢 `PEER-REVIEWED`"
    lines.append(f"### {idx}. {p.title}")
    lines.append(f"{badge} **{p.journal}** ({p.year})")
    lines.append(f"* **Authors:** {p.authors}")
    if p.url:
        lines.append(f"* **Direct Access:** [{p.doi or p.url}]({p.url})")
    if p.pmid:
        lines.append(f"* **PMID:** [{p.pmid}](https://pubmed.ncbi.nlm.nih.gov/{p.pmid}/)")

    m = p.metrics
    if m.has_metrics:
        metrics_summary = []
        if m.sample_sizes:
            metrics_summary.append(f"📊 **Cohort Size:** `{' '.join(m.sample_sizes)}`")
        if m.hazard_ratios:
            metrics_summary.append(f"⚖️ **Hazard Ratio:** `{' '.join(m.hazard_ratios)}`")
        if m.odds_ratios:
            metrics_summary.append(f"🎲 **Odds Ratio:** `{' '.join(m.odds_ratios)}`")
        if m.p_values:
            metrics_summary.append(f"🎯 **p-value:** `{' '.join(m.p_values)}`")
        if m.confidence_intervals:
            metrics_summary.append(f"📐 **CI:** `{' '.join(m.confidence_intervals)}`")
        if m.genes_and_targets:
            metrics_summary.append(f"🧬 **Key Targets:** `{' '.join(m.genes_and_targets)}`")

        lines.append("\n> **Extracted Clinical & Statistical Entities:**  ")
        for item in metrics_summary:
            lines.append(f"> {item}  ")

    if p.abstract:
        lines.append(f"\n<details><summary><strong>Abstract</strong></summary>\n\n{p.abstract}\n</details>")

    lines.append("\n---\n")
    return lines


def export_markdown(papers: List[Paper], query: str, output_path: str) -> None:
    """Generate a clean Markdown digest report with metadata and extracted metrics."""
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 🛰️ PaperPulse Literature Digest: {query}",
        f"*Generated on {date_str} via [paper-pulse](https://github.com/Lukecele/paper-pulse)*\n",
        "---",
        f"**Search Query:** `{query}`  ",
        f"**Total Papers Retrieved:** `{len(papers)}`\n",
        "## 📚 Curated Articles\n"
    ]

    for idx, p in enumerate(papers, 1):
        lines.extend(_render_paper_markdown_lines(idx, p))

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def export_multi_preset_markdown(preset_sections: List[Dict[str, Any]], output_path: str) -> None:
    """Generate a multi-section executive briefing across multiple research topics."""
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_papers = sum(len(sec["papers"]) for sec in preset_sections)
    lines = [
        "# 🛰️ Executive Biomedical Literature & Preprint Briefing",
        f"*Generated on {date_str} via [paper-pulse](https://github.com/Lukecele/paper-pulse)*\n",
        "---",
        f"**Total Tracked Research Areas:** `{len(preset_sections)}`  ",
        f"**Total Curated Papers:** `{total_papers}`\n",
        "## 📑 Table of Contents"
    ]

    for s_idx, sec in enumerate(preset_sections, 1):
        anchor = sec["title"].lower().replace(" ", "-").replace("&", "").replace("(", "").replace(")", "").replace("--", "-")
        lines.append(f"{s_idx}. [{sec['title']}](#{anchor}) (`{len(sec['papers'])}` papers)")

    lines.append("\n---\n")

    for sec in preset_sections:
        lines.append(f"## {sec['title']}\n")
        lines.append(f"*{sec['description']}*\n")
        lines.append(f"**Query Filter:** `{sec['query']}`\n")

        papers = sec["papers"]
        if not papers:
            lines.append("> ℹ️ *No new papers found in this category for the specified date window.*\n\n---\n")
            continue

        for idx, p in enumerate(papers, 1):
            lines.extend(_render_paper_markdown_lines(idx, p))

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def export_json(papers: List[Paper], output_path: str) -> None:
    """Export papers and metrics to formatted JSON."""
    data = [p.to_dict() for p in papers]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
