from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation,RandomActivation
import Agent as ac
from statistics import mean
import numpy as np
from scipy.stats import bernoulli
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

def agents_go_to_concert(self):
    all_guests = [a for a in self.schedule.agents if isinstance(a,ac.guest)]
    percentages = int((len(all_guests)/100)*90)     #get 90% of the guests

    counter = 0
    while percentages>counter:
        agent = self.random.choice(all_guests)
        if agent.at_concert == True:
            continue
        else:
            agent.at_concert = True
            counter+=1

def end_concert(self):
    all_guests = [a for a in self.schedule.agents if isinstance(a,ac.guest)]

    for a in all_guests:
        a.at_concert = False

class Model(Model):
    def __init__(self, N, height, width):
        super().__init__()
        self.N = N
        self.height = height
        self.width = width
        self.south_queue = []

        #Multigrid (The visual grid)
        self.grid = MultiGrid(width, height, torus=False) #torus wraps edges

        #Schedule (the logical grid)
        self.schedule = SimultaneousActivation(self)

        #Datacollector to collect our data (pouring time, dispatch time, etc)
        self.datacollector = DataCollector(model_reporters={"pouring_time": lambda m: pouring_time(self),
                                                            "busy": lambda m: busy_employees(self)})

        #Initiate minute, hour and day
        self.time_step = 1
        self.minute_count = 1
        self.hour_count = 1
        self.day_count = 1


        #The location of the beer stalls


        self.employees = []
        self.desk_pos = []
        self.busy = []

        self.sceneCoords = [(0,i) for i in range(math.floor(height/2)-7,math.floor(height/2)+6)]
        setUpGuests(self,N)
        setUpScene(self)
        setUpStalls(self)
        setUpEmployees(self)
        setUpFence(self)

    def step(self):
        emp = [e for e in self.schedule.agents if isinstance(e,ac.employee)]
      #  for e in emp:
       #     print(e.pos,e.stall.pos,e.id)
        self.time_step += 1

        if self.time_step%6==0:
            self.minute_count += 1
        if self.minute_count%60 == 0:
            self.hour_count += 1

        #Concert is starting
        if self.time_step == 90:
            agents_go_to_concert(self)
        #Concert is ending
        elif self.time_step == 630:
            end_concert(self)

        #With poisson-distribution people leave and join the concert
        if self.time_step in [i for i in range(91,630)]:
            p_leave = np.random.poisson(1/8)
            for i in range(0,p_leave):
                guests_at_concert = [a for a in self.schedule.agents if isinstance(a,ac.guest) and a.at_concert == True]
                agent = self.random.choice(guests_at_concert)
                agent.at_concert = False

            p_join = np.random.poisson(1/8)
            for i in range(0,p_join):
                if bernoulli(1/10) == 1:
                    guests_at_concert = [a for a in self.schedule.agents if isinstance(a,ac.guest) and a.at_concert == False]
                    agent = self.random.choice(guests_at_concert)
                    agent.at_concert = True
                else:
                    max_id = max([a.id for a in self.schedule.agents if isinstance(a,ac.guest)])
                    newAgent = ac.guest(max_id+1, self)
                    self.schedule.add(newAgent)
                    x_,y_ = self.random.choice([(25,0),(25,49),(40,0),(40,49),(49,10),(49,39)])
                    newAgent.at_concert = True
                    self.grid.place_agent(newAgent,(x_,y_))

        self.busy.append(busy_employees(self))
        self.schedule.step()
        self.datacollector.collect(self)

        busy_employees_at_stalls(self)


        mean_busy = mean(self.busy)

def setUpGuests(self,N):
    for i in range(0,N):
        newAgent = ac.guest(i, self)
        self.schedule.add(newAgent)
        x_,y = self.grid.find_empty()
        x = max(3,x_)
        self.grid.place_agent(newAgent,(x,y))

def setUpScene(self):
    coords = list.copy(self.sceneCoords)
    for i in range(1000,1000+len(coords)):
        newAgent = ac.orangeScene(i, self)
        self.schedule.add(newAgent)
        x,y = coords.pop()
        self.grid.place_agent(newAgent,(x,y))

def setUpStalls(self):
    pos = [(15,44),(40,6),(15,6),(40,44)]
    for i in range(2000,2000+len(pos)*5,5):
        newAgent = ac.beerstall(i, self)
        self.schedule.add(newAgent)
        x,y = pos.pop()
        self.grid.place_agent(newAgent,(x,y))

        #Here people order and pay for beer
        desk_pos = [(x-2,y),(x+2,y),(x,y-2),(x,y+2)]
        self.desk_pos = self.desk_pos + desk_pos

        #People cannot get past the desk-line (the ones colored pink)
        desk_pos_ = [(x-1,y-2),(x-2,y-2),(x-2,y-1),(x+1,y-2),(x+2,y-2),(x+2,y-1),
                     (x+1,y+2),(x+2,y+2),(x+2,y+1),(x-1,y+2),(x-2,y+2),(x-2,y+1)]

        for pos_ in desk_pos_:
            newAgent = ac.desk(pos_, self)
            self.schedule.add(newAgent)
            self.grid.place_agent(newAgent,pos_)

def setUpEmployees(self):
    teams = []
    positions = [(40,44),(15,6),(40,6),(15,44)]
    for pos in positions:
        e1 = (pos[0],pos[1]-1)
        e2 = (pos[0]-1,pos[1])
        e3 = (pos[0]+1,pos[1])
        e4 = (pos[0],pos[1]+1)
        team = (e1,e2,e3,e4)
        teams.append(team)
    dir = ("s","w","e","n")
    counter = 0
    for t in teams:
        stall = [stall for stall in self.schedule.agents if stall.id == 2000+counter][0]
        temp = []
        for i in range(0,4):
            newAgent = ac.employee(stall.id+(i+1), self)
            dirl = dir[i]
            newAgent.stall = stall
            self.schedule.add(newAgent)
            x,y = t[i]
            self.grid.place_agent(newAgent,(x,y))
            self.employees.append(newAgent)
            temp.append(newAgent)
            newAgent.queue_list = make_queue((x,y), dirl)
        stall.employees = temp
        counter += 5

def make_queue(pos, direction):
    x,y = pos
    queue_list = []
    if direction == 'n':
        queue_list = [(x,y+1), (x,y+2), (x+1,y+2), (x+2, y+2), (x+3, y+2), (x+3, y+3), (x+4, y+3), (x+5, y+3)]
    if direction == 's':
        queue_list = [(x,y-1), (x, y-2), (x+1, y-2), (x+1, y-3), (x+1, y-4), (x, y-4), (x, y-5), (x-1, y-5)]
    if direction == "e":
        queue_list = [(x+1, y), (x+2, y), (x+2, y+1), (x+3, y+1), (x+4, y+1), (x+4, y), (x+5, y), (x+6, y)]
    if direction == "w":
        queue_list = [(x-1, y), (x-2, y), (x-2, y+1), (x-3, y+1), (x-4, y+1), (x-4, y), (x-5, y), (x-6, y)]
    return queue_list

def setUpFence(self):
    #Positions of horizontal and vertical fence
    pos_vertical_fence = [(2,i) for i in range(16,33)]
    pos_horizontal_fence = [(0,16),(1,16),(0,32),(1,32)]
    ids = [i for i in range (3000,3000+len(pos_horizontal_fence)+len(pos_vertical_fence))]

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

