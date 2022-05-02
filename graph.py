import random as rd
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime


class Node:
    nodeIndex = 0
    def __init__(self, nodeIndex):
        self.nodeIndex = nodeIndex

class Demand:
    sourceNodeIndex = 0
    targetNodeIndex = 0
    localDemand = 0
    def __init__(self, sourceNodeIndex, targetNodeIndex, localDemand):
        self.sourceNodeIndex = sourceNodeIndex
        self.targetNodeIndex = targetNodeIndex
        self.localDemand = localDemand
class DirectedEdge:
    # from u to v
    uIndex = 0
    vIndex = 0
    length = 0.0
    capacity = 0.0
    weight = 0.0
    isUnderConstruct = 0
    def __init__(self, uIndex, vIndex, length, capacity, weight):
        self.uIndex = uIndex
        self.vIndex = vIndex
        self.length = length
        self.capacity = capacity
        self.weight = weight


class Graph:
    nodes = []
    edges = []
    demands = []

    def __init__(self):
        self.nodes = []
        self.edges = []
    
    def setWitNodesAndEdges(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges

    def generateRandomGraphWith(self, nodeNum, edgeGenerationProbability, capacityLB, capacityUB, weightLB, weightUB):
        for i in range(nodeNum):
            nodeItem = Node(i)
            self.nodes.append(nodeItem)
        for i in range(nodeNum):
            for j in range(nodeNum):
                if rd.uniform(0, 1) <= edgeGenerationProbability and i < j:
                    edgeItem = DirectedEdge(i,j,float(round(rd.uniform(1,11))),\
                        float(round(rd.uniform(capacityLB,capacityUB))), \
                        float(round(rd.uniform(weightLB,weightUB))))
                    edgeItemInverse = DirectedEdge(edgeItem.vIndex,edgeItem.uIndex,edgeItem.length,edgeItem.capacity, edgeItem.weight)
                    self.edges.append(edgeItem)
                    self.edges.append(edgeItemInverse)
        

    def generateRandomDemand(self, demandNum, demandLB, demandUB):
        if len(self.nodes) * (len(self.nodes) - 1) * 0.3 <= demandNum:
            return False
        else:
            rate = demandNum/(len(self.nodes) * (len(self.nodes) - 1))
            for i in range(len(self.nodes)):
                for j in range(len(self.nodes)):
                    if rd.uniform(0, 1) <= rate and i != j:
                        demandItem = Demand(i,j, float(round(rd.uniform(demandLB, demandUB))))
                        self.demands.append(demandItem)
            return True
    
    def showGraph(self):
        G = nx.DiGraph()
        for nodeItem in self.nodes:
            G.add_node(nodeItem.nodeIndex, id=str(nodeItem.nodeIndex))
        for edgeItem in self.edges:
            if edgeItem.isUnderConstruct == 1:
                G.add_edge(edgeItem.uIndex, edgeItem.vIndex, color = 'r')
            else:
                G.add_edge(edgeItem.uIndex, edgeItem.vIndex, color = 'g')
        edges = G.edges()
        pos = nx.kamada_kawai_layout(G)
        colors = [G[u][v]['color'] for u,v in edges]
        labels = nx.get_node_attributes(G, 'id') 
        nx.draw(G, pos, labels=labels, edge_color = colors)
        plt.show()
    def saveToFile(self):
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        filetime = round(timestamp)
        filetime = filetime - int(filetime/10000) * 10000 
        f = open("data/graph"+ str(filetime) + '.gra', 'w')
        f.write(str(len(self.nodes))+ '\n')
        for i in range(len(self.nodes)):
            f.write(str(self.nodes[i].nodeIndex) + '\n')
        f.write(str(len(self.edges))+ '\n')
        for i in range(len(self.edges)):
            f.write(str(self.edges[i].uIndex) + ',')
            f.write(str(self.edges[i].vIndex) + ',')
            f.write(str(self.edges[i].length) + ',')
            f.write(str(self.edges[i].capacity) + ',')
            f.write(str(self.edges[i].isUnderConstruct) + ',')
            f.write(str(self.edges[i].weight) + '\n')
        f.write(str(len(self.demands)) + '\n')
        for i in range(len(self.demands)):
            f.write(str(self.demands[i].sourceNodeIndex) + ',')
            f.write(str(self.demands[i].targetNodeIndex) + ',')
            f.write(str(self.demands[i].localDemand) + '\n')
    def saveToFileWithName(self, fileName):
        f = open("data/graph"+ str(fileName)+ '.gra', 'w')
        f.write(str(len(self.nodes))+ '\n')
        for i in range(len(self.nodes)):
            f.write(str(self.nodes[i].nodeIndex) + '\n')
        f.write(str(len(self.edges))+ '\n')
        for i in range(len(self.edges)):
            f.write(str(self.edges[i].uIndex) + ',')
            f.write(str(self.edges[i].vIndex) + ',')
            f.write(str(self.edges[i].length) + ',')
            f.write(str(self.edges[i].capacity) + ',')
            f.write(str(self.edges[i].isUnderConstruct) + ',')
            f.write(str(self.edges[i].weight) + '\n')
        f.write(str(len(self.demands)) + '\n')
        for i in range(len(self.demands)):
            f.write(str(self.demands[i].sourceNodeIndex) + ',')
            f.write(str(self.demands[i].targetNodeIndex) + ',')
            f.write(str(self.demands[i].localDemand) + '\n')
    def readFromFile(self, filename):
        f = open("data/" + filename,'r')
        lines = f.readlines()
        self.nodes = []
        self.edges = []
        self.demands = []
        state = 0
        readNum = 0
        count = 0
        for line in lines:
            if state == 0:
                readNum = int(line)
                state = 1
                count = 0
            elif state == 1 and readNum != 0:
                nodeItem = Node(int(line))
                self.nodes.append(nodeItem)
                count = count + 1
                if count == readNum:
                    state = 2
            elif state == 2:
                readNum = int(line)
                state = 3
                count = 0
            elif state == 3 and readNum != 0:
                data = line.split(",")
                edgeItem = DirectedEdge(int(data[0]), int(data[1]), float(data[2]), float(data[3]), float(data[5]))
                edgeItem.isUnderConstruct = int(data[4])
                self.edges.append(edgeItem)
                count = count + 1
                if count  ==  readNum:
                    state = 4
            elif state == 4:
                readNum = int(line)
                state = 5
                count = 0
            elif readNum != 0:
                data = line.split(",")
                demandItem = Demand(int(data[0]), int(data[1]), float(data[2]))
                self.demands.append(demandItem)
    def generateSTPairDemands(self):
        returnDemands = {}
        for item in self.demands:
            pos = (item.sourceNodeIndex, item.targetNodeIndex)
            returnDemands[pos] = item.localDemand
        return returnDemands
    def generateEdgeLengthCapacity(self):
        returnLC = {}
        for item in self.edges:
            pos = (item.uIndex, item.vIndex)
            value = [item.length, item.capacity]
            returnLC[pos] = value
        return returnLC
    def generateEdgeLengthCapacityIsUnderconstruct(self):
        returnLCIsC = {}
        for item in self.edges:
            pos = (item.uIndex, item.vIndex)
            value = [item.length, item.capacity, item.isUnderConstruct]
            returnLCIsC[pos] = value
        return returnLCIsC
    def generateEdgeLengthCapacityIsUnderconstructWeight(self):
        returnLCIsCW = {}
        for item in self.edges:
            pos = (item.uIndex, item.vIndex)
            value = [item.length, item.capacity, item.isUnderConstruct, item.weight]
            returnLCIsCW[pos] = value
        return returnLCIsCW
    def generateConstructSet(self):
        constructSet = []
        for item in self.edges:
            pos = (item.uIndex, item.vIndex)
            value = item.isUnderConstruct
            if value == 1:
                constructSet.append(pos)
        return constructSet
    def getNodeNum(self):
        return len(self.nodes)
    def refineDemand(self, rate):
        for item in self.demands:
            item.localDemand = item.localDemand * rate * 0.9
    def randomlyChooseEdgeUnderConstructWithProb(self, prob):
        for item in self.edges:
            if rd.uniform(0, 1) <= prob and item.vIndex <item.uIndex:
                item.isUnderConstruct = 1
                for itemA in self.edges:
                    if itemA.uIndex == item.vIndex and itemA.vIndex == item.uIndex:
                        itemA.isUnderConstruct = 1


