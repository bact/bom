# AGENTS.md -- Instructions for AI Agents

This file tells an AI agent how to orient quickly and work effectively in this repository. Read `DESIGN.md` next for full technical context.

---

## What this repo is

A vocabulary and crosswalk project for SBOM (Bill of Materials) minimum-element standards. It produces:

1. **`docs/bom.ttl`** -- a SKOS bridge ontology (v0.1.0) with stable IRIs for minimum-element concepts, provision type vocabulary, and type classes
2. **`docs/req/<prefix>/<prefix>.ttl`** -- per-standard files for information requirement specs (NTIA, CISA FSCT (3rd Ed.), CISA 2025, G7 AI, BSI TR, MOF)
3. **`docs/reg/<prefix>/<prefix>.ttl`** -- per-regulation files for legally binding instruments (EU AI Act; future: EU CRA)
4. **`docs/mapping/*.sssom.tsv`** -- SSSOM crosswalk files mapping a source standard to a target format (SPDX 3, CycloneDX, SEMIC)

Read `DESIGN.md` for architecture decisions, IRI scheme, namespace layout, and next-steps checklist.

---

## Repository layout

```text
bom/
├── DESIGN.md          <- full technical design (read this first for a new session)
├── AGENTS.md          <- this file
├── README.md
├── docs/
│   ├── bom.ttl                         <- bridge ontology; source of truth for bridge concepts
│   ├── index.html                      <- main landing page
│   ├── spdx-semic.xlsx                 <- working spreadsheet (non-canonical)
│   ├── releases/                       <- versioned W3C ReSpec specifications
│   │   └── 0.1.0/
│   │       ├── bom.ttl                 <- frozen v0.1.0 ontology
│   │       └── index.html              <- v0.1.0 ReSpec document
│   ├── req/                            <- bom:InfoRequirementSpec files
│   │   ├── ntia/ (ntia.ttl, index.html)
│   │   ├── fsct/ (fsct.ttl, index.html)
│   │   ├── cisa/ (cisa.ttl, index.html)
│   │   ├── g7ai/ (g7ai.ttl, index.html)
│   │   ├── bsi/ (bsi.ttl, index.html)
│   │   └── mof/ (mof.ttl, index.html)
│   ├── reg/                            <- bom:RegulatorySpec files
│   │   └── euaiact/
│   │       ├── euaiact.ttl             <- aggregate (owl:imports all sub-files)
│   │       ├── euaiact-art49.ttl       <- Art.49 eligibility flowchart (Q1-Q5)
│   │       ├── euaiact-anx8-a.ttl      <- Annex VIII Sec.A, Art.49(1) provider, high-risk
│   │       ├── euaiact-anx8-b.ttl      <- Annex VIII Sec.B, Art.49(2) provider, not-high-risk
│   │       ├── euaiact-anx8-c.ttl      <- Annex VIII Sec.C, Art.49(3) deployer
│   │       ├── euaiact-anx9.ttl        <- Annex IX, Art.60 real-world testing
│   │       └── index.html              <- EU AI Act spec page
│   └── mapping/                        <- SSSOM files: {source}-to-{target}.sssom.tsv
│       ├── bom-to-spdx31.sssom.tsv
│       ├── g7ai-to-spdx31.sssom.tsv
│       ├── ntia-to-spdx31.sssom.tsv
│       ├── bsi-to-spdx31.sssom.tsv
│       ├── euaiact-anx8-a-to-semic.sssom.tsv
│       ├── euaiact-anx8-b-to-semic.sssom.tsv
│       ├── euaiact-anx8-c-to-semic.sssom.tsv
│       ├── euaiact-anx9-to-semic.sssom.tsv
│       ├── ntia-to-semic.sssom.tsv
│       └── g7ai-to-semic.sssom.tsv
└── refs/              <- source PDFs for the standards (read-only reference)
```

---

## Key files to read before making changes

| File | Why |
|------|-----|
| `DESIGN.md` | Architecture, IRI scheme, all design decisions |
| `docs/bom.ttl` | Bridge ontology -- bridge concepts, provision vocab, type classes |
| `docs/req/g7ai/g7ai.ttl` | Most complex per-standard file (7 categories + 50 leaves) |
| `docs/mapping/g7ai-to-spdx31.sssom.tsv` | Canonical SSSOM template and most complete mapping (52 rows) |
| `docs/mapping/ntia-to-spdx31.sssom.tsv` | Reference implementation for object_qualifier column (9-column format) |
| `docs/reg/euaiact/euaiact-anx8-a.ttl` | Reference for regulatory spec pattern (bom:RegulatorySpec, ELI links) |

---

## Conventions to follow

### Turtle files

