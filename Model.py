from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
import Agent as agents
import numpy as np
from itertools import chain
from mesa.datacollection import DataCollector
import matplotlib.pyplot as plt

number_of_stalls = 4 ##Must be between 1 and 4

'''
The Model-class is responsible for the logical structure of our ABM. 

Here, we define our and set-up our visual grid and our logical algorithm

'''

class Model(Model):
    """
    Class representing Model

    Attributes
    ---------
    N : int
        Number of agents in grid in current timestep
    height : int
        height of grid
    width : int
        width of grid
    grid : grid
        Visual grid
    schedule : module
        Logical grid
    datacollector : module
        collects data that we want to analyze
    time_step : int
        Indicates current time step
    minute_count : int
        Counting minutes
    hour_count : int
        Counting hours

    """
    def __init__(self, N, height, width):
        super().__init__()
        self.N = N
        self.height = height
        self.width = width

        #Multigrid (The visual grid, torus wraps edges)
        self.grid = MultiGrid(width, height, torus=False)

        #Schedule (the logical grid)
        self.schedule = SimultaneousActivation(self)

        #Datacollector to collect our data, here we specify which system state we want to track throughout simulation
        self.datacollector = DataCollector(model_reporters={"busy": lambda m: busy_employees(self),
                                                            "queuing": lambda m: queuing(self),
                                                            "transaction": lambda m: number_of_transactions_during_concert(self),
                                                            "transaction_total":lambda m: number_of_transactions_total(self)})
        #Initiate time, minute and hour-count
        self.time_step = 1
        self.minute_count = 1
        self.hour_count = 1


        #The location of the beer stalls, according to how many stalls are currently present
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


        # setting up entre/exit positions
        self.entre_pos = [(5, 0), (6, 0), (5, 49), (6, 49), (35, 0), (35, 49), (36, 0), (36, 49), (49, 35), (49, 20)]
        self.concert_has_ended = False #in the beginning, concert has not started yet
        self.concert_is_on = False

        #making lists for employees, desk_positions and busy employees
        self.employees = []
        self.desk_pos = []
        self.busy = []
        #Setting up visuals: scene, guests, stalls, employees and fences.
        self.sceneCoords = [(0,i) for i in range(18,31)]
        self.scene_pos = (0,24)
        setUpGuests(self,N)
        setUpScene(self)
        setUpStalls(self)
        setUpEmployees(self)
        setUpFence(self)

        #List of all the queues' position (2D array flattened using chain.from_iterable)
        self.queues = list(chain.from_iterable([e.queue_list for e in self.schedule.agents if isinstance(e, agents.employee)]))
        self.deleted_agents = []
        setUpEntrePos(self)

    def step(self):
        """
        Function that is called for each time step, that makes sure our model behaves according to our
        predefined model assumptions.
        :return: None
        """
        #If concert is starting
        if self.time_step == 90:
            self.concert_is_on = True
            start_concert(self)
        #If concert is ending
        elif self.time_step == 630:
            self.concert_is_on = False
            self.concert_has_ended = True
            end_concert(self)
        #After concert remove agents that are at an entré-pos and thus are leaving the festival site
        elif self.time_step>630:
            remove_leaving_guests(self)

        ### People leave and join the concert (poisson-distribution) ###
        if self.time_step in [i for i in range(91,630)]:
            p_leave = np.random.poisson(1/4)
            for i in range(0,p_leave):
                guests_at_concert = [a for a in self.schedule.agents if isinstance(a, agents.guest) and a.at_concert == True]
                agent = self.random.choice(guests_at_concert)
                agent.at_concert = False

            p_join = np.random.poisson(1/8)
            for i in range(0,p_join):
                    max_id = max([a.id for a in self.schedule.agents if isinstance(a, agents.guest)])
                    newAgent = agents.guest(max_id + 1, self)
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

#Helper functions to collect data
def number_of_guests(self):
    """
    Function that counts number of guests.
    :param self:
    :return: int, number of guests.
    """
    guests = [a for a in self.schedule.agents if isinstance(a, agents.guest)]
    return len(guests)

