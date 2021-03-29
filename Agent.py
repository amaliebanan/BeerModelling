from mesa import Agent, Model
import math
from scipy.stats import truncnorm,bernoulli
import random

def wander(self):
    possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=False)
    possible_empty_steps,back_up_list = [],[]

    for position in possible_steps:
        if self.model.grid.is_cell_empty(position) and position not in self.model.queues:
            possible_empty_steps.append(position)

    #Hvis ingen af nabo-cellerne er tomme, må agenten gerne gå igennem andre guest-agenter (dog ikke igennem køen!)
    if possible_empty_steps == []:
         all_neighbors = self.model.grid.get_neighbors(self.pos,moore=True,include_center=False)
         for n in all_neighbors:
             if isinstance(n,guest):
                 if n.pos not in self.model.queues:
                    back_up_list.append(n.pos)
         pos = random.choice(back_up_list)
         self.model.grid.move_agent(self,pos)
    #Hvis køen ikke er tom, vælg random
    else:
        next_move = self.random.choice(possible_empty_steps)
        self.model.grid.move_agent(self, next_move)

def dispatch_time():             # genererer random integer mellem 1 og 12 der følger normalfordeling med mean 4 std deviation 2.
    lower, upper = 1, 12         #min 10 sek max 2 min
    mu, sigma = 4, 2               #mean 4 std deviation 2
    return math.floor(truncnorm.rvs((lower - mu) /sigma, (upper - mu) /sigma, loc = mu, scale=sigma)) #returnerer trunctuated normal distribution random variabel as int

def buy_beer(self, employee):
    self.model.grid.is_cell_empty(employee.queue_list[-1])
    time_at_counter = dispatch_time()

    employee.dispatch_time = time_at_counter
    employee.busy = True

    self.buying_beer_counter = time_at_counter
    beers_ordered = random.randint(1, 8)
    self.beers_bought = self.beers_bought + beers_ordered
    #employee.stall.beers_ready = employee.beers_ready - beers_ordered

def go_to_queue(self,employee):
    goal_pos = employee.queue_list[-1]
    possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
    possible_empty_steps = []

    for position in possible_steps:
        if self.model.grid.is_cell_empty(position) and position not in employee.queue_list[:-1] and position not in self.model.desk_pos:
            possible_empty_steps.append(position)

    if possible_empty_steps == []:
        return

    if goal_pos in possible_steps:

        if self.model.concert_is_on: ##Concert is on
            if not employee.queue_is_crowded():  ##Queue is not crowded, go there
                 self.model.grid.move_agent(self, goal_pos)
                 self.queuing = True
                 self.going_to_queue = False
            else:                   #Queue is crowded
                change_queue(self,employee)
        else: #Concert is not on
            if not employee.queue_is_full(): ## Queue is NOT full
                self.model.grid.move_agent(self, goal_pos)
                self.queuing = True
                self.going_to_queue = False
            else:
                change_queue(self,employee)

    else:#If goal_pos is not in possible steps, move to cell that is closest to goal_cell
        distances = []
        for pos in possible_empty_steps:
            distances.append((distance(goal_pos, pos), pos))
        x_,y_ = min(distances,key=lambda x:x[0])[1]
        self.model.grid.move_agent(self, (x_,y_))

def change_queue(self,employee1):
    the_three_other_employees = [e for e in self.model.schedule.agents if isinstance(e,employee) and 0.1 < distance(e.pos,employee1.pos) < 3]
    new_employee = the_three_other_employees[random.randint(0,2)]
    self.employer = new_employee
    go_to_queue(self,new_employee)

'''
Her bruges 1 tidsskridt mere per kunde, da vi først rykker hen til foreste plads i køen og så i næste tidsskridt
tjekker om vi står forest i køen og begynder buy_beer der.'''
def queuing(self, employee):
    for i in range(0, len(employee.queue_list)):
        if employee.queue_list[i] == self.pos:
            # hvis vi er foran i køen, køb øl
            if i == 0:
                buy_beer(self,employee)
                self.buying = True
            elif self.model.grid.is_cell_empty(employee.queue_list[i-1]):# hvis der er en ledig plass foran dig i køen, ryk fram
                self.model.grid.move_agent(self, employee.queue_list[i-1])
            else:
             # hvis der ikke er en ledig plass i køen foran deg, bliv stående.
                return
