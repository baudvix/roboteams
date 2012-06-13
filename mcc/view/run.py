#/usr/bin/env python

#Import Modules
import os,pygame
from ocempgui.widgets.Button import Button
from ocempgui.widgets.Renderer import Renderer

from pygame.locals import *


__author__ = 'mhhf'


def drawMap(parent):
    #Draw Background
    pygame.draw.rect(parent, (0, 0, 0), (402, 18, 604, 604))

    for x in range(200):
        for y in range(200):
            if  (x*201+y)%2==0:
                color = (70, 70, 70)
            else:
                color = (90, 90, 90)
            pygame.draw.rect(parent, color, (404+3*x, 20+3*y, 3, 3))

def main():

    pygame.init()
    screen = pygame.display.set_mode((1024, 640))
    pygame.display.set_caption('MCC - Mission Controll Center')

    #Create The Backgound
    graphTile = pygame.image.load('assets/background.jpg').convert()
    graphRect = graphTile.get_rect()
    background = pygame.Surface(screen.get_size())
    background.blit(graphTile, graphRect)


    #Display The Background
    screen.blit(background, (0, 0))

    clock = pygame.time.Clock()


    # Init GUI
    re = Renderer()
    re.screen = screen

    btn = Button("Klick")
    re.add_widget (btn)


    #Main Loop
    while 1:
        clock.tick(60)

        #Events
        events = pygame.event.get()

        #Handle Input Events
        for event in events:
            if event.type == QUIT:
                return

        #Distribute Events
        re.distribute_events (*events)

        #Draw Everything
        #Background
        screen.blit(background, (0, 0))

        #MAP
        drawMap(screen)


        # Update View
        re.refresh()
        pygame.display.flip()






#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()