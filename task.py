import graph as gp
import lpAlgorithms as lpa
g = gp.Graph()

g.readFromFile("graph0.gra")
lpa.solveGraph(g.generateSTPairDemands(), g.generateEdgeLengthCapacity(), g.getNodeNum())