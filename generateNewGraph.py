import graph as gp

def generateGraph():
    g = gp.Graph()
    g.generateRandomGraphWith(150, 0.02, 20,40,10,20)
    g.generateRandomDemand(80,20,40)
    g.randomlyChooseEdgeUnderConstructWithProb(0.3)
    g.showGraph()
    g.saveToFileWithName(9)

def generateGridGraph(num):
    g = gp.Graph()
    g.generateGridStarWithNum(30)
    g.showGraph()
    g.saveToFileWithName(str(num) + "tr")
def showGraphByName(num):
    g = gp.Graph()
    g.readFromFile("graph" + str(num) + ".gra")
    g.showGraph()


generateGridGraph(10)
#showGraphByName(7)