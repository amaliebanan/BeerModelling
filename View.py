from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from Model import Model, pouring_time,busy_employees
import Model as m
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
      portrayal["Color"] = "green"
      portrayal["scale"] = 0.9
    if isinstance(agent,ac.orangeScene):
      portrayal["Color"] = "orange"
      portrayal["scale"] = 0.9
    if isinstance(agent,ac.beerstall):
      portrayal["Shape"] = "resources/beer.png"
      portrayal["scale"] = 0.9

    if isinstance(agent,ac.employee):
      portrayal["Color"] = "black"
      portrayal["scale"] = 0.9

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

    return portrayal

class pouring_Time(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return "Pouring time: " + str(pouring_time(model))

class busy_employees(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        return "# of busy agents: " + str(busy_employees(model))

grid = CanvasGrid(draw, width, height, 1000,1000)

pouring_chart = ChartModule([{"Label":"pouring_time","Color":"Black"}], data_collector_name="datacollector")
#busy_employees_chart = ChartModule([{"Label":"busy","Color":"Black"}], data_collector_name="datacollector")
pt = pouring_Time()
#busy_ = busy_employees()
server = ModularServer(Model,
                       [grid,pt,pouring_chart],
                       "Covid Model",
                       {"N":50, "width":width, "height":height})

server.port = 8521 # The default
