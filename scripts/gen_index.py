#!/usr/bin/env python3
"""
Generate a minimal index.html for each spec subdirectory under docs/.

Usage:
    python scripts/gen_index.py

Writes docs/req/<prefix>/index.html and docs/reg/<prefix>/index.html
from the corresponding .ttl files.
"""

import html
import pathlib
import rdflib
from rdflib.namespace import RDF, RDFS, SKOS, OWL

DCTERMS = rdflib.Namespace("http://purl.org/dc/terms/")
SBOM    = rdflib.Namespace("https://w3id.org/sbom/")
XSD     = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")

ROOT = pathlib.Path(__file__).parent.parent / "docs"

CSS = """
body{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1.5rem;color:#222;line-height:1.6}
h1{font-size:1.4rem;border-bottom:2px solid #ddd;padding-bottom:.3rem}
p.meta{color:#555;font-size:.9rem;margin-top:-.4rem}
h2{font-size:1rem;margin-top:1.8rem;color:#444}
a{color:#0969da}
table{border-collapse:collapse;width:100%;font-size:.88rem}
th,td{text-align:left;padding:.35rem .6rem;border:1px solid #ddd;vertical-align:top}
th{background:#f6f8fa}
code{background:#f6f8fa;padding:.1rem .3rem;border-radius:3px;font-size:.85em}
.tag{display:inline-block;background:#e8f0fe;color:#1a56db;border-radius:3px;
     padding:.05rem .4rem;font-size:.8em;white-space:nowrap}
footer{margin-top:2.5rem;font-size:.82rem;color:#666;border-top:1px solid #ddd;padding-top:.8rem}
""".strip()


def first(g, s, p, lang="en"):
    """Return the first literal value for (s, p), preferring the given language."""
    vals = list(g.objects(s, p))
    if not vals:
        return ""
    for v in vals:
        if hasattr(v, "language") and v.language == lang:
            return str(v)
    return str(vals[0])


def provision_label(g, pt_iri):
    """Return the prefLabel of a provision-type concept."""
    if pt_iri is None:
        return ""
    label = first(g, pt_iri, SKOS.prefLabel)
    return label or str(pt_iri).split("/")[-1]


def concept_sort_key(g, c):
    """Sort key: notation string if present, else local name."""
    notations = list(g.objects(c, SKOS.notation))
    if notations:
        return (0, str(sorted(notations)[0]))
    local = str(c).split("/")[-1]
    return (1, local)


def build_html(ttl_path: pathlib.Path) -> str:
    g = rdflib.Graph()
    g.parse(str(ttl_path), format="turtle")

    # --- Scheme metadata ---
    schemes = list(g.subjects(RDF.type, SKOS.ConceptScheme))
    scheme  = schemes[0] if schemes else None

    # Title: prefer dcterms:title on the ontology declaration, then scheme prefLabel
    ontologies = list(g.subjects(RDF.type, OWL.Ontology))
    ont = ontologies[0] if ontologies else None

    title = ""
    if ont:
        title = first(g, ont, DCTERMS.title)
    if not title and scheme:
        title = first(g, scheme, SKOS.prefLabel)
    if not title:
        title = ttl_path.stem.upper()

    description = ""
    if ont:
        description = first(g, ont, DCTERMS.description)
    if not description and scheme:
        description = first(g, scheme, DCTERMS.description)

    version = ""
    if ont:
        version = first(g, ont, OWL.versionInfo)

    namespace = str(ont) if ont else str(scheme) if scheme else ""
    ttl_filename = ttl_path.name
    # Relative link depth: index.html is in same dir as the ttl
    ttl_rel = ttl_filename
    root_rel = "../../"   # e.g. docs/req/ntia/ -> docs/

    # --- Concepts ---
    concepts = list(g.subjects(RDF.type, SKOS.Concept))
    concepts.sort(key=lambda c: concept_sort_key(g, c))

    rows = []
    for c in concepts:
        iri       = str(c)
        local     = iri.split("/")[-1]
        label     = first(g, c, SKOS.prefLabel)
        defn      = first(g, c, SKOS.definition)
        scope     = first(g, c, SKOS.scopeNote)
        notations = sorted(str(n) for n in g.objects(c, SKOS.notation))
        pt        = next(g.objects(c, SBOM.provisionType), None)
        pt_label  = provision_label(g, pt)
        broader   = next(g.objects(c, SKOS.broader), None)
        broader_local = str(broader).split("/")[-1] if broader else ""

        notation_html = " ".join(
            f'<code>{html.escape(n)}</code>' for n in notations
        )
        defn_html = html.escape(defn) if defn else ""
        if scope:
            defn_html += f' <span style="color:#555">({html.escape(scope)})</span>'

        rows.append(
            f"<tr>"
            f"<td><code>{html.escape(local)}</code></td>"
            f"<td>{html.escape(label)}</td>"
            f"<td>{notation_html}</td>"
            f"<td>{'<span class=tag>' + html.escape(pt_label) + '</span>' if pt_label else ''}</td>"
            f"<td>{defn_html}</td>"
            f"</tr>"
        )

    table_html = (
        "<table>\n"
        "<tr><th>ID</th><th>Label</th><th>Notation</th><th>Type</th><th>Definition</th></tr>\n"
        + "\n".join(rows)
        + "\n</table>"
    ) if rows else "<p><em>No concepts found.</em></p>"

    # --- Assemble ---
    desc_html = f"<p>{html.escape(description)}</p>\n" if description else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <style>{CSS}</style>
</head>
<body>

<p class="meta"><a href="{root_rel}">SBOM Bridging Ontology for Mapping</a></p>
<h1>{html.escape(title)}</h1>
<p class="meta">Namespace: <code><a href="{html.escape(namespace)}">{html.escape(namespace)}</a></code>
  &nbsp;|&nbsp; <a href="{ttl_rel}">{ttl_rel}</a>{"&nbsp;|&nbsp; v" + html.escape(version) if version else ""}</p>

{desc_html}
<h2>Concepts ({len(concepts)})</h2>
{table_html}

<footer>
  <a href="https://orcid.org/0000-0002-9698-1899">Arthit Suriyawongkul</a> &nbsp;|&nbsp;
  <a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0-1.0</a> &nbsp;|&nbsp;
  <a href="https://github.com/openregtech/sbom">github.com/openregtech/sbom</a> &nbsp;|&nbsp;
  <a href="{root_rel}">SBOM Bridging Ontology for Mapping</a>
</footer>

</body>
</html>
"""


def main():
    # Find all .ttl files one level below docs/req/ and docs/reg/
    patterns = [
        ROOT / "req" / "*" / "*.ttl",
        ROOT / "reg" / "*" / "*.ttl",
    ]
    found = []
    for pat in patterns:
        found.extend(sorted(ROOT.glob(str(pat.relative_to(ROOT)))))

    for ttl_path in found:
        out = ttl_path.parent / "index.html"
        content = build_html(ttl_path)
        out.write_text(content, encoding="utf-8")
        print(f"  wrote {out.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
