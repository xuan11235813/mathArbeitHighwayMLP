import sys
import gurobipy as gp
from gurobipy import GRB

def testCallback(model, where):
    if where == GRB.Callback.SIMPLEX:
        itcnt = model.cbGet(GRB.Callback.SPX_ITRCNT)
        print(itcnt)

def testCallbackMIPNODE(model, where):
    if where == GRB.Callback.MIPNODE:
        status = model.cbGet(GRB.Callback.MIPNODE_STATUS)
        if status == GRB.OPTIMAL:
            print(model.cbGetNodeRel(model.getVars()))
            print(model.cbGetNodeRel(model._open))
            print(model.cbGetNodeRel(model._trans))
            '''
            if rel[0] + rel[1] > 1.1:
                model.cbCut(model._vars[0] + model._vars[1] <= 1)
                '''