import graph as gp
import lpAlgorithms as lpa

def refineNetwork(num):
    g = gp.Graph()
    g.readFromFile("graph"+ str(num) +".gra")
    rate = lpa.solveConcurrentFlow(g.generateSTPairDemands(), g.generateEdgeLengthCapacity(), g.getNodeNum())
    print(rate)
    g.refineDemand(rate)
    g.saveToFileWithName(str(num) + "r")

def checkNetworkCFRateDirect(num):
    g = gp.Graph()
    g.readFromFile("graph"+ str(num) +".gra")
    rate = lpa.solveConcurrentFlow(g.generateSTPairDemands(), g.generateEdgeLengthCapacity(), g.getNodeNum())
    print("Concurrent maximal delta: " + str(rate))

def checkNetworkCFRate(num):
    g = gp.Graph()
    g.readFromFile("graph"+ str(num) + "r" +".gra")
    rate = lpa.solveConcurrentFlow(g.generateSTPairDemands(), g.generateEdgeLengthCapacity(), g.getNodeNum())
    print("Concurrent maximal delta: " + str(rate))

def calculateDirectMIP(num):
    g = gp.Graph()
    g.readFromFile("graph"+ str(num) + "r" +".gra")
    value, conSetState = lpa.solveDirectMIPGP(g.generateSTPairDemands(),\
        g.generateEdgeLengthCapacityIsUnderconstructWeight(),\
        g.generateConstructSet(), g.getNodeNum())
    print("Maximal result from direct MIP using gurobi: "+ str(value))
    #test result
    sum = 0
    for u,v in conSetState:
        sum = sum + conSetState[u,v]*g.generateEdgeLengthCapacityIsUnderconstructWeight()[u,v][3]
    print("Check the result by variables: " + str(sum))

def checkEmptyDualCCF(num):
    g = gp.Graph()
    g.readFromFile("graph"+ str(num)+ "r" +".gra")
    emptyDict = {}
    value, _ = lpa.solveDualConcurrentLP( g.generateSTPairDemands(),\
        g.generateEdgeLengthCapacityIsUnderconstructWeight(), emptyDict, g.getNodeNum())
    print("Empty construction set dual test: "+str(value))

def calculateMetIneqCutMIP(num):
    g = gp.Graph()
    g.readFromFile("graph"+ str(num)+ "r" +".gra")
    value, conSetState = lpa.solveMIPGPWithCut(g.generateSTPairDemands(),\
        g.generateEdgeLengthCapacityIsUnderconstructWeight(),\
        g.generateConstructSet(), g.getNodeNum())
    print("Maximal result from metric inequalities cut: "+ str(value))
    #test result
    sum = 0
    for u,v in conSetState:
        sum = sum + conSetState[u,v]*g.generateEdgeLengthCapacityIsUnderconstructWeight()[u,v][3]
    print("Check the result by variables: " + str(sum))

def testFlow(num):
    refineNetwork(num)
    checkNetworkCFRate(num)
    checkEmptyDualCCF(num)
    calculateDirectMIP(num)
    calculateMetIneqCutMIP(num)


testFlow(3)