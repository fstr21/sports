#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EDGAR Reverse-Split Scanner (master.idx path, extra-verbose)
- Hard-coded SEC User-Agent for: Justin Foster <fstr21@gmail.com>
- Avoids JSON endpoints; uses classic master.idx files per day (robust and simple)
- Finds 8-K and DEF 14A filings; fetches each filing document; classifies fractional-share language
- Exports results.csv into the current working directory by default
"""

import os
import re
import csv
import sys
import time
import json
import argparse
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, date
from typing import List, Dict, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

USER_AGENT = "Justin Foster fstr21@gmail.com (ReverseSplitScanner/1.0)"
DEFAULT_FORMS = ["8-K", "DEF 14A"]
DEFAULT_SINCE_DAYS = 3
DEFAULT_SLEEP = 0.9
DB_FILE = "edgar_reverse_split.db"
TABLE_NAME = "filings"

MASTER_BASE = "https://www.sec.gov/Archives/edgar/daily-index"

KEYWORD_SETS = {
    "reverse_split": [
        r"\breverse\s+split\b",
        r"\bshare\s+consolidation\b",
        r"\bconsolidat(e|ion)\s+of\s+shares\b",
        r"\bcombination\s+of\s+shares\b",
        r"\b(\d+)\s*-\s*for\s*-\s*(\d+)\b",
    ],
    "fractional": [
        r"\bfractional\s+share",
        r"\bfractional\s+shares",
        r"\bfractional\s+interests?",
    ],
    "round_up": [
        r"\brounded?\s+up\b",
        r"\bround\s+up\b",
        r"\brounding\s+up\b",
        r"\bto\s+the\s+nearest\s+whole\s+share\b",
        r"\bany\s+fractional\s+share\s+shall\s+be\s+rounded\s+up\b",
    ],
    "cash_in_lieu": [
        r"\bcash[-\s]*in[-\s]*lieu\b",
        r"\bcash\s+in\s+lieu\b",
        r"\bpaid?\s+in\s+cash\s+for\s+fractional\b",
        r"\bno\s+fractional\s+shares\s+will\s+be\s+issued\b.*\bcash\b",
    ]
}

WINDOW_CHARS = 600
SESSION = requests.Session()

@dataclass
class FilingHit:
    cik: str
    company: str
    form: str
    filed_at: str
    primary_doc_url: str
    score: float
    classification: str
    context_snippets: List[str]
    ratio_hint: Optional[str] = None


def polite_get(url: str, sleep: float = DEFAULT_SLEEP, **kwargs) -> requests.Response:
    headers = kwargs.pop("headers", {})
    headers.setdefault("User-Agent", USER_AGENT)
    headers.setdefault("Accept-Encoding", "gzip, deflate")
    headers.setdefault("Accept", "text/plain, text/html;q=0.9, */*;q=0.8")
    headers.setdefault("Connection", "close")
    attempt = 0
    delay = sleep
    while True:
        try:
            if attempt > 0:
                print(f"Retrying GET ({attempt}) {url}")
                time.sleep(delay)
            resp = SESSION.get(url, headers=headers, timeout=25, **kwargs)
            if resp.status_code in (429, 403) or resp.status_code >= 500:
                attempt += 1
                delay = min(30, delay * 1.7)
                continue
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            attempt += 1
            if attempt > 6:
                print(f"ERROR: giving up on {url}: {e}")
                raise
            delay = min(30, delay * 1.7)


def ensure_db(path: str = DB_FILE):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cik TEXT,
            company TEXT,
            form TEXT,
            filed_at TEXT,
            primary_doc_url TEXT UNIQUE,
            score REAL,
            classification TEXT,
            ratio_hint TEXT,
            context_snippets TEXT,
            created_at TEXT
        );
    """)
    conn.commit()
    return conn


