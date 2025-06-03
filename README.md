# Airport and Flight Ontology 

Description
-----------

This project is part of the ECS7028P Data Semantics module at Queen Mary University of London.

The main goal of this project is to build a clear and organised semantic model of airports and flights that allows for advanced searching across different aviation data sources. This ontology connects information such as airport locations, flight details, and service data in a meaningful way. By combining data that would normally be separate, it helps users ask more complex questions and discover new insights.

Requirements
------------

Download `Protégé` software tool from [here](https://protege.stanford.edu). Use this tool to view the ontologies (.owl files).


Run the code
-----------
Python version: `3.9`

1. First run the populate_basic.py using the command: 

    ```
    python populate_basic.py 
    ```
    
    This script retrieves airport data from Wikidata via a SPARQL query and  populates the ontology, producing the output file populated_airports.owl. 

2. To verify the ontology, run the query_basic.py using the command: 

    ```
    python query_basic.py 
    ```
    
    This script allows querying the airport ontology to check if the data was populated correctly. 

3. Then, for the intermediate task, run the populate_intermediate.py as: 
 
    ```
    python populate_intermediate.py 
    ```
    
    This script reads flight information from the CSV file and adds it to the existing ontology, resulting in populated_flights.owl. 

4. Again, to verify the ontology, run the query_intermediate.py using: 
 
    ```
    python query_intermediate.py 
    ```
    This script enables querying both airport and flight data from the populated ontology. 

5. For the advanced task, open the populated_flights.owl in protege and run  the SWRL rules in the SWRLTab. If it becomes unresponsive, try running  one rule at a time to avoid overloading the reasoner.