# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import FPS
from src.interfaces import Listener
from src.model.EventTypes import TickEvent, QuitEvent
import pygame

# TickController.
# This class is responsible for the "main loop"
# of the architecture because it implements
# a run() method that posts TickEvents to the EventManager,
# who then informs the other listeners of a game tick, handling
# input, rendering stuff, whatever it is they need to do
# to make the game working.
# Implements:
#    Listener
class TickController(Listener):
    # Constructor
    # Parameter:
    #    evManager    :    EventManager
    def __init__(self, evManager):
        Listener.__init__(self, evManager)
        self.running = True
        self.clock = pygame.time.Clock()
        
    # Listener implementation method.
    # Parameter:
    #    event    :    The event posted by the EventManager
    def notify(self, event):
        # QuitEvent: Exit the run() loop by setting the running flag to False
        if isinstance(event, QuitEvent):
            self.running = False
        
    # Run method. Basically the heart of the game's main loop
    def run(self):
        # As long as this controller is running,
        # the pygame Clock ticks and its tick is broadcasted
        # via the EventManager
        while self.running:
            self.clock.tick(FPS)
            self.evManager.post(TickEvent(int(self.clock.get_fps())))