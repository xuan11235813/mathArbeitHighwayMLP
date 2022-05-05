from math import floor
import gurobipy as gp
from gurobipy import GRB
gp.setParam('OutputFlag', 0)
gp.setParam('Heuristics', 0)
gp.setParam('PreCrush', 1)
#gp.setParam('NodeLimit', 1)
gp.setParam('MIPFocus', 2)
#gp.setParam('Presolve', 0)
gp.setParam('Threads', 1)
gp.setParam('Cuts', 0)

cuttingNum = 1
directNum = 1
periodNum = 10
def testZeroCallbackMIPNODE(model,where):
    global cuttingNum
    global directNum
    if where == GRB.Callback.MIPNODE:
        status = model.cbGet(GRB.Callback.MIPNODE_STATUS)
        if status == GRB.OPTIMAL:
            print("cutting plane:" + str(directNum))
            directNum = directNum + 1



def testCallbackMIPNODE(model, where):
    global cuttingNum
    global directNum
    if where == GRB.Callback.MIPNODE:
        status = model.cbGet(GRB.Callback.MIPNODE_STATUS)
        if status == GRB.OPTIMAL:
            print("cutting plane:" + str(cuttingNum))
            cuttingNum =  cuttingNum + 1
            conCurrSetState = model.cbGetNodeRel(model._conSetState)
            value, alphaStar = solveDualConcurrentLP(model._dPairs, model._ELCIsW, conCurrSetState, model._nNum)
            model.cbCut(gp.quicksum(model._capacities[u,v]* alphaStar[u,v] * model._conSetState[u,v] for u,v in model._conEdgeSet)\
                <= gp.quicksum(model._capacities[u,v] * alphaStar[u,v] for u,v in model._edges) - 1)

def testCallbackMIPNODEWithPeriods(model, where):
    global cuttingNum
    global directNum
    if where == GRB.Callback.MIPNODE:
        status = model.cbGet(GRB.Callback.MIPNODE_STATUS)
        if status == GRB.OPTIMAL:
            print("cutting plane:" + str(cuttingNum))
            cuttingNum =  cuttingNum + 1
            conCurrSetState = model.cbGetNodeRel(model._conSetState)
            for i in model._periods:
                conCurrSetStateItem = {}
                for u,v in model._conEdgeSet:
                    conCurrSetStateItem[(u,v)] = conCurrSetState[i,u,v]
                _, alphaStar = solveDualConcurrentLP(model._dPairs, model._ELCIsW, conCurrSetStateItem, model._nNum)
                model.cbCut(gp.quicksum(model._capacities[u,v]* alphaStar[u,v] * model._conSetState[i,u,v] for u,v in model._conEdgeSet)\
                    <= gp.quicksum(model._capacities[u,v] * alphaStar[u,v] for u,v in model._edges) - 1)
                
def testCallbackInteger(model, where):
    global cuttingNum
    global directNum
    if where == GRB.Callback.MIPNODE:
        status = model.cbGet(GRB.Callback.MIPNODE_STATUS)
        if status == GRB.OPTIMAL:
            print("cutting plane:" + str(cuttingNum))
            cuttingNum =  cuttingNum + 1
            conCurrSetState = model.cbGetNodeRel(model._conSetState)
            value, alphaStar = solveDualConcurrentLP(model._dPairs, model._ELCIsW, conCurrSetState, model._nNum)
            minPara = 100000000
            for u,v in model._conEdgeSet:
                currValue = model._capacities[u,v]* alphaStar[u,v]
                if currValue > 0:
                    if currValue < minPara:
                        minPara = currValue
            lambdaValue = 1.01/minPara
            paraDict = {}
            for u,v in model._conEdgeSet:
                paraDict[(u,v)] = floor(lambdaValue * model._capacities[u,v]* alphaStar[u,v])
            rightSide = floor((sum(model._capacities[u,v] * alphaStar[u,v] for u,v in model._edges) - 1)* lambdaValue)
            model.cbCut(gp.quicksum(paraDict[u,v] * model._conSetState[u,v] for u,v in model._conEdgeSet) <= rightSide)

