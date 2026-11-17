#!/usr/bin/env python3
"""Check this static site using only the Python standard library.

Run from any directory: python3 scripts/check_site.py
External HTTP requests are deliberately excluded: publisher and profile sites
can reject automated requests even when their links work for readers.
"""

from collections import defaultdict
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
VOID_TAGS = set("area base br col embed hr img input link meta param source track wbr".split())
ARXIV_ID = r"\d{4}\.\d{4,5}"


def arxiv_id(url):
    parsed = urlsplit(url)
    if parsed.hostname not in {"arxiv.org", "www.arxiv.org"}:
        return None
    match = re.fullmatch(rf"/(?:abs|pdf)/({ARXIV_ID})(?:v\d+)?(?:\.pdf)?/?", parsed.path)
    return match.group(1) if match else None


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids = defaultdict(list)
        self.metadata = defaultdict(list)
        self.canonicals = []
        self.references = []
        self.aria_references = []
        self.papers = defaultdict(set)
        self.json_blocks = []
        self.title = []
        self.stack = []
        self.feed(path.read_text(encoding="utf-8"))
        self.close()

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        line = self.getpos()[0]
        paper = self.stack[-1][1] if self.stack else None
        if "pub" in (attrs.get("class") or "").split():
            paper = attrs.get("id") or f"paper at line {line}"
            self.papers[paper]  # Include entries with missing links.
        if attrs.get("id"):
            self.ids[attrs["id"]].append(line)
        for name in ("href", "src"):
            if attrs.get(name):
                self.references.append((attrs[name], line))
        for name in ("aria-labelledby", "aria-describedby", "aria-controls"):
            for target in (attrs.get(name) or "").split():
                self.aria_references.append((target, line))
        if tag == "meta":
            key = attrs.get("name") or attrs.get("property")
            if key:
                self.metadata[key].append(attrs.get("content") or "")
        if tag == "link" and "canonical" in (attrs.get("rel") or "").split():
            self.canonicals.append(attrs.get("href") or "")
        if tag == "a" and paper:
            identifier = arxiv_id(attrs.get("href") or "")
            if identifier:
                self.papers[paper].add(identifier)
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.json_blocks.append([line, ""])
        if tag not in VOID_TAGS:
            self.stack.append((tag, paper, attrs.get("type")))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.stack and self.stack[-1][0] == "title":
            self.title.append(data)
        if self.stack and self.stack[-1][0] == "script" and self.stack[-1][2] == "application/ld+json":
            self.json_blocks[-1][1] += data


