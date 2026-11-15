"""
Unified literature client connecting to Europe PMC API (PubMed + bioRxiv + medRxiv + Research Square)
and NCBI E-utilities.
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
from typing import List, Optional
from .models import Paper
from .extractor import clean_text, extract_clinical_metrics


def search_literature(
    query: str,
    days: Optional[int] = None,
    preprints_only: bool = False,
    peer_reviewed_only: bool = False,
    limit: int = 10,
    timeout: int = 15,
) -> List[Paper]:
    """Search biomedical literature across PubMed, bioRxiv, medRxiv, and PMC."""
    parts = [f"({query})"]

    if days is not None and days > 0:
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        parts.append(f"(FIRST_PDATE:[{start_date} TO {end_date}])")

    if preprints_only:
        parts.append("SRC:PPR")
    elif peer_reviewed_only:
        parts.append("(SRC:MED OR SRC:PMC)")

    full_query = " AND ".join(parts)
    encoded_query = urllib.parse.quote(full_query)

    url = (
        f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
        f"query={encoded_query}&format=json&pageSize={max(1, min(limit, 100))}&resultType=core&sort=P_PDATE_D%20desc"
    )

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "paper-pulse/1.0 (https://github.com/Lukecele/paper-pulse)",
            "Accept": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
    except Exception as e:
        raise RuntimeError(f"Literature query failed: {e}")

    results = data.get("resultList", {}).get("result", [])
    papers: List[Paper] = []

    for r in results:
        title = clean_text(r.get("title", "Untitled"))
        authors = clean_text(r.get("authorString", "Unknown authors"))
        source_code = r.get("source", "MED")
        is_preprint = source_code == "PPR"
        
        # Determine journal/repository name
        if is_preprint:
            publisher = r.get("bookOrReportDetails", {}).get("publisher")
            journal = f"Preprint ({publisher})" if publisher else "Preprint (bioRxiv/medRxiv)"
        else:
            journal = r.get("journalTitle") or ("PubMed Central" if source_code == "PMC" else "PubMed Indexed")

        pub_year = str(r.get("pubYear") or r.get("firstPublicationDate", "2026")[:4])
        doi = r.get("doi")
        pmid = r.get("pmid")

        # Determine best direct URL
        if doi:
            url_link = f"https://doi.org/{doi}"
        elif pmid:
            url_link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        else:
            url_link = f"https://europepmc.org/article/{source_code}/{r.get('id', '')}"

        abstract = clean_text(r.get("abstractText", ""))
        metrics = extract_clinical_metrics(abstract)

        paper = Paper(
            title=title,
            authors=authors,
            journal=journal,
            year=pub_year,
            doi=doi,
            pmid=pmid,
            url=url_link,
            abstract=abstract,
            is_preprint=is_preprint,
            source="Preprint" if is_preprint else "Peer-Reviewed",
            metrics=metrics,
        )
        papers.append(paper)

    return papers