def solveConcurrentFlow(demandPairs, edgeLengthCapacityIsUnderConstructWeight, nodeNum):
    nodes = range(nodeNum)
    stPairs, demands =gp.multidict(demandPairs)
    edges, _, capacities, _, _  = gp.multidict(edgeLengthCapacityIsUnderConstructWeight)
    model = gp.Model('MCFlow')
    flow = model.addVars(stPairs, edges,lb=0.0, name="flow")
    delta = model.addVar(lb=0.0)

    model.setObjective(delta, GRB.MAXIMIZE)
    # capacity constraints
    for u,v in edges:
        model.addConstr(sum(flow[s,t,u,v] for s,t in stPairs) <= capacities[u,v], "cap[%s,%s]" % (u,v))
    # demand constraints & flow conservation
    for s,t in stPairs:
        for node in nodes:
            if node == s:
                model.addConstr(gp.quicksum(flow[s,t,u,v] for u,v in edges.select(node,'*'))\
                - gp.quicksum(flow[s,t,u,v] for u,v in edges.select('*', node)) == demands[s,t] * delta, "node")
            elif node == t:
                model.addConstr(gp.quicksum(flow[s,t,u,v] for u,v in edges.select(node,'*'))\
                - gp.quicksum(flow[s,t,u,v] for u,v in edges.select('*', node)) == -demands[s,t] * delta, "node")
            else:
                model.addConstr(gp.quicksum(flow[s,t,u,v] for u,v in edges.select(node,'*'))\
                - gp.quicksum(flow[s,t,u,v] for u,v in edges.select('*', node)) == 0, "node")

    model.optimize()


    obj = model.getObjective()
    return obj.getValue()
def solveConcurrentFlowUnderconstruct(demandPairs, edgeLengthCapacityIsUnderConstructWeight, nodeNum, constructParam):
    nodes = range(nodeNum)
    stPairs, demands =gp.multidict(demandPairs)
    edges, _, capacities, _, _  = gp.multidict(edgeLengthCapacityIsUnderConstructWeight)
    model = gp.Model('MCFlow')
    flow = model.addVars(stPairs, edges,lb=0.0, name="flow")
    delta = model.addVar(lb=0.0)

    for u,v in constructParam:
        capacities[u,v] = capacities[u,v] * (1 - constructParam[u,v])

    model.setObjective(delta, GRB.MAXIMIZE)
    # capacity constraints
    for u,v in edges:
        model.addConstr(sum(flow[s,t,u,v] for s,t in stPairs) <= capacities[u,v], "cap[%s,%s]" % (u,v))
    # demand constraints & flow conservation
    for s,t in stPairs:
        for node in nodes:
            if node == s:
                model.addConstr(gp.quicksum(flow[s,t,u,v] for u,v in edges.select(node,'*'))\
                - gp.quicksum(flow[s,t,u,v] for u,v in edges.select('*', node)) == demands[s,t] * delta, "node")
            elif node == t:
                model.addConstr(gp.quicksum(flow[s,t,u,v] for u,v in edges.select(node,'*'))\
                - gp.quicksum(flow[s,t,u,v] for u,v in edges.select('*', node)) == -demands[s,t] * delta, "node")
            else:
                model.addConstr(gp.quicksum(flow[s,t,u,v] for u,v in edges.select(node,'*'))\
                - gp.quicksum(flow[s,t,u,v] for u,v in edges.select('*', node)) == 0, "node")

    model.optimize()


    obj = model.getObjective()
    return obj.getValue()