def save_hit(conn, hit: FilingHit):
    c = conn.cursor()
    try:
        c.execute(f"""
            INSERT OR IGNORE INTO {TABLE_NAME}
            (cik, company, form, filed_at, primary_doc_url, score, classification, ratio_hint, context_snippets, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            hit.cik, hit.company, hit.form, hit.filed_at, hit.primary_doc_url, hit.score,
            hit.classification, hit.ratio_hint, json.dumps(hit.context_snippets),
            datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()
    except sqlite3.Error as e:
        print("DB error:", e, file=sys.stderr)


def export_csv(conn, out_path: str):
    c = conn.cursor()
    rows = c.execute(f"SELECT cik, company, form, filed_at, primary_doc_url, score, classification, ratio_hint, context_snippets FROM {TABLE_NAME} ORDER BY filed_at DESC;").fetchall()
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["cik","company","form","filed_at","primary_doc_url","score","classification","ratio_hint","context_snippets"])
        for r in rows:
            writer.writerow(r)
    print(f"Exported {len(rows)} rows to {out_path}")


def extract_primary_doc_url(filing_page_html: str) -> Optional[str]:
    soup = BeautifulSoup(filing_page_html, "lxml")
    candidates = []
    for a in soup.select("a"):
        href = a.get("href", "")
        text = (a.get_text() or "").strip().lower()
        if href.endswith((".htm", ".html")) and "/Archives/" in href:
            candidates.append(href)
        elif text in ("complete submission text file", "documents"):
            if href and "/Archives/" in href:
                candidates.append(href)
    if candidates:
        candidates.sort(key=lambda x: len(x))
        return candidates[0] if candidates[0].startswith("http") else f"https://www.sec.gov{candidates[0]}"
    return None


def fetch_and_extract_text(doc_url: str) -> str:
    resp = polite_get(doc_url)
    content = resp.text
    if doc_url.lower().endswith(".txt"):
        return content
    soup = BeautifulSoup(content, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text)
    return text


def find_context_windows(text: str, pattern: re.Pattern, window: int = WINDOW_CHARS) -> List[str]:
    snippets = []
    for m in pattern.finditer(text):
        start = max(0, m.start() - window)
        end = min(len(text), m.end() + window)
        snippets.append(text[start:end])
    return snippets


def guess_ratio(text: str) -> Optional[str]:
    m = re.search(r"\b(\d+)\s*-\s*for\s*-\s*(\d+)\b", text, flags=re.I)
    if m:
        return f"{m.group(1)}-for-{m.group(2)}"
    return None


def classify_text(text: str) -> Tuple[str, float, List[str]]:
    contexts = []
    score = 0.0

    compiled = {k: [re.compile(p, re.I) for p in KEYWORD_SETS[k]] for k in KEYWORD_SETS.keys()}

    def present(key: str) -> bool:
        return any(p.search(text) for p in compiled[key])

    if present("reverse_split"):
        score += 1.0
        for p in compiled["reverse_split"]:
            contexts += find_context_windows(text, p)
    if present("fractional"):
        score += 1.0
        for p in compiled["fractional"]:
            contexts += find_context_windows(text, p)

    has_round_up = present("round_up")
    has_cash = present("cash_in_lieu")

    if has_round_up:
        score += 2.0
        for p in compiled["round_up"]:
            contexts += find_context_windows(text, p)
    if has_cash:
        score += 1.0
        for p in compiled["cash_in_lieu"]:
            contexts += find_context_windows(text, p)

    if (score >= 2.0) and has_round_up and not has_cash:
        cls = "round_up"
    elif (score >= 2.0) and has_cash and not has_round_up:
        cls = "cash_in_lieu"
    elif (score >= 2.0) and has_cash and has_round_up:
        cls = "ambiguous"
    else:
        cls = "ambiguous"

    uniq = []
    seen = set()
    for s in contexts:
        s2 = s.strip()
        if s2 not in seen:
            uniq.append(s2)
            seen.add(s2)

    return cls, score, uniq[:8]


def quarter_for_month(m: int) -> str:
    if 1 <= m <= 3:
        return "QTR1"
    if 4 <= m <= 6:
        return "QTR2"
    if 7 <= m <= 9:
        return "QTR3"
    return "QTR4"


def master_idx_url_for_date(d: date) -> str:
    q = quarter_for_month(d.month)
    # master.YYYYMMDD.idx
    fname = f"master.{d.strftime('%Y%m%d')}.idx"
    return f"{MASTER_BASE}/{d.year}/{q}/{fname}"


def parse_master_idx(text: str, forms: List[str]) -> List[Dict]:
    """
    master.idx is a pipe-delimited list near the bottom, columns:
    CIK|Company Name|Form Type|Date Filed|Filename
    """
    items = []
    lines = text.splitlines()
    # Skip header (first 10-11 lines usually)
    for line in lines:
        if '|' not in line:
            continue
        parts = line.split('|')
        if len(parts) != 5:
            continue
        cik, comp, form, filed, filename = parts
        form = form.strip()
        if form in forms:
            items.append({
                "cik": cik.strip(),
                "companyName": comp.strip(),
                "formType": form,
                "filedAt": filed.strip(),
                "filename": filename.strip(),  # e.g., edgar/data/0000320193/0001193125-20-123456.txt
            })
    return items


def filing_doc_url_from_filename(filename: str) -> str:
    # Full URL to the submission text file
    return f"https://www.sec.gov/Archives/{filename}"


def process_idx_item(item: Dict, verbose: bool = False) -> Optional[FilingHit]:
    cik = item.get("cik", "")
    company = item.get("companyName", "")
    form = item.get("formType", "")
    filed_at = item.get("filedAt", "")
    filename = item.get("filename", "")
    if not filename:
        return None
    doc_url = filing_doc_url_from_filename(filename)

    # Try to find a primary HTML doc from the submission page if possible
    primary_doc = doc_url
    try:
        # Some .txt submissions include embedded HTML link; attempt to find one by fetching the filing detail page
        # Build an index page URL by replacing -index.htm if recognizable; otherwise use the .txt directly
        text = fetch_and_extract_text(doc_url)
        # If it already contains HTML, classification will proceed; otherwise attempt to find a document link
        m = re.search(r"https://www\.sec\.gov/Archives/[\w/\-\.]+\.htm", text, flags=re.I)
        if m:
            primary_doc = m.group(0)
    except Exception:
        pass

    text = fetch_and_extract_text(primary_doc)
    classification, score, snippets = classify_text(text)
    ratio = guess_ratio(text)

    if verbose:
        print(f"  -> {company} [{form}]  doc: {primary_doc}  class={classification} score={score:.1f}")

    return FilingHit(
        cik=cik,
        company=company,
        form=form,
        filed_at=filed_at,
        primary_doc_url=primary_doc,
        score=score,
        classification=classification,
        context_snippets=snippets,
        ratio_hint=ratio
    )


def iterate_master_days(start: date, end: date, forms: List[str]) -> List[Dict]:
    cur = start
    acc = []
    total = (end - start).days + 1
    idx = 0
    while cur <= end:
        idx += 1
        url = master_idx_url_for_date(cur)
        print(f"[{idx}/{total}] Fetching master.idx for {cur.isoformat()} -> {url}")
        try:
            resp = polite_get(url)
            day_items = parse_master_idx(resp.text, forms)
            print(f"   {len(day_items)} matching filings")
            acc.extend(day_items)
        except Exception as e:
            print(f"   (skip {cur.isoformat()}): {e}")
        time.sleep(DEFAULT_SLEEP)
        cur = cur + timedelta(days=1)
    print(f"Collected {len(acc)} filings across {total} days.")
    return acc


def run(start: datetime, end: datetime, forms: List[str], export_path: Optional[str], verbose: bool):
    t0 = time.time()
    print("Starting scan via master.idx...")
    conn = ensure_db(DB_FILE)
    items = iterate_master_days(start.date(), end.date(), forms)
    print(f"Scanning {len(items)} candidate filings...")

    count = 0
    for i, it in enumerate(items, 1):
        try:
            print(f"[{i}/{len(items)}] Processing {it.get('companyName','')} ({it.get('formType')}) ...")
            hit = process_idx_item(it, verbose=verbose)
            if hit:
                save_hit(conn, hit)
                count += 1
        except Exception as e:
            print(f"  Error: {e}")
        time.sleep(DEFAULT_SLEEP)

    print(f"Processed {count} filings in {time.time()-t0:.1f}s.")
    if export_path is None or export_path.strip() == "":
        export_path = os.path.join(os.getcwd(), "results.csv")
    export_csv(conn, export_path)


def parse_args():
    ap = argparse.ArgumentParser(description="Scan EDGAR (master.idx) for reverse-split fractional-share language. Extra-verbose.")
    ap.add_argument("--since", type=int, default=DEFAULT_SINCE_DAYS, help="Days back from today (mutually exclusive with --start/--end).")
    ap.add_argument("--start", type=str, help="Start date YYYY-MM-DD")
    ap.add_argument("--end", type=str, help="End date YYYY-MM-DD (inclusive)")
    ap.add_argument("--forms", type=str, default=",".join(DEFAULT_FORMS), help="Comma-separated form types, e.g., 8-K,DEF 14A")
    ap.add_argument("--export", type=str, help="Optional CSV export path (defaults to ./results.csv)")
    ap.add_argument("--sleep", type=float, default=DEFAULT_SLEEP, help="Seconds between HTTP requests")
    ap.add_argument("--verbose", action="store_true", help="Verbose per-filing details")
    return ap.parse_args()


def main():
    print("EDGAR Reverse-Split Scanner (master.idx, verbose)")
    print("User-Agent:", USER_AGENT)
    args = parse_args()
    forms = [f.strip() for f in args.forms.split(",") if f.strip()]

    if args.start or args.end:
        if not args.start or not args.end:
            print("Provide both --start and --end, or use --since.", file=sys.stderr)
            sys.exit(2)
        start = dateparser.parse(args.start).replace(tzinfo=timezone.utc)
        end = dateparser.parse(args.end).replace(tzinfo=timezone.utc)
    else:
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=args.since)

    print(f"Date range: {start.date()} to {end.date()}  | Forms: {forms}")
    global DEFAULT_SLEEP
    DEFAULT_SLEEP = max(0.6, float(args.sleep))

    run(start, end, forms, export_path=args.export, verbose=args.verbose)


if __name__ == "__main__":
    main()
