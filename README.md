# Kenya (KE) — legislation as Markdown

Part of [LawCodex](https://github.com/LawCodex): the legislation of every country as plain Markdown in git.

Legislation of the Republic of Kenya, in **English**, from official Parliament of Kenya sources:

* the **Constitution of Kenya, 2010** — National Council for Law Reporting edition as promulgated, from the
  Parliament of Kenya Library institutional repository;
* the **Acts of Parliament published by the National Assembly** on parliament.go.ke ("House Business → Acts"),
  as enacted (Kenya Gazette Supplement prints), plus the Parliamentary Service Act (2019) page.

Retrieved 2026-10-13.

<!-- COUNTS -->
| Directory | Files |
|---|---|
| `acts/` | 27 |
| `constitution/` | 1 |
| **Total** | **28** |
<!-- /COUNTS -->

## Structure

```
constitution/constitution-of-kenya-2010.md   Constitution of Kenya, 2010
acts/<year>/<slug>.md                        Acts of Parliament (year = year in the Act's short title)
```

File names are slugs of the short title (taken from the "may be cited as" section where possible). Front matter:
`identifier` is the Act number (`Act No. N of YYYY`) when printed on the Act, `status` is `unknown` (the source does
not say whether an Act has since been amended or repealed), `note` flags texts obtained by OCR.

Headings: `PART`/`CHAPTER`/`SCHEDULE` become headings; sections (articles in the Constitution) are headings
`Section N` / `Article N`. The printed "Arrangement of sections/articles" (table of contents) is dropped. Marginal
notes of the printed Acts are kept where the PDF text layer places them, sometimes inside the section text.

## Sources

| Source | URL | Used for |
|---|---|---|
| Parliament of Kenya — National Assembly, Acts | https://www.parliament.go.ke/the-national-assembly/house-business/acts | Acts |
| Parliament of Kenya — Parliamentary Service Act | https://www.parliament.go.ke/parliamentary-service-act | Parliamentary Service Act |
| Parliament of Kenya Library repository (DSpace) | https://libraryir.parliament.go.ke/handle/123456789/1090 | Constitution of Kenya, 2010 |

## Not covered / known gaps

**This is far from the full body of Kenyan law** (status: partial).

* The consolidated **Laws of Kenya** (revised edition, Caps) are published by the National Council for Law
  Reporting (Kenya Law, kenyalaw.org / new.kenyalaw.org). That site runs on the AfricanLII/Laws.Africa "Peachjam"
  platform, whose terms forbid scraping/bulk download and which blocks AI crawlers; it was deliberately **not**
  used (nor archived copies of it). Republishing the Laws of Kenya here would need the consent of Kenya Law.
* The National Assembly website exposes only ~30 Acts (mostly 2011–2013 devolution-era Acts plus a few 2025 Acts).
  The Parliament library repository (libraryir.parliament.go.ke) holds scattered Gazette supplements and Bills but
  no systematic Acts collection, so it was used only for the Constitution.
* The Kenya Law Reform Commission site (klrc.go.ke) serves a CAPTCHA/bot challenge and was not used. No official
  Government Printer / Kenya Gazette site was reachable.
* Constitution: the 2010 text as promulgated; there have been no formal amendments to the text adopted since,
  but no consolidation was checked.
* No consolidation: Acts are as enacted; amendment Acts are separate files. County legislation and subsidiary
  legislation (Legal Notices) are not included.
* 4 Acts (2025) were published only as scanned PDFs; their text was produced by OCR (tesseract) and is marked in
  the `note` field (the OCR text includes some noise from stamps/seals).

## Copyright

Kenyan Acts and the Constitution are official public texts of the Republic of Kenya published by Parliament for
public information; the sources used state no terms restricting reuse. The Markdown conversion is provided as is, for information; the authoritative texts are the
printed Kenya Gazette supplements.

## Regenerate

```
python3 -m pip install -r scripts/requirements.txt   # plus poppler (pdftotext) and tesseract
python3 scripts/ke_fetch.py        # downloads to ../_raw/ke and writes constitution/ and acts/
python3 scripts/ke_readme.py       # refresh the counts table
```
