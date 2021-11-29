# Importamos las clases que se requieren para manejar los agentes (Agent) y su entorno (Model).
# Cada modelo puede contener múltiples agentes.
import random
from mesa import Agent, Model, model

# Debido a que necesitamos que existe un solo agente por celda, elegimos ''SingleGrid''.
from mesa.space import MultiGrid, SingleGrid

# Con ''SimultaneousActivation, hacemos que todos los agentes se activen ''al mismo tiempo''.
from mesa.time import SimultaneousActivation

# Haremos uso de ''DataCollector'' para obtener información de cada paso de la simulación.
from mesa.datacollection import DataCollector

# Importamos los siguientes paquetes para el mejor manejo de valores numéricos.
import numpy as np
import pandas as pd

import math

def get_grid(model):
    width=model.agentGrid.width
    height =model.agentGrid.height
    grid = np.zeros( (width,height) )
    for i in range(width):
        for j in range(height):
            grid[i][j] = model.storage[i][j]
    
    return grid


class RobotAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.hasBox =0
        self.dir=-1
    def step(self):    
       
        if not self.hasBox:
            #busca una caja
            if(self.boxInNeighbourgs(self.pos[0],self.pos[1])):
                self.hasBox =1
            #si no hay una caja cerca avanza
            else:
                newpos= self.getNewPos()
                self.model.storage[self.pos[0]][self.pos[1]] =0
                self.pos=newpos
                self.model.storage[newpos[0]][newpos[1]] =5

        else:
            #busca un stack
            if(self.stackInNeighbourgs(self.pos[0],self.pos[1])):
                self.hasBox =0
                self.model.unsortedBoxes-=1
            #si no hay una caja cerca avanza
            else:
                newpos= self.getNewPos()
                self.model.storage[self.pos[0]][self.pos[1]] =0
                self.pos=newpos
                self.model.storage[newpos[0]][newpos[1]] =5

    def boxInNeighbourgs(self,x,y):
        if(self.model.validCoor(x+1,y) and self.model.storage[x+1][y] ==1):
            self.model.storage[x+1][y]=0
            return True
        elif(self.model.validCoor(x-1,y) and self.model.storage[x-1][y] ==1):
            self.model.storage[x-1][y]=0
            return True
        elif(self.model.validCoor(x,y+1) and self.model.storage[x][y+1] ==1):
            self.model.storage[x][y+1]=0
            return True
        elif(self.model.validCoor(x,y-1) and self.model.storage[x][y-1] ==1):
            self.model.storage[x][y-1]=0
            return True
        return False

    def stackInNeighbourgs(self,x,y):
        #stack with 1 
        if(self.model.validCoor(x+1,y) and self.model.storage[x+1][y] ==-1 ):
            self.model.storage[x+1][y]=2
            self.model.unsortedBoxes-=1
            return True
        elif(self.model.validCoor(x-1,y) and self.model.storage[x-1][y] ==-1 ):
            self.model.storage[x-1][y]=2
            self.model.unsortedBoxes-=1
            return True
        elif(self.model.validCoor(x,y+1) and self.model.storage[x][y+1] ==-1 ):
            self.model.storage[x][y+1]=2
            self.model.unsortedBoxes-=1
            return True
        elif(self.model.validCoor(x,y-1) and self.model.storage[x][y-1] ==-1 ):
            self.model.storage[x][y-1]=2
            self.model.unsortedBoxes-=1
            return True
        #stack with <5
        elif(self.model.validCoor(x+1,y) and self.model.storage[x+1][y] >1 and self.model.storage[x+1][y] <5 ):
            self.model.storage[x+1][y]+=1
            return True
        elif(self.model.validCoor(x-1,y) and self.model.storage[x-1][y] >1 and self.model.storage[x-1][y] <5 ):
            self.model.storage[x-1][y]+=1
            return True
        elif(self.model.validCoor(x,y+1) and self.model.storage[x][y+1] >1 and self.model.storage[x][y+1] <5 ):
            self.model.storage[x][y+1]+=1
            return True
        elif(self.model.validCoor(x,y-1) and self.model.storage[x][y-1] >1 and self.model.storage[x][y-1] <5 ):
            self.model.storage[x][y-1]+=1
            return True
        return False
    
    def getNewPos(self):
        #0 derecha 1 izqierda 2arriba 3 abajo
        if (self.dir ==-1):
            arr =[0,1,2,3]
            direction= random.choice(arr)
            self.dir=direction
        else:
            direction = self.dir
            
        if direction == 0:
            newpos=(self.pos[0]+1,self.pos[1])
        elif  direction == 1:
            newpos=(self.pos[0]-1,self.pos[1])
        elif  direction == 2:
            newpos=(self.pos[0],self.pos[1]+1)
        elif  direction == 3:
            newpos=(self.pos[0],self.pos[1]-1)

        if(self.model.validCoor(newpos[0],newpos[1]) and self.model.storage[newpos[0]][newpos[1]]==0):
            return newpos
        else:
            self.dir=-1
            return self.pos



class StorageModel(Model):
    def __init__(self,width, height,numAgents,numBoxes):
        self.numAgents = numAgents
        self.num_Boxes = numBoxes
        self.unsortedBoxes =numBoxes
        self.agentMovements = 0  
        self.storage = np.zeros((width,height),int)  
        self.agentGrid = SingleGrid(width, height, False)
        self.schedule = SimultaneousActivation(self)

        stacks = math.ceil(self.num_Boxes/5)
        boxesToPlace = self.num_Boxes - stacks
        for i in range(width):
            for j in range(height):
                if stacks:
                    self.storage[i][j] = -1
                    stacks-=1
                elif boxesToPlace:
                    self.storage[i][j] = 1
                    boxesToPlace-=1
                else:
                    break
        
        np.random.shuffle(self.storage)
       

        agent=0
        leftAgents=numAgents
        for i in range(width):
            for j in range(height):
                if self.storage[i][j]==0 and leftAgents:
                    a = RobotAgent(agent, self)
                    agent+=1
                    self.agentGrid.place_agent(a,(i,j))
                    self.schedule.add(a)
                    print("added agent in ->",i,j)
                    self.storage[i][j] = 5
                    leftAgents-=1
                elif not leftAgents:
                    break

        self.datacollector = DataCollector(model_reporters={"Grid": get_grid})


    def step(self):
        """ Ejecuta un paso de la simulación."""
        self.datacollector.collect(self)
        self.schedule.step()
        pass

    def validCoor(self,x,y):
        if x >=0 and x< self.agentGrid.width and y >= 0 and y < self.agentGrid.height:
            return True
        return False
        