def solveDirectMIPGP(demandPairs, edgeLengthCapacityIsUnderConstructWeight, constructEdgeSet, nodeNum):
    
    nodes = range(nodeNum)
    stPairs, demands =gp.multidict(demandPairs)
    edges, _, capacities, _, weight = gp.multidict(edgeLengthCapacityIsUnderConstructWeight)
    model = gp.Model('directMIP')
    flow = model.addVars(stPairs, edges, lb=0.0, name="flow")
    conSet = model.addVars(constructEdgeSet, lb=0.0, ub=1.0, vtype=GRB.BINARY, name="conSet")
    model._conSetState = conSet
    model._capacities = capacities
    model._edges = edges
    model._conEdgeSet= constructEdgeSet
    model._nNum = nodeNum
    model._dPairs = demandPairs
    model._ELCIsW = edgeLengthCapacityIsUnderConstructWeight


    model.setObjective(gp.quicksum(weight[u,v]*conSet[u,v] for u,v in constructEdgeSet), GRB.MAXIMIZE)
    for u,v in edges:
        if (u,v) in constructEdgeSet:
            model.addConstr(sum(flow[s,t,u,v] for s,t in stPairs) <= capacities[u,v] * (1 - conSet[u,v]), "cap[%s,%s]" % (u,v))
        else:
            model.addConstr(sum(flow[s,t,u,v] for s,t in stPairs) <= capacities[u,v], "cap[%s,%s]" % (u,v))
    for s,t in stPairs:
        for node in nodes:
            if node == s:
                model.addConstr(gp.quicksum(flow[s,t,u,v] for u,v in edges.select(node,'*'))\
                - gp.quicksum(flow[s,t,u,v] for u,v in edges.select('*', node)) == demands[s,t], "node")
            elif node == t:
                model.addConstr(gp.quicksum(flow[s,t,u,v] for u,v in edges.select(node,'*'))\
                - gp.quicksum(flow[s,t,u,v] for u,v in edges.select('*', node)) == -demands[s,t], "node")
            else:
                model.addConstr(gp.quicksum(flow[s,t,u,v] for u,v in edges.select(node,'*'))\
                - gp.quicksum(flow[s,t,u,v] for u,v in edges.select('*', node)) == 0, "node")

    model.optimize(testZeroCallbackMIPNODE)
    objValue = model.getObjective().getValue()
    #conSetResult = [var.X for var in model.getVars() if "conSet" in var.VarName]
    conSetResult = {}
    for u,v in conSet:
        conSetResult[u,v] = conSet[u,v].X
    

    return objValue, conSetResult


def solveDualConcurrentLP(demandPairs, edgeLengthCapacityIsUnderConstructWeight, conSetStateDict,  nodeNum):
    nodes = range(nodeNum)
    stPairs, demands =gp.multidict(demandPairs)
    edges, _, capacities, _, _ = gp.multidict(edgeLengthCapacityIsUnderConstructWeight)
    model = gp.Model('dualConcurrentLP')
    beta = model.addVars(stPairs, nodes, lb=0.0, name="beta")
    alpha = model.addVars(edges, lb=0.0, name="alpha")
    edgeNoConstruct=[]
    for u,v in edges:
        if (u,v) not in conSetStateDict:
            edgeNoConstruct.append((u,v))
    
    model.setObjective(gp.quicksum(capacities[u,v]*alpha[u,v] for u,v in edgeNoConstruct)\
        +gp.quicksum(capacities[u,v]*(1 - conSetStateDict[u,v])*alpha[u,v] for u,v in conSetStateDict),
         GRB.MINIMIZE)

    for u,v in edges:
        for s,t in stPairs:
            model.addConstr(alpha[u,v] + beta[s,t,u] - beta[s,t,v] >= 0, "beta")
    model.addConstr(gp.quicksum(demands[s,t] * (beta[s,t,t] - beta[s,t,s]) for s,t in demandPairs) == 1)

    model.optimize()
    objValue = model.getObjective().getValue()
    alphaValue = {}
    for u,v in alpha:
        alphaValue[u,v] = alpha[u,v].X
    return objValue, alphaValue


