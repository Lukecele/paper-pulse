# 🛰️ paper-pulse

<p align="center">
  <a href="https://github.com/Lukecele/paper-pulse/actions/workflows/ci.yml"><img src="https://github.com/Lukecele/paper-pulse/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/dependencies-zero-success.svg?style=flat-square" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Europe_PMC-PubMed_%2B_bioRxiv_%2B_medRxiv-orange.svg?style=flat-square" alt="Sources">
</p>

<p align="center">
  <b>Real-time biomedical literature & preprint intelligence CLI with automated clinical entity and statistical metric extraction.</b>
</p>

```
┌────────────────────────────────────────────────────────────────────────┐
│ 🛰️  paper-pulse v1.0.0 — Real-Time Biomedical Literature Intelligence    │
│                                                                        │
│ ⭐ Support Open Science & Automated Research: Please Star on GitHub!   │
│ 👉 https://github.com/Lukecele/paper-pulse                             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Why `paper-pulse`?

Staying on top of rapidly evolving biomedical literature across **PubMed**, **PMC**, **bioRxiv**, **medRxiv**, and **Research Square** is overwhelming. Traditional search engines return walls of text requiring manual screening to determine whether a study provides statistical power, survival benefits, or relevance to your target biomarker.

`paper-pulse` solves this by combining high-speed EBI Europe PMC APIs with an **automated clinical and statistical entity extractor**:

- 🧬 **Zero Dependencies**: Pure Python 3 standard library. No bloated transformers or slow installs. Runs instantly anywhere.
- 📊 **Automated Clinical Entity Extraction**: Instantly parses sample cohorts ($N$), Hazard Ratios ($HR$), Odds Ratios ($OR$), $p$-values, $95\%$ Confidence Intervals, and target biomarkers directly from abstracts.
- ⚡ **Preprint & Recency Filters**: Screen the latest preprints (`--preprints`) or restrict searches to the last $N$ days (`--days 7`).
- 🔗 **Clickable Terminal Cards**: Rich ANSI output with native OSC 8 clickable DOI/PubMed hyperlinks.
- 💾 **Automated Academic Export**: Export literature digests straight into publication-ready **Markdown reports**, **BibTeX** references (`.bib`), or structured **JSON**.

---

## 🚀 Quickstart & Installation

Install directly from GitHub using `pip`:

```bash
pip install git+https://github.com/Lukecele/paper-pulse.git
```

Or clone and run with zero installation:

```bash
git clone https://github.com/Lukecele/paper-pulse.git
cd paper-pulse
python3 paper_pulse/cli.py "osimertinib resistance"
```

---

## 💻 CLI Usage & Examples

### 1. Monitor the Latest Preprints (bioRxiv, medRxiv, Research Square)
Track cutting-edge discoveries before they reach peer review:

```bash
paper-pulse "spatial transcriptomics tumor microenvironment" --preprints --limit 5
```

### 2. Track Oncology Trials Published in the Last 7 Days
Find newly published clinical trial results with automated cohort and hazard ratio extraction:

```bash
paper-pulse "non-small cell lung cancer osimertinib" --days 7 --limit 5
```

### 3. Generate a Curated Markdown Literature Digest
Build a formatted Markdown briefing with metadata and metric badges for journal clubs or team syncs:

```bash
paper-pulse "KRAS G12C inhibitors" --days 30 --export markdown -o kras_update.md
```

### 4. Export BibTeX for LaTeX / Overleaf Manuscripts
Automatically format literature search results into clean BibTeX entries:

```bash
paper-pulse "ctDNA minimal residual disease" --export bibtex -o references.bib
```

### 5. Curated Research Presets & Multi-Topic Executive Briefings
Run pre-configured expert queries across translational oncology and spatial biology:

```bash
# List available research presets
paper-pulse --list-presets

# Track EGFR resistance mutations (C797S, MET, etc.)
paper-pulse --preset egfr-resistance --days 14 --limit 5

# Generate a multi-topic executive briefing across all pillars
paper-pulse --preset all --days 7 --export markdown -o Weekly_Briefing.md
```

### 6. Inspect Abstracts in Verbose Mode
Display full abstract snippets directly in the terminal:

```bash
paper-pulse "immunotherapy response prediction" --verbose --limit 3
```

---

## 📋 Command Line Flags

| Flag | Short | Description |
| :--- | :--- | :--- |
| `query` | — | Search term (e.g. `'osimertinib'`, `'spatial proteomics'`) |
| `--preset` | — | Run a curated preset (`egfr-resistance`, `ctdna-mrd`, `spatial-immunology`, `all`) |
| `--list-presets` | — | Display all available curated presets and exit |
| `--topic` | `-q` | Named topic argument alternative |
| `--days` | `-d` | Filter papers published within the last $N$ days (e.g. `7`, `30`) |
| `--limit` | `-n` | Maximum number of results to retrieve (default: `10`) |
| `--preprints`| `-p` | Filter for preprints only (*bioRxiv*, *medRxiv*, *Research Square*) |
| `--peer-reviewed` | `-j` | Filter for peer-reviewed journal articles only (*PubMed*, *PMC*) |
| `--verbose` | `-v` | Display abstract text in terminal cards |
| `--export` | `-e` | Export results to `markdown`, `bibtex`, or `json` |
| `--out` | `-o` | Output file path for export (defaults to auto-generated name) |

---

## 📊 Extracted Metrics

`paper-pulse` inspects abstracts in real time and automatically tags:

| Metric | Pattern Detected | Example Tag in CLI |
| :--- | :--- | :--- |
| **Cohort Size** | $N=\dots$, $n=\dots$, `X patients`, `X cases` | `📊 N=450` |
| **Hazard Ratio** | $\text{HR}: \dots$, $\text{HR}=\dots$ | `⚖️ HR=0.46` |
| **Odds Ratio** | $\text{OR}: \dots$, $\text{OR}=\dots$ | `🎲 OR=2.15` |
| **Confidence Interval** | $95\%\text{ CI } [\dots]$ | `📐 95%CI [0.37-0.57]` |
| **$p$-Value** | $p < \dots$, $p = \dots$, $p \le \dots$ | `🎯 p<0.001` |
| **Biomarkers & Targets** | EGFR, KRAS, TP53, BRAF, ALK, PD-L1, ctDNA, etc. | `🧬 EGFR KRAS PD-L1` |

---

## 🛠️ Python API Usage

You can also import `paper-pulse` as a lightweight library in your Python pipelines:

```python
from paper_pulse.clients import search_literature

papers = search_literature(
    query="osimertinib",
    days=14,
    preprints_only=True,
    limit=5
)

for paper in papers:
    print(f"[{paper.source}] {paper.title} ({paper.year})")
    if paper.metrics.has_metrics:
        print("  Metrics:", paper.metrics.p_values, paper.metrics.hazard_ratios)
```

---

## 🧪 Testing

Run the full unit test suite:

```bash
python3 -m unittest discover -s tests -v
```

All 14 unit tests run in $<0.01$ seconds with zero third-party requirements.

---

## 👤 Author & Academic Attribution

Developed and maintained by **Luca Celebrano**:
- 🏛️ MD Candidate, Università degli Studi di Napoli Federico II
- 🆔 ORCID: [0009-0007-0931-3555](https://orcid.org/0009-0007-0931-3555)
- 🐙 GitHub: [@Lukecele](https://github.com/Lukecele)
- 🌐 Research Portfolio: [lukecele.github.io](https://lukecele.github.io)

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).
Feel free to use, modify, and integrate it into your bioinformatics and research workflows. If you find it helpful, please consider **starring the repository**! ⭐
