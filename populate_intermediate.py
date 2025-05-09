import csv
from rdflib import Graph, Namespace, Literal, URIRef, XSD
from rdflib.namespace import RDF, RDFS
import re

# Helper to convert time values
def format_time(time_value):
    if not time_value or time_value == "":
        return None
    
    # Convert to string and ensure 4 digits (add leading zeros if needed)
    time_str = str(int(float(time_value))).zfill(4)
    
    # Format as HH:MM
    if len(time_str) == 4:
        return f"{time_str[:2]}:{time_str[2:]}"
    return None

# Load existing ontology
g = Graph()
g.parse("populated_airports.owl", format="xml")

AIRPORT = Namespace("http://www.semanticweb.org/marikaitiprimenta/ontologies/2025/4/airports#")
g.bind("airport", AIRPORT)

# Helper to make a safe URI
def sanitize_for_uri(text):
    return re.sub(r'\W+', '_', text.strip())

# Build a map of IATA code → Airport URI
iata_map = {}
for s, p, o in g.triples((None, AIRPORT.hasIATACode, None)):
    iata_map[str(o)] = s

# Keep track of added airline individuals
added_airlines = {}

# Read the flight CSV
with open("flights.csv") as f:
    reader = csv.reader(f)
    counter = 0
    for row in reader:
        if counter == 0:
            counter += 1
            continue  # Skip header
        src_iata = row[13]
        dst_iata = row[14]
        airline = row[20]
        flight_number = row[11]

        # Extract time-related data
        dep_time = format_time(row[4])
        arr_time = format_time(row[7])
        air_time = row[15]  # Duration in minutes
        distance = row[16]  # Distance in miles
        date_str = f"{row[1]}-{row[2]}-{row[3]}"

        # Match IATA codes to Airport individuals
        if src_iata in iata_map and dst_iata in iata_map:
            src_airport = iata_map[src_iata]
            dst_airport = iata_map[dst_iata]

            # Add Flight
            flight_uri = URIRef(AIRPORT + f"Flight_{src_iata}_{dst_iata}_{sanitize_for_uri(airline)}")
            g.add((flight_uri, RDF.type, AIRPORT.Flight))
            g.add((flight_uri, AIRPORT.hasDepartureAirport, src_airport))
            g.add((flight_uri, AIRPORT.hasArrivalAirport, dst_airport))
            g.add((flight_uri, AIRPORT.operatedBy, Literal(airline)))

            # Add Airline as individual of class Airline
            if airline not in added_airlines:
                airline_uri = AIRPORT[f"Airline_{sanitize_for_uri(airline)}"]
                g.add((airline_uri, RDF.type, AIRPORT.Airline))
                g.add((airline_uri, RDFS.label, Literal(airline, lang="en")))
                added_airlines[airline] = airline_uri

            g.add((flight_uri, AIRPORT.operatedBy, added_airlines[airline]))

            # Add time-related data properties
            if dep_time:
                g.add((flight_uri, AIRPORT.hasDepartureTime, Literal(dep_time, datatype=XSD.string)))
            
            if arr_time:
                g.add((flight_uri, AIRPORT.hasArrivalTime, Literal(arr_time, datatype=XSD.string)))
            
            if air_time and air_time.strip():
               
                duration_minutes = int(float(air_time))
                # Store duration in minutes
                g.add((flight_uri, AIRPORT.hasDuration, Literal(duration_minutes, datatype=XSD.integer)))
            
            if distance and distance.strip():
               g.add((flight_uri, AIRPORT.hasDistance, Literal(distance, datatype=XSD.integer)))
            

print(f"Ontology now has {len(g)} triples")
g.serialize("populated_flights.owl", format="xml")