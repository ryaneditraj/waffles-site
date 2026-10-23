#!/usr/bin/env python3
"""Checks for the Potato Fan Club static site.

The script is the CI job. It looks for required files, the potato copy,
unsafe DOM writes, secret-shaped strings, broken local links, and the
SEO files a public page is expected to ship.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "index.html",
    "stats.html",
    "assets/site.css",
    "assets/home.js",
    "assets/stats.js",
    "assets/favicon.svg",
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    ".gitignore",
    ".env.example",
    "robots.txt",
    "sitemap.xml",
    "llms.txt",
    "_headers",
    ".github/workflows/ci.yml",
    ".github/dependabot.yml",
    ".github/CODEOWNERS",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    "docs/screenshots/home.png",
    "docs/screenshots/stats.png",
    "docs/screenshots/membership-text.png",
    "docs/screenshots/demo.gif",
]

PHRASES = {
    "index.html": [
        "Welcome to the greatest potato website ever made.",
        "CLICK POTATO",
        "Give Fact",
        "Go To Secret Potato Stats Page",
        "What is the Potato Fan Club?",
        "Does joining the club save or share my name?",
    ],
    "stats.html": [
        "Potato Stats Center",
        "Scientists definitely did not help make these statistics.",
        "Rate Me",
        "Change Color",
        "→ Back Home",
    ],
    "assets/home.js": [
        'funnyName + " is now officially a potato fan."',
        "A potato never pays taxes.",
        ".textContent",
    ],
    "assets/stats.js": [
        '"Supreme Potato Wizard"',
        '"that is a short thing"',
        '"wow long thing"',
        ".textContent",
        'addEventListener("keyup", checkStuff)',
    ],
}

CODE_FILES = [
    "index.html",
    "stats.html",
    "assets/site.css",
    "assets/home.js",
    "assets/stats.js",
    "assets/favicon.svg",
]

UNSAFE_SNIPPETS = [
    "innerHTML",
    "outerHTML",
    "insertAdjacentHTML",
    "document.write",
    "eval(",
    "new Function",
    "javascript:",
]

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ASIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk_live_[A-Za-z0-9]{10,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
]

INLINE_HANDLER = re.compile(r"\son[a-z]+\s*=", re.IGNORECASE)
ROOT_ABSOLUTE = re.compile(r"""(?:href|src)\s*=\s*["']/(?!/)""")
JSON_LD = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>',
    re.DOTALL,
)
META_TAG = re.compile(r"<meta\b([^>]*)>", re.IGNORECASE)
LINK_TAG = re.compile(r"<link\b([^>]*)>", re.IGNORECASE)
LOCAL_REF = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)

REQUIRED_META = [
    "description",
    "og:title",
    "og:description",
    "og:url",
    "og:image",
    "twitter:card",
    "twitter:title",
    "twitter:image",
]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def csp_hash(script_text: str) -> str:
    digest = hashlib.sha256(script_text.encode("utf-8")).digest()
    return "sha256-" + base64.b64encode(digest).decode("ascii")


