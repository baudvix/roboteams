import pygame
from pygame.constants import QUIT
from mcc.control.controller import Controller

def main():
    """
        main run method

    """

    # Create Map
    controller = Controller()

    """
    # Fill Map with simulated content
    for p in sim.nxtList:
        for x in range(15):
            for y in range(10):
                map.increase_point(p.x_coord-2+x, p.y_coord-2+y)
    """


    clock = pygame.time.Clock()

    #Main Loop
    while 1:
        clock.tick(30)

        #Event Handling
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                return

        p = controller.sim.go_point()
        for x in range(15):
            for y in range(10):
                controller.map.increase_point(p.x_coord-2+x, p.y_coord-2+y)


        controller.view.log( p.x_coord.__str__()+" "+p.y_coord.__str__() )
        controller.view.update(events)



    #this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()