import rdflib

# create a neo4j backed Graph
g = rdflib.Graph(store='neo4j-n10s')

# set the configuration to connect to your Neo4j DB 
theconfig = {'uri': "bolt://localhost:11006", 'database': 'neo4j', 'auth': {'user': "vinay", 'pwd': "periconto"}}

g.open(theconfig, create = False)

g.parse("https://github.com/heinz-preisig/PeriConto/blob/main/ontologyRepository/ontology_kg.ttl", "Turtle")


print("--- Success!: coating knowledge graph loaded ---")



# A more Pyhonic approach to access neo4j DB using neo4j.GraphDatabase. 
# ...............................  

# from neo4j import GraphDatabase
# class HelloWorldExample:

#     def __init__(self, uri, user, password):
#         self.driver = GraphDatabase.driver(uri, auth=(user, password))

#     def close(self):
#         self.driver.close()

#     def print_greeting(self, message):
#         with self.driver.session() as session:
#             greeting = session.execute_write(self._create_and_return_greeting, message)
#             print(greeting)

#     @staticmethod
#     def _create_and_return_greeting(tx, message):
#         result = tx.run("CREATE (a:Greeting) "
#                         "SET a.message = $message "
#                         "RETURN a.message + ', from node ' + id(a)", message=message)
#         return result.single()[0]


# if __name__ == "__main__":
#     greeter = HelloWorldExample("bolt://localhost:7687", "neo4j", "test")
#     greeter.print_greeting("hello, world")
#     greeter.close()