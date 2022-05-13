import graph as gp

def generateGraph():
    g = gp.Graph()
    g.generateRandomGraphWith(200, 0.05, 20,40,10,20)
    #g.generateRandomDemandSingleDirection(20,20,40)
    g.generateRandomDemandBidirection(60,20,40)
    g.randomlyChooseEdgeUnderConstructWithProb(0.04)
    g.showGraph()
    g.saveToFileWithName(12)

def generateGridGraph(num):
    g = gp.Graph()
    g.generateGridStarWithNum(30)
    g.showGraph()
    g.saveToFileWithName(str(num) + "tr")
def showGraphByName(num):
    g = gp.Graph()
    g.readFromFile("graph" + str(num) + ".gra")
    g.showGraph()


generateGraph()
#showGraphByName("6")