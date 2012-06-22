import pygame
import random
import math
from mcc.control.controller import Controller
from mcc.utils import Point

def main():
    """
        main run method
    """

    # Create Map

    controller = Controller()
    controller.sim.generate_list()

    # Fill Map with simulated content
    controller.sim.generate_list()
    last_point = Point(0, 0)
    for p in controller.sim.nxt_list:
        if last_point.x_coord < p.x_coord and last_point.y_coord < p.y_coord:
            for x in range(last_point.x_coord - 5, p.x_coord + 5):
                for y in range(last_point.y_coord - 5, p.y_coord + 5):
                    controller.map.increase_point(x, y)
        elif last_point.x_coord > p.x_coord and last_point.y_coord < p.y_coord:
            for x in range(p.x_coord + 5, last_point.x_coord - 5, -1):
                for y in range(last_point.y_coord - 5, p.y_coord + 5):
                    controller.map.increase_point(x, y)
        elif last_point.x_coord < p.x_coord and last_point.y_coord > p.y_coord:
            for x in range(last_point.x_coord - 5, p.x_coord + 5):
                for y in range(p.y_coord + 5, last_point.y_coord - 5, -1):
                    controller.map.increase_point(x, y)
        else:
            for x in range(p.x_coord + 5, last_point.x_coord - 5, -1):
                for y in range(p.y_coord + 5, last_point.y_coord - 5, -1):
                    controller.map.increase_point(x, y)
        last_point = p

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
        if last_point.x_coord < p.x_coord and last_point.y_coord < p.y_coord:
            for x in range(last_point.x_coord - 5, p.x_coord + 5):
                for y in range(last_point.y_coord - 5, p.y_coord + 5):
                    controller.map.increase_point(x, y)
        elif last_point.x_coord > p.x_coord and last_point.y_coord < p.y_coord:
            for x in range(p.x_coord + 5, last_point.x_coord - 5, -1):
                for y in range(last_point.y_coord - 5, p.y_coord + 5):
                    controller.map.increase_point(x, y)
        elif last_point.x_coord < p.x_coord and last_point.y_coord > p.y_coord:
            for x in range(last_point.x_coord - 5, p.x_coord + 5):
                for y in range(p.y_coord + 5, last_point.y_coord - 5, -1):
                    controller.map.increase_point(x, y)
        else:
            for x in range(p.x_coord + 5, last_point.x_coord - 5, -1):
                for y in range(p.y_coord + 5, last_point.y_coord - 5, -1):
                    controller.map.increase_point(x, y)
        last_point = p


        controller.view.log( p.x_coord.__str__()+" "+p.y_coord.__str__() )
        controller.view.update(events)


        #this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()