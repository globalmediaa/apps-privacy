#!/usr/bin/env python3
"""Identity tokens for the privacy pages live in tools/values.json.

  python3 tools/fill.py           replace {{VERI_SORUMLUSU}} {{ADRES}} {{EPOSTA}} {{VERBIS}} in every .html file
  python3 tools/fill.py --check   exit 1 if any {{...}} token is left in any .html file (also run after fill)

VERBIS may be empty: its paragraph (<p class="verbis">{{VERBIS}}</p>) is then removed.
The other three values must not be empty. Values are HTML-escaped when written.
"""
import html, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKEN = re.compile(r"\{\{[^{}]*\}\}")
REQUIRED = ("VERI_SORUMLUSU", "ADRES", "EPOSTA")
OPTIONAL = ("VERBIS",)

def pages():
    return sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)

def leftovers():
    bad = []
    for p in pages():
        for m in TOKEN.finditer(p.read_text(encoding="utf-8")):
            bad.append("%s: %s" % (p.relative_to(ROOT), m.group(0)))
    return sorted(set(bad))

def fill():
    values = json.loads((ROOT / "tools" / "values.json").read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED if not str(values.get(k, "")).strip()]
    if missing:
        sys.exit("values.json: empty required value(s): " + ", ".join(missing))
    for p in pages():
        text = p.read_text(encoding="utf-8")
        if "{{" not in text:
            continue
        if not str(values.get("VERBIS", "")).strip():
            text = re.sub(r'\s*<p class="verbis">\s*\{\{VERBIS\}\}\s*</p>', "", text)
        for k in REQUIRED + OPTIONAL:
            text = text.replace("{{%s}}" % k, html.escape(str(values.get(k, "")), quote=False))
        p.write_text(text, encoding="utf-8")

if __name__ == "__main__":
    if "--check" not in sys.argv:
        fill()
    bad = leftovers()
    if bad:
        print("Unfilled tokens:\n  " + "\n  ".join(bad))
        sys.exit(1)
    print("OK: no {{...}} tokens in %d html files" % len(pages()))
