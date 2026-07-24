# BOM Mapping — Design Document

> **Purpose:** Full context for continuing work in any future session. Read this before touching any file in the repo.

---

## 1. Ultimate Goal

Given any compliance document (an SPDX or CycloneDX file), determine automatically which information-requirement obligations it satisfies — whether from a minimum-element specification (CISA, MOF, G7) or from a regulation (EU AI Act, EU CRA).

This requires machine-readable, citable mappings between the "what must be present" layer and the "how it is encoded" layer — shared infrastructure that any compliance tool can consume rather than each tool maintaining its own private crosswalk.

---

## 2. Conceptual Model

The project operates across three distinct layers of document, connected by a bridge vocabulary and a compliance checking query direction.

### 2.1 Layer A — Information Requirement Specifications

Documents that **enumerate specific information elements** and state which ones are mandatory, conditional, or optional. Each information element is assigned a stable IRI by this project.

Examples: Model Openness Framework (MOF), BSI TR-03183-2, CISA FSCT (3rd Ed.).

Key characteristic: the document itself itemises the requirements explicitly. Assigning IRIs and mapping to the bridge is straightforward.

### 2.2 Layer B — Exchange Format Specifications

Technical standards that define **how to serialise compliance content**. These already provide stable IRIs or identifiers for every field.

Examples: SPDX 3.1 (`spdx3-core:`, `spdx3-sw:`, `spdx3-ai:`, …), CycloneDX 1.6.

Key characteristic: IRIs exist already. The mapping task is purely semantic (does this spec field carry the same meaning as that requirement element?).

### 2.3 Layer C — Regulatory and Framework Documents

Documents that define **obligations or assessment criteria** but do not itemise specific information fields in the same granular, enumerable way as Layer A. Before the bridge pattern can apply, an **itemisation step** is required.

Examples: EU AI Act (Art. 11 technical documentation, Annex VIII/IX registration), EU CRA, Model Openness Framework (MOF).

**Itemisation approaches — in priority order:**

1. **Own TTL** (preferred): Create a purpose-built concept scheme (e.g. `euaiact.ttl`) containing only the concepts relevant to information requirements. These are scoped by competency questions ("what information must an BOM record to satisfy this provision?") and carry provision types (`bom:provisionType`). They form the `subject_id` in SSSOM mapping files.

