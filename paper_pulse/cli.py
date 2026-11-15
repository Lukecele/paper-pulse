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
from typing import List, Dict, Any

# Ensure parent directory is in sys.path for direct script execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from paper_pulse import __version__
    from paper_pulse.models import Paper
    from paper_pulse.clients import search_literature
    from paper_pulse.presets import RESEARCH_PRESETS
    from paper_pulse.exporters import export_markdown, export_bibtex, export_json, export_multi_preset_markdown
except ImportError:
    from . import __version__
    from .models import Paper
    from .clients import search_literature
    from .presets import RESEARCH_PRESETS
    from .exporters import export_markdown, export_bibtex, export_json, export_multi_preset_markdown

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


def display_presets() -> None:
    print(f"\n{C_BOLD}{C_CYAN}📚 Available Research Presets:{C_RESET}\n")
    for key, p in RESEARCH_PRESETS.items():
        print(f"  {C_BOLD}{C_GREEN}• {key}{C_RESET}: {C_BOLD}{p['title']}{C_RESET}")
        print(f"    {C_DIM}Description:{C_RESET} {p['description']}")
        print(f"    {C_DIM}Query:{C_RESET}       {C_BLUE}{p['query']}{C_RESET}\n")
    print(f"  {C_BOLD}{C_GREEN}• all{C_RESET}: Run all research presets into an aggregated multi-topic executive briefing.\n")


def main() -> None:
    if sys.stdout.isatty():
        sys.stdout.write(BANNER)
        sys.stdout.flush()

    parser = argparse.ArgumentParser(
        prog="paper-pulse",
        description="paper-pulse: Real-Time Biomedical Literature & Preprint Intelligence CLI",
        epilog="Examples:\n"
               "  paper-pulse 'osimertinib resistance' --days 7 --limit 5\n"
               "  paper-pulse --preset egfr-resistance --days 14 --limit 5\n"
               "  paper-pulse --preset all --days 7 --export markdown -o Weekly_Pulse.md\n"
               "  paper-pulse --list-presets\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("query", nargs="?", default=None, help="Search query (e.g. 'osimertinib', 'spatial transcriptomics')")
    parser.add_argument("-q", "--topic", dest="topic_query", help="Alternative flag for search topic")
    parser.add_argument("--preset", choices=list(RESEARCH_PRESETS.keys()) + ["all"], help="Execute a curated oncology/biomarker research preset")
    parser.add_argument("--list-presets", action="store_true", help="List all available curated research presets")
    parser.add_argument("-d", "--days", type=int, default=None, help="Filter papers published in last N days (e.g. 7, 30)")
    parser.add_argument("-n", "--limit", type=int, default=10, help="Maximum number of papers to retrieve (default: 10)")
    parser.add_argument("-p", "--preprints", action="store_true", help="Retrieve preprints only (bioRxiv, medRxiv, Research Square)")
    parser.add_argument("-j", "--peer-reviewed", action="store_true", help="Retrieve peer-reviewed journal articles only")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show abstract snippets in terminal output")
    parser.add_argument("-e", "--export", choices=["markdown", "bibtex", "json"], help="Export results to structured file format")
    parser.add_argument("-o", "--out", help="Output file path for export (default: auto-generated filename)")

    args = parser.parse_args()

    if args.list_presets:
        display_presets()
        sys.exit(0)

    # Multi-preset mode ("all")
    if args.preset == "all":
        print(f"\n{C_BOLD}{C_CYAN}🚀 Running Full Executive Research Briefing across {len(RESEARCH_PRESETS)} Pillars...{C_RESET}")
        if args.days:
            print(f"{C_DIM}⏳ Filter window:{C_RESET} Last {args.days} days")
        print(f"{C_DIM}" + "═" * 72 + f"{C_RESET}")

        preset_sections: List[Dict[str, Any]] = []
        all_papers_flat: List[Paper] = []

        for p_key, p_meta in RESEARCH_PRESETS.items():
            print(f"\n{C_BOLD}{C_MAGENTA}▶ Section: {p_meta['title']}{C_RESET}")
            print(f"{C_DIM}🔍 Query: {p_meta['query']}{C_RESET}")

            t0 = time.time()
            try:
                papers = search_literature(
                    query=p_meta["query"],
                    days=args.days,
                    preprints_only=args.preprints,
                    peer_reviewed_only=args.peer_reviewed,
                    limit=args.limit,
                )
            except Exception as e:
                print(f"{C_YELLOW}❌ Error querying {p_key}:{C_RESET} {e}", file=sys.stderr)
                papers = []

            dt = time.time() - t0
            print(f"{C_GREEN}✅ Found {len(papers)} papers in {dt:.2f}s{C_RESET}")

            for idx, paper in enumerate(papers, 1):
                render_paper_card(idx, paper, verbose=args.verbose)

            preset_sections.append({
                "key": p_key,
                "title": p_meta["title"],
                "description": p_meta["description"],
                "query": p_meta["query"],
                "papers": papers,
            })
            all_papers_flat.extend(papers)
            print(f"{C_DIM}" + "─" * 72 + f"{C_RESET}")

        # Multi-preset Export
        if args.export:
            default_filename = f"Executive_Briefing_{time.strftime('%Y%m%d')}"
            if args.export == "markdown":
                out_path = args.out or f"{default_filename}.md"
                export_multi_preset_markdown(preset_sections, out_path)
            elif args.export == "bibtex":
                out_path = args.out or f"{default_filename}.bib"
                export_bibtex(all_papers_flat, out_path)
            elif args.export == "json":
                out_path = args.out or f"{default_filename}.json"
                export_json(all_papers_flat, out_path)

            print(f"\n{C_GREEN}💾 Exported multi-topic briefing ({len(all_papers_flat)} total papers) to {args.export.upper()}:{C_RESET} {C_BOLD}{out_path}{C_RESET}\n")

        sys.exit(0)

    # Single-preset or direct query mode
    search_term = None
    if args.preset:
        preset_info = RESEARCH_PRESETS[args.preset]
        search_term = preset_info["query"]
        print(f"\n{C_BOLD}{C_MAGENTA}📌 Active Preset [{args.preset}]:{C_RESET} {C_BOLD}{preset_info['title']}{C_RESET}")
    else:
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
        sanitized_name = args.preset or "".join(c if c.isalnum() else "_" for c in search_term)[:30].strip("_")
        default_filename = f"literature_{sanitized_name}.{ext_map[args.export]}"
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
