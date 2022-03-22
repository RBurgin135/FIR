#=========================wall of Richard Burgins hard work, may it stand eternal and unto it I pledge my life======================================================
#===================================================================================================================================================================
#===================================================================================================================================================================

import copy
import math
import random
import numpy

#Objects==========
class NeuralNet:
    def __init__(self):
        #               left, right, speed control
        self.topnum = 3 #number of topologies
        self.layernum = [3, 3, 3] #number of layers
        self.neuronnum = [[2,2,1], [2,2,1], [4,3,1]] #neurons for each layer
        self.inputnum = [[1,2,2], [1,2,2], [1,4,3]] #inputs for each layer

        self.layers = []
        for t in range(self.topnum): #cycles through the topologies
            self.layers.append([]) #adds new topology
            for l in range(self.layernum[t]): #cycles through the layers
                self.layers[t].append([]) #adds new layer
                for _ in range(self.neuronnum[t][l]): #cycles through the neurons
                    self.layers[t][l].append(Neuron(self.inputnum[t][l])) #adds new neuron

        #meta
        self.score = 0
        self.state = "new"

    def Forward(self, inputs):
        outputs = []
        for t in range(self.topnum): #cycles through topologies
            for l in range(self.layernum[t]): #cycles through layers
                if l != 0: #input layer
                    thislayer = copy.deepcopy(nextlayer)
                nextlayer = []
                
                for n in range(self.neuronnum[t][l]): #cycles through neurons
                    if l == 0:#if input nodes
                        nextlayer.append(self.layers[t][l][n].ActivationFunction([inputs[t][n]]))
                    elif l == self.layernum[t]-1: #if output nodes
                        outputs.append(self.layers[t][l][n].ActivationFunction(thislayer))
                    else: #the rest
                        nextlayer.append(self.layers[t][l][n].ActivationFunction(thislayer))
        return outputs

    def Scoring(self, details):
        self.score = 0
        self.score += details[0]
        #self.score -= details[1]
       
#======= 
class Neuron:
    def __init__(self, inputnumber):
        self.inputnumber = inputnumber
        self.bias = 0
        self.weight = []
        for _ in range(self.inputnumber):
            self.weight.append(random.uniform(-1,1))
        self.weightnum = len(self.weight)
        self.activated = False
    
    def ActivationFunction(self, processinginput):
        total = sum(numpy.multiply(processinginput,self.weight))
        return (self.passing(total)+ self.bias)

    def ReLU(self, x):
        result = max(x, 0)
        return result

    def sigmoid(self, x):
        try:
            result = 1/(1+math.exp(-x))
        except:
            OverflowError
            if x > 0.5:
                result = 1
            else:
                result = 0

        return result

    def step(self, x):
        if x > 0:
            self.activated = True
            return 1
        else:
            self.activated = False
            return -1

    def passing(self, x):
        if x > 0:
            self.activated = True
        else:
            self.activated = False

        return x

#Functions==========
def Review(pop):
    #numbers
    clonenumber = 1

    #initiation
    netlists = []
    for i in pop:
        net = i.Nn
        net.Scoring(i.scoringvalues)
        netlists.append(net)
        net.state = "processing"
    netlists = Sort(netlists)

    #clone
    cloned = []
    for i in range(clonenumber):
        x = netlists[i]
        x.state = "cloned"
        cloned.append(x)

    #mutate
    mutated = []
    for i in range(len(pop)-clonenumber):
        z = Mutate(copy.deepcopy(random.choice(cloned)))
        if z.state != "bred":
            z.state = "mutated" 
        mutated.append(z)

    #export
    z = cloned + mutated
    return z

def Sort(List):
    #Bubble sort
    Sorted = False
    while Sorted == False:
        Sorted = True
        for i in range(0, len(List)-1):
            if List[i].score < List[i+1].score:
                Sorted = False
                Buffer = List[i]
                List[i] = List[i+1]
                List[i+1] = Buffer


    return List

def Mutate(net):
    #Fence is the max degree of mutation, prob is the likelihood of mutating
    fence = 0.5
    prob = 1
    
    #inputs
    for t in net.layers: #cycles through topologies
        for l in t: #cycles through layers
            for n in l: #cycles through neurons
                for w in n.weight: #cycles through weights
                    if random.random() < prob:
                        w += random.uniform(-fence, fence) #mutate weights
                if random.random() < prob:
                    n.bias += random.uniform(-fence, fence) #mutate bias

    return net

def Breed(ParentA,ParentB):
    Child = NeuralNet()

    Net = ParentA
    for t in range(Net.topnum): #cycles through topologies
        for l in range(Net.layernum[t]): #cycles through layers
            for n in range(Net.neuronnum[t][l]): #cycles through neurons
                for w in range(Net.layers[t][l][n].weightnum): #cycles through weights
                    Child.layers[t][l][n].weight[w] = (ParentA.layers[t][l][n].weight[w] + ParentB.layers[t][l][n].weight[w])/2 #finds average between two parent weights
                Child.layers[t][l][n].bias = (ParentA.layers[t][l][n].bias + ParentB.layers[t][l][n].bias)/2 #finds average between two parent biases

    return Child

def Write(gennumber, pop, name):
    f = open("files\\savefiles\\"+name+".txt", "w")
    Nets = []
    for i in range(0,len(pop)):
        Nets.append(pop[i].Nn)

    #encodes the data
    f.write((str(gennumber)+","))
    for z in Nets: #cycles through the nets
        f.write("N,")
        for t in z.layers: #cycles through topologies
            f.write("T,")
            for l in t: #cycles through layers
                f.write("L,")
                for n in l: #cycles through neurons
                    f.write("n,")
                    for w in n.weight: #cycles through weights
                        f.write(("w,"+str(w)+","))
                    f.write(("b,"+str(n.bias)+","))
    f.close()

def Read(pop, name):
    f = open("files\\savefiles\\"+name+".txt", "r")

    #nets
    newnets = []
    for i in range(0, len(pop)):
        newnets.append(NeuralNet())

    #decodes the data
    block = f.readline()
    chunks = block.split(",")
    #declaring indexes
    Ni = -1
    gennumber = int(chunks[0])
    for i in range(len(chunks)):
        if chunks[i] == "N":#cycles through the nets
            Ni += 1
            Ti = -1
        if chunks[i] == "T":#cycles through the topologies 
            Ti += 1
            Li = -1
        if chunks[i] == "L":#cycles through the layers
            Li += 1
            ni = -1
        if chunks[i] == "n":#cycles through neurons
            ni += 1
            wi = -1
        if chunks[i] == "w":#cycles through weights
            wi += 1
            newnets[Ni].layers[Ti][Li][ni].weight[wi] = float(chunks[i+1])
        if chunks[i] == "b":
            newnets[Ni].layers[Ti][Li][ni].bias = float(chunks[i+1])
    f.close()

    #resets pawns
    for i in range(len(pop)):
        pop[i].NewGenReset(newnets[i])

    return pop, gennumber