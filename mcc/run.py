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
    #for p in sim.nxtList:
    #    map.increase_point(p.x_coord, p.y_coord)
    map.increase_point(100,100)
    map.increase_point(100,101)
    map.increase_point(100,102)

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


        view.update(events)



    #this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()