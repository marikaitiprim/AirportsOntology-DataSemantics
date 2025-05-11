import csv
from rdflib import Graph, Namespace, Literal, URIRef, XSD
from rdflib.namespace import RDF, RDFS
import re

AIRPORT = Namespace("http://www.semanticweb.org/marikaitiprimenta/ontologies/2025/4/airports#")

def format_time(time_value): # Helper function to convert time values
    if not time_value or time_value == "":
        return None
    
    time_str = str(int(float(time_value))).zfill(4)
    
    # Format as HH:MM
    if len(time_str) == 4:
        return f"{time_str[:2]}:{time_str[2:]}"
    return None

def populate_ontology(g):
    """Populate the ontology with flight data"""

    iata_map = {}
    for s, _, o in g.triples((None, AIRPORT.hasIATACode, None)): # Build a map of IATA code → Airport URI
        iata_map[str(o)] = s

    airlines_map = {}

    with open("flights.csv") as f:  # Read CSV file with the flight data
        reader = csv.reader(f)

        counter = 0
        for row in reader: 

            if counter == 0: # Skip header row
                counter += 1
                continue  

            if counter == 500: # Limit to 500 rows 
                break
            
            counter += 1

            src_iata = row[13]
            dst_iata = row[14]
            airline = row[20]
            flight_number = row[11]
            depart_time = format_time(row[4])
            arrival_time = format_time(row[7])
            air_time = row[15]  
            distance = row[16] 

            if src_iata in iata_map and dst_iata in iata_map: # Match IATA codes to Aiports
                src_airport = iata_map[src_iata]
                dst_airport = iata_map[dst_iata]

                airline_sanitized = re.sub(r'\W+', '_', airline.strip())

                # Add Flight
                flight_uri = URIRef(AIRPORT + f"Flight_{src_iata}_{dst_iata}_{airline_sanitized}_{flight_number}")
                g.add((flight_uri, RDF.type, AIRPORT.Flight))
                g.add((flight_uri, AIRPORT.hasDepartureAirport, src_airport))
                g.add((flight_uri, AIRPORT.hasArrivalAirport, dst_airport))
                g.add((flight_uri, AIRPORT.operatedBy, Literal(airline)))

                # Add Airline
                if airline not in airlines_map:
                    airline_uri = AIRPORT[f"Airline_{airline_sanitized}"]
                    g.add((airline_uri, RDF.type, AIRPORT.Airline))
                    g.add((airline_uri, RDFS.label, Literal(airline, lang="en")))
                    airlines_map[airline] = airline_uri

                g.add((flight_uri, AIRPORT.operatedBy, airlines_map[airline]))

                if flight_number:
                    g.add((flight_uri, AIRPORT.hasFlightNumber, Literal(flight_number, datatype=XSD.integer)))

                if depart_time:
                    g.add((flight_uri, AIRPORT.hasDepartureTime, Literal(depart_time, datatype=XSD.string)))
                
                if arrival_time:
                    g.add((flight_uri, AIRPORT.hasArrivalTime, Literal(arrival_time, datatype=XSD.string)))
                
                if air_time and air_time.strip():
                    duration_minutes = int(float(air_time))
                    g.add((flight_uri, AIRPORT.hasDuration, Literal(duration_minutes, datatype=XSD.integer)))
                
                if distance and distance.strip():
                    g.add((flight_uri, AIRPORT.hasDistance, Literal(distance, datatype=XSD.integer)))

    return g

if __name__ == "__main__":

    g = Graph()
    g.parse("populated_airports.owl", format="xml") # Load the populated airports ontology
    g.bind("airport", AIRPORT)
    
    print(f"Loaded ontology with {len(g)} triples")
    
    g = populate_ontology(g) # Populate the ontology
    
    g.serialize(destination="populated_flights.owl", format="xml") # Save the populated ontology
    print(f"Saved populated ontology to populated_flights.owl")