- **Encoding:** ASCII / Latin-1 only. No Unicode box-drawing, en dashes, or non-Latin characters.
- **Bridge concepts in `bom.ttl`:** always in `bom:bridge`; always have `skos:broader` pointing to one of the 6 top categories.
- **IRI naming convention for bridge concepts:**
  - Top categories: `bom:bom-{category}` (e.g. `bom:bom-document`, `bom:bom-component`)
  - Document leaves: `bom:doc-{name}` (e.g. `bom:doc-author`, `bom:doc-timestamp`)
  - Component leaves: `bom:component-{name}` (e.g. `bom:component-name`)
  - AI leaves: `bom:ai-{name}`; dataset: `bom:dataset-{name}`; infra: `bom:infra-{name}`; security: `bom:security-{name}`
- **IRI naming convention for source specs:**
  - Information requirement specs: `https://w3id.org/bom/req/<prefix>/`
  - Regulatory specs: `https://w3id.org/bom/reg/<prefix>/`
  - Tiered assessment frameworks: `https://w3id.org/bom/req/<prefix>/` (same namespace as content requirement specs)
- **Source concepts** in their standard's file (`req/ntia/ntia.ttl`, etc.); link to bridge via `skos:exactMatch` or `skos:closeMatch`.
- **Provision type assertions:** belong in per-standard files, not in `bom.ttl`. Use `bom:provisionType` with one of: `bom:Requirement`, `bom:ConditionalRequirement`, `bom:Recommendation`, `bom:Permission`, `bom:PossibilityAndCapability`, `bom:ExternalConstraint`.
- **Type class declarations:**
  - Information requirement specs: `<prefix>:scheme a skos:ConceptScheme, bom:InfoRequirementSpec .`
  - Regulatory specs: `<prefix>:scheme a skos:ConceptScheme, bom:RegulatorySpec .`
  - Provision type for regulatory concepts: always `bom:ExternalConstraint`
  - Value constraints (MOF-style): `<prefix>:concept bom:valueConstraint <prefix>:allowed-values-collection .`
- **SARIF notations:** use `^^bom:SarifRuleId` datatype; pattern `BOM-[SPEC]-[CAT]-[NNN]`. The checker generates this as `BOM-{spec.id.upper()}-{category.code}-{rule.number:03d}`. See `ntia_conformance_checker/rules/` for canonical YAML definitions.
- **Do not add source-specific prefixes to `bom.ttl`** -- each per-standard file manages its own prefix.
- **Validate** after every edit (see commands below).

### SSSOM (`.sssom.tsv`)

- **Columns (exactly 9, tab-separated):** `subject_id`, `subject_label`, `predicate_id`, `object_id`, `object_label`, `mapping_justification`, `see_also`, `comment`, `object_qualifier`
- **`object_qualifier`:** the OWL class in the target ontology that owns the mapped property (Option B for SPDX 3 property-on-class precision). Empty for mappings to top-level classes. Example: `spdx3-core:CreationInfo` for `spdx3-core:createdBy`. Declared in header with `extension_slot` and `extension_slot_uri`.
- **`mapping_justification`:** always `semapv:ManualMappingCuration`
- **`see_also`:** bridge concept CURIE, e.g. `bom:doc-author`
- **Predicates:** `skos:exactMatch`, `skos:closeMatch`, `skos:broadMatch`, `skos:narrowMatch`
- **Header:** YAML comment block; `mapping_set_id` must match `https://w3id.org/bom/mapping/<filename-without-extension>`
- **CURIE prefix for SPDX 3:** use `spdx3-core:` and `spdx3-sw:` (not `spdx31-core:`) -- target is SPDX 3.x

### SSSOM filename convention

`{source-namespace}-to-{target-namespace}.sssom.tsv`. Use ELI abbreviations for euaiact sections (`anx8-a`, `anx9`, etc.). Use `semic` as umbrella label for SEMIC-maintained vocabularies (DCAT-AP, MLDCAT-AP) plus Schema.org and DPV used as complementary terms.

### One-hop mapping

Source concept → bridge concept → exchange format field. All current files use this pattern. Cross-standard alignment (e.g. EU AI Act overlaps NTIA) belongs in SSSOM via the shared bridge concept, not as OWL property assertions in the TTL.

---

## How to add a new source standard

### Information requirement spec (`req/`)

1. Create `docs/req/<prefix>/<prefix>.ttl`:

   ```turtle
   @prefix <prefix>: <https://w3id.org/bom/req/<prefix>/> .
   @prefix bom: <https://w3id.org/bom/> .

   <https://w3id.org/bom/req/<prefix>/>  a owl:Ontology ; owl:imports <https://w3id.org/bom/> .

   <prefix>:scheme  a skos:ConceptScheme, bom:InfoRequirementSpec ;
       skos:prefLabel "..." ; ...

   <prefix>:concept-name
       a skos:Concept ;
       skos:inScheme <prefix>:scheme ;
       skos:exactMatch bom:<bridge-concept> .

   <prefix>:concept-name  bom:provisionType  bom:Requirement .
   ```