def solveMIPGPWithCut(demandPairs, edgeLengthCapacityIsUnderConstructWeight, constructEdgeSet, nodeNum):
    
    nodes = range(nodeNum)
    stPairs, demands =gp.multidict(demandPairs)
    edges, _, capacities, _, weight = gp.multidict(edgeLengthCapacityIsUnderConstructWeight)
    model = gp.Model('directMIP')
    flow = model.addVars(stPairs, edges, lb=0.0, name="flow")
    conSet = model.addVars(constructEdgeSet, lb=0.0, ub=1.0, vtype=GRB.BINARY, name="conSet")
    model._conSetState = conSet
    model._capacities = capacities
    model._edges = edges
    model._conEdgeSet= constructEdgeSet
    model._nNum = nodeNum
    model._dPairs = demandPairs
    model._ELCIsW = edgeLengthCapacityIsUnderConstructWeight


    model.setObjective(gp.quicksum(weight[u,v]*conSet[u,v] for u,v in constructEdgeSet), GRB.MAXIMIZE)
    for u,v in edges:
        if (u,v) in constructEdgeSet:
            model.addConstr(sum(flow[s,t,u,v] for s,t in stPairs) <= capacities[u,v] * (1 - conSet[u,v]), "cap[%s,%s]" % (u,v))
        else:
            model.addConstr(sum(flow[s,t,u,v] for s,t in stPairs) <= capacities[u,v], "cap[%s,%s]" % (u,v))
    for s,t in stPairs:
        for node in nodes:
            if node == s:
                model.addConstr(gp.quicksum(flow[s,t,u,v] for u,v in edges.select(node,'*'))\
                - gp.quicksum(flow[s,t,u,v] for u,v in edges.select('*', node)) == demands[s,t], "node")
            elif node == t:
                model.addConstr(gp.quicksum(flow[s,t,u,v] for u,v in edges.select(node,'*'))\
                - gp.quicksum(flow[s,t,u,v] for u,v in edges.select('*', node)) == -demands[s,t], "node")
            else:
                model.addConstr(gp.quicksum(flow[s,t,u,v] for u,v in edges.select(node,'*'))\
                - gp.quicksum(flow[s,t,u,v] for u,v in edges.select('*', node)) == 0, "node")

    model.optimize(testCallbackMIPNODE)
    objValue = model.getObjective().getValue()
    #conSetResult = [var.X for var in model.getVars() if "conSet" in var.VarName]
    conSetResult = {}
    for u,v in conSet:
        conSetResult[u,v] = conSet[u,v].X

    return objValue, conSetResult


def solveDirectMIPGPWithPeriod(demandPairs, edgeLengthCapacityIsUnderConstructWeight, constructEdgeSet, nodeNum):
    global periodNum
    nodes = range(nodeNum)
    periods = range(periodNum)
    stPairs, demands =gp.multidict(demandPairs)
    edges, _, capacities, _, weight = gp.multidict(edgeLengthCapacityIsUnderConstructWeight)
    model = gp.Model('directMIPWithPeriod')
    flow = model.addVars(periods, stPairs, edges, lb=0.0, name="flow")
    conSet = model.addVars(periods, constructEdgeSet, lb=0.0, ub=1.0, vtype=GRB.BINARY, name="conSet")
    z = model.addVar(lb=0.0, name="z")
    model._conSetState = conSet
    model._capacities = capacities
    model._edges = edges
    model._conEdgeSet= constructEdgeSet
    model._nNum = nodeNum
    model._dPairs = demandPairs
    model._ELCIsW = edgeLengthCapacityIsUnderConstructWeight
    model._periods = periods


    model.setObjective(z, GRB.MINIMIZE)
    for u,v in constructEdgeSet:
        model.addConstr(sum(conSet[i,u,v] for i in periods) == 1)
    for i in periods:
        model.addConstr(gp.quicksum(weight[u,v]*conSet[i,u,v] for u,v in constructEdgeSet) <= z)
        for u,v in edges:
            if (u,v) in constructEdgeSet:
                model.addConstr(sum(flow[i,s,t,u,v] for s,t in stPairs) <= capacities[u,v] * (1 - conSet[i,u,v]), "cap[%s,%s, %s]" % (u,v,i))
            else:
                model.addConstr(sum(flow[i,s,t,u,v] for s,t in stPairs) <= capacities[u,v], "cap[%s,%s]" % (u,v))
        for s,t in stPairs:
            for node in nodes:
                if node == s:
                    model.addConstr(gp.quicksum(flow[i,s,t,u,v] for u,v in edges.select(node,'*'))\
                    - gp.quicksum(flow[i,s,t,u,v] for u,v in edges.select('*', node)) == demands[s,t], "node")
                elif node == t:
                    model.addConstr(gp.quicksum(flow[i,s,t,u,v] for u,v in edges.select(node,'*'))\
                    - gp.quicksum(flow[i,s,t,u,v] for u,v in edges.select('*', node)) == -demands[s,t], "node")
                else:
                    model.addConstr(gp.quicksum(flow[i,s,t,u,v] for u,v in edges.select(node,'*'))\
                    - gp.quicksum(flow[i,s,t,u,v] for u,v in edges.select('*', node)) == 0, "node")

    model.optimize()
    objValue = model.getObjective().getValue()
    #conSetResult = [var.X for var in model.getVars() if "conSet" in var.VarName]
    conSetResult = []
    for i in periods:
        conSetResultItem = {}
        for u,v in constructEdgeSet:
            conSetResultItem[u,v] = conSet[i,u,v].X
        conSetResult.append(conSetResultItem)
    return objValue, conSetResult

