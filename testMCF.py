from ctypes import sizeof
import gurobipy as gp
from gurobipy import GRB
import networkx as nx
import matplotlib.pyplot as plt


graphNodeNum = 5

nodes = [0,1,2,3,4]

stPairs, demands =gp.multidict({
    (0,4): 10,
    (1,3): 20,
    (2,4): 10,
    (4,1): 30
})

edges, lengths, capacities = gp.multidict({
    (0,1): [3,10],
    (1,0): [3,20],
    (0,3): [2,25],
    (3,0): [2,20],
    (0,2): [2,15],
    (2,0): [2,20],
    (2,3): [3.5,10],
    (3,2): [3.5,10],
    (2,1): [4,20],
    (1,2): [4,10],
    (2,4): [5,30],
    (4,2): [5,45]
})



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


G = nx.DiGraph()
for nodeItem in nodes:
    attrStr = ":"
    for i in range(len(stPairs)):
        if stPairs[i][0] == nodeItem:
            attrStr += "s"+ str(i) + ","
    G.add_node(nodeItem, id=str(nodeItem) + attrStr)
for edgeItem in edges:
    G.add_edge(edgeItem[0], edgeItem[1])
labels = nx.get_node_attributes(G, 'id') 
nx.draw(G, labels=labels)
plt.show()