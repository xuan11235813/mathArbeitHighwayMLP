import graph as gp

g = gp.Graph()
'''
g.generateRandomGraphWith(20, 0.2, 20,40)
g.generateRandomDemand(20,15,30)
g.showGraph()
g.saveToFileWithName(0)
'''
g.readFromFile("graph0.gra")
g.saveToFileWithName(1)
g.showGraph()
'''
print(g.generateSTPairDemands())
print(g.generateEdgeLengthCapacity())
'''