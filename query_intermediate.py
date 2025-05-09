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
    """Dictionary of predefined queries combining flights, airports and countries"""
    return {
        "1": {
            "name": "List all flights with departure and arrival airport details",
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
                ORDER BY ?depIATA ?arrIATA
                LIMIT 20
            """
        },
        "2": {
            "name": "Flights by airline with airport countries",
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
                LIMIT 15
            """
        },
        "3": {
            "name": "International flights (different departure and arrival countries)",
            "query": """
                SELECT ?flight ?depAirportLabel ?depCountryLabel ?arrAirportLabel ?arrCountryLabel ?airline ?duration
                WHERE {
                    ?flight rdf:type airport:Flight .
                    ?flight airport:hasDepartureAirport ?depAirport .
                    ?flight airport:hasArrivalAirport ?arrAirport .
                    ?flight airport:operatedBy ?airline .
                    
                    ?depAirport rdfs:label ?depAirportLabel .
                    ?arrAirport rdfs:label ?arrAirportLabel .
                    
                    ?depAirport airport:isLocatedIn ?depCountry .
                    ?depCountry rdfs:label ?depCountryLabel .
                    
                    ?arrAirport airport:isLocatedIn ?arrCountry .
                    ?arrCountry rdfs:label ?arrCountryLabel .
                    
                    OPTIONAL { ?flight airport:hasDuration ?duration }
                    
                    FILTER(?depCountry != ?arrCountry)
                }
                ORDER BY ?depCountryLabel ?arrCountryLabel
                LIMIT 15
            """
        },
        "4": {
            "name": "Long-haul flights with country information",
            "query": """
                SELECT ?flight ?depAirportLabel ?depCountryLabel ?arrAirportLabel ?arrCountryLabel ?airline ?duration
                WHERE {
                    ?flight rdf:type airport:Flight .
                    ?flight airport:hasDepartureAirport ?depAirport .
                    ?flight airport:hasArrivalAirport ?arrAirport .
                    ?flight airport:operatedBy ?airline .
                    ?flight airport:hasDuration ?duration .
                    
                    ?depAirport rdfs:label ?depAirportLabel .
                    ?arrAirport rdfs:label ?arrAirportLabel .
                    
                    ?depAirport airport:isLocatedIn ?depCountry .
                    ?depCountry rdfs:label ?depCountryLabel .
                    
                    ?arrAirport airport:isLocatedIn ?arrCountry .
                    ?arrCountry rdfs:label ?arrCountryLabel .
                    
                    FILTER(?duration > 180)
                }
                ORDER BY DESC(?duration)
                LIMIT 15
            """
        },
        "5": {
            "name": "Countries with most airport connectivity (flight routes)",
            "query": """
                SELECT ?countryLabel (COUNT(DISTINCT ?route) as ?routeCount)
                WHERE {
                    ?flight rdf:type airport:Flight .
                    
                    # Create a unique route identifier combining departure and arrival airports
                    BIND(CONCAT(STR(?depAirport), "-", STR(?arrAirport)) AS ?route)
                    
                    ?flight airport:hasDepartureAirport ?depAirport .
                    ?depAirport airport:isLocatedIn ?country .
                    ?country rdfs:label ?countryLabel .
                    
                    ?flight airport:hasArrivalAirport ?arrAirport .
                }
                GROUP BY ?countryLabel
                ORDER BY DESC(?routeCount)
                LIMIT 10
            """
        },
        "6": {
            "name": "Morning international flights by country pairs",
            "query": """
                SELECT ?depCountryLabel ?arrCountryLabel (COUNT(?flight) as ?flightCount)
                WHERE {
                    ?flight rdf:type airport:Flight .
                    ?flight airport:hasDepartureAirport ?depAirport .
                    ?flight airport:hasArrivalAirport ?arrAirport .
                    ?flight airport:hasDepartureTime ?depTime .
                    
                    ?depAirport airport:isLocatedIn ?depCountry .
                    ?depCountry rdfs:label ?depCountryLabel .
                    
                    ?arrAirport airport:isLocatedIn ?arrCountry .
                    ?arrCountry rdfs:label ?arrCountryLabel .
                    
                    FILTER(?depCountry != ?arrCountry)
                    FILTER(STRSTARTS(?depTime, "0") || STRSTARTS(?depTime, "1"))
                }
                GROUP BY ?depCountryLabel ?arrCountryLabel
                ORDER BY DESC(?flightCount)
                LIMIT 15
            """
        },
        "7": {
            "name": "Airlines operating international flights",
            "query": """
                SELECT ?airlineLabel (COUNT(?flight) as ?intlFlightCount)
                WHERE {
                    ?flight rdf:type airport:Flight .
                    ?flight airport:hasDepartureAirport ?depAirport .
                    ?flight airport:hasArrivalAirport ?arrAirport .
                    ?flight airport:operatedBy ?airline .
                    ?airline rdfs:label ?airlineLabel .
                    
                    ?depAirport airport:isLocatedIn ?depCountry .
                    ?arrAirport airport:isLocatedIn ?arrCountry .
                    
                    FILTER(?depCountry != ?arrCountry)
                }
                GROUP BY ?airlineLabel
                ORDER BY DESC(?intlFlightCount)
                LIMIT 10
            """
        },
        "8": {
            "name": "Airport pairs with most connecting flights",
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
                LIMIT 15
            """ 
        },
        "9": {
            "name": "Marking international flights",
            "query": """
                PREFIX airport: <http://www.semanticweb.org/marikaitiprimenta/ontologies/2025/4/airports#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                CONSTRUCT {
                    ?flight airport:isInternational true .
                }
                WHERE {
                    ?flight rdf:type airport:Flight .
                    ?flight airport:hasDepartureAirport ?dep .
                    ?flight airport:hasArrivalAirport ?arr .
                    ?dep airport:isLocatedIn ?c1 .
                    ?arr airport:isLocatedIn ?c2 .
                    FILTER(?c1 != ?c2)
                }

            """
        }
    }


def queries_execution(g):
    """Select queries to execute"""
    queries = predefined_queries()
    
    while True:
        for key, query in queries.items():
            print(f"{key}. {query['name']}")
        
        query_choice = input("\nSelect a query (1-9): ").strip()
        if query_choice in queries:
            query = queries[query_choice]["query"]
            print(f"\nExecuting query: {queries[query_choice]['name']}")
            results = g.query(query)
            if results:
                print("\n" + format_results(results))
        else:
            print("Invalid query selection.")

if __name__ == "__main__":
    # Use the combined ontology file
    ontology_file = "populated_flights.owl"
    
    g = Graph()
    g.parse(ontology_file, format="xml")
    
    # Bind namespaces
    g.bind("airport", AIRPORT)
    g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    g.bind("owl", "http://www.w3.org/2002/07/owl#")
    
    print(f"Loaded ontology with {len(g)} triples")
    
    # Start query execution
    queries_execution(g)