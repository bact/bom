import rdflib
from rdflib.namespace import RDF, SKOS
import re

g = rdflib.Graph()
g.parse('docs/bom.ttl', format='turtle')

BOM = rdflib.Namespace('https://w3id.org/bom/')

# Define the Top Concepts and Collections we want to render
categories = [
    (BOM['MetadataDocument'], 'Document Metadata (<code>bom:MetadataDocument</code>)', True),
    (BOM['MetadataComponent'], 'Component Metadata (<code>bom:MetadataComponent</code>)', True),
    (BOM['MetadataRelationship'], 'Relationship Metadata (<code>bom:MetadataRelationship</code>)', True),
    (BOM['CollectionSoftware'], 'Software Profile (<code>bom:CollectionSoftware</code>)', False),
    (BOM['CollectionAI'], 'AI System and Model Profile (<code>bom:CollectionAI</code>)', False),
    (BOM['CollectionDataset'], 'Dataset Profile (<code>bom:CollectionDataset</code>)', False),
    (BOM['CollectionInfra'], 'Infrastructure Profile (<code>bom:CollectionInfra</code>)', False),
    (BOM['CollectionSecurity'], 'Security Profile (<code>bom:CollectionSecurity</code>)', False),
]

concepts = list(g.subjects(RDF.type, SKOS.Concept))
bridge_concepts = [c for c in concepts if (c, SKOS.inScheme, BOM['bridge']) in g]

sections_html = []
for cat_iri, cat_title, is_top_concept in categories:
    cat_concepts = []
    
    if is_top_concept:
        # Find all concepts that have skos:broader = cat_iri
        for c in bridge_concepts:
            if (c, SKOS.broader, cat_iri) in g:
                cat_concepts.append(c)
    else:
        # Find all concepts that are skos:member of cat_iri
        for c in bridge_concepts:
            if (cat_iri, SKOS.member, c) in g:
                cat_concepts.append(c)
                
    cat_concepts.sort(key=lambda c: str(c))
    if not cat_concepts:
        continue
    
    rows = []
    for c in cat_concepts:
        curie = f'bom:{str(c).split("/")[-1]}'
        label = str(g.value(c, SKOS.prefLabel) or '')
        defn = str(g.value(c, SKOS.definition) or '')
        rows.append(f'''            <tr>
              <td class="curie">{curie}</td>
              <td>{label}</td>
              <td>{defn}</td>
            </tr>''')
            
    rows_str = '\\n'.join(rows)
    sec_html = f'''      <section>
        <h3>{cat_title}</h3>
        <table class="definition">
          <thead>
            <tr>
              <th>Concept</th>
              <th>Preferred Label</th>
              <th>Definition</th>
            </tr>
          </thead>
          <tbody>
{rows_str}
          </tbody>
        </table>
      </section>'''
    sections_html.append(sec_html)

all_sections_html = '\\n\\n'.join(sections_html)

with open('docs/releases/0.1.0/index.html', 'r') as f:
    html_content = f.read()

pattern = re.compile(r'<h2>Bridge Concepts</h2>.*?(?=\n  </body>)', re.DOTALL)
new_bridge_section = f'''<h2>Bridge Concepts</h2>
      <p>
        The neutral bridge concepts are grouped by structural metadata category and domain profiles:
      </p>

{all_sections_html}
    </section>'''

new_html = pattern.sub(new_bridge_section, html_content)

with open('docs/releases/0.1.0/index.html', 'w') as f:
    f.write(new_html)

print('Updated docs/releases/0.1.0/index.html')
