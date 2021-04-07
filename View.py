from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from Model import Model,busy_employees,number_of_guests

import Agent as ac

width, height = 50,50
def agent_portrayal(agent):
    """
    Function for portrayal of agents in grid
    :param agent:
    :return: dictionary portrayal
    """
    portrayal = {"Shape": "circle",
                 "Color": "red",
                 "Filled": "true",
                 "Layer": 0,
                 "r": 0.5}
    return portrayal

def draw(agent):
    """
    Function to draw agent. Changes according to instances in agent classes.
    e.g. : Agents at concert are red. Agents drinking beer are gold.
    :param agent:
    :return: dictionary portrayal
    """
    if agent is None: #if no agent, don't do anything
        return
    portrayal = {"Shape": "circle", "r": 0.8, "Filled": "true", "Layer": 0}
    if isinstance(agent,ac.guest): # if guest
      if agent.at_concert == True:
          portrayal["Color"] = "#F56C00" #if guest is at concert, red
      if agent.drinking_ == True: #if guest is drinking, gold
        portrayal["Color"] = "gold"
      if agent.going_to_queue == True: #going to queue are gray
          portrayal["Color"] = "#797979"
      if agent.queuing == True:
          portrayal["Color"] = "#5BB2E8" #queuing are light blue
      if agent.buying == True:
            portrayal["Color"] = "#13679B" #buying guests are dark blue
      if agent.at_concert == False and agent.drinking_beer == False and agent.going_to_queue == False and agent.queuing == False:
          portrayal["Color"] = "#54a173" #agents wandering around, not at concert, going to queue, queuing nor drinking beer are green.
          portrayal["scale"] = 0.9

    if isinstance(agent,ac.orangeScene):
      portrayal["Color"] = "orange" #set orange scene to orange
      portrayal["scale"] = 0.9
      if agent.model.time_step in range(90,630): #during concert, lights at scene are blinking
          if agent.model.time_step % 2 == 0:
              portrayal["Color"] = "yellow"
          else: portrayal["Color"] = "orange"


    if isinstance(agent,ac.beerstall):
      portrayal["Shape"] = "resources/beer.png" #shows a beer at the middle of a stall
      portrayal["scale"] = 0.9

    if isinstance(agent,ac.employee):
      portrayal["Color"] = "black" #employees are black if not busy
      portrayal["scale"] = 0.9
      if agent.busy == True:
         portrayal["Color"] = "red" #employees are red if busy

    if isinstance(agent,ac.fence): #setting up the fence
        if agent.orientation == 'v':
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "Black"
            portrayal["w"] = 0.2
            portrayal["h"] = 1
        elif agent.orientation == 'h':
            portrayal["Shape"] = "rect"
            portrayal["Color"] = "Black"
            portrayal["w"] = 1
            portrayal["h"] = 0.2
    if isinstance(agent,ac.desk): #setting up the desks at each stall
        portrayal["Shape"] = "rect"
        portrayal["Color"] = "pink"
        portrayal["w"] = 0.75
        portrayal["h"] = 0.75
    if isinstance(agent,ac.exit): #showing portal at exits.
        portrayal["Shape"] = "resources/portal2.jpg"
        portrayal["scale"] = 0.9


    return portrayal

class pouring_Time(TextElement):
    """
    Class to represent number of guests
    """
    def __init__(self):
        pass

    def render(self, model):
        """
        function that returns number of guests
        :param model: Model
        :return: string + number of guests (int)
        """
        return "Number of guests: " + str(number_of_guests(model))

class busy_employees(TextElement):
    """
    class to represent busy employees
    """
    def __init__(self):
        pass

    def render(self, model):
        return "# of busy agents: " + str(busy_employees(model))

grid = CanvasGrid(draw, width, height, 1200,1200) #making grid

#busy_employees_chart = ChartModule([{"Label":"busy","Color":"Black"}], data_collector_name="datacollector")
pt = pouring_Time()
busy_ = busy_employees()
server = ModularServer(Model, #setting up server
                       [grid,pt],
                       "Roskilde Model",
                       {"N":500, "width":width, "height":height})

server.port = 8521 # The default
