from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from Model import Model,busy_employees,number_of_guests

import Agent as ac

width, height = 50,50
def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Color": "red",
                 "Filled": "true",
                 "Layer": 0,
                 "r": 0.5}
    return portrayal

def draw(agent):
    if agent is None:
        return
    portrayal = {"Shape": "circle", "r": 0.8, "Filled": "true", "Layer": 0}
    if isinstance(agent,ac.guest):
      if agent.at_concert == True:
          portrayal["Color"] = "#F56C00"
      if agent.drinking_ == True:
        portrayal["Color"] = "gold"
      if agent.going_to_queue == True:
          portrayal["Color"] = "#797979"
      if agent.queuing == True:
          portrayal["Color"] = "#5BB2E8"
      if agent.buying == True:
            portrayal["Color"] = "#13679B"
      if agent.at_concert == False and agent.drinking_beer == False and agent.going_to_queue == False and agent.queuing == False:
          portrayal["Color"] = "#54a173"
          portrayal["scale"] = 0.9

    if isinstance(agent,ac.orangeScene):
      portrayal["Color"] = "orange"
      portrayal["scale"] = 0.9
      if agent.model.time_step in range(90,630):
          if agent.model.time_step % 2 == 0:
              portrayal["Color"] = "yellow"
          else: portrayal["Color"] = "orange"


    if isinstance(agent,ac.beerstall):
      portrayal["Shape"] = "resources/beer.png"
      portrayal["scale"] = 0.9

    if isinstance(agent,ac.employee):
      portrayal["Color"] = "black"
      portrayal["scale"] = 0.9
      if agent.busy == True:
         portrayal["Color"] = "red"

    if isinstance(agent,ac.fence):
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
    if isinstance(agent,ac.desk):
        portrayal["Shape"] = "rect"
        portrayal["Color"] = "pink"
        portrayal["w"] = 0.75
        portrayal["h"] = 0.75
    if isinstance(agent,ac.exit):
        portrayal["Shape"] = "resources/portal2.jpg"
        portrayal["scale"] = 0.9


    return portrayal

class pouring_Time(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return "Number of guests: " + str(number_of_guests(model))

class busy_employees(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return "# of busy agents: " + str(busy_employees(model))

grid = CanvasGrid(draw, width, height, 1200,1200)

pouring_chart = ChartModule([{"Label":"number_of_guests","Color":"Black"}], data_collector_name="datacollector")
#busy_employees_chart = ChartModule([{"Label":"busy","Color":"Black"}], data_collector_name="datacollector")
pt = pouring_Time()
busy_ = busy_employees()
server = ModularServer(Model,
                       [grid,pt],
                       "Roskilde Model",
                       {"N":500, "width":width, "height":height})

server.port = 8521 # The default
