# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import COLOR_TEXT, FONTSTYLE_CAPTION, PATH_GRAPHICS_SPRITES
from src.controller import GlobalServices
from src.interfaces import ViewInterface
from src.utilities import center_image
import os
import pygame

# MapLoadingView.
# The loading screen whenever a map is being loaded
class MapLoadingView(ViewInterface):
    # Constructor
    def __init__(self):
        ViewInterface.__init__(self)
        self.tr = GlobalServices.getTextRenderer()
        self.logo = self.tr.write("Loading", 0, COLOR_TEXT, (200, 200), FONTSTYLE_CAPTION)
        self.name = None
        self.img = pygame.image.load(os.path.join(PATH_GRAPHICS_SPRITES, "loading_screen_bg.png")).convert_alpha()
        self.pos = center_image(self.img)
        
    # Renders the screen
    def render(self, screen):
        screen.blit(self.img, self.pos)
        
    # Sets the name of the map being rendered
    # so that it is displayed on the loading screen as well
    # Parameter:
    #    name    :    Name of the map to be rendered
    def setName(self, name):
        self.name = self.tr.write(name, 0, COLOR_TEXT, (250, 250))