2. Add bridge concepts to `bom.ttl` only if needed (see DESIGN.md for IRI naming)
3. Create `docs/mapping/<prefix>-to-spdx31.sssom.tsv` (9-column format; see `ntia-to-spdx31` as reference)
4. Add a SARIF rule YAML to `ntia_conformance_checker/rules/<prefix>.yaml` on the `sarif-output` branch; verify generated IDs match the `^^bom:SarifRuleId` notations in the TTL

### Regulatory spec (`reg/`)

Same pattern but:

- Use `https://w3id.org/bom/reg/<prefix>/` as namespace; add ELI `rdfs:seeAlso` links
- Declare `a skos:ConceptScheme, bom:RegulatorySpec`
- Use `bom:provisionType bom:ExternalConstraint` for all provisions
- Split large regulations into per-provision files with an aggregate importer (see `euaiact/` as reference)
- Map to SEMIC vocabularies in `<prefix>-to-semic.sssom.tsv`; map to SPDX in `<prefix>-to-spdx31.sssom.tsv`

---

## Validation commands

```bash
# Validate all TTL files and count triples
python3 -c "
from rdflib import Graph; import glob
for path in sorted(glob.glob('docs/**/*.ttl', recursive=True)):
    g = Graph(); g.parse(path, format='turtle')
    print(f'{len(g):4d} triples: {path}')
"

# Check SSSOM column count (all data rows must have exactly 9 tab-separated fields)
python3 -c "
import glob
for path in sorted(glob.glob('docs/mapping/*.sssom.tsv')):
    lines = open(path).readlines()
    data = [l for l in lines if not l.startswith('#') and '\t' in l]
    bad = [(i, len(r.split('\t'))) for i, r in enumerate(data) if len(r.split('\t')) != 9]
    print(f'{path}: {len(data)-1} rows; bad={bad}')
"

# Check no old flat-namespace IRIs remain
grep -rn 'w3id.org/bom/ntia\|w3id.org/bom/g7ai\|w3id.org/bom/bsi\|w3id.org/bom/fsct\|w3id.org/bom/cisa' \
  docs/ --include='*.ttl' --include='*.tsv'
# (should return nothing)
```

---

## Pending work (as of 2026-06-17)

- [ ] SSSOM: EU AI Act Anx.VIII Sec.A/B/C + Anx.IX ↔ SPDX 3.1-dev (`euaiact-anx8-{a,b,c}-to-spdx31.sssom.tsv`, `euaiact-anx9-to-spdx31.sssom.tsv`)
- [ ] SSSOM: SPDX 3.1-dev ↔ SEMIC vocabularies (`spdx31-to-semic.sssom.tsv`) — format transformation leg
- [ ] SSSOM: FSCT ↔ SPDX 3.1-dev (`docs/mapping/fsct-to-spdx31.sssom.tsv`)
- [ ] SSSOM: CISA 2025 ↔ SPDX 3.1-dev (`docs/mapping/cisa-to-spdx31.sssom.tsv`)
- [ ] SSSOM: any standard ↔ CycloneDX
- [ ] Verify provision types for cisa against source doc (TODO annotation in cisa.ttl)
- [ ] Verify provision types for g7ai against source doc (TODO annotation in g7ai.ttl)
- [ ] Commit `euaiact.yaml` to `sarif-output` branch of ntia-conformance-checker and open PR
- [ ] GitHub Pages setup
- [ ] w3id.org registration PR

---

## Related repository

`ntia-conformance-checker` (sibling repo at `/Users/art/projects/ntia-conformance-checker/`) -- the upstream spdx/ntia-conformance-checker repo. The SARIF rule ID scheme (`BOM-[SPEC]-[CAT]-[NNN]`) is developed in the `sarif-output` branch of the fork at `https://github.com/bact/ntia-conformance-checker/tree/sarif-output`. Check `ntia_conformance_checker/rules/ntia.yaml` and `rules/fsct.yaml` in that branch for canonical rule IDs before assigning new notations.

The `sarif-output` branch (`bact/ntia-conformance-checker`) contains `rules/ntia.yaml`, `rules/fsct.yaml`, and `rules/euaiact.yaml` (32 rules across 4 categories: ANX8-A, ANX8-B, ANX8-C, ANX9). Generated rule IDs follow `BOM-{SPEC.upper()}-{CAT}-{NNN}`; the TTL `^^bom:SarifRuleId` notations must match exactly. This branch is not yet merged.

The `object_qualifier` SSSOM column may in future drive `probe` fields in checker YAML as an alternative to SHACL-based validation. Not yet formalised.
