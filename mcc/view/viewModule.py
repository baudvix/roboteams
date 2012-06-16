#/usr/bin/env python

#Import Modules
import os,pygame
import random
from ocempgui.widgets import *

from pygame.locals import *
from pygame.surface import Surface

__author__ = 'mhhf'


class View:
    found = False
    label = Label('')

    def success(self,b):
        self.found = True
        self.log('button Clicked')

    def log(self,text):
        self.label.text += text+'\n'

    def getPoint(self):
        r = random.randint(0,10)
        if r <= 5:
            return 0
        elif r<8:
            return 1
        elif r<10:
            return 2
        else:
            return 3

    def drawMap(self,parent):
        #Draw Background
        pygame.draw.rect(parent, (0, 0, 0), (0, 0, 604, 604))


        for x in range(200):
            for y in range(200):
                point = self.map.get_point(x,y)

                if(point == 0):
                    if  (x*201+y)%2==0:
                        color = (70, 70, 70)
                    else:
                        color = (90, 90, 90)
                elif(point == 1):
                    color = (254, 250, 232)
                elif(point == 2):
                    color = (230, 255, 210)
                else:
                    color = (155, 255, 76)



                pygame.draw.rect(parent, color, (2+3*x, 2+3*y, 3, 3))

    def __init__(self, map):

        self.map = map

        pygame.init()
        self.screen = screen = pygame.display.set_mode((1024, 760), pygame.DOUBLEBUF)
        pygame.display.set_caption('MCC - Mission Controll Center')

        #Create The Backgound
        graphTile = pygame.image.load('view/assets/background.jpg').convert()
        graphRect = graphTile.get_rect()
        background = pygame.Surface(screen.get_size())
        background.blit(graphTile, graphRect)


        #Display The Background
        screen.blit(background, (0, 0))


        # Init GUI
        self.re = Renderer()
        self.re.screen = screen

        btn = Button("Klick")
        btn.topleft = (10,10)
        btn.connect_signal(Constants.SIG_CLICKED, self.success, btn)

        console = ScrolledWindow(1004,100)
        console.topleft = (10,650)
        console.child = self.label
        self.label.multiline = True


        self.re.add_widget (btn)
        self.re.add_widget(console)


        self.mapSurface = pygame.Surface((604, 604))

    def update(self,events):
        #Events

        #Handle Input Events
        self.re.distribute_events (*events)

        # Update View
        self.re.update()

        # Update MAP
        self.drawMap(self.mapSurface)
        self.screen.blit(self.mapSurface,(412,8))

        #Flip the Screen
        pygame.display.flip()
