from mesa import Agent, Model
import math
from scipy.stats import truncnorm
import random

def wander(self):
    possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=False)
    possible_empty_steps = []
    for position in possible_steps:
        if self.model.grid.is_cell_empty(position):
            possible_empty_steps.append(position)

    if len(possible_empty_steps) != 0:
        next_move = self.random.choice(possible_empty_steps)
        self.model.grid.move_agent(self, next_move)

def dispatch_time():             # genererer random integer mellem 1 og 12 der følger normalfordeling med mean 4 std deviation 2.
    lower, upper = 1, 12         #min 10 sek max 2 min
    mu, sigma = 4, 2               #mean 4 std deviation 2
    return math.floor(truncnorm.rvs((lower - mu) /sigma, (upper - mu) /sigma, loc = mu, scale=sigma)) #returnerer trunctuated normal distribution random variabel as int

def buy_beer(self):
    self.queuing = False
    correct_employee = [a for a in self.model.grid.get_neighbors(self.pos,moore=True,include_center=False,radius=1) if isinstance(a,employee)][0]
    self.employer = correct_employee

    number_beers_bought = 2

    if correct_employee.busy is False:
        correct_employee.busy = True
        correct_employee.dispatch_time = dispatch_time()
        self.buying_beer_counter = correct_employee.dispatch_time
        self.beers_bought = random.randint(1,8) #køber mellem 1 og 8 øl
        correct_employee.stall.beers_ready = correct_employee.stall.beers_ready - number_beers_bought #trækker fra antall øl købt

    #if correct_employee.busy is True:
        #queue() - skriv funktion er sætter gæsten i kø.

def go_to_queue(self,employee):
    distances = []
    possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
    possible_empty_steps = []

    for position in possible_steps:
        if self.model.grid.is_cell_empty(position):
            possible_empty_steps.append(position)

    if possible_empty_steps == []:
       # print("NO STEPS TO GO",self.id,self.pos,employee.id)
        return

    for pos in possible_empty_steps:
        distances.append((distance(employee.queue_list[-1], pos), pos))
   # print(self.pos,self.employer.id, self.employer.stall.id, employee.stall.id,employee.queue_list[-1])
    x_, y_ = min(distances, key= lambda X:[0])[1]

    self.model.grid.move_agent(self, (x_,y_))

    if self.pos == employee.queue_list[-1]:
        self.queuing = True

def queuing(self, employee):
    for i in range(0, len(employee.queue_list)):
        if employee.queue_list[i] == self.pos:
            # hvis vi er foran i køen, køb øl
            if i == 0:
                buy_beer(self)
            if self.model.grid.is_cell_empty(employee.queue_list[i-1]): # hvis der er en ledig plass foran dig i køen, ryk fram
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
        self.buying_beer_counter = 0
        self.beers_bought = 0 #antall øl købt (skal denne tælles genem hele simulationen?)
        self.hey = False

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
         if self.queuing == False:
             if self.at_concert == False:
                 if self.going_to_queue == True:
                     go_to_queue(self,self.employer)
                 elif self.going_to_queue == False:
                     stall = [s for s in self.model.schedule.agents if isinstance(s,beerstall) and distance(s.pos,self.pos) < 5]
        #             print(self.pos,stall)
                     if stall == []:
                         wander(self)
                     else:
                         employees_closest = [e for e in self.model.schedule.agents if isinstance(e, employee) and e.stall == stall[0]] #lager en liste av employees ved den nærmeste stall
                         ids_ = [e.id for e in employees_closest]
                         pos_ = [e.pos for e in employees_closest]

                         chosen_employee = employees_closest[random.randint(0,3)] #vælger en tilfældig employee i listen
                         self.employer = chosen_employee
                         go_to_queue(self,chosen_employee)
                         print(self.pos,self.employer.queue_list)
                         self.going_to_queue = True



             else:
                 self.go_to_scene()
         else:
            queuing(self, self.employer)

         #If buying beer, stay at desk
         if self.buying_beer_counter > 0:
             self.buying_beer_counter = max(0,self.buying_beer_counter-1)
             if self.buying_beer_counter == 0:
                 self.employer.busy = False

             return
         #If just arrived to desk, start process of buying the beer
         elif self.pos in self.model.desk_pos:
             buy_beer(self)

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
