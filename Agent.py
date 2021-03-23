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

class guest(Agent):
     def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model
        self.queuing = False

     def step(self):
         wander(self)


class employee(Agent):
     def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model

        self.pouring = False
        self.pouring_time = 5
        self.stall = ()

class beerstall(Agent):
    def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model

class orangeScene(Agent):
     def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model
