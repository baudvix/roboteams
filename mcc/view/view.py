#/usr/bin/env python

#Import Modules
import pygame
import random
import threading

from ocempgui.widgets import Label, Renderer, Button, Constants, ScrolledWindow


class View(threading.Thread):
    found = False
    label = Label('')

    def __init__(self, main_map):

        self.map = main_map
        self._clock = pygame.time.Clock()
        pygame.init()
        self.screen = screen = pygame.display.set_mode((1024, 760), pygame.DOUBLEBUF)
        pygame.display.set_caption('MCC - Mission Control Center')

        #Create the background
        #graph_tile = pygame.image.load('background.jpg').convert()
        #graph_rect = graph_tile.get_rect()
        #background = pygame.Surface(screen.get_size())
        #background.blit(graph_tile, graph_rect)

        #Display The Background
        #screen.blit(background, (0, 0))

        # Init GUI
        self.re = Renderer()
        self.re.screen = screen

        btn = Button("Click")
        btn.topleft = (10, 10)
        btn.connect_signal(Constants.SIG_CLICKED, self.success, btn)

        console = ScrolledWindow(1004, 100)
        console.topleft = (10, 650)
        console.child = self.label
        self.label.multiline = True
        self.re.add_widget(btn)
        self.re.add_widget(console)

        self.map_surface = pygame.Surface((604, 604))
        threading.Thread.__init__(self)

    def run(self):
        while True:
            self._clock.tick(30)

            #Event Handling
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    return
            self.update(events)

    def success(self, b):
        self.found = True
        self.log('Button clicked')

    def log(self, text):
        self.label.text = text + '\n' + self.label.text

    def getPoint(self):
        r = random.randint(0, 10)
        if r <= 5:
            return 0
        elif r < 8:
            return 1
        elif r < 10:
            return 2
        else:
            return 3

    def drawMap(self, parent):
        #Draw Background
        pygame.draw.rect(parent, (0, 0, 0), (0, 0, 604, 604))
        #TODO: Draw color calculated with map.max_free_count/ dodge_count
        for x in range(200):
            for y in range(200):
                point = self.map.get_point(x, y)

                if not point:
                    if  (x * 201 + y) % 2 == 0:
                        color = (70, 70, 70)
                    else:
                        color = (90, 90, 90)
                elif point == 1:
                    color = (148, 91, 91)
                elif point == 2:
                    color = (223, 223, 87)
                else:
                    color = (25, 210, 25)

                pygame.draw.rect(parent, color, (2 + 3 * x, 2 + 3 * y, 3, 3))

    #TODO: Draw updated points ( more efficent)
    #TODO: Draw map based on overlay / map selection
    #TODO: increase the reaction time of the gui - draw map / point = new Thread??

    def update(self, events):
        #Events

        #Handle Input Events
        self.re.distribute_events(*events)

        # Update View
        self.re.update()

        # Update MAP
        self.drawMap(self.map_surface)
        self.screen.blit(self.map_surface, (412, 8))

        #Flip the Screen
        pygame.display.flip()
