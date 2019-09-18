# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.controller import AudioDevice, Logger, GlobalServices, EventManager, \
    InputController, TickController
from src.model import Game
from src.model.EventTypes import MapLoadingFailedEvent
from src.view import View
import pygame

# main.
# This class initializes the necessary Model-View-Controller structure of the application
# and introduces dependent components to each other. Finally, the event manager
# is introduced and every listener registered.
# This class does not define an explicit main loop! Instead, the last line of this class
# orders the TickController to start running and posting tick events, which causes the loop.
class Main:
    # Run method called by run.py
    def run(self):
        # Initialize pygame
        pygame.init()
        # Pygame sound mixer init
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.mixer.init()
        # Setup the event manager
        evManager = EventManager.EventManager()
        # Setup the input controller
        inputctrl = InputController.InputController(evManager)
        # Setup the tick controller
        ticker = TickController.TickController(evManager)
        # Setup a logger (this may be commented out after completion so that no logging occurs)
        GlobalServices.init(evManager)
        logger = Logger.Logger(evManager)
        GlobalServices.setLogger(logger)
        logger.setFilter([MapLoadingFailedEvent])
        evManager.register(logger)
        # Setup an audio device
        GlobalServices.setAudioDevice(AudioDevice.AudioDevice())
        # Setup the top-most view "controller"
        view = View.View(evManager)
        
        # Register different listeners at the event manager
        evManager.register(inputctrl)
        evManager.register(ticker)
        evManager.register(view)
        
        # Setup the game object providing access to game entities & register it as well
        game = Game.Game(evManager)
        evManager.register(game)
        
        # Start the tick controller, which then fires tick events and thereby "induces" the game loop
        ticker.run()