#!/usr/bin/env python3
"""
paper-pulse: Real-Time Biomedical Literature & Preprint Intelligence CLI
Search PubMed, bioRxiv, medRxiv with automated clinical entity and metric extraction.
Author: Luca Celebrano (@Lukecele)
License: MIT
"""

import sys
import os
import argparse
import time
from typing import List

# Ensure parent directory is in sys.path for direct script execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from paper_pulse import __version__
    from paper_pulse.models import Paper
    from paper_pulse.clients import search_literature
    from paper_pulse.exporters import export_markdown, export_bibtex, export_json
except ImportError:
    from . import __version__
    from .models import Paper
    from .clients import search_literature
    from .exporters import export_markdown, export_bibtex, export_json

# ANSI Color Tokens
C_RESET = "\x1b[0m"
C_BOLD = "\x1b[1m"
C_DIM = "\x1b[2m"
C_CYAN = "\x1b[36m"
C_GREEN = "\x1b[32m"
C_YELLOW = "\x1b[33m"
C_BLUE = "\x1b[34m"
C_MAGENTA = "\x1b[35m"
C_WHITE = "\x1b[37m"

BANNER = (
    f"{C_BOLD}{C_CYAN}┌────────────────────────────────────────────────────────────────────────┐\n"
    f"│ {C_GREEN}🛰️  paper-pulse v{__version__} — Real-Time Biomedical Literature Intelligence{C_CYAN}    │\n"
    f"│                                                                        │\n"
    f"│ {C_YELLOW}⭐ Support Open Science & Automated Research: Please Star on GitHub!  {C_CYAN} │\n"
    f"│ 👉 {C_BLUE}https://github.com/Lukecele/paper-pulse{C_CYAN}                             │\n"
    f"└────────────────────────────────────────────────────────────────────────┘{C_RESET}\n"
)


def make_hyperlink(url: str, text: str) -> str:
    """Format an OSC 8 terminal hyperlink if terminal supports it."""
    if not url:
        return text
    return f"\x1b]8;;{url}\x1b\\{text}\x1b]8;;\x1b\\"


def render_paper_card(idx: int, p: Paper, verbose: bool = False) -> None:
    badge = f"{C_YELLOW}[PREPRINT]{C_RESET}" if p.is_preprint else f"{C_GREEN}[PEER-REVIEWED]{C_RESET}"
    link = make_hyperlink(p.url or "", p.doi or p.url or "Direct Link")

    print(f"\n{C_BOLD}{C_CYAN}#{idx:02d}{C_RESET} {badge} {C_BOLD}{C_WHITE}{p.title}{C_RESET}")
    print(f"    {C_DIM}Authors:{C_RESET} {p.authors}")
    print(f"    {C_DIM}Source:{C_RESET}  {C_MAGENTA}{p.journal}{C_RESET} ({p.year}) | {C_BLUE}{link}{C_RESET}")

    # Metrics highlight
    m = p.metrics
    if m.has_metrics:
        tokens = []
        if m.sample_sizes:
            tokens.append(f"{C_GREEN}📊 {' '.join(m.sample_sizes)}{C_RESET}")
        if m.hazard_ratios:
            tokens.append(f"{C_YELLOW}⚖️ {' '.join(m.hazard_ratios)}{C_RESET}")
        if m.odds_ratios:
            tokens.append(f"{C_YELLOW}🎲 {' '.join(m.odds_ratios)}{C_RESET}")
        if m.p_values:
            tokens.append(f"{C_CYAN}🎯 {' '.join(m.p_values)}{C_RESET}")
        if m.confidence_intervals:
            tokens.append(f"{C_WHITE}📐 {' '.join(m.confidence_intervals)}{C_RESET}")
        if m.genes_and_targets:
            tokens.append(f"{C_MAGENTA}🧬 {' '.join(m.genes_and_targets)}{C_RESET}")

        print(f"    {C_BOLD}Metrics:{C_RESET} " + " | ".join(tokens))

    if verbose and p.abstract:
        print(f"    {C_DIM}Abstract:{C_RESET} {p.abstract[:380]}...")