def tag_attrs(tag_html: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for match in re.finditer(
        r"""([:\w-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')""",
        tag_html,
    ):
        value = match.group(2) if match.group(2) is not None else match.group(3)
        found[match.group(1).lower()] = value
    return found


def collect_meta(html: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for raw in META_TAG.findall(html):
        attrs = tag_attrs(raw)
        key = (attrs.get("name") or attrs.get("property") or "").lower()
        if key:
            found[key] = attrs.get("content", "")
        if attrs.get("http-equiv", "").lower() == "content-security-policy":
            found["content-security-policy"] = attrs.get("content", "")
    return found


def canonical_href(html: str) -> str | None:
    for raw in LINK_TAG.findall(html):
        attrs = tag_attrs(raw)
        if attrs.get("rel", "").lower() == "canonical":
            return attrs.get("href")
    return None


def main() -> int:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing file: {relative}")
            continue
        if path.stat().st_size == 0:
            errors.append(f"empty file: {relative}")

    for relative, size in (
        ("docs/screenshots/home.png", 20_000),
        ("docs/screenshots/stats.png", 20_000),
        ("docs/screenshots/membership-text.png", 20_000),
        ("docs/screenshots/demo.gif", 20_000),
    ):
        path = ROOT / relative
        if path.is_file() and path.stat().st_size < size:
            errors.append(f"{relative} looks too small to be a real capture")

    for relative, phrases in PHRASES.items():
        path = ROOT / relative
        if not path.is_file():
            continue
        text = read(relative)
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{relative} is missing {phrase!r}")

    for relative in CODE_FILES:
        path = ROOT / relative
        if not path.is_file():
            continue
        text = read(relative)
        for snippet in UNSAFE_SNIPPETS:
            if snippet in text:
                errors.append(f"{relative} contains unsafe snippet {snippet!r}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"{relative} matches secret pattern {pattern.pattern}")
        if relative.endswith(".html") and INLINE_HANDLER.search(text):
            errors.append(f"{relative} has an inline event handler")
        if relative.endswith(".html") and ROOT_ABSOLUTE.search(text):
            errors.append(
                f"{relative} uses a root-absolute link, which breaks GitHub project pages"
            )

    gitignore = read(".gitignore") if (ROOT / ".gitignore").is_file() else ""
    if ".env" not in gitignore or "!.env.example" not in gitignore:
        errors.append(".gitignore must ignore .env and keep .env.example")

    license_text = read("LICENSE") if (ROOT / "LICENSE").is_file() else ""
    if "MIT License" not in license_text or "Ryan Editraj" not in license_text:
        errors.append("LICENSE should be the MIT license for Ryan Editraj")

    robots = read("robots.txt") if (ROOT / "robots.txt").is_file() else ""
    if "Sitemap: https://waffleshackclub.netlify.app/sitemap.xml" not in robots:
        errors.append("robots.txt is missing the sitemap URL")

    headers = read("_headers") if (ROOT / "_headers").is_file() else ""
    for needle in (
        "X-Content-Type-Options: nosniff",
        "Referrer-Policy: strict-origin-when-cross-origin",
        "X-Frame-Options: DENY",
        "frame-ancestors 'none'",
    ):
        if needle not in headers:
            errors.append(f"_headers is missing {needle}")

    if (ROOT / "sitemap.xml").is_file():
        sitemap = read("sitemap.xml")
        for loc in (
            "https://waffleshackclub.netlify.app/",
            "https://waffleshackclub.netlify.app/stats.html",
        ):
            if loc not in sitemap:
                errors.append(f"sitemap.xml is missing {loc}")

    if (ROOT / "llms.txt").is_file():
        llms = read("llms.txt")
        for needle in (
            "Potato Fan Club",
            "https://github.com/ryaneditraj",
            "https://instagram.com/ryaneditraj",
            "stats.html",
        ):
            if needle not in llms:
                errors.append(f"llms.txt is missing {needle}")

    readme = read("README.md") if (ROOT / "README.md").is_file() else ""
    for needle in (
        "docs/screenshots/home.png",
        "docs/screenshots/stats.png",
        "docs/screenshots/demo.gif",
        "https://github.com/ryaneditraj",
        "https://instagram.com/ryaneditraj",
        "## FAQ",
        "## Roadmap",
        "MIT",
    ):
        if needle not in readme:
            errors.append(f"README.md is missing {needle}")

    for page in ("index.html", "stats.html"):
        if not (ROOT / page).is_file():
            continue
        html = read(page)
        meta = collect_meta(html)
        for key in REQUIRED_META:
            if not meta.get(key):
                errors.append(f"{page} is missing meta {key}")
        if meta.get("twitter:card") != "summary_large_image":
            errors.append(f"{page} twitter:card should be summary_large_image")
        if not canonical_href(html):
            errors.append(f"{page} is missing a canonical link")
        policy = meta.get("content-security-policy", "")
        if "unsafe-inline" in policy or "default-src 'self'" not in policy:
            errors.append(f"{page} Content-Security-Policy is missing or too loose")
        blocks = JSON_LD.findall(html)
        if not blocks:
            errors.append(f"{page} is missing JSON-LD")
            continue
        for block in blocks:
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"{page} JSON-LD does not parse: {exc}")
            token = "'" + csp_hash(block) + "'"
            if token not in policy:
                errors.append(
                    f"{page} CSP is missing the JSON-LD hash {csp_hash(block)}"
                )
        if 'referrerpolicy="no-referrer"' not in html:
            errors.append(f"{page} images should set referrerpolicy=\"no-referrer\"")
        if "<img" in html and " alt=" not in html:
            errors.append(f"{page} images need alt text")

        for match in LOCAL_REF.finditer(html):
            url = match.group(1)
            if url.startswith(("http://", "https://", "data:", "mailto:")):
                continue
            if url.startswith("#"):
                continue
            target = (ROOT / page).parent / url.split("#", 1)[0]
            if not target.is_file():
                errors.append(f"{page} links to missing file {url}")

    if (ROOT / "index.html").is_file():
        html = read("index.html")
        section = re.search(
            r'<section class="potatobox" id="faq">(.*?)</section>',
            html,
            re.DOTALL,
        )
        blocks = JSON_LD.findall(html)
        if section and blocks:
            visible = [
                (re.sub(r"\s+", " ", question).strip(), re.sub(r"\s+", " ", answer).strip())
                for question, answer in re.findall(
                    r"<h3>(.*?)</h3>\s*<p>(.*?)</p>",
                    section.group(1),
                    re.DOTALL,
                )
            ]
            data = json.loads(blocks[0])
            faq = next(
                node for node in data["@graph"] if node.get("@type") == "FAQPage"
            )
            structured = [
                (
                    item["name"],
                    re.sub(r"\s+", " ", item["acceptedAnswer"]["text"]).strip(),
                )
                for item in faq["mainEntity"]
            ]
            if visible != structured:
                errors.append("FAQ JSON-LD does not match the questions on the home page")

    if errors:
        print("site check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("site check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
