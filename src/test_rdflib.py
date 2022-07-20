from rdflib import Graph, Namespace, Literal, RDF, XSD

# base = "http://test.com/ns#"
foobar = Namespace("http://test.com/ns")
g = Graph() #base = base)
# x = Namespace("http://www.w3.org/2001/XMLSchema#xxx" )
g.bind('foobar', foobar)
# g.bind('gugus', x )

g.add((foobar.something, XSD.string, Literal("hello")))
g.add((foobar.something, XSD.integer, Literal("12")))

g.add((foobar.something, RDF.type, Literal('Blah')))
g.add((foobar.something, foobar.contains, Literal('a property')))

g.add((foobar.anotherthing, RDF.type, Literal('Blubb')))
g.add((foobar.anotherthing, foobar.contains, Literal('another property')))

print(g.serialize(format='turtle'))
