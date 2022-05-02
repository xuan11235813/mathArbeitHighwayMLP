import graph as gp

def generateGraph():
    g = gp.Graph()
    g.generateRandomGraphWith(80, 0.3, 20,40,10,20)
    g.generateRandomDemand(20,15,30)
    g.randomlyChooseEdgeUnderConstructWithProb(0.2)
    g.showGraph()
    g.saveToFileWithName(3)

def showGraphByName(num):
    g = gp.Graph()
    g.readFromFile("graph" + str(num) + ".gra")
    g.showGraph()
'''
g.readFromFile("graph0.gra")
g.showGraph()

print(g.generateSTPairDemands())
print(g.generateEdgeLengthCapacity())
print(g.generateEdgeLengthCapacityIsUnderconstructWeight())
print(g.generateConstructSet())
'''

#generateGraph()
showGraphByName(3)