def solveAfterFlowConstriant(demandPairs, edgeLengthCapacityIsUnderConstructWeight, constructEdgeSet, nodeNum):
    global periodNum
    nodes = range(nodeNum)
    periods = range(periodNum)
    stPairs, demands =gp.multidict(demandPairs)
    edges, _, capacities, _, weight = gp.multidict(edgeLengthCapacityIsUnderConstructWeight)
    model = gp.Model('directMIPWithPeriod')
    flow = model.addVars(periods, stPairs, edges, lb=0.0, name="flow")
    conSet = model.addVars(periods, constructEdgeSet, lb=0.0, ub=1.0, vtype=GRB.BINARY, name="conSet")
    z = model.addVar(lb=0.0, name="z")
    model._conSetState = conSet
    model._capacities = capacities
    model._edges = edges
    model._conEdgeSet= constructEdgeSet
    model._nNum = nodeNum
    model._dPairs = demandPairs
    model._ELCIsW = edgeLengthCapacityIsUnderConstructWeight
    model._periods = periods

    model.setObjective(z, GRB.MINIMIZE)
    for u,v in constructEdgeSet:
        model.addConstr(sum(conSet[i,u,v] for i in periods) == 1)
    for i in periods:
        model.addConstr(gp.quicksum(weight[u,v]*conSet[i,u,v] for u,v in constructEdgeSet) <= z)
    flag  = True
    conSetResult = []
    objValue = 0
    while flag == True:
        model.optimize()
        objValue = model.getObjective().getValue()
        print(objValue)
        conSetResult = []
        for i in periods:
            conSetResultItem = {}
            for u,v in constructEdgeSet:
                conSetResultItem[u,v] = conSet[i,u,v].X
            conSetResult.append(conSetResultItem)
        flag = False
        for conSetItem in conSetResult:
            value = solveConcurrentFlowUnderconstruct(demandPairs, edgeLengthCapacityIsUnderConstructWeight, nodeNum, conSetItem)
            if value < 1:
                
                for i in range(periodNum):
                    model.addConstr(gp.quicksum(conSetItem[u,v] * model._conSetState[i,u,v] for u,v in model._conEdgeSet)\
                        <= sum(conSetItem[u,v] for u,v in model._conEdgeSet) - 1)
                
                _, alphaStar = solveDualConcurrentLP(demandPairs, edgeLengthCapacityIsUnderConstructWeight, conSetItem,  nodeNum)
                for i in range(periodNum):
                    model.addConstr(gp.quicksum(model._capacities[u,v]* alphaStar[u,v] * model._conSetState[i,u,v] for u,v in model._conEdgeSet)\
                        <= gp.quicksum(model._capacities[u,v] * alphaStar[u,v] for u,v in model._edges) - 1)
                        
                flag = True
    return objValue, conSetResult

