import gurobipy as gp
from gurobipy import GRB

def solveGraph(demandPairs, edgeLengthCapacity, nodeNum):
    nodes = range(nodeNum)
    stPairs, demands =gp.multidict(demandPairs)
    edges, lengths, capacities = gp.multidict(edgeLengthCapacity)
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


    solution = model.getAttr('X', flow)
    print(delta)