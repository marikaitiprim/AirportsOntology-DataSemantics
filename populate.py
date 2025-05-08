from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL
from SPARQLWrapper import SPARQLWrapper, JSON

# Define namespaces
AIRPORT = Namespace("http://www.semanticweb.org/marikaitiprimenta/ontologies/2025/4/airports#")
WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")
    

def get_airport_data():
    """Get airport data from Wikidata"""

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
   
    query = """

    SELECT ?airport ?airportLabel ?iata ?icao ?country ?countryLabel ?coord ?runwayLabel ?runwayLength
    WHERE {
        ?airport wdt:P31 wd:Q1248784 .        # Instance of airport
        OPTIONAL { ?airport wdt:P238 ?iata. } # IATA airport code
        OPTIONAL { ?airport wdt:P239 ?icao. } # ICAO airport code
        OPTIONAL { ?airport wdt:P17 ?country. } # Country 
        OPTIONAL { ?airport wdt:P625 ?coord. }  # Coordinates

        OPTIONAL {
            ?airport p:P529 ?runwayStatement .
            OPTIONAL { ?runwayStatement pq:P2043 ?runwayLength. } # Runway length
        }

        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en".
        }
    }
    LIMIT 500
    """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    
    print(f"Retrieved {len(results['results']['bindings'])} airports")
    return results['results']['bindings']

def populate_ontology(g, airport_data):
    """Populate the ontology with airport data"""
    country_map = {}
    
    # Create all country entities
    for airport in airport_data:
        if 'country' in airport:
            country_uri = airport['country']['value']
            country_label = airport['countryLabel']['value']
            country_id = country_uri.split('/')[-1]
            
            if country_id not in country_map:  # check if country already exists
                country_entity = AIRPORT[f"Country_{country_id}"]
                country_map[country_id] = country_entity
                
                # Add country to ontology
                g.add((country_entity, RDF.type, AIRPORT.Country))
                g.add((country_entity, RDFS.label, Literal(country_label, lang="en")))
                g.add((country_entity, OWL.sameAs, URIRef(country_uri)))
    
    # Process airport data
    for airport in airport_data:
        airport_uri = airport['airport']['value']
        airport_id = airport_uri.split('/')[-1]
        airport_entity = AIRPORT[f"Airport_{airport_id}"]
        
        # Add airport class
        g.add((airport_entity, RDF.type, AIRPORT.Airport))
        g.add((airport_entity, RDFS.label, Literal(airport['airportLabel']['value'], lang="en")))
        g.add((airport_entity, OWL.sameAs, URIRef(airport_uri)))
        
        # Add IATA code if available
        if 'iata' in airport:
            g.add((airport_entity, AIRPORT.hasIATACode, Literal(airport['iata']['value'])))
        
        # Add ICAO code if available
        if 'icao' in airport:
            g.add((airport_entity, AIRPORT.hasICAOCode, Literal(airport['icao']['value'])))
        
        # Add coordinates if available
        if 'coord' in airport:
            g.add((airport_entity, AIRPORT.hasCoordinates, Literal(airport['coord']['value'])))
        
        # Add runway length if available
        if 'runwayLength' in airport:
            g.add((airport_entity, AIRPORT.hasRunwayLen, Literal(airport['runwayLength']['value'])))
        
        # Link to country if available
        if 'country' in airport:
            country_id = airport['country']['value'].split('/')[-1]
            if country_id in country_map:  # Make sure country exists in map
                country_entity = country_map[country_id]
                g.add((airport_entity, AIRPORT.isLocatedIn, country_entity))
    
    print(f"Populated ontology has {len(g)} triples")
    return g

if __name__ == "__main__":

    input_file = "airports_ontology.rdf"
    output_file = "populated_airports.owl"
    
    # Load the ontology
    g = Graph()
    g.parse(input_file, format="xml")
    
    # Bind namespaces
    g.bind("airport", AIRPORT)
    g.bind("wd", WD)
    g.bind("wdt", WDT)
    
    print(f"Loaded ontology with {len(g)} triples")
    
    # Fetch airport data
    airport_data = get_airport_data()
    
    # Populate the ontology
    g = populate_ontology(g, airport_data)
    
    # Save the populated ontology
    g.serialize(destination=output_file, format="xml")
    print(f"Saved populated ontology to {output_file}")