2. **Third-party vocabulary** (as supplement): If a well-maintained external vocabulary already itemises the regulation (e.g. DPV's `eu-aiact:` namespace), link to it via `skos:exactMatch` or `skos:closeMatch` **at the bridge layer** (Layer D), not as a replacement for the own TTL. Third-party vocabs are typically more comprehensive but less explicit about requirement levels and operational scope.

The own TTL is always the authoritative source for mapping. Third-party vocabulary alignment is carried on the bridge concepts in `bom.ttl`.

### 2.4 Layer D — Bridge Concepts (`bom.ttl`)

A neutral, stable vocabulary that abstracts across all Layer A and Layer C sources. Bridge concepts serve as the **pivot** between the "what" layer (A/C) and the "how" layer (B).

Two roles:

- **Pivot for mappings**: `see_also` in every SSSOM row cites the bridge concept shared by both the source requirement and the target format field.
- **Semantic alignment**: bridge concepts carry `skos:closeMatch` / `skos:relatedMatch` alignments to well-known ontologies (Dublin Core, DCAT-AP, MLDCAT-AP, W3C ML Schema, Schema.org, DPV, DPV AI, DPV EU AI Act). This allows tools that know DCAT to understand what `bom:bom-dataset` means without reading this spec.

### 2.5 External Vocabulary Alignments (Layer E)

Vocabularies that bridge concepts align *to*, but which are not sources or targets in the compliance mapping:

| Vocabulary | Prefix | Role |
|---|---|---|
| Dublin Core Terms | `dcterms:` | Core metadata terms (creator, identifier, license, …) |
| DCAT / DCAT-AP | `dcat:` | Dataset and distribution cataloguing |
| MLDCAT-AP 3.1.0 | `mldcatap:` | ML model cataloguing (EU, `http://data.europa.eu/it6/`) |
| W3C ML Schema | `mls:` | ML training and evaluation (`http://www.w3.org/ns/mls#`) |
| Schema.org | `schema:` | Broad web vocabulary gap-filler (`https://schema.org/`) |
| W3C DPV | `dpv:` | Data privacy vocabulary |
| DPV AI | `ai:` | AI technology concepts (`https://w3id.org/dpv/ai#`) |
| DPV EU AI Act | `eu-aiact:` | EU AI Act regulatory concepts (`https://w3id.org/dpv/legal/eu/aiact#`) |
| SEMIC CCCEV / CV | `cv:` | Criterion and Evidence vocabulary |

These alignments live in `bom.ttl` as SKOS match predicates on bridge concepts. They are **not** used in compliance mapping SSSOM files (those map Layer A/C → Layer B only).

---

## 3. Architecture: N+M Bridge Pattern

The bridge reduces **conceptual mapping work**, not file count.

Without a bridge, mapping N source standards to M target formats requires N×M independent crosswalks — each one authored from scratch with no shared vocabulary. With the bridge, every source maps *to* the bridge via `skos:exactMatch`/`closeMatch` assertions in its own TTL file, and every target format can be mapped *from* the bridge once:

```
Layer A / C concept  →  Layer D bridge concept  →  Layer B format field
(e.g. ntia:supplier)    (bom:component-supplier)   (spdx3-core:suppliedBy)
```

**The N+M pattern operates in two passes:**

**First pass — N+M, fully automatic.** Map each source concept to a bridge concept (in the source TTL via `skos:exactMatch`/`closeMatch`). Map each bridge concept to target format fields once (in a `bom-{target}.sssom.tsv` file). A transitive join over these two layers produces a working source → target SSSOM for every source standard automatically — usable immediately for conformance checking and gap discovery at bridge-level granularity.

**Refinement pass — optional, per source-target pair.** Where the bridge's abstraction introduces imprecision, a hand-authored SSSOM file refines the generated one:

- A `closeMatch` at the bridge level that should be `narrowMatch` for a specific source concept.
- A gap that only exists for one particular standard (e.g. BSI's `structured-property` has no SPDX 3.1 equivalent, even though the bridge concept `bom:component-structured-property` exists).
- A value-level constraint the bridge does not capture (e.g. BSI mandates SHA-512 specifically).
- Source-specific commentary and `object_qualifier` details.

The `docs/mapping/` files are refinement-pass artefacts — they replace the generated first-pass mapping with higher-precision, hand-curated rows. They are optional: the first pass is already usable. The refinement pass trades automation for accuracy.

What the bridge buys in both passes:

- **Immediate coverage.** Any source standard mapped to the bridge gets a working (if coarse) mapping to every target format that has a `bom-{target}.sssom.tsv` file — for free, with no additional SSSOM authoring.
- **Maintenance leverage.** When a target format renames a field, querying which bridge concepts map to that field immediately surfaces all affected source standards.
- **Compounding reuse.** Each new standard mapped to the bridge gains a shared anchor for cross-standard queries ("which standards require something like `bom:doc-author`?") without extra work.
- **Structured refinement.** The bridge pre-structures the semantic space so that hand-authored refinement files are faster to write and more consistent across authors.
- **Version management.** The bridge serves as a stable semantic anchor across successive versions of both source specs and target formats (see Section 3a).

For **Layer C (regulatory) sources**, there is an additional preprocessing step before the bridge pattern applies:

```
Regulation obligation  →  [Itemisation]  →  Own TTL concept  →  Bridge  →  Format field
(EU AI Act Art. 11)        (euaiact.ttl)     (euaiact:a6-data-and-logic)   →  …  →  …
```

Once itemised, a regulatory source follows exactly the same bridge pattern as a Layer A source.

The bridge concept IRI appears in the SSSOM `see_also` column, annotating why the source→target mapping holds: *"Concept A in Layer A/C is mapped to Concept B in Layer B because both are instances of abstract Concept C in Layer D."*

---

## 3a. Version Management

The bridge acts as a **semantic version registry** across successive versions of both source specs and target formats. Two distinct scenarios:

### Target format version update (e.g. SPDX 3.0 → SPDX 3.1)

Without the bridge, updating N source → SPDX 3.0 SSSOM files to SPDX 3.1 means touching all N files for every renamed or restructured field. With the bridge:

- Update `sbom-spdx31.sssom.tsv` (bridge → SPDX 3.1) once.
- The change propagates to all source standards via the first-pass transitive join automatically.
- Only hand-authored refinement-pass files that reference the changed field directly need manual attention.

A concrete example already in this project: SPDX 3.x removed `PackageFileName` (present in SPDX 2.x). This is why `bsi:component-filename` became a documented gap — the bridge concept `bom:component-filename` exists, but the bridge → SPDX 3 mapping has no direct field to point to.

### Source spec version update (e.g. CISA SBOM Minimum Elements 2025 draft → 2026 final)

Map both versions independently to the bridge (`cisa2025.ttl`, `cisa2026.ttl`). The diff at the bridge level reveals the semantic change precisely:

- Concepts that map to the **same bridge concept** across versions are **compatible** — the same SPDX field satisfies both versions, and existing SSSOM rows need no change.
- Concepts that **change their bridge mapping** between versions represent a semantic shift — the information requirement changed, not just the label.
- Concepts that **appear or disappear** between versions are new or removed requirements — only these need new or retired SSSOM rows.

The bridge → target SSSOM (`sbom-spdx31.sssom.tsv`) does not need to change at all unless genuinely new information element categories appear. This makes version transitions low-cost to track and easy to communicate: "CISA 2026 adds two new concepts that map to bridge concepts not covered by any existing SPDX 3.1 field — these are gaps requiring attention."

---

## 4. Compliance Checking: Bidirectional Use

The SSSOM files are authored **left-to-right** (requirement → exchange format), following how a spec author thinks. But compliance checking runs **right-to-left**:

> *"This SPDX file has `spdx3-core:suppliedBy` populated. Which NTIA requirements does that satisfy? Which BSI requirements? Which EU AI Act registration items?"*

Because SSSOM rows are bidirectional in principle (subject↔object), the same files support inverse queries. A compliance checker would:

1. For each field present in the compliance document, find all SSSOM rows where `object_id` matches that field.
2. The `subject_id` in those rows is the requirement concept that the field satisfies (partially — exactMatch = fully, closeMatch/narrowMatch = partially).
3. Cross-reference with `bom:provisionType` in the source TTL to know if that requirement was mandatory.
4. Report: mandatory requirements satisfied, mandatory requirements not satisfied (gaps), recommendations met.

**Important scope note:** The current mappings establish **structural presence** — whether a field *can* express the required information. Value-level constraints (e.g. BSI mandates SHA-512 specifically, not just any hash) are noted in SSSOM `comment` fields but not yet formally modelled. A future constraint layer will address this.

---

## 5. Iterative Improvement Loop

The mapping process is intentionally iterative, similar to a learning loop:

1. **Map** a new source standard to the bridge and then to a target format.
2. **Discover** gaps: bridge concepts that don't exist yet (new requirement in the source), SKOS mismatches (concepts that are only relatedMatch between source and target, indicating a semantic difference worth capturing), and format gaps (fields the target format simply cannot represent).
3. **Refine** the bridge: add new bridge concepts if needed; improve SKOS alignments to external vocabularies (Layer E) as the semantic gaps become clearer.
4. **Propagate**: updated bridge concepts automatically improve all existing mappings that reference them.
5. **Feed back**: format gaps (like BSI's `structured-property` in SPDX 3.1) become citable, documented issues to raise with SPDX and CycloneDX working groups.

The bridge vocabulary (`bom.ttl`) is the shared artefact that benefits from every new mapping pair added.

---

## 6. Why This Is Worth Doing

1. **The regulatory landscape is fragmenting fast.** EU AI Act, EU CRA, G7 AI commitments, US Executive Order 14028, and national requirements (BSI, ANSSI) all require SBOMs with overlapping but not identical field sets. Without shared infrastructure, every compliance tool maintains its own private N×M mapping — duplicated, unreviewed, and inconsistent.

2. **SBOM tooling currently checks format, not content compliance.** Existing validators tell you if an SPDX file is syntactically valid; they do not tell you if it satisfies NTIA. This project provides the data layer to build content-compliance checkers.

3. **Gap analysis is directly actionable.** When a mapping file documents that BSI's `structured-property` has no equivalent in SPDX 3.1-dev, that is a citable, specific input to the SPDX working group — not a vague complaint.

4. **Bridge reuse compounds.** Each new source standard mapped to the bridge immediately gains a shared anchor for cross-standard queries and a structured starting point for mapping to any target format. The per-source SSSOM files still need to be authored, but they are produced faster and more consistently because the bridge pre-structures the semantic space.

5. **Machine-readable and open.** SSSOM is a W3C-adjacent standard. The output files can power SPARQL queries, documentation generators, spreadsheet views, and compliance APIs without further transformation.

---

## 7. Document Categories (OWL Classes)

| Class | Meaning | Examples |
|---|---|---|
| `bom:InfoRequirementSpec` | Layer A — standard or guidance enumerating specific SBOM information elements with provision levels | NTIA, G7 AI, BSI TR-03183-2, CISA FSCT (3rd Ed.) |
| `bom:ExchangeFormatSpec` | Layer B — technical standard defining SBOM serialisation | SPDX 3.1, CycloneDX 1.6 |
| `bom:RegulatorySpec` | Layer C — legally binding instrument defining compliance-related obligations (subclass of `dpv:Regulation`) | EU AI Act, EU CRA |

Assessment frameworks (MOF) do not fit neatly into Layer A or C — MOF defines maturity levels whose *criteria* can overlap with SBOM minimum elements. MOF is treated as a separate `bom:InfoRequirementSpec` whose concepts are the individual criteria; mapping to the bridge links MOF criteria to the same concepts as NTIA/G7.

---

## 8. Source Standards Covered

| Prefix | Standard | Layer | Source File |
| - | - | - | - |
| `ntia:` | NTIA SBOM Minimum Elements (2021) | A | `docs/req/ntia/ntia.ttl` |
| `fsct:` | CISA Framing Software Component Transparency 3rd Ed. (2024) | A | `docs/req/fsct/fsct.ttl` |
| `cisa:` | CISA SBOM Minimum Elements (2025) | A | `docs/req/cisa/cisa.ttl` |
| `g7ai:` | G7 SBOM for AI — Minimum Elements (2026-05-12) | A | `docs/req/g7ai/g7ai.ttl` |
| `bsi:` | BSI TR-03183-2 v2.1.0 (2025-08-20) | A | `docs/req/bsi/bsi.ttl` |
| `mof:` | Model Openness Framework (LF AI & Data, 2024) | A* | `docs/req/mof/mof.ttl` |
| `euaiact:` | EU AI Act Annex VIII/IX registration items | C (itemised) | `docs/reg/euaiact/euaiact.ttl` (aggregate imports 5 sub-files) |

*MOF is classified A for practical mapping purposes; its maturity-level nature is noted in the TTL scopeNotes.

Reference PDFs are in `refs/`.

---

## 9. Mapping Files Completed

| File | Source | Target | Rows | Status |
|---|---|---|---|---|
**Naming convention:** `{source-namespace}-to-{target-namespace}.sssom.tsv`. Namespace names follow ELI abbreviations where applicable (`anx8`, `anx9`, `art49`). `semic` is used as the umbrella label for SEMIC-maintained vocabularies (DCAT-AP, MLDCAT-AP, etc.) plus closely related terms (Schema.org, DPV).

| File | Source | Target | Rows | Status |
|---|---|---|---|---|
| `bom-to-spdx31.sssom.tsv` | Bridge | SPDX 3.1-dev | 51 | Done — pivot file for first-pass auto-generation |
| `sbom-to-spdx30.sssom.tsv` | Bridge | SPDX 3.0.1 | ~50 | Planned — differs in: `infra-hardware` gap (no Hardware profile in 3.0.1), `doc-version` gap |
| `g7ai-to-spdx31.sssom.tsv` | G7 AI | SPDX 3.1-dev | 52 | Done |
| `ntia-to-spdx31.sssom.tsv` | NTIA | SPDX 3.1-dev | 8 | Done |
| `bsi-to-spdx31.sssom.tsv` | BSI TR-03183-2 | SPDX 3.1-dev | 25 | Done |
| `euaiact-anx8-a-to-semic.sssom.tsv` | EU AI Act Anx.VIII Sec.A — Art.49(1) provider, high-risk | SEMIC vocabularies | 35 | Done |
| `euaiact-anx8-b-to-semic.sssom.tsv` | EU AI Act Anx.VIII Sec.B — Art.49(2) provider, not-high-risk | SEMIC vocabularies | 21 | Done |
| `euaiact-anx8-c-to-semic.sssom.tsv` | EU AI Act Anx.VIII Sec.C — Art.49(3) deployer | SEMIC vocabularies | 8 | Done |
| `euaiact-anx9-to-semic.sssom.tsv` | EU AI Act Annex IX — Art.60 real-world testing | SEMIC vocabularies | 10 | Done |
| `ntia-to-semic.sssom.tsv` | NTIA | SEMIC vocabularies | 14 | Done |
| `g7ai-to-semic.sssom.tsv` | G7 AI | SEMIC vocabularies | 94 | Done |

Planned: FSCT↔SPDX, CISA 2025↔SPDX, BSI↔CycloneDX, G7 AI↔CycloneDX, NTIA↔CycloneDX.

---

## 10. Namespace / IRI Scheme

Base namespace: `https://w3id.org/bom/`

| IRI prefix | Contents |
|---|---|
| `https://w3id.org/bom/` | Bridge concepts + ontology declaration (`docs/bom.ttl`) |
| `https://w3id.org/bom/req/ntia/` | NTIA source scheme |
| `https://w3id.org/bom/req/fsct/` | FSCT (3rd Ed.) source scheme |
| `https://w3id.org/bom/req/cisa/` | CISA 2025 source scheme |
| `https://w3id.org/bom/req/g7ai/` | G7 AI source scheme |
| `https://w3id.org/bom/req/bsi/` | BSI TR-03183-2 source scheme |
| `https://w3id.org/bom/req/mof/` | MOF source scheme |
| `https://w3id.org/bom/reg/euaiact/` | EU AI Act itemised registration concepts |
| `https://w3id.org/bom/mapping/` | SSSOM mapping set files |

`req/` = information requirement specs (Layer A). `reg/` = regulatory documents (Layer C, itemised).

`https://w3id.org/bom` is **not yet registered** at w3id.org. A PR to [perma-id/w3id.org](https://github.com/perma-id/w3id.org) is needed once GitHub Pages is live.

---

## 11. Repository Structure

```text
bom/
├── DESIGN.md                          ← this file
├── AGENTS.md                          ← AI agent instructions
├── README.md
├── LICENSE
├── refs/                              ← source PDFs (not published)
│   ├── 2021-ntia-sbom-minimum-elements.pdf
│   ├── 2024-cisa-sbom-baseline-attributes.pdf
│   ├── 2025-bsi-sbom-content-requirements.pdf
│   ├── 2025-cisa-sbom-minimum-elements.pdf
│   ├── 2025-enia-sbom-analysis.pdf
│   └── 2026-g7-sbom-for-ai-minimum-elements.pdf
└── docs/                              ← GitHub Pages source
    ├── bom.ttl                        ← Layer D: bridge ontology (SKOS/OWL, Turtle)
    ├── index.html                     ← Main landing page
    ├── spdx-semic.xlsx                 ← working spreadsheet (non-canonical)
    ├── releases/                      ← versioned W3C ReSpec specifications
    │   └── 0.1.0/
    │       ├── bom.ttl                ← frozen v0.1.0 ontology
    │       └── index.html             <- v0.1.0 ReSpec document
    ├── req/                           ← Layer A: information requirement specs
    │   ├── ntia/ (ntia.ttl, index.html)
    │   ├── fsct/ (fsct.ttl, index.html)
    │   ├── cisa/ (cisa.ttl, index.html)
    │   ├── g7ai/ (g7ai.ttl, index.html)
    │   ├── bsi/ (bsi.ttl, index.html)
    │   └── mof/ (mof.ttl, index.html)
    ├── reg/                           ← Layer C: regulatory documents (itemised)
    │   └── euaiact/
    │       ├── euaiact.ttl                    ← aggregate (owl:imports all sub-files)
    │       ├── euaiact-art49.ttl              ← Q1-Q5 Art.49 eligibility flowchart
    │       ├── euaiact-anx8-a.ttl             ← Annex VIII Sec.A, Art.49(1) provider, high-risk
    │       ├── euaiact-anx8-b.ttl             ← Annex VIII Sec.B, Art.49(2) provider, not-high-risk
    │       ├── euaiact-anx8-c.ttl             ← Annex VIII Sec.C, Art.49(3) deployer
    │       ├── euaiact-anx9.ttl               ← Annex IX, Art.60 real-world testing
    │       └── index.html                     <- EU AI Act spec page
    └── mapping/                       ← SSSOM crosswalk files
        ├── g7ai-to-spdx31.sssom.tsv
        ├── ntia-to-spdx31.sssom.tsv
        ├── bsi-to-spdx31.sssom.tsv
        ├── bom-to-spdx31.sssom.tsv
        ├── euaiact-anx8-a-to-semic.sssom.tsv
        ├── euaiact-anx8-b-to-semic.sssom.tsv
        ├── euaiact-anx8-c-to-semic.sssom.tsv
        ├── euaiact-anx9-to-semic.sssom.tsv
        ├── ntia-to-semic.sssom.tsv
        └── g7ai-to-semic.sssom.tsv
```

---

## 12. Bridge Ontology — `docs/bom.ttl`

### 12.1 Prefixes

```turtle
@prefix skos:     <http://www.w3.org/2004/02/skos/core#> .
@prefix owl:      <http://www.w3.org/2002/07/owl#> .
@prefix rdfs:     <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dcterms:  <http://purl.org/dc/terms/> .
@prefix xsd:      <http://www.w3.org/2001/XMLSchema#> .
@prefix dpv:      <https://w3id.org/dpv#> .
@prefix cv:       <http://data.europa.eu/m8g/> .
@prefix dcat:     <http://www.w3.org/ns/dcat#> .
@prefix mls:      <http://www.w3.org/ns/mls#> .
@prefix schema:   <https://schema.org/> .
@prefix eu-aiact: <https://w3id.org/dpv/legal/eu/aiact#> .
@prefix ai:       <https://w3id.org/dpv/ai#> .
@prefix bom:     <https://w3id.org/bom/> .
```

Source-specific prefixes (`ntia:`, `g7ai:`, `euaiact:`, …) are **not** in `bom.ttl`; they live only in per-standard files.

### 12.2 Type Classes

```turtle
bom:InfoRequirementSpec   a owl:Class .   # Layer A
bom:ExchangeFormatSpec    a owl:Class .   # Layer B
bom:RegulatorySpec        a owl:Class ;   # Layer C
    rdfs:subClassOf dpv:Regulation .
```

### 12.3 Custom Datatype

```turtle
bom:SarifRuleId  a rdfs:Datatype .
```

Pattern: `BOM-[SPEC]-[CAT]-[NNN]`. Lowercasing yields a valid OSCAL catalog control-id. Used as the datatype for `skos:notation` on concepts that correspond to automated conformance checker rules.

### 12.4 Bridge Concept Scheme

**Top-level categories (7):**

| Category IRI | Label | Notes |
|---|---|---|
| `bom:bom-document` | Bill of Materials Document | Document-level metadata: authorship, format, lifecycle, tooling, relationships |
| `bom:bom-component` | Component | Generic to any component type (software, hardware, AI, data). **No** external vocab alignment — intentionally generic |
| `bom:bom-sw` | Software Component | Software-specific properties. `skos:closeMatch schema:SoftwareApplication` |
| `bom:bom-ai` | AI System and Model | AI/ML-specific. Aligns to `dcat:Dataset`, `mls:Model`, `ai:AISystem`, `ai:Model`, `schema:SoftwareApplication` |
| `bom:bom-dataset` | Dataset | `skos:exactMatch dcat:Dataset`, `skos:closeMatch schema:Dataset` |
| `bom:bom-infra` | Infrastructure | Software and hardware runtime environment |
| `bom:bom-security` | Security | Compliance, controls, vulnerabilities, performance metrics |

**IRI naming convention for leaf concepts:**

| Category | Pattern | Example |
|---|---|---|
| Document | `bom:doc-{name}` | `bom:doc-author` |
| Component (generic) | `bom:component-{name}` | `bom:component-hash` |
| Software | `bom:component-{name}` (same namespace) | `bom:component-filename` |
| AI/ML | `bom:ai-{name}` | `bom:ai-training-properties` |
| Dataset | `bom:dataset-{name}` | `bom:dataset-provenance` |
| Infrastructure | `bom:infra-{name}` | `bom:infra-hardware` |
| Security | `bom:security-{name}` / `bom:performance-{name}` / `bom:vulnerability-{name}` | `bom:security-compliance` |

### 12.5 Provision Type Vocabulary

**Property:** `bom:provisionType` — links a source concept to its normative strength.

**Six provision types** (aligned with ISO/IEC Directives Part 2 §7 and RFC 2119):

| Concept | ISO verbal form | RFC 2119 |
|---|---|---|
| `bom:Requirement` | shall | MUST |
| `bom:ConditionalRequirement` | shall [if condition] | MUST IF *(extension)* |
| `bom:Recommendation` | should | SHOULD |
| `bom:Permission` | may | MAY |
| `bom:PossibilityAndCapability` | can | *(none)* |
| `bom:ExternalConstraint` | must *(external)* | *(none)* |

Assertions live in per-standard files, not in `bom.ttl`. Example:

```turtle
bsi:component-hash-deployable  bom:provisionType  bom:Requirement .
bsi:doc-uri                   bom:provisionType  bom:ConditionalRequirement .
bsi:component-license-effective bom:provisionType bom:Permission .
```

### 12.6 Other Properties

```turtle
bom:satisfiedBy   # Links a regulatory provision to the InfoRequirementSpec that satisfies it
bom:valueConstraint  # Links a concept to a collection of allowed values (sub-property of cv:constraint)
```

---

## 13. Per-Standard Source Files

### 13.1 Structure (Layer A — `docs/req/*/`)

Each file imports `bom.ttl` and contains:

1. Ontology declaration with `owl:imports`
2. Concept scheme (`a skos:ConceptScheme, bom:InfoRequirementSpec`)
3. Concept definitions with bridge-concept alignments (`skos:exactMatch`, `skos:closeMatch`)
4. Provision type assertions

```turtle
ntia:supplier
    a skos:Concept ;
    skos:exactMatch bom:component-supplier ;
    ...

ntia:supplier  bom:provisionType  bom:Requirement .
```

### 13.2 Structure (Layer C — `docs/reg/*/`)

Same structure as Layer A, but:

- Concept scheme is `a skos:ConceptScheme, bom:RegulatorySpec`
- Concepts are derived from regulatory text by answering the competency question: *"What specific information must be present to satisfy this provision?"*
- Concepts may additionally carry `skos:exactMatch` or `skos:closeMatch` to third-party regulatory vocabularies (e.g. `eu-aiact:AuthorisedRepresentative` from DPV EU AI Act)

```turtle
euaiact:a3-authorised-rep
    a skos:Concept ;
    skos:closeMatch bom:component-supplier ;
    skos:exactMatch eu-aiact:AuthorisedRepresentative ;
    ...
```

### 13.3 Source File Statistics

| File | Layer | Concepts | Notes |
|---|---|---|---|
| `req/ntia/ntia.ttl` | A | 7 | 2 doc + 5 component |
| `req/fsct/fsct.ttl` | A | 13 | 5 doc + 8 component |
| `req/cisa/cisa.ttl` | A | ~12 | Similar to FSCT |
| `req/g7ai/g7ai.ttl` | A | 50 | Full G7 AI element set |
| `req/bsi/bsi.ttl` | A | 20 | 3 doc + 17 component; distinguishes distribution/original/effective licence |
| `req/mof/mof.ttl` | A* | ~20 | MOF Level 1–4 criteria |
| `reg/euaiact/euaiact.ttl` | C | — | Aggregate index only; owl:imports all 5 sub-files |
| `reg/euaiact/euaiact-classification.ttl` | C | 5 | Q1-Q5 eligibility flowchart (Art.49 path determination) |
| `reg/euaiact/euaiact-a.ttl` | C | 13 | Annex VIII Sec.A provider items (Art.49(1), high-risk) |
| `reg/euaiact/euaiact-b.ttl` | C | 9 | Annex VIII Sec.B provider items (Art.49(2), not-high-risk) |
| `reg/euaiact/euaiact-c.ttl` | C | 5 | Annex VIII Sec.C deployer items (Art.49(3)) |
| `reg/euaiact/euaiact-ix.ttl` | C | 5 | Annex IX real-world testing items (Art.60) |

---

## 14. SSSOM Mapping Files

### 14.1 File Naming

`docs/mapping/<source>-<target>.sssom.tsv`

Mapping set IRI: `https://w3id.org/bom/mapping/<source>-<target>`

### 14.2 Columns

| Column | Notes |
|---|---|
| `subject_id` | Source concept CURIE (e.g. `ntia:supplier`) |
| `subject_label` | Human-readable label |
| `predicate_id` | SKOS match predicate |
| `object_id` | Target format field CURIE (e.g. `spdx3-core:suppliedBy`) |
| `object_label` | Field name |
| `mapping_justification` | Always `semapv:ManualMappingCuration` |
| `see_also` | Bridge concept CURIE (Layer D pivot) |
| `comment` | Rationale; GAP notes |
| `object_qualifier` | (optional) SPDX class context for the target field |

### 14.3 SKOS Predicates Used

| Predicate | Meaning |
|---|---|
| `skos:exactMatch` | Semantically equivalent; direct one-to-one correspondence |
| `skos:closeMatch` | Same intent, minor difference (e.g. scope, cardinality, value constraint) |
| `skos:relatedMatch` | Overlapping but meaningfully different; partial fit |
| `skos:broadMatch` | Target concept is broader than the source requirement |
| `skos:narrowMatch` | No dedicated target field; mapped to a container or indirect path |

### 14.4 Key Design Decisions

**`mapping_justification` vs `see_also`**
Per SSSOM spec, `mapping_justification` is single-valued and must be a `semapv:` CURIE. The bridge concept IRI goes in `see_also`. This means `see_also` is how the N+M pivot is recorded.

**GAP documentation**
When no adequate target field exists, still include a row with the closest available predicate (typically `skos:narrowMatch` or `skos:relatedMatch`) and prefix the `comment` with `GAP:`. This makes gaps discoverable in queries rather than silently absent.

**One SSSOM file per source-target pair**
Keeps each crosswalk self-contained with its own `curie_map`. Multiple rows per source concept are allowed (e.g. when a concept maps to two different target fields that cover complementary aspects).

**Multiple target vocabularies in one file**
A single SSSOM file may reference multiple target vocabularies (e.g. `euaiact-a-mldcatap.sssom.tsv` maps to MLDCAT-AP, Schema.org, and DPV EU AI Act). The `curie_map` header declares all namespaces used.

**TTL vs SSSOM — where alignment lives**
Source-spec → bridge alignment is expressed as SKOS triples in the per-standard TTL (`skos:exactMatch`, `skos:closeMatch` etc.). There is no `ntia-to-bom.sssom.tsv` or equivalent. SSSOM is used only for the heterogeneous cross-format leg (concepts → exchange format fields), where `mapping_justification`, `object_qualifier`, `comment`, and `see_also` add precision that plain SKOS triples do not carry well. The TTL-side alignment is homogeneous (same vocabulary family, same predicate semantics) and needs no additional columns.

**Where mapping rationale lives**
Rationale for *why two concepts from different standards are considered equivalent* belongs on the bridge concept in `bom.ttl` as `skos:scopeNote`. This is the one place that sees all source standards simultaneously, so cross-standard reasoning is visible regardless of which per-spec SSSOM file a reader consults. Rationale for *why a bridge concept maps to a specific exchange-format field* belongs in the SSSOM `comment` column of the relevant mapping file.

**ELI IRI and eur-lex HTML anchor on regulatory concepts**
Regulatory concepts in `reg/` TTL files carry two `rdfs:seeAlso` references to their legal source:

1. **ELI IRI** (primary) — the stable, dereferenceable ELI canonical identifier for the provision, at article or annex granularity. Example: `<http://data.europa.eu/eli/reg/2024/1689/anx_8/oj>`.
2. **eur-lex HTML anchor** (secondary) — a jump-link into the eur-lex HTML rendering for human navigation. Example: `<https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689#anx_VIII>`.

ELI IRIs are stable and machine-readable; HTML anchors provide direct human access. Both are placed on individual `skos:Concept` instances (not only on the ontology header), so any concept is self-documenting about its legal source. Neither is a SKOS match predicate — `rdfs:seeAlso` is used as both are document locations, not concepts. Item-level precision within an annex is carried by `skos:notation` (e.g. `"A.4"`).

Where the match between our concept and the legal source is not exact (e.g. a bridge concept in `bom.ttl` that covers part of an annex provision), `skos:broadMatch` or `skos:closeMatch` may be used instead of `rdfs:seeAlso`.

---

## 15. Gap Taxonomy

Gaps discovered during mapping fall into four categories (recorded in the `comment` field):

| Gap type | Description | Example |
|---|---|---|
| **Missing field** | Target format has no concept for this requirement at all | BSI `structured-property` in SPDX 3.1-dev |
| **Indirect path** | Field exists but requires an indirect multi-hop structure | BSI `component-filename` in SPDX 3.1-dev: needs File element + hasDistributionArtifact relationship |
| **Vocabulary mismatch** | Field exists but value vocabulary differs semantically | BSI `executable-property` (binary flag) vs SPDX `primaryPurpose` (purpose taxonomy) |
| **Semantic gap** | Field exists but carries a different perspective | BSI `effective-licence` (licensee's actual usage) vs SPDX `hasConcludedLicense` (analyst's determination) |

Gaps in Layer B (exchange format) feed into working group input for SPDX and CycloneDX evolution.

---

## 16. Adding New Content

### 16.1 New Layer A Standard

1. Create `docs/req/<prefix>/<prefix>.ttl` with prefix block, ontology declaration, concept scheme, concept definitions with bridge alignments, and provision assertions.
2. If existing bridge concepts cover all requirements: no change to `bom.ttl`.
3. If a new requirement is not covered: add a new bridge leaf concept to `bom.ttl` (see §16.3).
4. Create `docs/mapping/<prefix>-spdx3.sssom.tsv` (and/or `<prefix>-cdx.sssom.tsv`).

### 16.2 New Layer C Regulatory Document

1. Read the regulation; identify provisions that create specific compliance information obligations.
2. Check whether a third-party vocabulary (DPV, etc.) already itemises those concepts at sufficient granularity.
3. Create `docs/reg/<prefix>/<prefix>.ttl`. Concepts should answer: *"What specific information field must be present to satisfy this provision?"*
4. In the concept definitions, link to any matching third-party IRIs via `skos:exactMatch`/`skos:closeMatch`.
5. Add provision type assertions (`bom:provisionType`).
6. Follow the same SSSOM mapping steps as for Layer A.

### 16.3 New Bridge Concept

Only add if a source standard requires something not covered by any existing leaf concept.

1. Choose the appropriate top category.
2. Assign a new IRI per the naming convention (§12.4).
3. Add `skos:inScheme bom:bridge`, `skos:broader bom:<parent>`, `skos:prefLabel`, `skos:definition`.
4. Add external vocab alignments (SKOS predicates) if applicable.
5. Add `skos:notation "SBOM-..."^^bom:SarifRuleId` if the concept corresponds to a conformance checker rule.

### 16.4 New Top Category

Rare. Only if a new family of concepts doesn't fit any of the 7 existing categories (bom-document, bom-component, bom-sw, bom-ai, bom-dataset, bom-infra, bom-security). Add to `skos:hasTopConcept` in `bom:bridge`.

---

## 17. Current Status

| Item | Status |
|---|---|
| Bridge ontology `bom.ttl` with 7 categories + ~45 leaf concepts | Done |
| External vocab alignments: dcterms, dcat, mls, schema, dpv, ai:, eu-aiact: | Done |
| Type classes and provision vocabulary | Done |
| Source TTLs: NTIA, FSCT (3rd Ed.), CISA 2025, G7 AI, BSI TR-03183-2 | Done |
| Regulatory TTLs: EU AI Act split into 5 files (`euaiact-art49.ttl`, `euaiact-anx8-{a,b,c}.ttl`, `euaiact-anx9.ttl`) with ELI links | Done |
| SSSOM `{source}-to-{target}` naming convention applied across all files | Done |
| `bom-to-spdx31.sssom.tsv` — bridge ↔ SPDX 3.1-dev | Done |
| `g7ai-to-spdx31.sssom.tsv` — G7 AI ↔ SPDX 3.1-dev | Done |
| `ntia-to-spdx31.sssom.tsv` — NTIA ↔ SPDX 3.1-dev | Done |
| `bsi-to-spdx31.sssom.tsv` — BSI TR-03183-2 ↔ SPDX 3.1-dev | Done |
| `euaiact-anx8-a-to-semic.sssom.tsv` — EU AI Act Anx.VIII Sec.A ↔ SEMIC vocabularies | Done |
| `euaiact-anx8-b-to-semic.sssom.tsv` — EU AI Act Anx.VIII Sec.B ↔ SEMIC vocabularies | Done |
| `euaiact-anx8-c-to-semic.sssom.tsv` — EU AI Act Anx.VIII Sec.C ↔ SEMIC vocabularies | Done |
| `euaiact-anx9-to-semic.sssom.tsv` — EU AI Act Anx.IX ↔ SEMIC vocabularies | Done |
| `ntia-to-semic.sssom.tsv` — NTIA ↔ SEMIC vocabularies | Done |
| `g7ai-to-semic.sssom.tsv` — G7 AI ↔ SEMIC vocabularies | Done |
| `euaiact.yaml` in ntia-conformance-checker (`sarif-output` branch) with 4 categories, 32 rules | Done |
| SARIF rule IDs updated to `BOM-EUAIACT-ANX8-A/B/C-NNN` and `BOM-EUAIACT-ANX9-NNN` | Done |
| `euaiact-anx8-a-to-spdx31.sssom.tsv` — EU AI Act Anx.VIII Sec.A ↔ SPDX 3.1-dev | Not started |
| `euaiact-anx8-b-to-spdx31.sssom.tsv` | Not started |
| `euaiact-anx8-c-to-spdx31.sssom.tsv` | Not started |
| `euaiact-anx9-to-spdx31.sssom.tsv` | Not started |
| `spdx31-to-semic.sssom.tsv` — SPDX 3.1-dev ↔ SEMIC vocabularies (format transformation leg) | Not started |
| `fsct-to-spdx31.sssom.tsv` | Not started |
| `cisa-to-spdx31.sssom.tsv` | Not started |
| Any ↔ CycloneDX | Not started |
| EU Cyber Resilience Act (CRA) regulatory TTL (`reg/eucra/eucra.ttl`) | Not started |
| GitHub Pages setup | Not started |
| w3id.org registration | Not started |
| Value-constraint layer (beyond structural presence) | Future |
| `tools/generate_yaml_spec.py` to auto-generate checker YAML from TTL + SSSOM | Future |

---

## 18. Key Decisions Log

| Decision | Rationale |
|---|---|
| SKOS (not OWL) for bridge concepts | SKOS is lighter, better suited to concept mapping; OWL reasoning not needed at this stage |
| Source schemes in per-standard files (not bom.ttl) | Separation of concerns; each standard's vocabulary is independently versioned |
| `req/` vs `reg/` directory split | Distinguishes information requirement specs (Layer A) from itemised regulatory documents (Layer C) |
| Own TTL always as source; third-party vocab alignment at bridge level only | Own TTLs are scoped by competency questions and carry provision types. Third-party vocabs (DPV, etc.) are more comprehensive but less operationally scoped. Clean separation prevents conflation of roles. |
| `bom:bom-component` carries no external vocab alignments | bom-component is intentionally generic (covers SW, HW, AI, data). Alignments live only on narrower concepts (bom-sw, bom-ai, bom-dataset). |
| GAP rows always included in SSSOM | Gaps should be findable by query, not silent absences. Comment prefix `GAP:` enables filtering. |
| `mapping_justification: semapv:ManualMappingCuration` always | SSSOM spec compliance; semapv vocabulary required |
| Bridge concept IRI in SSSOM `see_also` (not `mapping_justification`) | `mapping_justification` is single-valued and must be a semapv term; see_also carries the pivot concept |
| `bom:ConditionalRequirement` extends ISO's six provision types | BSI TR-03183-2 uses a conditional SHALL tier not present in ISO/IEC Directives; extension is BOM-scoped |
| Compliance checking is right-to-left; files are authored left-to-right | The SSSOM format supports both directions. Compliance tools invert the mapping at query time. |
| `bom:SarifRuleId` custom datatype for notations | Enables tooling to recognise SARIF rule IDs; lowercasing yields OSCAL control IDs |
| ISO/IEC Directives Part 2 §7 as primary alignment for provision types | Most complete and precise set of provision types; RFC 2119 keywords added as altLabels |
| `skos:notation "SBOM-..."^^bom:SarifRuleId` on source concepts (not bridge) | One rule per information element requirement. The source concept owns the stable rule ID; the bridge is a shared pivot, not a per-standard rule catalogue. |
| MOF tiers as a single `mof.ttl` with `bom:maturityLevel` (not three separate specs) | MOF tiers are cumulative (III ⊇ II ⊇ I). Splitting into three specs would duplicate ~28 concept definitions across tiers and require three SSSOM files. The checker's `SpecMaturity` + `maturity:` mechanism was designed for exactly this pattern. |
| SSSOM filename convention: `{source-ns}-to-{target-ns}.sssom.tsv` | Dot (`.`) rejected — ambiguous with `.sssom.tsv` extension. Double-dash (`--`) rejected — POSIX flag conflict. Single hyphen `-to-` is unambiguous and readable. |
| EU AI Act TTL split by ELI provision: `euaiact-art49.ttl`, `euaiact-anx8-{a,b,c}.ttl`, `euaiact-anx9.ttl`; `euaiact.ttl` is aggregate importer | Each file has its own ontology IRI and ELI `rdfs:seeAlso` links. Flat file was unwieldy at 280+ triples. Naming follows ELI abbreviation conventions (`anx_8/oj`, `art_49/oj`). |
| SEMIC as umbrella label in SSSOM filenames (e.g. `g7ai-to-semic`) | Primary targets are SEMIC-maintained vocabs (DCAT-AP, MLDCAT-AP). Schema.org and DPV are included as complementary terms for gaps. Using `semic` avoids an unwieldy multi-vocab label in filenames. |
| `euaiact.yaml` in checker uses one spec (`id: euaiact`) with categories `ANX8-A/B/C`, `ANX9` | Avoids redundant segment in rule IDs (a per-provision spec.id would produce `BOM-EUAIACT-ANX8-A-ANX8-A-001`). The TTL split and YAML split are independent concerns. |
| `bom:satisfiedBy` removed | Was intended to link a regulatory provision to an InfoRequirementSpec, but cross-standard alignment belongs in SSSOM via shared bridge concepts. No usages existed. |
| No `{spec}-to-bom.sssom.tsv` files | Source-spec → bridge alignment is expressed directly as SKOS triples in the per-standard TTL. SSSOM is reserved for heterogeneous cross-format legs where additional columns (justification, qualifier, comment) add value not available in plain SKOS. |
| ELI IRI (primary) + eur-lex HTML anchor (secondary) on regulatory concepts | ELI IRIs (`data.europa.eu/eli/…`) are stable and machine-readable; eur-lex HTML anchors (`eur-lex.europa.eu/…#anx_VIII`) provide direct human navigation. Both placed as `rdfs:seeAlso` on individual concepts, not only on ontology headers. HTML anchors are at article/annex granularity — item-level precision within an annex is carried by `skos:notation`. |
| EU CRA as next regulatory spec | BSI TR-03183-2 explicitly implements CRA SBOM obligations — the BSI req/ TTL and CRA reg/ TTL will be cross-linked to make this provenance visible. CRA SBOM requirements overlap significantly with NTIA and other Layer A specs. |
| Cross-standard mapping rationale in `bom.ttl` `skos:scopeNote`, not in SSSOM `comment` | The bridge concept is the single vantage point that sees all source standards. Rationale placed there (e.g. why two standards' terms for the same concept use different labels) is visible from every downstream SSSOM file via the `see_also` pivot. Per-target rationale (why a bridge concept maps to a specific exchange-format field) belongs in the SSSOM `comment`. |

---

## 19. Conformance Checker Integration

This section describes how the mapping ontology drives the future version of `ntia-conformance-checker` (and conceptually any standards-agnostic BOM / compliance conformance checker).

### Existing architecture

The checker (`ntia_conformance_checker`) already has a clean rule engine:

- **`rules/<id>.yaml`** — declarative spec file; defines categories, maturity levels, and rules.
- **`spec.py`** — frozen dataclasses: `Spec`, `SpecRule`, `SpecCategory`, `SpecMaturity`.
- **`spec_loader.py`** — loads YAML → `Spec`.
- **`probes/`** — pluggable presence checks (`require_component_attribute`, `require_document_attribute`).
- **`rule_based_checker.py`** — generic runner: given a `Spec`, runs all active probes against a compliance document.
- **`report_sarif.py`** — emits SARIF from findings; rule IDs follow `BOM-{SPEC}-{CAT}-{NNN}`.

Adding a new standard today means dropping a `rules/<id>.yaml` file. The mapping ontology replaces (or generates) that YAML.

### Integration approach: generate YAML from TTL + SSSOM

Rather than requiring the checker to parse RDF at runtime, the bom repo acts as the **source of truth** and generates checker-compatible YAML specs as derived artifacts. This keeps the checker simple and dependency-light.

```text
docs/req/<spec>/<spec>.ttl          (provision types, SARIF rule IDs, labels)
docs/mapping/<spec>-spdx3.sssom.tsv (exactMatch / closeMatch field mappings)
        |
        v
tools/generate_yaml_spec.py
        |
        v
<spec>.yaml   →  drop into ntia_conformance_checker/rules/
```

The checker needs no RDF parser. The YAML is a stable, human-readable derived artifact that can be reviewed and diffed like any other source file.

### Rule derivation logic

For each concept `C` in `<spec>.ttl`:

1. **Filter**: include only concepts where `C bom:provisionType` ∈ {`bom:Requirement`, `bom:ConditionalRequirement`, `bom:Recommendation`}. Skip `bom:Permission` (cannot be violated) and `bom:ExternalConstraint` (classification conditions, not field requirements).

2. **Rule ID**: read `C skos:notation ?id^^bom:SarifRuleId`. This is the stable `BOM-{SPEC}-{CAT}-{NNN}` string; its category code and number are already encoded in the literal.

3. **Labels**: `C skos:prefLabel` → `warning`; `C skos:definition` → rule help text.

4. **Severity**: derived from `bom:provisionType`:
   - `bom:Requirement` → `provision: requirement` → SARIF `error`
   - `bom:ConditionalRequirement` → `provision: recommendation` → SARIF `warning`
   - `bom:Recommendation` → `provision: recommendation` → SARIF `warning`

5. **Probe**: look up all SSSOM rows where `subject_id = C`:
   - `skos:exactMatch` or `skos:closeMatch` rows with a resolvable SPDX 3 field → generate a presence probe for that field.
   - If the row's `comment` starts with `GAP:` → `status: catalogue-only` (checker advertises the rule but cannot verify it automatically).
   - `skos:narrowMatch` / `skos:relatedMatch` rows are informational; they do not generate probes but appear in the rule's `help_text`.

### SPDX 3 field → probe parameter mapping

The SSSOM `object_id` gives the RDF property IRI; the checker's probes use an abstract `attribute` name. A static registry in `tools/field_registry.py` bridges them:

| `object_id` | `object_qualifier` | probe | `attribute` |
|---|---|---|---|
| `spdx3-core:createdBy` | `spdx3-core:CreationInfo` | `require_document_attribute` | `author` |
| `spdx3-core:created` | `spdx3-core:CreationInfo` | `require_document_attribute` | `timestamp` |
| `spdx3-core:name` | `spdx3-core:Element` | `require_component_attribute` | `name` |
| `spdx3-sw:packageVersion` | `spdx3-sw:Package` | `require_component_attribute` | `version` |
| `spdx3-core:suppliedBy` | `spdx3-core:Artifact` | `require_component_attribute` | `supplier` |
| `spdx3-core:originatedBy` | `spdx3-core:Artifact` | `require_component_attribute` | `originator` |
| `spdx3-sw:packageUrl` | `spdx3-sw:Package` | `require_component_attribute` | `unique_identifier` |
| `spdx3-core:externalIdentifier` | `spdx3-core:Element` | `require_component_attribute` | `unique_identifier` |
| `spdx3-core:Relationship` | — | `require_document_attribute` | `dependency_relationship` |
| `spdx3-core:verifiedUsing` | `spdx3-core:Artifact` | `require_component_attribute` | `hash` |
| `spdx3-core:externalRef` | `spdx3-core:Element` | `require_component_attribute` | `external_ref` |
| `spdx3-core:spdxId` | `spdx3-sw:Sbom` | `require_document_attribute` | `doc_identifier` |

Fields with no entry in the registry (AI-specific, dataset-specific, gap rows) generate `status: catalogue-only` rules.

### SARIF rule ID table

| Standard | Category codes | Rule range |
|---|---|---|
| NTIA 2021 | DF | `BOM-NTIA-DF-001..007` |
| FSCT | META, COMP | `BOM-FSCT-META-001..005`, `BOM-FSCT-COMP-001..008` |
| BSI TR-03183-2 | DOC, COMP | `BOM-BSI-DOC-001..003`, `BOM-BSI-COMP-001..017` |
| G7 AI | MD, SLP, MDL, DP, INF, SP, KPI | `BOM-G7AI-{CAT}-001..NNN` (50 total) |
| EU AI Act | ANX8-A, ANX8-B, ANX8-C, ANX9 | `BOM-EUAIACT-ANX8-A-001..013`, `BOM-EUAIACT-ANX8-B-001..009`, `BOM-EUAIACT-ANX8-C-001..005`, `BOM-EUAIACT-ANX9-001..005` |

Lowercasing any rule ID yields the OSCAL control ID (e.g. `bom-ntia-df-001`).

### Priority: SPDX 3 JSON-LD

The first integration target is SPDX 3 JSON-LD, which the checker already supports via `spdx_python_model.v3_0_1`. The generated `ntia-spdx3.yaml` (already hand-authored) validates the pattern before automation.

### What changes in `ntia-conformance-checker`

1. Add generated YAML spec files for BSI, G7 AI, EU AI Act to `ntia_conformance_checker/rules/`.
2. Extend the field registry in `probes/` or a new `spdx3_field_registry.py` with the AI/dataset attribute names and their corresponding SPDX 3 accessor patterns.
3. The CLI `--comply <id>` already routes to any registered spec, so no new CLI changes needed.
4. Future: optionally add a `sssom_spec_loader.py` that generates `Spec` instances directly from SSSOM at import time, bypassing the YAML intermediate.

---

## 20. Related Work and Future Considerations

### MMV — Mapping Metadata Vocabulary

Alzahrani and O'Sullivan (ADAPT Centre / TCD, IEEE ICSC 2026) introduced the **Mapping Metadata Vocabulary (MMV)**, an OWL ontology for capturing lifecycle metadata of declarative mapping projects — phases (analysis, design, development, testing, maintenance), maintainers, review history, and governance status.

MMV is a different layer from SSSOM: where SSSOM holds the individual subject/predicate/object mapping rows, MMV describes the *project* that produced those rows. The two are complementary.

If adopted in this project, MMV metadata would live in the TTL layer (not in SSSOM TSV headers), most naturally as an additional metadata block in each ontology declaration (`owl:Ontology`) or in a dedicated `docs/mapping-project.ttl`. The `skos:scopeNote` pattern already used for cross-standard rationale in `bom.ttl` covers the concept-level equivalent of what MMV addresses at the project level.

MMV tooling is not yet available (as of mid-2026). Watch the ADAPT Centre and W3C Semantic Web communities for adoption signals before integrating.

Reference: <https://ieeexplore.ieee.org/document/11486499/>
