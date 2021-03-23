from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation,RandomActivation
import Agent as ac
import numpy as np
import random
import math
import sys
from mesa.datacollection import DataCollector


'''
The Model-object is responsible for the logical structure of our ABM. 

Here, we define our and set-up our visual grid, 
our logical algorithm (e.g. should the agents move randomly or simultaneously?)

'''
class Model(Model):
    def __init__(self, N, height, width):
        super().__init__()
        self.N = N
        self.height = height
        self.width = width

        #Multigrid (The visual grid)
        self.grid = MultiGrid(width, height, torus=False) #torus wraps edges

        #Schedule (the logical grid)
        self.schedule = SimultaneousActivation(self)

        #Initiate minute, hour and day
        self.minute_count = 1
        self.hour_count = 1
        self.day_count = 1

        #The location of the beer stalls
        self.stall_positions = [(15,6),(40,6),(15,44),(40,44)]

        setUpGuests(self,N)
        setUpScene(self)
        setUpStalls(self)
        setUpEmployees(self)

    def step(self):

        self.schedule.step()


def setUpGuests(self,N):
    for i in range(0,N):
        newAgent = ac.guest(i, self)
        self.schedule.add(newAgent)
        x,y = self.grid.find_empty()
        self.grid.place_agent(newAgent,(x,y))

def setUpScene(self):
    w,h = self.width, self.height
    y_coords = [i for i in range(math.floor(h/2)-7,math.floor(h/2)+6)]
    for i in range(1000,1000+len(y_coords)):
        newAgent = ac.orangeScene(i, self)
        self.schedule.add(newAgent)
        x = 0
        y = y_coords.pop()
        self.grid.place_agent(newAgent,(x,y))

def setUpStalls(self):
    pos = list.copy(self.stall_positions)
    for i in range(2000,2000+len(pos)*5,5):
        newAgent = ac.beerstall(i, self)
        self.schedule.add(newAgent)
        x,y = pos.pop()
        self.grid.place_agent(newAgent,(x,y))

def setUpEmployees(self):
    employees = []
    for pos in self.stall_positions:
        e1 = (pos[0],pos[1]-1)
        e2 = (pos[0]-1,pos[1])
        e3 = (pos[0]+1,pos[1])
        e4 = (pos[0],pos[1]+1)
        stall = (pos,e1,e2,e3,e4)
        employees.append(stall)

    counter = 0
    for stalls in employees:
        stall = [stall for stall in self.schedule.agents if stall.id == 2000+counter][0]
        for e in range(1,5):
            newAgent = ac.employee(stall.id+e, self)
            newAgent.stall = stall
            self.schedule.add(newAgent)
            x,y = stalls[e]
            self.grid.place_agent(newAgent,(x,y))
        counter += 5


