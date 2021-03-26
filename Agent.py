from mesa import Agent, Model
import math
from scipy.stats import truncnorm
import random

def wander(self):
    possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=False)
    possible_empty_steps,back_up_list = [],[]

    for position in possible_steps:
        if self.model.grid.is_cell_empty(position) and position not in self.model.queues:
            possible_empty_steps.append(position)

    if possible_empty_steps == []:
         all_neighbors = self.model.grid.get_neighbors(self.pos,moore=True,include_center=False)
         for n in all_neighbors:
             if isinstance(n,guest):
                 if n.pos not in self.model.queues:
                    back_up_list.append(n.pos)
         pos = random.choice(back_up_list)
         self.model.grid.move_agent(self,pos)
    else:
        next_move = self.random.choice(possible_empty_steps)
        self.model.grid.move_agent(self, next_move)

def dispatch_time():             # genererer random integer mellem 1 og 12 der følger normalfordeling med mean 4 std deviation 2.
    lower, upper = 1, 12         #min 10 sek max 2 min
    mu, sigma = 4, 2               #mean 4 std deviation 2
    return math.floor(truncnorm.rvs((lower - mu) /sigma, (upper - mu) /sigma, loc = mu, scale=sigma)) #returnerer trunctuated normal distribution random variabel as int

def buy_beer(self, employee):
    self.queuing = False
    self.going_to_queue = False
    employee.dispatch_time = 2
    self.buying_beer_counter = employee.dispatch_time
    beers_ordered = random.randint(1, 8)
    self.beers_bought = self.beers_bought + beers_ordered
    #employee.stall.beers_ready = employee.beers_ready - beers_ordered

def go_to_queue(self,employee):
    distances = []
    goal_pos = employee.queue_list[-1]
    possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
    possible_empty_steps = []

    for position in possible_steps:
        if self.model.grid.is_cell_empty(position) and position not in employee.queue_list[:-1] and position not in self.model.desk_pos:
            possible_empty_steps.append(position)

    if possible_empty_steps == []:
        return

    for pos in possible_empty_steps:
        distances.append((distance(goal_pos, pos), pos))
    x_,y_ = min(distances,key=lambda x:x[0])[1]

    self.model.grid.move_agent(self, (x_,y_))

    if self.pos == employee.queue_list[-1]:
        self.queuing = True

def queuing(self, employee):
    for i in range(0, len(employee.queue_list)):
        if employee.queue_list[i] == self.pos:
            # hvis vi er foran i køen, køb øl
            if i == 0:
                buy_beer(self,employee)
            elif self.model.grid.is_cell_empty(employee.queue_list[i-1]): # hvis der er en ledig plass foran dig i køen, ryk fram
                self.model.grid.move_agent(self, employee.queue_list[i-1])
            else:
                return

            # hvis der ikke er en ledig plass i køen foran deg, bliv stående.

def distance(pos1,pos2):
    return math.sqrt((pos2[0]-pos1[0])**2+(pos2[1]-pos1[1])**2)

class guest(Agent):
     def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model
        self.at_concert = False
        self.looking_for_beer = False
        self.employer = () #Hvem ekspederer agenten? Bliver opdateret så snart agenten bliver ekspederet (buy_beer-funktionen)
        self.queuing = False
        self.going_to_queue = False
        self.drinking_ = False
        self.buying_beer_counter = 0
        self.beers_bought = 0 #antall øl købt (skal denne tælles genem hele simulationen?)
        self.hey = False
        self.drinking_beer = 0

     def go_to_scene(self):
         distances = []
         scene_pos = (0,24)
         possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=False)
         possible_empty_steps = []
         for position in possible_steps:
            if self.model.grid.is_cell_empty(position):
                possible_empty_steps.append(position)

         if possible_empty_steps == []:
             return
         for pos in possible_empty_steps:
             distances.append((distance(scene_pos,pos),pos))
         x_,y_ = min(distances,key=lambda x:x[0])[1]
         self.model.grid.move_agent(self,(x_,y_))

     def step(self):
        self.drinking_beer = max(0, self.drinking_beer - 1)
        if self.drinking_beer == 0:
            self.drinking_ = False

        if self.buying_beer_counter > 0:
            self.buying_beer_counter -= self.buying_beer_counter
            if self.buying_beer_counter == 0:
                self.drinking_beer = 20
                self.drinking_ = True
                self.go_to_scene()
                wander(self)

            return
        if self.drinking_beer>0:
              self.go_to_scene()


        if self.queuing == False:
             if self.at_concert == False:
                 if self.going_to_queue == True:
                     go_to_queue(self,self.employer)
                 elif self.going_to_queue == False and self.drinking_beer == 0:
                     stall = [s for s in self.model.schedule.agents if isinstance(s,beerstall) and distance(s.pos,self.pos) < 5]
                     if stall == []:
                         wander(self)
                     else:
                         employees_closest = [e for e in self.model.schedule.agents if isinstance(e, employee) and e.stall == stall[0]] #lager en liste av employees ved den nærmeste stall
                         chosen_employee = employees_closest[random.randint(0,3)] #vælger en tilfældig employee i listen
                         self.employer = chosen_employee
                         go_to_queue(self,chosen_employee)
                         self.going_to_queue = True

             else:
                 self.go_to_scene()
        else:
            queuing(self, self.employer)

class employee(Agent):
     def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model

        self.pouring = False
        self.pouring_time = 5

        self.dispatch = False
        self.dispatch_time = 5

        self.busy = False
        self.stall = ()

        self.queue_list = []

     def step(self):
         #If there is less than 10 beers ready, pour beers, takes 2 minutes
         if self.stall.beers_ready < 10:
            '''tbi'''
         if self.pouring == True:
            self.pouring_time = max(0,self.pouring_time-1)
            self.stall.beers_ready = self.stall.beers_ready+8

            #Agent is done pouring up beers
            if self.pouring_time == 0:

                self.busy = False
                self.pouring = False

class beerstall(Agent):
    def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model

        self.employees = []
        self.queue_starting_pos = []
        self.beers_ready = 15

class orangeScene(Agent):
     def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model

class fence(Agent):
     def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model
        self.orientation = ()

class desk(Agent):
      def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model
        self.orientation = ()
