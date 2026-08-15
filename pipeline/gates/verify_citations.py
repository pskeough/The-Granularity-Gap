"""Verify every \\bibitem in the manuscript against OpenAlex and arXiv.

For each entry: pull the title, search OpenAlex, and report the closest match with its
similarity, year and DOI. Any arXiv identifier in the entry is resolved directly against
the arXiv API, which is stricter than a title search.

Exit 0 if every entry resolves; 1 if any entry is unmatched or mismatched.
"""
import difflib
import json
import re
import sys
import time
import urllib.parse
import urllib.request

TEX = r"C:\Research\Sychophancy\main_granularitygap_v2.tex"
MAILTO = "pskeough@gmail.com"
UA = {"User-Agent": f"granularity-gap-citation-check (mailto:{MAILTO})"}


def clean(s):
    s = re.sub(r"\\textit\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\&", "&", s)
    s = re.sub(r"\\[a-zA-Z]+", " ", s)
    s = re.sub(r"[{}]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_entries(path):
    txt = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem\{|\\end\{thebibliography\})",
                         txt, re.S):
        key, body = m.group(1), clean(m.group(2))
        year = re.search(r"\((\d{4})\)", body)
        arx = re.search(r"arXiv[:\s]*(\d{4}\.\d{4,5})", body)
        # title is the sentence after "(YEAR)."
        title = ""
        if year:
            after = body[year.end():].lstrip(". ")
            title = after.split(". ")[0].strip().rstrip(".")
        out.append({
            "key": key,
            "raw": body,
            "year": int(year.group(1)) if year else None,
            "arxiv": arx.group(1) if arx else None,
            "title": title,
        })
    return out


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def openalex(title):
    q = urllib.parse.quote(title[:220])
    url = f"https://api.openalex.org/works?search={q}&per-page=3&mailto={MAILTO}"
    try:
        d = get_json(url)
    except Exception as e:
        return None, f"api error: {e}"
    if not d.get("results"):
        return None, "no results"
    best, score = None, 0.0
    for w in d["results"]:
        t = (w.get("title") or "").lower()
        s = difflib.SequenceMatcher(None, title.lower(), t).ratio()
        if s > score:
            best, score = w, s
    return (best, score) if best else (None, "no results")


def arxiv_lookup(aid):
    url = f"http://export.arxiv.org/api/query?id_list={aid}"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            xml = r.read().decode("utf-8", "replace")
    except Exception as e:
        return None, f"api error: {e}"
    m = re.search(r"<entry>.*?<title>(.*?)</title>", xml, re.S)
    if not m:
        return None, "no entry"
    return re.sub(r"\s+", " ", m.group(1)).strip(), None


entries = parse_entries(TEX)
print(f"{len(entries)} bibitems parsed\n")

bad = 0
for e in entries:
    print(f"--- {e['key']} ({e['year']}) ---")
    print(f"    claimed: {e['title'][:96]}")
    verdict = []

    if e["arxiv"]:
        t, err = arxiv_lookup(e["arxiv"])
        if err:
            verdict.append(f"arXiv {e['arxiv']}: {err}")
            bad += 1
        else:
            sim = difflib.SequenceMatcher(None, e["title"].lower(), t.lower()).ratio()
            tag = "MATCH" if sim > 0.75 else "MISMATCH"
            if tag == "MISMATCH":
                bad += 1
            verdict.append(f"arXiv {e['arxiv']} {tag} ({sim:.2f}): {t[:90]}")
        time.sleep(3)

    res, score = openalex(e["title"]) if e["title"] else (None, "no title parsed")
    if res is None:
        verdict.append(f"OpenAlex: {score}")
        if not e["arxiv"]:
            bad += 1
    else:
        doi = res.get("doi") or "no doi"
        tag = "MATCH" if score > 0.75 else ("WEAK" if score > 0.5 else "MISMATCH")
        if tag == "MISMATCH" and not e["arxiv"]:
            bad += 1
        verdict.append(f"OpenAlex {tag} ({score:.2f}) {res.get('publication_year')} "
                       f"{doi}\n              {(res.get('title') or '')[:90]}")
    for v in verdict:
        print(f"    {v}")
    print()
    time.sleep(1)

print(f"\nentries needing a look: {bad} of {len(entries)}")
sys.exit(1 if bad else 0)