'''
Her bruges ikke 1 "ekstra" tidsskridt, da vi rykker hen til foreste plads i køen 
og begynder buy_beer der med det samme'''
def queuing2(self,employee):
    for i in range(1,len(employee.queue_list)):
        if employee.queue_list[i] == self.pos:
            if self.model.grid.is_cell_empty(employee.queue_list[i-1]):#move in queue
                self.model.grid.move_agent(self, employee.queue_list[i-1])
                if self.pos == employee.queue_list[0]: #Tjek når agenten har rykket sig om den står forest i køen
                    buy_beer(self,employee)
                    self.buying = True
            else:#cant move in queue
                return

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
        self.buying = False
        self.leave = False
        self.has_left = False
        self.exit_position = ()

     def go_to_exit(self, exit_pos):
         distances = []
         possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=False)
         possible_empty_steps = []
         for position in possible_steps:
            if self.model.grid.is_cell_empty(position):
                possible_empty_steps.append(position)

         if possible_empty_steps == []:
             return
         for pos in possible_empty_steps:
             distances.append((distance(exit_pos,pos),pos))
         x_,y_ = min(distances,key=lambda x:x[0])[1]
         if (x_,y_) == exit_pos:
             self.has_left = True

         self.model.grid.move_agent(self,(x_,y_))

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

     def go_to_closest_stall(self):
         if self.model.concert_is_on == False:
             d = 7
         else:
             d = 15
         stall = [s for s in self.model.schedule.agents if isinstance(s,beerstall) and distance(s.pos,self.pos) < d]
         if stall == []:
             wander(self)
         else:
             employees_closest = [e for e in self.model.schedule.agents if isinstance(e, employee) and e.stall == stall[0]] #lager en liste av employees ved den nærmeste stall
             get_distance_to_employees = [(distance(e.pos,self.pos),e) for e in employees_closest]
             closest_employee = min(get_distance_to_employees,key=lambda x:x[0])[1]
             self.employer = closest_employee
             self.going_to_queue = True
             go_to_queue(self,self.employer)

     def go_to_random_stall(self):
         random_stall = [s for s in self.model.schedule.agents if isinstance(s,beerstall)][random.randint(0,3)]
         employees_closest = [e for e in self.model.schedule.agents if isinstance(e, employee) and e.stall == random_stall] #lager en liste av employees ved den nærmeste stall
         chosen_employee = employees_closest[random.randint(0,3)]
         self.employer = chosen_employee
         go_to_queue(self,self.employer)
         self.going_to_queue = True

     def step(self):
        self.drinking_beer = max(0, self.drinking_beer - 1)
        if self.drinking_beer == 0:
            self.drinking_ = False


        if self.buying_beer_counter > 0:
            self.buying_beer_counter = max(0,self.buying_beer_counter-1)
            if self.buying_beer_counter == 0:
                self.buying = False
                self.queuing = False
                self.drinking_beer = 100
                self.drinking_ = True
                if self.model.concert_has_ended == False:
                    self.go_to_scene()
                else:
                     if self.exit_position == ():
                        pos = random.choice(self.model.entre_pos)
                        self.exit_position = pos
                        self.go_to_exit(self.exit_position)
            else:
                return

        if self.drinking_beer>0:
            if self.model.concert_has_ended == False:
              self.go_to_scene()
            else:
                if self.exit_position == ():
                    pos = random.choice(self.model.entre_pos)
                    self.exit_position = pos
                    self.go_to_exit(self.exit_position)
                else:
                    self.go_to_exit(self.exit_position)

        if self.leave == True:
            if self.exit_position == ():
                pos = random.choice(self.model.entre_pos)
                self.exit_position = pos

            self.go_to_exit(self.exit_position)

        if self.queuing == False:
             if self.at_concert == False:
                 if self.going_to_queue == True:
                     go_to_queue(self,self.employer)
                 elif self.going_to_queue == False and self.drinking_beer == 0 and self.leave == False:
                      #Før og efter koncerten, tag de agenter, der er tæt på stall
                     if self.model.time_step < 630:
                         self.go_to_closest_stall()
                     else: #Hvis koncerten er start og agenten IKKE deltager (at_concert=False), så tag random stall og
                         # random employee i den stall og gå hen mod den
                         a = bernoulli.rvs(0.6)
                         if a == 1:
                             self.go_to_random_stall()
                         else:
                             wander(self)
                             self.leave = True


             else: #at_concert = True, gå til koncert
                 self.go_to_scene()
        else: #queuing = True, gå i køen
            queuing2(self, self.employer)

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

    #Returns True is queue is full, False is there is room in queue
     def queue_is_full(self):
         a = [self.model.grid.is_cell_empty(a) for a in self.queue_list]
         return not any(a)

     def queue_is_crowded(self):
        a = [self.model.grid.is_cell_empty(a) for a in self.queue_list]
        if sum(a)>4:
            return False
        else:
            return True


     def step(self):
         self.dispatch_time = max(0,self.dispatch_time-1)
         #Kun busy=False, hvis din dispatch_time = 0 OG der ikke er nogen forest i din kø
         if self.dispatch_time==0 and self.model.grid.is_cell_empty(self.queue_list[0]):
             self.busy = False

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