def check():
    errors = []
    page = Page(ROOT / "index.html")

    def require(condition, message):
        if not condition:
            errors.append(message)

    require(bool("".join(page.title).strip()), "index.html: missing page title")
    require(len(page.canonicals) == 1, "index.html: expected one canonical URL")
    canonical = page.canonicals[0] if page.canonicals else ""
    origin = urlsplit(canonical)
    require(origin.scheme == "https" and bool(origin.netloc) and origin.path == "/",
            "index.html: canonical must be the HTTPS site root ending in /")
    for key in ("description", "og:title", "og:description", "og:type", "og:url", "og:image"):
        values = page.metadata[key]
        require(len(values) == 1 and bool(values[0].strip()), f"index.html: missing or duplicated {key}")
    require(page.metadata["og:url"] == [canonical], "index.html: og:url differs from canonical")
    for key in ("og:image", "twitter:image"):
        page.references.extend((url, 0) for url in page.metadata[key])

    for identifier, lines in page.ids.items():
        require(len(lines) == 1, f"index.html:{lines}: duplicate id {identifier!r}")
    for target, line in page.aria_references:
        require(target in page.ids, f"index.html:{line}: missing ARIA target {target!r}")

    parsed_pages = {ROOT / "index.html": page}

    def local_reference(url, source):
        supplied = urlsplit(url)
        parsed = urlsplit(urljoin(canonical, url))
        if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != origin.netloc.lower():
            return
        relative = unquote(parsed.path).lstrip("/")
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT):
            errors.append(f"{source}: local URL escapes site root: {url}")
            return
        if parsed.path.endswith("/"):
            path /= "index.html"
        # A GitHub Pages hostname can also serve projects from other repos.
        # Absolute URLs to those projects are external to this checkout.
        if supplied.netloc and not path.is_file() and parsed.path != origin.path:
            return
        require(path.is_file(), f"{source}: missing local file for {url}")
        if path.is_file() and path.suffix.lower() in {".html", ".htm"} and parsed.fragment:
            if path not in parsed_pages:
                parsed_pages[path] = Page(path)
            require(unquote(parsed.fragment) in parsed_pages[path].ids,
                    f"{source}: missing fragment target in {url}")

    for url, line in page.references:
        local_reference(url, f"index.html:{line}")

    require(bool(page.json_blocks), "index.html: missing JSON-LD")
    for line, content in page.json_blocks:
        try:
            value = json.loads(content)
        except json.JSONDecodeError as exc:
            errors.append(f"index.html:{line}: invalid JSON-LD: {exc.msg}")
            continue
        require(isinstance(value, (dict, list)), f"index.html:{line}: JSON-LD must be an object or array")
        if isinstance(value, dict) and value.get("@type") == "Person":
            require(value.get("url") == canonical, f"index.html:{line}: Person URL differs from canonical")

    bibliography = (ROOT / "publications.bib").read_text(encoding="utf-8")
    bib_ids = re.findall(rf"\beprint\s*=\s*[{{\"]\s*({ARXIV_ID})(?:v\d+)?\s*[}}\"]", bibliography)
    require(len(bib_ids) == len(set(bib_ids)), "publications.bib: duplicate arXiv identifiers")
    site_ids = []
    for paper, identifiers in page.papers.items():
        require(len(identifiers) == 1, f"index.html: {paper} should link to one consistent arXiv identifier")
        site_ids.extend(identifiers)
    require(bool(site_ids), "index.html: no arXiv paper entries found")
    require(len(site_ids) == len(set(site_ids)), "index.html: multiple paper entries use the same arXiv identifier")
    require(set(site_ids) == set(bib_ids),
            "Papers/BibTeX mismatch: missing from BibTeX " + str(sorted(set(site_ids) - set(bib_ids)))
            + "; missing from page " + str(sorted(set(bib_ids) - set(site_ids))))
    for entry in re.split(r"(?m)(?=^@\w+\s*\{)", bibliography):
        identifier = re.search(rf"\beprint\s*=\s*[{{\"]\s*({ARXIV_ID})", entry)
        if identifier:
            url = re.search(r"\burl\s*=\s*[{\"]([^}\"]+)[}\"]", entry)
            require(url is not None and arxiv_id(url.group(1).strip()) == identifier.group(1),
                    f"publications.bib: URL does not match eprint {identifier.group(1)}")

    sitemap_url = urljoin(canonical, "sitemap.xml")
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    listed_sitemaps = re.findall(r"^Sitemap:\s*(\S+)\s*$", robots, flags=re.MULTILINE | re.IGNORECASE)
    require(sitemap_url in listed_sitemaps, "robots.txt: missing canonical sitemap URL")
    try:
        sitemap = ET.parse(ROOT / "sitemap.xml")
        locations = [node.text or "" for node in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        require(canonical in locations, "sitemap.xml: missing canonical homepage")
        for url in locations:
            require(urlsplit(url).netloc.lower() == origin.netloc.lower(),
                    f"sitemap.xml: URL belongs to another site: {url}")
            local_reference(url, "sitemap.xml")
    except ET.ParseError as exc:
        errors.append(f"sitemap.xml: invalid XML: {exc}")

    if errors:
        print("Site checks failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Site checks passed: {len(page.ids)} IDs, {len(page.references)} references, "
          f"{len(page.papers)} papers matched with BibTeX, and valid site metadata.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(check())
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Site checks failed: {exc}", file=sys.stderr)
        sys.exit(1)
