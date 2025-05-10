from rdflib import Graph, Namespace
from tabulate import tabulate

AIRPORT = Namespace("http://www.semanticweb.org/marikaitiprimenta/ontologies/2025/4/airports#")

def formatted_results(results):
    """Format the query results for better readability"""

    if not results or len(results) == 0:
        return "No results found."
    
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
                val_str = str(val)
                if val_str.startswith('http://'):
                    if '#' in val_str:   # Extract the fragment identifier or the last part of the URI
                        val_str = val_str.split('#')[-1]
                    else:
                        val_str = val_str.split('/')[-1]
                row_values.append(val_str)
        rows.append(row_values)
    
    return tabulate(rows, headers=[str(h) for h in headers], tablefmt="grid")

def defined_queries():
    """Dictionary of predefined queries"""
    return {
        "1": {
            "name": "List 30 flights with departure and arrival details",
            "query": """
                SELECT ?flight ?depAirportLabel ?depIATA ?arrAirportLabel ?arrIATA ?airline ?depTime ?arrTime
                WHERE {
                    ?flight rdf:type airport:Flight .
                    ?flight airport:hasDepartureAirport ?depAirport .
                    ?flight airport:hasArrivalAirport ?arrAirport .
                    ?flight airport:operatedBy ?airline .
                    
                    ?depAirport rdfs:label ?depAirportLabel .
                    ?depAirport airport:hasIATACode ?depIATA .
                    
                    ?arrAirport rdfs:label ?arrAirportLabel .
                    ?arrAirport airport:hasIATACode ?arrIATA .
                    
                    OPTIONAL { ?flight airport:hasDepartureTime ?depTime }
                    OPTIONAL { ?flight airport:hasArrivalTime ?arrTime }
                }
                LIMIT 30
            """
        },
        "2": {
            "name": "List flights by airline",
            "query": """
                SELECT ?airlineLabel ?depAirportLabel ?depCountryLabel ?arrAirportLabel ?arrCountryLabel ?depTime
                WHERE {
                    ?flight rdf:type airport:Flight .
                    ?flight airport:hasDepartureAirport ?depAirport .
                    ?flight airport:hasArrivalAirport ?arrAirport .
                    ?flight airport:operatedBy ?airline .
                    ?airline rdfs:label ?airlineLabel .
                    
                    ?depAirport rdfs:label ?depAirportLabel .
                    ?arrAirport rdfs:label ?arrAirportLabel .
                    
                    ?depAirport airport:isLocatedIn ?depCountry .
                    ?depCountry rdfs:label ?depCountryLabel .
                    
                    ?arrAirport airport:isLocatedIn ?arrCountry .
                    ?arrCountry rdfs:label ?arrCountryLabel .
                    
                    OPTIONAL { ?flight airport:hasDepartureTime ?depTime }
                }
                ORDER BY ?airlineLabel ?depTime
                LIMIT 30
            """
        },
        "3": {
            "name": "List morning flights with countries",
            "query": """
                SELECT ?flight ?depTime 
                    ?depAirportLabel ?depCountryLabel 
                    ?arrAirportLabel ?arrCountryLabel
                WHERE {
                    ?flight rdf:type airport:Flight .
                    ?flight airport:hasDepartureTime ?depTime .
                    ?flight airport:hasDepartureAirport ?depAirport .
                    ?flight airport:hasArrivalAirport ?arrAirport .

                    ?depAirport rdfs:label ?depAirportLabel .
                    ?depAirport airport:isLocatedIn ?depCountry .
                    ?depCountry rdfs:label ?depCountryLabel .

                    ?arrAirport rdfs:label ?arrAirportLabel .
                    ?arrAirport airport:isLocatedIn ?arrCountry .
                    ?arrCountry rdfs:label ?arrCountryLabel .

                    FILTER(?depTime < "12:00")
                }
                ORDER BY ?depTime
                LIMIT 30
            """
        },
        "4": {
            "name": "List airport pairs with the most connecting flights",
            "query": """
                SELECT ?depAirportLabel ?depIATA ?arrAirportLabel ?arrIATA (COUNT(?flight) as ?flightCount)
                WHERE {
                    ?flight rdf:type airport:Flight .
                    ?flight airport:hasDepartureAirport ?depAirport .
                    ?flight airport:hasArrivalAirport ?arrAirport .
                    
                    ?depAirport rdfs:label ?depAirportLabel .
                    ?depAirport airport:hasIATACode ?depIATA .
                    
                    ?arrAirport rdfs:label ?arrAirportLabel .
                    ?arrAirport airport:hasIATACode ?arrIATA .
                }
                GROUP BY ?depAirportLabel ?depIATA ?arrAirportLabel ?arrIATA
                ORDER BY DESC(?flightCount)
                LIMIT 30
            """ 
        }
    }


def queries_exec(g):
    """Select queries to execute - interactive user interface"""
    queries = defined_queries()
    
    while True:
        print("Select a query to execute:")
        for key, query in queries.items():
            print(f"{key}. {query['name']}")
        
        query_choice = input("\nSelect a query (1-4): ").strip()

        if query_choice in queries:
            query = queries[query_choice]["query"]
            print(f"\nExecuting query: {queries[query_choice]['name']}")
            results = g.query(query)
            if results:
                print("\n" + formatted_results(results))
        else:
            print("Invalid query selection.")

if __name__ == "__main__":
    
    ontology_file = "populated_flights.owl" #populated ontology for airports and flights (from file populate_intermediate.py)
    
    g = Graph()
    g.parse(ontology_file, format="xml")
    
    g.bind("airport", AIRPORT)
    g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    g.bind("owl", "http://www.w3.org/2002/07/owl#")
    
    queries_exec(g)