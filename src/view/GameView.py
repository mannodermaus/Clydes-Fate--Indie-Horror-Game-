# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from libs import tiledtmxloader
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, CURRENT_SHELF_FILENAME, \
    THUMBNAIL_SIZE, COLOR_HIGHLIGHTED_OBJECT, COLOR_TEXT, FONTSTYLE_CAPTION
from src.controller import GlobalServices
from src.interfaces import ViewInterface
from src.view import OverlayFactory
import pygame

# GameView.
# This class holds the render state of the main game screen.
# It is responsible for drawing a tiled map, highlighted objects
# and several effect layers to the screen, and is held by the
# central view controller.
# Implements:
#   ViewInterface
class GameView(ViewInterface):
    # Constructor
    def __init__(self):
        ViewInterface.__init__(self)
        # Renderer object that displays the map
        self.renderer = tiledtmxloader.helperspygame.RendererPygame()
        self.renderer.set_camera_position_and_size(200, 300, SCREEN_WIDTH, SCREEN_HEIGHT)
        # Reference to current map to be rendered (will be updated whenever the Game object posts a MapChangeEvent)
        self.currentmap = None
        # Reference to currently highlighted object (will be set by the view controller whenever that actually happens)
        self.highlighted = None
        # Reference to currently highlighted inventory item (only relevant when it's actually open)
        self.invitem = None
        # Boolean switch that depicts if the inventory is open or not
        self.inventory_open = False
        # Boolean switch that depicts if the game menu is open or not
        self.gamemenu_open = False
        self.darkened = OverlayFactory.create_by_color((0,0,0), 0, 200)
        self.backtogame = [GlobalServices.getTextRenderer().writeAsSurface(\
                          "Back to Game", COLOR_TEXT, FONTSTYLE_CAPTION),\
                           (100,300)]
        self.backtomainmenu = [GlobalServices.getTextRenderer().writeAsSurface(\
                              "Back to Main menu", COLOR_TEXT, FONTSTYLE_CAPTION),\
                               (100,328)]
        self.selected = None
        # Screen handle, used for screenshot saving
        self.screen_surface = None
        
    # Setter method for more understandable access to the current map.
    # Parameter:
    #   map :   The new current map object
    def setCurrentMap(self, m):
        self.currentmap = m
        
    # Setter method for more understandable access to the highlighted object.
    # Parameter:
    #   obj :   The object that is to be treated as the new highlighted object
    def setHighlightedObject(self, obj):
        self.highlighted = obj
        
    # Setter method for more understandable access to the highlighted inventory item.
    # Parameter:
    #   obj :   The object that is to be treated as the new highlighted item
    def setHighlightedInventoryItem(self, obj):
        self.invitem = obj
        
    # Getter method for the currently highlighted object.
    # Returns:
    #   The highlighted object, or None if there is none.
    def getHighlightedObject(self):
        return self.highlighted
        
    # Setter for the display of the inventory.
    # Parameter:
    #   bool    :   True, if the inventory should be displayed, False otherwise
    def setInventoryDisplay(self, b):
        self.inventory_open = b
        
    # Setter for the display of the game menu.
    # Parameter:
    #   bool    :   True, if the game menu should be displayed, False otherwise
    def setGameMenuDisplay(self, b):
        self.gamemenu_open = b
        if b:
            self.selected = None
        
    # Checks if the given position collides with any of
    # the Game Menu's text items.
    # Returns:
    #    A constant referring to the highlighted item, or None
    def checkForGameMenuHighlight(self, pos):
        found = None
        c = 1
        for i in [self.backtogame, self.backtomainmenu]:
            rect = pygame.Rect(i[1][0], i[1][1],\
                               i[0].get_rect().width, i[0].get_rect().height)
            if rect.collidepoint(pos):
                self.selected = i
                found = i
                return c
            c += 1
        if found is None:
            self.selected = None
        return None
        
    # Saves a screenshot to the disk. This will be read again by the Loading menu,
    # displaying a little thumbnail of the game's status to be picked up from
    def saveScreenshot(self):
        file_name = "%s.png" % CURRENT_SHELF_FILENAME[0]
        thumbnail = pygame.transform.scale(self.screen_surface, THUMBNAIL_SIZE)
        pygame.image.save(thumbnail, file_name)
        
    # ViewInterface implementation.
    # Parameter:
    #   screen  :   The surface to be drawn onto
    def render(self, screen):
        self.screen_surface = screen
        # Only render if a map has been passed    
        if self.currentmap is None:
            return
            
        # Render the map
        self.currentmap.renderMap(self.renderer, screen)
        
        # Render the highlighted object (if any)
        if self.highlighted is not None:
            h = self.highlighted
            pos = self.renderer.get_screen_pos(self.currentmap._cLayer,\
                h.rect.topleft[0], h.rect.topleft[1])
            rect = pygame.Rect(pos[0], pos[1], \
                   h.rect.width,\
                   h.rect.height)
            pygame.draw.rect(screen, COLOR_HIGHLIGHTED_OBJECT, rect, 2)
            
        # Render the map's overlays
        overlays_active = not (self.inventory_open or self.gamemenu_open)
        self.currentmap.renderOverlays(self.renderer, screen, overlays_active)
        
        # Else, render the inventory stuff if necessary
        if self.gamemenu_open:
            # Darken the screen with the overlay property
            self.darkened.render(screen, True)
            # Render the menu items
            screen.blit(self.backtogame[0], self.backtogame[1])
            screen.blit(self.backtomainmenu[0], self.backtomainmenu[1])
            # Highlight one of them
            if self.selected is not None:
                rect = pygame.Rect(self.selected[1][0],self.selected[1][1], \
                self.selected[0].get_rect().width,\
                self.selected[0].get_rect().height)
                pygame.draw.rect(screen, COLOR_HIGHLIGHTED_OBJECT, rect, 2)
        elif self.inventory_open:
            # Render inventory and items
            inv = self.currentmap.getPlayer().inventory
            inv.render(screen)
            
            # Render highlighted item (if any)
            if self.invitem is not None:
                pygame.draw.rect(screen, COLOR_HIGHLIGHTED_OBJECT,\
                                 self.invitem.rect, 2)
        