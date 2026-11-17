# Behrooz Moosavi — Academic Website

Live site: [behroozmoosavi.github.io](https://behroozmoosavi.github.io/)

A personal academic website focused on the calculus of variations and nonlinear
partial differential equations. The page presents current research, eight papers
(mathematics first, followed by econometrics and statistics), education, teaching,
and related resources. The normalized p-Laplacian paper and its companion Lean
formalization site are linked together in the mathematics papers section.

## Files

| Path | Purpose |
| --- | --- |
| `index.html` | Website content, embedded CSS, and a small navigation script |
| `100827158.jpeg` | Profile photograph and browser icon |
| `publications.bib` | BibTeX entries for the eight listed papers |
| `cv/CV.tex` | LaTeX source for the CV |
| `cv.pdf` | Generated CV served by the website |
| `robots.txt`, `sitemap.xml` | Search-engine discovery |
| `scripts/check_site.py` | Local website checks |
| `.github/workflows/` | Website checks and CV build automation |

The page loads Source Serif 4 from Google Fonts, with local fallback fonts. Paper
PDFs, lecture notes, academic profiles, and the Lean project are linked to their
external sources.

## Update the website

Edit `index.html` directly. Update `publications.bib` whenever paper titles,
authors, links, or publication details change, so the citation download agrees
with the page. Review the corresponding `sitemap.xml` modification date when
publishing updated content.

When updating the CV, edit `cv/CV.tex`. The **Build CV** workflow compiles it and
commits the generated `cv.pdf` at the repository root. A manual replacement of
`cv.pdf` can be overwritten by the next source build, so keep the LaTeX source
authoritative. Website-only edits do not require changing the CV.

## Preview and check locally

From the repository root, run:

```sh
python3 scripts/check_site.py
python3 -m http.server 8000
```

Open [localhost:8000](http://localhost:8000/) to preview the page. Check both wide
and narrow windows, navigation, expanded paper descriptions, and the CV and
BibTeX downloads. Stop the preview server with `Ctrl+C`. The local checks do not
replace reviewing linked papers or verifying external publication metadata.

## Deployment and CV builds

GitHub Pages publishes the website from `main`. The repository's Actions tab
shows the deployment and check results.

**Build CV** runs when a pushed branch changes LaTeX files under `cv/` and can also
be started manually from Actions. It compiles and updates the PDF on that branch; only runs
on `main` request a Pages rebuild. For an Overleaf or other working-branch update,
review and merge the source changes into `main` to publish the revised CV.