def main() -> None:
    if sys.stdout.isatty():
        sys.stdout.write(BANNER)
        sys.stdout.flush()

    parser = argparse.ArgumentParser(
        prog="paper-pulse",
        description="paper-pulse: Real-Time Biomedical Literature & Preprint Intelligence CLI",
        epilog="Examples:\n"
               "  paper-pulse 'osimertinib resistance' --days 7 --limit 5\n"
               "  paper-pulse 'spatial transcriptomics' --preprints --export markdown\n"
               "  paper-pulse 'ctDNA lung cancer' --export bibtex -o references.bib\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("query", nargs="?", default=None, help="Search query (e.g. 'osimertinib', 'spatial transcriptomics')")
    parser.add_argument("-q", "--topic", dest="topic_query", help="Alternative flag for search topic")
    parser.add_argument("-d", "--days", type=int, default=None, help="Filter papers published in last N days (e.g. 7, 30)")
    parser.add_argument("-n", "--limit", type=int, default=10, help="Maximum number of papers to retrieve (default: 10)")
    parser.add_argument("-p", "--preprints", action="store_true", help="Retrieve preprints only (bioRxiv, medRxiv, Research Square)")
    parser.add_argument("-j", "--peer-reviewed", action="store_true", help="Retrieve peer-reviewed journal articles only")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show abstract snippets in terminal output")
    parser.add_argument("-e", "--export", choices=["markdown", "bibtex", "json"], help="Export results to structured file format")
    parser.add_argument("-o", "--out", help="Output file path for export (default: auto-generated filename)")

    args = parser.parse_args()

    search_term = args.query or args.topic_query
    if not search_term:
        parser.print_help()
        sys.exit(1)

    print(f"\n{C_DIM}🔍 Searching PubMed, bioRxiv, and medRxiv for:{C_RESET} {C_BOLD}'{search_term}'{C_RESET}")
    if args.days:
        print(f"{C_DIM}⏳ Filter window:{C_RESET} Last {args.days} days")
    if args.preprints:
        print(f"{C_DIM}📂 Source filter:{C_RESET} Preprints Only (bioRxiv / medRxiv / Research Square)")
    elif args.peer_reviewed:
        print(f"{C_DIM}📂 Source filter:{C_RESET} Peer-Reviewed Articles Only")

    start_time = time.time()
    try:
        papers = search_literature(
            query=search_term,
            days=args.days,
            preprints_only=args.preprints,
            peer_reviewed_only=args.peer_reviewed,
            limit=args.limit,
        )
    except Exception as e:
        print(f"\n{C_YELLOW}❌ Search error:{C_RESET} {e}", file=sys.stderr)
        sys.exit(1)

    elapsed = time.time() - start_time

    if not papers:
        print(f"\n{C_YELLOW}⚠️  No papers found matching the specified query and date filter.{C_RESET}\n")
        sys.exit(0)

    print(f"{C_GREEN}✅ Found {len(papers)} papers in {elapsed:.2f}s:{C_RESET}")

    for idx, paper in enumerate(papers, 1):
        render_paper_card(idx, paper, verbose=args.verbose)

    print("\n" + f"{C_DIM}" + "─" * 72 + f"{C_RESET}")

    # Handle Exports
    if args.export:
        ext_map = {"markdown": "md", "bibtex": "bib", "json": "json"}
        sanitized_topic = "".join(c if c.isalnum() else "_" for c in search_term)[:30].strip("_")
        default_filename = f"literature_{sanitized_topic}.{ext_map[args.export]}"
        out_path = args.out or default_filename

        if args.export == "markdown":
            export_markdown(papers, search_term, out_path)
        elif args.export == "bibtex":
            export_bibtex(papers, out_path)
        elif args.export == "json":
            export_json(papers, out_path)

        print(f"{C_GREEN}💾 Exported {len(papers)} papers to {args.export.upper()}:{C_RESET} {C_BOLD}{out_path}{C_RESET}\n")


if __name__ == "__main__":
    main()
