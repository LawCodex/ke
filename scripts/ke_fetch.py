#!/usr/bin/env python3
"""Kenya: fetch the Constitution of Kenya 2010 (Parliament of Kenya library repository) and the
Acts published on the National Assembly website (parliament.go.ke), convert to Markdown.

Usage: python3 ke_fetch.py [--no-download]
Raw files are cached in ../../_raw/ke (outside the repo)."""
import hashlib
import html
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ke_text as T  # noqa

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(os.path.dirname(REPO), "_raw", "ke")
RETRIEVED = os.environ.get("LC_RETRIEVED", "2026-10-13")
NA = "https://www.parliament.go.ke"
ACT_PAGES = [NA + "/the-national-assembly/house-business/acts?field_parliament_value=%s&title=&page=%d" % (v, p)
             for v in ("All", "2013", "2017", "2018", "2019", "2020", "2021", "2022") for p in (0, 1)]
EXTRA = [NA + "/parliamentary-service-act"]
CONST = {
    "url": "https://libraryir.parliament.go.ke/server/api/core/bitstreams/95abbe3f-8d3f-4b0d-b4a6-1bbd03e5b8e9/content",
    "page": "https://libraryir.parliament.go.ke/handle/123456789/1090",
}
DL = "--no-download" not in sys.argv


def act_links():
    links = {}
    for k, u in enumerate(ACT_PAGES + EXTRA):
        p = os.path.join(RAW, "list", "%02d.html" % k)
        if DL:
            T.fetch(u, p, delay=2)
        if not os.path.exists(p):
            continue
        t = open(p, encoding="utf-8", errors="replace").read()
        for href, title in re.findall(r'<a href="(https://www\.parliament\.go\.ke/sites/default/files/[^"]+\.pdf)"[^>]*title="([^"]+)"', t):
            title = html.unescape(title)
            if re.search(r"hansard|order paper|appointment|bill|notice paper|votes", title, re.I):
                continue
            if not re.search(r"act", title, re.I):
                continue
            links[href] = title
    return links


FIRSTTITLE = re.compile(r"^(THE\s+)?([A-Z][A-Z ,()'’&\-]+?\bACT)(,?\s*(\d{4}|CAP\.?\s*\d+\w*))?\.?$")


def guess_title(lines, fname):
    txt = re.sub(r"\s+", " ", " ".join(lines))
    m = re.search(r"may be cited as the ([A-Z][^.;]{3,150}?\bAct(?:,? (?:No\. ?\d+ of )?\d{4})?)(?:[.;,]| and\b)", txt)
    if m:
        t = re.sub(r"\b(Short title( and( commencement)?)?|Commencement)\b ?", "", m.group(1))
        t = re.sub(r"\b((?:[A-Za-z] ){2,}[A-Za-z])\b", lambda k: k.group(1).replace(" ", ""), t)
        return re.sub(r"^The ", "", re.sub(r"\s+", " ", t).strip())
    for x in lines[:250]:
        x2 = re.sub(r"\s+", " ", x).strip()
        m = FIRSTTITLE.match(x2)
        if m and len(x2) < 140 and not x2.startswith(("AN ACT", "ACT ")):
            return x2
    base = urllib.parse.unquote(os.path.basename(fname))[:-4]
    base = re.sub(r"_\d$", "", base).replace("_", " ")
    base = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", base)
    return re.sub(r"\s+", " ", base).strip()


def number_year(lines, title):
    txt = " ".join(lines[:300])
    m = re.search(r"((19|20)\d\d)", title)
    y = m.group(1) if m else None
    for m in re.finditer(r"\bNo\.?\s*(\d{1,3})\s+of\s+((19|20)\d\d)\b", txt):
        if y is None or m.group(2) == y:
            return m.group(1), m.group(2)
    return None, y


def nice(t):
    t = re.sub(r"\s+", " ", t).strip()
    if t.isupper():
        small = {"and", "of", "the", "for", "to", "in", "on", "a", "an", "by", "with", "or"}
        w = t.lower().split(" ")
        t = " ".join(x if (i and x.strip("(),") in small) else re.sub(r"[a-z][a-z']*", lambda m: m.group(0).capitalize(), x, count=1) for i, x in enumerate(w))
    return t


def do_constitution():
    pdf = os.path.join(RAW, "pdf", "constitution-2010.pdf")
    if DL:
        T.fetch(CONST["url"], pdf, delay=2, check_pdf=True)
    if not os.path.exists(pdf) or not T.pdf_ok(pdf):
        print("constitution missing")
        return
    pages, _ = T.pdf_text(pdf, "eng", tmpdir=RAW, ocr=False)
    lines = T.drop_toc(T.clean_pages(pages), starts=(r"^We,? the [Pp]eople",))
    body = T.structure(lines, "en", art_word="Article")
    meta = {"title": "The Constitution of Kenya, 2010", "identifier": "Constitution of Kenya 2010", "type": "constitution",
            "jurisdiction": "ke", "language": "en", "date": "2010-08-27", "status": "in_force",
            "source": CONST["page"], "source_file": CONST["url"], "retrieved": RETRIEVED,
            "note": "National Council for Law Reporting edition as promulgated (2010); later amendments not incorporated."}
    T.write_md(os.path.join(REPO, "constitution", "constitution-of-kenya-2010.md"), meta, meta["title"], body)


def main():
    os.makedirs(RAW, exist_ok=True)
    do_constitution()
    seen = set()
    n = 0
    for href, title in sorted(act_links().items()):
        fn = hashlib.sha1(href.encode()).hexdigest()[:16] + ".pdf"
        pdf = os.path.join(RAW, "pdf", fn)
        if DL:
            T.fetch(href, pdf, delay=2, check_pdf=True)
        if not os.path.exists(pdf) or not T.pdf_ok(pdf):
            print("MISSING/BAD", href)
            continue
        h = hashlib.md5(open(pdf, "rb").read()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        pages, ocr = T.pdf_text(pdf, "eng", tmpdir=RAW, ocr=True)
        good = [p for p in pages if len(p.strip()) > 100]
        if len(good) < max(1, len(pages) * 0.5) or T.text_quality(" ".join(pages)) < 0.75:
            print("SKIP (no/garbled text layer)", href, len(pages), T.text_quality(" ".join(pages)))
            continue
        lines = T.clean_pages(pages)
        t = nice(guess_title([x for x in lines if x], href))
        num, year = number_year(lines, t)
        if year and not re.search(r"\d{4}", t):
            t = t + ", " + year
        body = T.structure(T.drop_toc(lines), "en")
        ident = "Act No. %s of %s" % (num, year) if num and year else None
        meta = {"title": t, "identifier": ident, "type": "act", "jurisdiction": "ke", "language": "en",
                "year": int(year) if year else None, "status": "unknown", "source": href, "retrieved": RETRIEVED,
                "note": "As enacted (Kenya Gazette Supplement print); not consolidated." + (" Text obtained by OCR (scanned PDF); may contain recognition errors." if ocr else "")}
        d = os.path.join(REPO, "acts", year or "undated")
        name = T.slug(t) + ".md"
        if os.path.exists(os.path.join(d, name)):
            name = T.slug(t) + "-" + h[:6] + ".md"
        T.write_md(os.path.join(d, name), meta, t, body)
        n += 1
        print("ok", year, t)
    print("acts", n)


if __name__ == "__main__":
    main()
