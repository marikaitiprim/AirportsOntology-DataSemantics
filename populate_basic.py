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

    SELECT ?airport ?airportLabel ?iata ?icao ?city ?cityLabel ?country ?countryLabel ?coord ?runway ?runwayLabel ?runwayLength
        WHERE {
        ?airport wdt:P31 wd:Q1248784 .        # Instance of airport
        OPTIONAL { ?airport wdt:P238 ?iata. }
        OPTIONAL { ?airport wdt:P239 ?icao. }
        OPTIONAL { ?airport wdt:P625 ?coord. }
        OPTIONAL { ?airport wdt:P17 ?country. }
        OPTIONAL { ?airport wdt:P131 ?city. }  # City or administrative area

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

# def populate_ontology(g, airport_data):
#     """Populate the ontology with airport data"""
#     country_map = {}
    
#     # Create all country entities
#     for airport in airport_data:
#         if 'country' in airport:
#             country_uri = airport['country']['value']
#             country_label = airport['countryLabel']['value']
#             country_id = country_uri.split('/')[-1]
            
#             if country_id not in country_map:  # check if country already exists
#                 country_entity = AIRPORT[f"Country_{country_id}"]
#                 country_map[country_id] = country_entity
                
#                 # Add country to ontology
#                 g.add((country_entity, RDF.type, AIRPORT.Country))
#                 g.add((country_entity, RDFS.label, Literal(country_label, lang="en")))
#                 g.add((country_entity, OWL.sameAs, URIRef(country_uri)))
    
#     # Process airport data
#     for airport in airport_data:
#         airport_uri = airport['airport']['value']
#         airport_id = airport_uri.split('/')[-1]
#         airport_entity = AIRPORT[f"Airport_{airport_id}"]
        
#         # Add airport class
#         g.add((airport_entity, RDF.type, AIRPORT.Airport))
#         g.add((airport_entity, RDFS.label, Literal(airport['airportLabel']['value'], lang="en")))
#         g.add((airport_entity, OWL.sameAs, URIRef(airport_uri)))
        
#         # Add IATA code if available
#         if 'iata' in airport:
#             g.add((airport_entity, AIRPORT.hasIATACode, Literal(airport['iata']['value'])))
        
#         # Add ICAO code if available
#         if 'icao' in airport:
#             g.add((airport_entity, AIRPORT.hasICAOCode, Literal(airport['icao']['value'])))
        
#         # Add coordinates if available
#         if 'coord' in airport:
#             g.add((airport_entity, AIRPORT.hasCoordinates, Literal(airport['coord']['value'])))
        
#         # Add runway length if available
#         if 'runwayLength' in airport:
#             g.add((airport_entity, AIRPORT.hasRunwayLen, Literal(airport['runwayLength']['value'])))
        
#         # Link to country if available
#         if 'country' in airport:
#             country_id = airport['country']['value'].split('/')[-1]
#             if country_id in country_map:  # Make sure country exists in map
#                 country_entity = country_map[country_id]
#                 g.add((airport_entity, AIRPORT.isLocatedIn, country_entity))
    
#     print(f"Populated ontology has {len(g)} triples")
#     return g


def populate_ontology(g, airport_data):
    """Populate the ontology with airport data"""
    country_map = {}
    city_map = {}
    runway_map = {}
    
    # Create all country entities first
    print("Processing countries...")
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
    
    # Create all city entities next
    print("Processing cities...")
    for airport in airport_data:
        if 'city' in airport:
            city_uri = airport['city']['value']
            city_label = airport['cityLabel']['value']
            city_id = city_uri.split('/')[-1]
            
            if city_id not in city_map:  # check if city already exists
                city_entity = AIRPORT[f"City_{city_id}"]
                city_map[city_id] = city_entity
                
                # Add city to ontology
                g.add((city_entity, RDF.type, AIRPORT.City))
                g.add((city_entity, RDFS.label, Literal(city_label, lang="en")))
                g.add((city_entity, OWL.sameAs, URIRef(city_uri)))
                print(f"Added city: {city_label} ({city_id})")
                
                # Link city to country if available
                if 'country' in airport:
                    country_id = airport['country']['value'].split('/')[-1]
                    if country_id in country_map:
                        g.add((city_entity, AIRPORT.isLocatedIn, country_map[country_id]))
                        print(f"  - Linked city {city_label} to country {country_id}")
    
    # Process airport data
    print("Processing airports...")
    for airport in airport_data:
        if 'airport' not in airport or 'airportLabel' not in airport:
            print("Skipping airport with missing data")
            continue
            
        airport_uri = airport['airport']['value']
        airport_id = airport_uri.split('/')[-1]
        airport_entity = AIRPORT[f"Airport_{airport_id}"]
        airport_label = airport['airportLabel']['value']
        
        # Add airport class
        g.add((airport_entity, RDF.type, AIRPORT.Airport))
        g.add((airport_entity, RDFS.label, Literal(airport_label, lang="en")))
        g.add((airport_entity, OWL.sameAs, URIRef(airport_uri)))
        print(f"Added airport: {airport_label} ({airport_id})")
        
        # Add IATA code if available
        if 'iata' in airport:
            iata_code = airport['iata']['value']
            g.add((airport_entity, AIRPORT.hasIATACode, Literal(iata_code)))
            print(f"  - IATA: {iata_code}")
        
        # Add ICAO code if available
        if 'icao' in airport:
            icao_code = airport['icao']['value']
            g.add((airport_entity, AIRPORT.hasICAOCode, Literal(icao_code)))
            print(f"  - ICAO: {icao_code}")
        
        # Add coordinates if available
        if 'coord' in airport:
            coord_value = airport['coord']['value']
            g.add((airport_entity, AIRPORT.hasCoordinates, Literal(coord_value)))
            print(f"  - Coordinates: {coord_value}")
        
        # Process runway information
        if 'runway' in airport:
            runway_uri = airport['runway']['value']
            runway_id = runway_uri.split('/')[-1]
            
            # Create runway entity if not already created
            if runway_id not in runway_map:
                runway_entity = AIRPORT[f"Runway_{runway_id}"]
                runway_map[runway_id] = runway_entity
                
                # Add runway class
                g.add((runway_entity, RDF.type, AIRPORT.Runway))
                
                if 'runwayLabel' in airport:
                    runway_label = airport['runwayLabel']['value']
                    g.add((runway_entity, RDFS.label, Literal(runway_label, lang="en")))
                    print(f"  - Runway: {runway_label}")
                
                # Add runway length if available
                if 'runwayLength' in airport:
                    runway_length = airport['runwayLength']['value']
                    g.add((runway_entity, AIRPORT.hasRunwayLen, Literal(runway_length)))
                    print(f"    - Length: {runway_length}")
            
            # Link airport to runway
            runway_entity = runway_map[runway_id]
            g.add((airport_entity, AIRPORT.hasRunway, runway_entity))
        
        # Link to country if available
        if 'country' in airport:
            country_id = airport['country']['value'].split('/')[-1]
            if country_id in country_map:  # Make sure country exists in map
                country_entity = country_map[country_id]
                g.add((airport_entity, AIRPORT.isLocatedIn, country_entity))
        
        # Link to city if available
        if 'city' in airport:
            city_id = airport['city']['value'].split('/')[-1]
            if city_id in city_map:  # Make sure city exists in map
                city_entity = city_map[city_id]
                g.add((airport_entity, AIRPORT.isLocatedInCity, city_entity))
                city_label = None
                for _, _, label in g.triples((city_entity, RDFS.label, None)):
                    city_label = str(label)
                print(f"  - Located in city: {city_label if city_label else city_id}")
    
    # Print summary
    print(f"\nSummary:")
    print(f"- Countries: {len(country_map)}")
    print(f"- Cities: {len(city_map)}")
    print(f"- Airports: {len(set(g.subjects(RDF.type, AIRPORT.Airport)))}")
    print(f"- Runways: {len(runway_map)}")
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