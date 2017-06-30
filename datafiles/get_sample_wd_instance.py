
#boris becker
sparql = """
PREFIX entity: <http://www.wikidata.org/entity/>
#partial results

SELECT DISTINCT ?p
WHERE
{
  entity:Q76334 ?p ?o .
}   
"""

import json
ids = []

with open('becker.json') as data_file:    
    data = json.load(data_file)
    for d in data:
        parts = d['p'].split("/")

        if parts[-1].startswith('P'):
            ids.append(parts[-1])

    print ids

