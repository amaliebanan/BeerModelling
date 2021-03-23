from mesa import Agent, Model
import math

def wander(self):
    possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=False)
    possible_empty_steps = []
    for position in possible_steps:
        if self.model.grid.is_cell_empty(position):
            possible_empty_steps.append(position)

    if len(possible_empty_steps) != 0:
        next_move = self.random.choice(possible_empty_steps)
        self.model.grid.move_agent(self, next_move)

def buy_beer(self):
    print("TO BE IMPLEMENTED")
    correct_employee = [a for a in self.model.grid.get_neighbors(self.pos,moore=True,include_center=False,radius=1) if isinstance(a,employee)][0]
    correct_employee.dispatch_time = 1
    self.employer = correct_employee
    correct_employee.busy = True

    self.buying_beer_counter = 3

class guest(Agent):
     def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model

        self.at_concert = False
        self.looking_for_beer = False

        self.employer = () #Hvem ekspederer agenten? Bliver opdateret så snart agenten bliver ekspederet (buy_beer-funktionen)
        self.queuing = False
        self.buying_beer_counter = 0

     def step(self):
         wander(self)

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

     def step(self):
         #If there is less than 10 beers ready, pour beers, takes 2 minutes
         if self.stall.beers_ready < 10:
            print("TO BE IMPLEMENTED")

         if self.pouring == True:
            self.pouring_time = max(0,self.pouring_time-1)
            self.stall.beers_ready = self.stall.beers_ready+8

            #Agent is done pouring up beers
            if self.pouring_time == 0:
                print("TO BE IMPLEMENTED")
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