def busy_employees(self):
    """
    Function that counts number of busy employees
    :param self:
    :return: int, number of busy employees
    """
    employees_busy = [a for a in self.schedule.agents if isinstance(a, agents.employee) and a.busy == True]
    return len(employees_busy)

def number_of_transactions_during_concert(self):
        """
        Function that counts number of transactions during concert.
        :param self:
        :return:  int, number of transactions during concert.
        """
        if self.time_step<123:
            agents_ = [a for a in self.schedule.agents if isinstance(a, agents.guest)]
            deleted = [a for a in self.deleted_agents]
            for a in agents_+deleted:
                a.number_of_transaction = 0

        agents_ = [a.number_of_transaction for a in self.schedule.agents if isinstance(a, agents.guest)]
        deleted = [a.number_of_transaction for a in self.deleted_agents]
        return sum(agents_+deleted)

def number_of_transactions_total(self):
    """
        Function that counts number of transactions in total.
        :param self:
        :return:  int, number of transactions in total.
        """
    agents_ = [a.number_of_transaction for a in self.schedule.agents if isinstance(a, agents.guest)]
    deleted = [a.number_of_transaction for a in self.deleted_agents]
    return sum(agents_+deleted)

def queuing(self):
     """
        Function that counts number of agents queuing
        :param self:
        :return:  int, number of agents queuing.
        """
     agents_queuing = [a for a in self.schedule.agents if isinstance(a, agents.guest) and a.queuing == True]
     return len(agents_queuing)

def end_concert(self):
    """
    Function ending concert by setting all agents.at_concert= False
    :param self:
    :return: None
    """
    all_guests = [a for a in self.schedule.agents if isinstance(a, agents.guest)]
    for a in all_guests:
        a.at_concert = False

def start_concert(self):
    """
    Function starting concert by setting all agents.at_concert= True
    :param self:
    :return: None
    """
    all_guests = [a for a in self.schedule.agents if isinstance(a, agents.guest)]
    for a in all_guests:
        a.at_concert = True

def remove_leaving_guests(self):
    """
    Function removing guests that hits the exit/entre positions.
    :param self:
    :return: None
    """
    agents_that_left = [a for a in self.schedule.agents if isinstance(a, agents.guest) and a.has_left == True] #checking if agent has hit entre pos
    for a in agents_that_left:
        self.deleted_agents.append(a)
        self.schedule.remove(a) #removing from logical grid
        self.grid.remove_agent(a) #removing from visual grid


"""
 Functions below set up the model (both logical and visual)
"""
def setUpGuests(self,N):
    """
    Function adding guests to logical and visual grid. Guests are randomly placed on empty cell in visual grid,
    however, x value must be at least 3, so they do not get placed inside the scene.
    :param self:
    :param N: int, number of guests
    :return: None
    """
    for i in range(0,N):
        newAgent = agents.guest(i, self) #making N new agents
        self.schedule.add(newAgent) # Adding new agents to the logical grid
        x_,y = self.grid.find_empty() #finding empty spots in visual grid
        x = max(3,x_)
        self.grid.place_agent(newAgent,(x,y)) #placing agents in grid

def setUpScene(self):
    """
    Function adding scene to logical and visual grid. Copy self.sceneCoords so the original list is not emptied by pop()-operation.
    We need original list for later (when concert is on and guests are attracted to the scene).
    Scene is NOT placed randomly.
    :param self:
    :return: None
    """
    coords = list.copy(self.sceneCoords) #getting scene coordinates
    for i in range(1000,1000+len(coords)):
        newAgent = agents.orangeScene(i, self) #making agent orange scene
        self.schedule.add(newAgent)  #placing scene on logical grid
        x,y = coords.pop()
        self.grid.place_agent(newAgent,(x,y)) #placing scene

