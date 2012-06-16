import os,pygame
from pygame.locals import *
from view.viewModule import View

def main():
    clock = pygame.time.Clock()
    view = View()

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
if __name__ == '__main__': main()