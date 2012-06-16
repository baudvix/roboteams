import pygame
from pygame.constants import QUIT
from model.map import MapModel
from simulator.simulator import Simulator
from view.viewModule import View

def main():
    """
        main run method

    """
    ## Simulate Environment
    sim = Simulator()
    sim.generateList()

    # Create Map
    map = MapModel()

    # Fill Map with simulated content
    for p in sim.nxtList:
        for x in range(5):
            for y in range(5):
                map.increase_point(p.x_coord-2+x, p.y_coord-2+y)

    clock = pygame.time.Clock()
    view = View(map)

    #Main Loop
    while 1:
        clock.tick(30)

        #Event Handling
        events = pygame.event.get()

        for event in events:
            if event.type == QUIT:
                return

        p = sim.goPoint()
        for x in range(5):
            for y in range(5):
                map.increase_point(p.x_coord-2+x, p.y_coord-2+y)


        view.log( p.x_coord.__str__()+" "+p.y_coord.__str__() )
        view.update(events)



    #this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()