def setUpStalls(self):
    """
    Function adding the beer stalls to logical and visual grid and everything that goes with it;exits from the stalls and the desks in the beer stalls.
    Copy self.stall_positions so the original list is not emptied by pop()-operation. We need original list for later
    Stalls, exit positions and desks are NOT placed randomly.
    :param self:
    :return: None
    """
    positions = list.copy(self.stall_positions) #Getting stall positions
    counter=0
    for i in range(2000,2000+len(self.stall_positions)*5,5):
        newAgent = agents.beerstall(i, self) #making new agent beerstall
        self.schedule.add(newAgent) #adding beerstall to logical grid
        x,y = positions.pop()
        self.grid.place_agent(newAgent,(x,y)) #placing scene

        if y>25: #Where to put stall's exit-positions - depends on where on the grid the stall is
            newAgent.stall_exit_pos.append((x - 7, y - 3))
            newAgent.stall_exit_pos.append((x + 7, y - 3))
        else:
            newAgent.stall_exit_pos.append((x - 7, y + 3))
            newAgent.stall_exit_pos.append((x + 7, y + 3))


        #People cannot get past the desk-line (the ones colored pink)
        desk_pos_ = [(x-1,y-1),(x+1,y+1),(x-1,y+1),(x+1,y-1)]

        for pos_ in desk_pos_:
            newAgent = agents.desk(pos_, self)
            self.schedule.add(newAgent)
            self.grid.place_agent(newAgent,pos_)
        counter+=1

def setUpEmployees(self):
    """
    Function adding employees. Employees are connected to a beerstall and they are NOT placed randomly.
    They all have one list of positions, this is where guests can queue for beer.
    :param self:
    :return: None
    """
    teams = []
    positions = reversed(self.stall_positions)

    #Put employees at right positions in regards to beerstalls
    for pos in positions:
        e1 = (pos[0],pos[1]-1)
        e2 = (pos[0]-1,pos[1])
        e3 = (pos[0]+1,pos[1])
        e4 = (pos[0],pos[1]+1)

        team = (e1,e2,e3,e4) #defining teams
        teams.append(team)

    dir = ("s","w","e","n") #defining directions - used to set up queue accordingly


    #add the employees to the correct beerstall, make their queue-positions and add them to the logical and visual grid
    counter = 0
    for t in teams:
        stall = [stall for stall in self.schedule.agents if stall.id == 2000+counter][0]
        temp = []
        for i in range(0,4): #setting up employees and defining their id
            newAgent = agents.employee(stall.id + (i + 1), self)
            direction = dir[i] #setting direction
            newAgent.stall = stall #setting which stall the employee belongs to
            self.schedule.add(newAgent) #adding new agent to logical grid
            x,y = t[i] #getting position of team
            self.grid.place_agent(newAgent,(x,y)) #placing agent at position
            self.employees.append(newAgent) #adding employee to list
            temp.append(newAgent)
            newAgent.queue_list = make_queue((x,y), direction) #setting the queue to the employee according to what direction they are standing in

        stall.employees = temp
        counter += 5

def make_queue(pos, direction):
    """
    The queues' shape are pre-defined, make_queue functions creates a queue based on direction and position on grid
    :param pos: tuple
    :param direction: character literal, representing direction
    :return: list, with positions for queue
    """
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
    """
    Function making positions of horizontal and vertical fence
    :param self:
    :return: None
    """
    pos_vertical_fence = [(2,i) for i in range(16,33)]
    pos_horizontal_fence = [(0,16),(1,16),(0,32),(1,32)]
    ids = [i for i in range (3000,3000+len(pos_horizontal_fence)+len(pos_vertical_fence))]

    for pos in pos_vertical_fence: #vertical fence positions
        newAgent = agents.fence(ids.pop(), self)
        self.schedule.add(newAgent) #adding to logical grid
        newAgent.orientation = 'v'
        x,y = pos
        self.grid.place_agent(newAgent,(x,y)) #adding to visual grid

    for pos in pos_horizontal_fence: #horizontal fence positions
        newAgent = agents.fence(ids.pop(), self)
        self.schedule.add(newAgent) #adding to logical grid
        newAgent.orientation = 'h'
        x,y = pos
        self.grid.place_agent(newAgent,(x,y)) #adding to visual grid

def setUpEntrePos(self):
     """
     Function making entre positions where guests join throughout the concert and where guests leave when concert is done
     :param self:
     :return: None
     """
     ids = [i for i in range (4000, 4000 + len(self.entre_pos))]
     for pos in self.entre_pos:
        newAgent = agents.exit(ids.pop(), self)
        self.schedule.add(newAgent) #adding exit to logical grid
        self.grid.place_agent(newAgent,pos) #adding to visual grid
