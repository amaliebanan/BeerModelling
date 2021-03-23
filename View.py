from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from Model import Model
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

    return portrayal

grid = CanvasGrid(draw, width, height, 1000,1000)

#infected_chart = ChartModule([{"Label":"infected","Color":"Black"}], data_collector_name="datacollector")

server = ModularServer(Model,
                       [grid],
                       "Covid Model",
                       {"N":30, "width":width, "height":height})

server.port = 8521 # The default
