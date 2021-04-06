from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation,RandomActivation
import Agent as ac
from statistics import mean
import numpy as np
from scipy.stats import bernoulli
import random
import collections

import math
from itertools import chain
import sys
from mesa.datacollection import DataCollector

number_of_stalls = 4 ##Must be between 1 and 4

'''
The Model-object is responsible for the logical structure of our ABM. 

Here, we define our and set-up our visual grid and our logical algorithm

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

        #Datacollector to collect our data (pouring time, dispatch time, etc)
        self.datacollector = DataCollector(model_reporters={"busy": lambda m: busy_employees(self),
                                                            "queuing": lambda m: queuing(self),
                                                            "transaction": lambda m: number_of_transactions_during_concert(self),
                                                            "transaction_total":lambda m: number_of_transactions_total(self)})
        #Initiate minute, hour and day
        self.time_step = 1
        self.minute_count = 1
        self.hour_count = 1
        self.day_count = 1

        
        #The location of the beer stalls
        if number_of_stalls == 1:
            self.stall_positions = [(15,44)]
        elif number_of_stalls == 2:
            self.stall_positions = [(15,44),(15,7)]
        elif number_of_stalls == 3:
            self.stall_positions = [(15,44),(15,7),(40,44)]
        elif number_of_stalls == 4:
            self.stall_positions = [(15,44),(15,7),(40,44),(40,7)]
        else:
            self.stall_positions = [(15,44),(15,7),(40,44),(40,7)]
            print("Invalid number of stalls, default # of stalls chosen which is 4")



        self.entre_pos = [(5, 0), (6, 0), (5, 49), (6, 49), (35, 0), (35, 49), (36, 0), (36, 49), (49, 35), (49, 20)]
        self.concert_has_ended = False
        self.concert_is_on = False


        self.employees = []
        self.desk_pos = []
        self.busy = []

        self.sceneCoords = [(0,i) for i in range(math.floor(height/2)-7,math.floor(height/2)+6)]
        self.scene_pos = (0,24)
        setUpGuests(self,N)
        setUpScene(self)
        setUpStalls(self)
        setUpEmployees(self)
        setUpFence(self)

        #List of all the queues' position (2D array flattened using chain.from_iterable)
        self.queues = list(chain.from_iterable([e.queue_list for e in self.schedule.agents if isinstance(e,ac.employee)]))
        self.deleted_agents = []
        setUpEntrePos(self)

    def step(self):

        #Concert is starting
        if self.time_step == 90:
            self.concert_is_on = True
            start_concert(self)
        #Concert is ending
        elif self.time_step == 630:
            self.concert_is_on = False
            self.concert_has_ended = True
            end_concert(self)
        #Remove agents that are at an entré-pos and thus are leaving the festival site
        elif self.time_step>630:
            remove_leaving_guests(self)

        #With poisson-distribution people leave and join the concert
        if self.time_step in [i for i in range(91,630)]:
            p_leave = np.random.poisson(1/4)
            for i in range(0,p_leave):
                guests_at_concert = [a for a in self.schedule.agents if isinstance(a,ac.guest) and a.at_concert == True]
                agent = self.random.choice(guests_at_concert)
                agent.at_concert = False

            p_join = np.random.poisson(1/8)
            for i in range(0,p_join):
                    max_id = max([a.id for a in self.schedule.agents if isinstance(a,ac.guest)])
                    newAgent = ac.guest(max_id+1, self)
                    self.schedule.add(newAgent)
                    x_,y_ = self.random.choice(self.entre_pos)
                    newAgent.at_concert = True
                    self.grid.place_agent(newAgent,(x_,y_))


        #Update time
        self.time_step += 1
        if self.time_step%6==0:
            self.minute_count += 1
        if self.minute_count%60 == 0:
            self.hour_count += 1

        #Activate all agents' step-function
        self.schedule.step()
        #Collect data after each (time)step
        self.datacollector.collect(self)

        #Stop model after 720 timesteps
        if self.time_step == 720:
            self.running = False

#Helper functions to collect data and
def number_of_guests(self):
    guests = [a for a in self.schedule.agents if isinstance(a,ac.guest)]
    return len(guests)

def busy_employees(self):
    employees_busy = [a for a in self.schedule.agents if isinstance(a,ac.employee) and a.busy == True]
    return len(employees_busy)

def number_of_transactions_during_concert(self):
   # if self.time_step<90:
    #    agents = [a for a in self.schedule.agents if isinstance(a,ac.guest)]
     #   deleted = [a for a in self.deleted_agents]
      #  for a in agents+deleted:
       #     a.number_of_transaction = 0
       # return 0
    #else:
        agents = [a.number_of_transaction for a in self.schedule.agents if isinstance(a,ac.guest)]
        deleted = [a.number_of_transaction for a in self.deleted_agents]
        return sum(agents+deleted)

def number_of_transactions_total(self):
    agents = [a.number_of_transaction for a in self.schedule.agents if isinstance(a,ac.guest)]
    deleted = [a.number_of_transaction for a in self.deleted_agents]
    return sum(agents+deleted)

def queuing(self):
     agents_queuing = [a for a in self.schedule.agents if isinstance(a,ac.guest) and a.queuing == True]
     return len(agents_queuing)

def end_concert(self):
    all_guests = [a for a in self.schedule.agents if isinstance(a,ac.guest)]
    for a in all_guests:
        a.at_concert = False

def start_concert(self):
    all_guests = [a for a in self.schedule.agents if isinstance(a,ac.guest)]
    for a in all_guests:
        a.at_concert = True

def remove_leaving_guests(self):
    agents_that_left = [a for a in self.schedule.agents if isinstance(a,ac.guest) and a.has_left == True]
    for a in agents_that_left:
        self.deleted_agents.append(a)
        self.schedule.remove(a)
        self.grid.remove_agent(a)

 ##Set up functions##
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
    positions = list.copy(self.stall_positions)
    counter=0
    for i in range(2000,2000+len(self.stall_positions)*5,5):
        newAgent = ac.beerstall(i, self)
        self.schedule.add(newAgent)
        x,y = positions.pop()
        self.grid.place_agent(newAgent,(x,y))

        if y>25: #Where to put stall's exit-positions
            newAgent.stall_exit_pos.append((x - 7, y - 3))
            newAgent.stall_exit_pos.append((x + 7, y - 3))
        else:
            newAgent.stall_exit_pos.append((x - 7, y + 3))
            newAgent.stall_exit_pos.append((x + 7, y + 3))


        #People cannot get past the desk-line (the ones colored pink)
        desk_pos_ = [(x-1,y-1),(x+1,y+1),(x-1,y+1),(x+1,y-1)]

        for pos_ in desk_pos_:
            newAgent = ac.desk(pos_, self)
            self.schedule.add(newAgent)
            self.grid.place_agent(newAgent,pos_)
        counter+=1

def setUpEmployees(self):
    teams = []
    positions = reversed(self.stall_positions)

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
            direction = dir[i]
            newAgent.stall = stall
            self.schedule.add(newAgent)
            x,y = t[i]
            self.grid.place_agent(newAgent,(x,y))
            self.employees.append(newAgent)
            temp.append(newAgent)
            newAgent.queue_list = make_queue((x,y), direction)

        stall.employees = temp
        counter += 5

#The queues' shape are pre-defined, make_queue functions creates a queue based on direction and position on grid
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

def setUpEntrePos(self):
     ids = [i for i in range (4000, 4000 + len(self.entre_pos))]
     for pos in self.entre_pos:
        newAgent = ac.exit(ids.pop(), self)
        self.schedule.add(newAgent)
        self.grid.place_agent(newAgent,pos)
