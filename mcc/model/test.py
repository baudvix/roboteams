from mcc.model import map
from mcc.util import utils

mapTest = map.MapModel()

mapSection = mapTest.firstMapSection

mapTest.addMapSection(5, "willi")

mapTest.firstMapSection = 2

mapTest.targetPosition = 2

x_ax = 0
y_ax = -4

align = {"x": ("rightGrid" if x_ax > 0 else "leftGrid"),
         "y": ("topGrid" if y_ax > 0 else "bottomGrid")}

print mapSection.__getattribute__(align["x"])

print align["x"]
print align["y"]

"""
mapSection.printGrid()

print "\n"

mapSection.updateGrid([[0, 0], [1, 3], [4, 7]])

mapSection.printGrid()
"""