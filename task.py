import graph as gp
import lpAlgorithms as lpa

def refineNetwork():
    g = gp.Graph()
    g.readFromFile("graph0.gra")
    rate = lpa.solveConcurrentFlow(g.generateSTPairDemands(), g.generateEdgeLengthCapacity(), g.getNodeNum())
    print(rate)
    g.refineDemand(rate)
    g.saveToFileWithName("2")

def checkNetworkCFRate():
    g = gp.Graph()
    g.readFromFile("graph2.gra")
    rate = lpa.solveConcurrentFlow(g.generateSTPairDemands(), g.generateEdgeLengthCapacity(), g.getNodeNum())
    print("Concurrent maximal delta: " + str(rate))

def calculateDirectMIP():
    g = gp.Graph()
    g.readFromFile("graph2.gra")
    value, conSetState = lpa.solveDirectMIPGP(g.generateSTPairDemands(),\
        g.generateEdgeLengthCapacityIsUnderconstructWeight(),\
        g.generateConstructSet(), g.getNodeNum())
    print("Maximal result from direct MIP using gurobi: "+ str(value))
    #test result
    sum = 0
    for u,v in conSetState:
        sum = sum + conSetState[u,v]*g.generateEdgeLengthCapacityIsUnderconstructWeight()[u,v][3]
    print("Check the result by variables: " + str(sum))

def checkEmptyDualCCF():
    g = gp.Graph()
    g.readFromFile("graph2.gra")
    emptyDict = {}
    value, _ = lpa.solveDualConcurrentLP( g.generateSTPairDemands(),\
        g.generateEdgeLengthCapacityIsUnderconstructWeight(), emptyDict, g.getNodeNum())
    print("Empty construction set dual test: "+str(value))

def calculateMetIneqCutMIP():
    g = gp.Graph()
    g.readFromFile("graph2.gra")
    value, conSetState = lpa.solveMIPGPWithCut(g.generateSTPairDemands(),\
        g.generateEdgeLengthCapacityIsUnderconstructWeight(),\
        g.generateConstructSet(), g.getNodeNum())
    print("Maximal result from metric inequalities cut: "+ str(value))
    #test result
    sum = 0
    for u,v in conSetState:
        sum = sum + conSetState[u,v]*g.generateEdgeLengthCapacityIsUnderconstructWeight()[u,v][3]
    print("Check the result by variables: " + str(sum))

checkNetworkCFRate()
checkEmptyDualCCF()
calculateDirectMIP()
calculateMetIneqCutMIP()