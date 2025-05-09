from rdflib import Graph, Namespace
from tabulate import tabulate

# Define namespaces
AIRPORT = Namespace("http://www.semanticweb.org/marikaitiprimenta/ontologies/2025/4/airports#")

def format_results(results):
    """Format the query results for display"""
    if not results or len(results) == 0:
        return "No results found."
    
    # Get column names from the results
    headers = results.vars
    
    # Convert results to a list of lists for tabulate
    rows = []
    for row in results:
        row_values = []
        for col in headers:
            val = row.get(col)
            if val is None:
                row_values.append("")
            else:
                # Clean up URIs to display only the relevant part
                val_str = str(val)
                if val_str.startswith('http://'):
                    # Extract the fragment identifier or the last part of the URI
                    if '#' in val_str:
                        val_str = val_str.split('#')[-1]
                    else:
                        val_str = val_str.split('/')[-1]
                row_values.append(val_str)
        rows.append(row_values)
    
    # Return formatted table
    return tabulate(rows, headers=[str(h) for h in headers], tablefmt="grid")

def predefined_queries():
    """Dictionary of predefined queries"""
    return {
        "1": {
            "name": "List all airports",
            "query": """
                SELECT ?airport ?label ?iata ?icao
                WHERE {
                    ?airport rdf:type airport:Airport .
                    ?airport rdfs:label ?label .
                    OPTIONAL { ?airport airport:hasIATACode ?iata }
                    OPTIONAL { ?airport airport:hasICAOCode ?icao }
                }
                ORDER BY ?label
                LIMIT 20
            """
        },
        "2": {
            "name": "Airports by country",
            "query": """
                SELECT ?airport ?airportLabel ?country ?countryLabel
                WHERE {
                    ?airport rdf:type airport:Airport .
                    ?airport rdfs:label ?airportLabel .
                    ?airport airport:isLocatedIn ?country .
                    ?country rdfs:label ?countryLabel .
                }
                ORDER BY ?countryLabel ?airportLabel
                LIMIT 20
            """
        },
        "3": {
            "name": "Airports with IATA code starting with 'L'",
            "query": """
                SELECT ?airport ?label ?iata
                WHERE {
                    ?airport rdf:type airport:Airport .
                    ?airport rdfs:label ?label .
                    ?airport airport:hasIATACode ?iata .
                    FILTER(STRSTARTS(?iata, "L"))
                }
                ORDER BY ?iata
                LIMIT 20
            """
        },
        "4": {
            "name": "Count airports by country",
            "query": """
                SELECT ?countryLabel (COUNT(?airport) as ?airportCount)
                WHERE {
                    ?airport rdf:type airport:Airport .
                    ?airport airport:isLocatedIn ?country .
                    ?country rdfs:label ?countryLabel .
                }
                GROUP BY ?countryLabel
                ORDER BY DESC(?airportCount)
                LIMIT 10
            """
        }
    }

def queries_execution(g):
    """Select queries to execute"""
    queries = predefined_queries()
    
    while True:
        for key, query in queries.items():
            print(f"{key}. {query['name']}")
        
        query_choice = input("\nSelect a query (1-4): ").strip()
        if query_choice in queries:
            query = queries[query_choice]["query"]
            print(f"\nExecuting query: {queries[query_choice]['name']}")
            results = g.query(query)
            if results:
                print("\n" + format_results(results))
        else:
            print("Invalid query selection.")

if __name__ == "__main__":
    
    ontology_file = "populated_airports.owl"

    g = Graph()
    g.parse(ontology_file, format="xml")
    
    g.bind("airport", AIRPORT)
    g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    g.bind("owl", "http://www.w3.org/2002/07/owl#")
    
    print(f"Loaded ontology with {len(g)} triples")
    
    queries_execution(g)