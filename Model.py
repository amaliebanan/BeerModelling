from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation,RandomActivation
import Agent as ac
from statistics import mean
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

def pouring_time(self):
    sump = 0
    for a in self.employees:
        sump += a.pouring_time
    return sump

def busy_employees(self):
    busy = 0
    for a in self.employees:
        if a.busy == True:
            busy+=1
    return busy

def busy_employees_at_stalls(self):
    stalls = [s for s in self.schedule.agents if isinstance(s,ac.beerstall)]
    busy = []
    for stall in stalls:
        busy_employees = 0
        for employee in stall.employees:
            if employee.busy == True:
                busy_employees+=1
        busy.append((stall.id,busy_employees))
    return busy

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

        #Datacollector to collect our data (pouring time, dispatch time, etc)
        self.datacollector = DataCollector(model_reporters={"pouring_time": lambda m: pouring_time(self),
                                                            "busy": lambda m: busy_employees(self)})

        #Initiate minute, hour and day
        self.minute_count = 1
        self.hour_count = 1
        self.day_count = 1

        #The location of the beer stalls
        self.stall_positions = [(10,6),(40,6),(15,44),(40,44)]

        self.employees = []
        self.desk_pos = []

        self.busy = []

        setUpGuests(self,N)
        setUpScene(self)
        setUpStalls(self)
        setUpEmployees(self)
        setUpFence(self)

    def step(self):
        self.busy.append(busy_employees(self))
        self.schedule.step()
        self.datacollector.collect(self)

        busy_employees_at_stalls(self)
        busy_employees_at_stalls(self)
        self.minute_count += 1
        if self.minute_count%60 == 0:
            self.hour_count += 1

        mean_busy = mean(self.busy)

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

        desk_pos = [(x-2,y),(x+2,y),(x,y-2),(x,y+2)]
        self.desk_pos = self.desk_pos + desk_pos

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
        temp = []
        for e in range(1,5):
            newAgent = ac.employee(stall.id+e, self)
            newAgent.stall = stall
            self.schedule.add(newAgent)
            x,y = stalls[e]
            self.grid.place_agent(newAgent,(x,y))
            self.employees.append(newAgent)
            temp.append(newAgent)
        stall.employees = temp
        counter += 5

def setUpFence(self):
    ids = [i for i in range (3000,3100)]
    #Positions of horizontal fence
    pos_vertical_fence = [(2,i) for i in range(16,33)]
    pos_horizontal_fence = [(0,16),(1,16),(0,32),(1,32)]

    for pos in pos_vertical_fence:
        newAgent = ac.fence(ids.pop(), self)
        self.schedule.add(newAgent)
        newAgent.orientation = 'v'
        x,y = pos
        self.grid.place_agent(newAgent,(x,y))


    for pos in pos_horizontal_fence:
        newAgent = ac.fence(ids.pop(), self)
        self.schedule.add(newAgent)
        newAgent.orientation = 'h'
        x,y = pos
        self.grid.place_agent(newAgent,(x,y))

