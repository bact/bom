# SBOM Bridging Ontology for Mapping

A SKOS bridge vocabulary and SSSOM crosswalk files for
Software Bill of Materials (SBOM) minimum-element standards.

## What this is

1) Different organisations (BSI, CISA, G7, NTIA) publish their own lists of
   minimum elements that an SBOM shall or should contain.
2) Different SBOM data exchange (CycloneDX, SPDX) and serialisation formats have
   their own field names.
3) This project provides a neutral bridge vocabulary that connects (1) and (2).

**`docs/sbom.ttl`** -- a small [SKOS] ontology that assigns stable,
persistent IRIs to each minimum-element concept. It has two layers:

- a *bridge concept scheme* (`sbom:bridge`) that abstracts across all source standards
- per-standard concept schemes whose concepts link to bridge concepts
  via `skos:exactMatch` / `skos:closeMatch`

**`docs/mapping/*.sssom.tsv`** -- [SSSOM] mapping files that record how each
minimum-element concept maps to a field in a target format, with the shared
bridge concept cited in the `see_also` column.

[SKOS]: https://www.w3.org/TR/skos-reference/
[SSSOM]: https://mapping-commons.github.io/sssom/dev/

## Covered standards

| Prefix | Standard | Layer |
| ------ | -------- | ----- |
| `ntia:` | NTIA SBOM Minimum Elements (2021) | Information requirement |
| `fsct:` | CISA Framing Software Component Transparency, 3rd Ed. (2024) | Information requirement |
| `cisa:` | CISA SBOM Minimum Elements (2025) | Information requirement |
| `g7ai:` | G7 SBOM for AI — Minimum Elements (2026) | Information requirement |
| `bsi:` | BSI TR-03183-2: Cyber Resilience Requirements Part 2: SBOM (2025) | Information requirement |
| `mof:` | Model Openness Framework (LF AI & Data, 2024) | Tiered assessment |
| `euaiact:` | EU AI Act Annex VIII/IX registration items (Regulation (EU) 2024/1689) | Regulatory |

## Completed mappings

SSSOM files follow the `{source}-to-{target}.sssom.tsv` naming convention. `semic` is the umbrella label for SEMIC-maintained vocabularies (DCAT-AP, MLDCAT-AP) and related terms (Schema.org, DPV).

| File | Source | Target | Rows |
| ---- | ------ | ------ | ---- |
| `docs/mapping/sbom-to-spdx31.sssom.tsv` | Bridge ontology | SPDX 3.1-dev | 51 |
| `docs/mapping/g7ai-to-spdx31.sssom.tsv` | G7 SBOM for AI | SPDX 3.1-dev | 52 |
| `docs/mapping/ntia-to-spdx31.sssom.tsv` | NTIA | SPDX 3.1-dev | 8 |
| `docs/mapping/bsi-to-spdx31.sssom.tsv` | BSI TR-03183-2 | SPDX 3.1-dev | 25 |
| `docs/mapping/euaiact-anx8-a-to-semic.sssom.tsv` | EU AI Act Anx.VIII Sec.A | SEMIC vocabularies | 35 |
| `docs/mapping/euaiact-anx8-b-to-semic.sssom.tsv` | EU AI Act Anx.VIII Sec.B | SEMIC vocabularies | 21 |
| `docs/mapping/euaiact-anx8-c-to-semic.sssom.tsv` | EU AI Act Anx.VIII Sec.C | SEMIC vocabularies | 8 |
| `docs/mapping/euaiact-anx9-to-semic.sssom.tsv` | EU AI Act Anx.IX | SEMIC vocabularies | 10 |
| `docs/mapping/ntia-to-semic.sssom.tsv` | NTIA | SEMIC vocabularies | 14 |
| `docs/mapping/g7ai-to-semic.sssom.tsv` | G7 SBOM for AI | SEMIC vocabularies | 94 |

## Namespace

Base IRI: `https://w3id.org/sbom/`  

## Repository layout

```text
docs/           Published vocabulary and mappings (GitHub Pages source)
refs/           Source PDFs for the standards listed above
DESIGN.md       Architecture, design decisions, and next-steps checklist
AGENTS.md       Guide for AI agents continuing work in this repo
```

## License

[CC0-1.0](LICENSE)
