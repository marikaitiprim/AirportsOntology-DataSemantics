from rdflib import Graph, Namespace, Literal, URIRef, XSD
from rdflib.namespace import RDF, RDFS, OWL
from SPARQLWrapper import SPARQLWrapper, JSON
import re

# Define namespaces
AIRPORT = Namespace("http://www.semanticweb.org/marikaitiprimenta/ontologies/2025/4/airports#")
WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")
    
def query_airport():
    """Get airport data from Wikidata"""

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
   
    query = """

    SELECT ?airport ?airportLabel ?iata ?icao ?city ?cityLabel ?country ?countryLabel ?coord ?runway ?runwayLabel ?runwayLength
        WHERE {
            ?airport wdt:P31 wd:Q1248784 .        
            OPTIONAL { ?airport wdt:P238 ?iata. }
            OPTIONAL { ?airport wdt:P239 ?icao. }
            OPTIONAL { ?airport wdt:P625 ?coord. }
            OPTIONAL { ?airport wdt:P17 ?country. }
            OPTIONAL { ?airport wdt:P131 ?city. }  
            OPTIONAL {
                ?airport p:P529 ?runwayStatement .
                ?runwayStatement ps:P529 ?runway .
                OPTIONAL { ?runwayStatement pq:P2043 ?runwayLength. }
            }
            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "en" .
                ?airport rdfs:label ?airportLabel .
                ?country rdfs:label ?countryLabel .
                ?city rdfs:label ?cityLabel .
                ?runway rdfs:label ?runwayLabel .
            }
        }
    LIMIT 2000
    """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    
    print(f"Retrieved {len(results['results']['bindings'])} airports")
    return results['results']['bindings']


def populate_ontology(g, airport_data):
    """Populate the ontology with airport data"""

    country_map = {}
    city_map = {}
    runway_map = {}
    
    for airport in airport_data:

        # Create all country entities 
        if 'country' in airport:
            country_uri = airport['country']['value']
            country_label = airport['countryLabel']['value']
            country_id = country_uri.split('/')[-1]
            
            if country_id not in country_map:  # check if country already exists
                country_entity = AIRPORT[f"Country_{country_id}"]
                country_map[country_id] = country_entity
                
                g.add((country_entity, RDF.type, AIRPORT.Country))  # Add to ontology
                g.add((country_entity, RDFS.label, Literal(country_label, lang="en")))
                g.add((country_entity, OWL.sameAs, URIRef(country_uri)))
                
    for airport in airport_data:
    
        # Create all city entities
        if 'city' in airport:
            city_uri = airport['city']['value']
            city_label = airport['cityLabel']['value']
            city_id = city_uri.split('/')[-1]
            
            if city_id not in city_map:  # check if city already exists
                city_entity = AIRPORT[f"City_{city_id}"]
                city_map[city_id] = city_entity
                
                g.add((city_entity, RDF.type, AIRPORT.City))    # Add to ontology
                g.add((city_entity, RDFS.label, Literal(city_label, lang="en")))
                g.add((city_entity, OWL.sameAs, URIRef(city_uri)))
                
                if 'country' in airport:        # Link city to country
                    country_id = airport['country']['value'].split('/')[-1]
                    if country_id in country_map:
                        g.add((city_entity, AIRPORT.isLocatedIn, country_map[country_id]))

    for airport in airport_data:

        # Create all airport entities
        if 'airport' not in airport or 'airportLabel' not in airport:
            print("Skipping airport with missing data")
            continue
            
        airport_uri = airport['airport']['value']
        airport_id = airport_uri.split('/')[-1]
        airport_entity = AIRPORT[f"Airport_{airport_id}"]
        airport_label = airport['airportLabel']['value']
        
        g.add((airport_entity, RDF.type, AIRPORT.Airport)) # Add to ontology 
        g.add((airport_entity, RDFS.label, Literal(airport_label, lang="en")))
        g.add((airport_entity, OWL.sameAs, URIRef(airport_uri)))
        
        if 'iata' in airport:   # Add IATA code
            iata_code = airport['iata']['value']
            g.add((airport_entity, AIRPORT.hasIATACode, Literal(iata_code, datatype=XSD.string)))
        
        if 'icao' in airport:  # Add ICAO code 
            icao_code = airport['icao']['value']
            g.add((airport_entity, AIRPORT.hasICAOCode, Literal(icao_code, datatype=XSD.string)))
        
        if 'coord' in airport: # Add coordinates 
            coord_value = airport['coord']['value']
            g.add((airport_entity, AIRPORT.hasCoordinates, Literal(coord_value, datatype=XSD.string)))
        
        if 'runway' in airport: # Process runway information
            runway_uri = airport['runway']['value']
            runway_id = runway_uri.split('/')[-1]
            
            # Create runway entity
            if runway_id not in runway_map:

                runway_sanitized = re.sub(r'\W+', '_', runway_id.strip())
                runway_entity = AIRPORT[f"Runway_{runway_sanitized}"]
                runway_map[runway_id] = runway_entity
                
                g.add((runway_entity, RDF.type, AIRPORT.Runway))
                
                if 'runwayLabel' in airport:
                    runway_label = airport['runwayLabel']['value']
                    g.add((runway_entity, RDFS.label, Literal(runway_label, lang="en")))
                
                if 'runwayLength' in airport:  # Add runway length
                    runway_length = airport['runwayLength']['value']
                    g.add((runway_entity, AIRPORT.hasRunwayLen, Literal(runway_length, datatype=XSD.string)))
            
            runway_entity = runway_map[runway_id]    # Link airport to runway
            g.add((airport_entity, AIRPORT.hasRunway, runway_entity))
         
        if 'country' in airport: # Link airport to country
            country_id = airport['country']['value']
            country_id = country_id.split('/')[-1]

            if country_id in country_map:  # Check if country exists in map
                country_entity = country_map[country_id]
                g.add((airport_entity, AIRPORT.isLocatedIn, country_entity))
        
        if 'city' in airport: # Link airport to city
            city_id = airport['city']['value']
            city_id = city_id.split('/')[-1]
            if city_id in city_map:  # Check if city exists in map
                city_entity = city_map[city_id]
                g.add((airport_entity, AIRPORT.servesCity, city_entity))
    
    return g

if __name__ == "__main__":
    
    g = Graph()
    g.parse("airports_ontology.rdf", format="xml") # Load the base ontology
    
    g.bind("airport", AIRPORT)
    g.bind("wd", WD)
    g.bind("wdt", WDT)
    
    print(f"Loaded ontology with {len(g)} triples")
    
    airport_data = query_airport() # Query airport data from Wikidata
    g = populate_ontology(g, airport_data) # Populate the ontology
    
    g.serialize(destination="populated_airports.owl", format="xml") # Save the populated ontology
    print(f"Saved populated ontology to populated_airports.owl")