# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from glob import glob
from src.constants import PATH_GRAPHICS_SPRITES, SCREEN_WIDTH, SCREEN_HEIGHT, \
    COLOR_TEXT, FONTSTYLE_CAPTION, COLOR_HIGHLIGHTED_OBJECT, \
    COLOR_TEXT_HIGHLIGHTED, PATH_SAVES, MAIN_MENU_ITEM_BEGIN, VOLUME_SOUND, \
    VOLUME_MUSIC
from src.controller import GlobalServices
from src.controller.AudioDevice import MUSIC, SOUND
from src.interfaces import ViewInterface
from src.model.EventTypes import LoadMenuToggleEvent, NewGameToggleEvent, \
    NoSavesFoundEvent
import os
import pygame
import time

# MainMenuView.
# This class holds the render state of the main menu.
# It is responsible for drawing the menu items and background
# in the main menu screen, and is held by the central view controller.
# Implements:
#   ViewInterface
class MainMenuView(ViewInterface):
    # Constructor
    def __init__(self):
        # Initialize via superclass constructor
        ViewInterface.__init__(self)
        # Write out the logo and menu items using the TextRenderer module
        self.writeTexts()
        # Menu item highlighted by the user, or "None"
        self.mouseover = None
        # BG image
        self.bg = pygame.transform.smoothscale(\
                    pygame.image.load(os.path.join(PATH_GRAPHICS_SPRITES,\
                    "main_menu_bg.png")), (SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
        # Title image
        self.title = pygame.image.load(os.path.join(PATH_GRAPHICS_SPRITES, "title.png"))
        # Load menu stuff. First, Boolean if it is open
        self.loadmenu_open = False
        tr = GlobalServices.getTextRenderer()
        self.loadmenu_caption = tr.writeAsSurface("Where do you want to pick up?",\
                                                  COLOR_TEXT, FONTSTYLE_CAPTION)
        back = tr.writeAsSurface("Back", COLOR_TEXT, FONTSTYLE_CAPTION)
        self.menu_backbutton = (back, pygame.Rect((500, 20), back.get_rect().size))
        # The list of save game folders to choose from
        self.loadmenu_saves = []
        # New game menu stuff. Boolean if it is open
        self.newgame_open = False
        self.newgame_caption = tr.writeAsSurface("Enter a save game name. Proceed with Enter...",\
                                                 COLOR_TEXT, FONTSTYLE_CAPTION)
        # List of characters that make up the save game name
        self.newgame_name = []
        self.newgame_surf = tr.writeAsSurface("_")
        # Play BGM
        self.ad = GlobalServices.getAudioDevice()
        self.ad.play(MUSIC, "maincredit", VOLUME_MUSIC + 0.2, -1)
        
    # Write the buttons and logo to the screen
    def writeTexts(self):
        tr = GlobalServices.getTextRenderer()
        #self.logo = tr.write(APP_NAME.upper(), 0, COLOR_TEXT, (200, 200), FONTSTYLE_LOGO)
        self.buttons = []
        x = 100
        self.buttons.append(tr.write("Begin", 0, COLOR_TEXT, (x, 300), FONTSTYLE_CAPTION, False))
        self.buttons.append(tr.write("Load", 0, COLOR_TEXT, (x, 325), FONTSTYLE_CAPTION, False))
        #self.buttons.append(tr.write("Settings", 0, COLOR_TEXT, (x, 350), FONTSTYLE_CAPTION, False))
        self.buttons.append(tr.write("Quit", 0, COLOR_TEXT, (x, 350), FONTSTYLE_CAPTION, False))
        
    # Render method implementation from ViewInterface
    # Parameter:
    #   screen  :   The surface to render onto
    def render(self, screen):
        # Code to render background, animations etc. during the main menu goes here!
        screen.blit(self.bg, (0,0))
        screen.blit(self.title, (50, SCREEN_HEIGHT/2))
        # Load menu stuff goes on top of that
        if self.loadmenu_open:
            self.renderLoadMenu(screen)
        elif self.newgame_open:
            self.renderNewGame(screen)
            
    # Render new game menu
    # Parameter:
    #   screen  :   The surface to render onto
    def renderNewGame(self, screen):
        # Blit the load menu title and "Back" button
        screen.blit(self.newgame_caption, (50, 20))
        screen.blit(self.menu_backbutton[0], self.menu_backbutton[1].topleft)
        # Blit new game input text (TODO centering?)
        screen.blit(self.newgame_surf, (200, 200))
        # Highlighted back button is indicated by a rect
        if self.mouseover is not None:
            rect = self.mouseover[1]
            pygame.draw.rect(screen, COLOR_HIGHLIGHTED_OBJECT, rect, 2)
        
    # Render load menu
    # Parameter:
    #   screen    :    The surface to render onto
    def renderLoadMenu(self, screen):
        # Blit the load menu title and "Back" button
        screen.blit(self.loadmenu_caption, (50, 20))
        screen.blit(self.menu_backbutton[0], self.menu_backbutton[1].topleft)
        # Blit save game information
        for i in range(len(self.loadmenu_saves)):
            save = self.loadmenu_saves[i]
            image = save[1]
            imagerect = save[2]
            name = save[3]
            namepos = save[4]
            mt = save[5]
            mtpos = save[6]
            
            screen.blit(image, imagerect.topleft)
            screen.blit(name, namepos)
            screen.blit(mt, mtpos)
            
        # Highlighted saves are indicated by a rect
        if self.mouseover is not None:
            rect = self.mouseover[1] if self.mouseover == self.menu_backbutton else self.mouseover[2]
            pygame.draw.rect(screen, COLOR_HIGHLIGHTED_OBJECT, rect, 2)
        
    # Method to be called from the view controller when it recognized a MouseMotionEvent.
    # It orders the MainMenuView to check the new mouse position's collision with a menu item.
    # If this occurs, the MainMenuView's highlighted object is set to the hovered-on menu item.
    # Parameter:
    #   pos :   The tuple of the mouse position
    def checkMotion(self, pos):
        # This method's behaviour is dependent on whether the load menu screen is open or not.
        if self.loadmenu_open or self.newgame_open:
            self._checkMotionOnLoadOrNewGameMenu(pos)
        else:
            self._checkMotionOnMainMenu(pos)
            
    # Checks the collision of the given mouse position with any save game to be loaded
    # Parameter:
    #   pos :   The mouse position tuple
    def _checkMotionOnLoadOrNewGameMenu(self, pos):
        foundOne = False
        # Check the save images and the back button
        for i in self.loadmenu_saves:
            rect = i[2]
            if rect.collidepoint(pos):
                foundOne = True
                if not (self.mouseover == i):
                    # Play the highlight sound & color that save
                    self.ad.play(SOUND, "menu_hover", VOLUME_SOUND - 0.4)
                    self.mouseover = i
        # If every item was checked and not a single collision occured,
        # check the back button text
        if not foundOne:
            if self.menu_backbutton[1].collidepoint(pos):
                if not (self.mouseover == self.menu_backbutton):
                    # Play the highlight sound & color that item red
                    self.ad.play(SOUND, "menu_hover", VOLUME_SOUND - 0.4)
                    self.mouseover = self.menu_backbutton
            else:
                self.mouseover = None
    
    # Checks the collision of the given mouse position with any of the main menu items.
    # Parameter:
    #   pos :   The mouse position tuple
    def _checkMotionOnMainMenu(self, pos):
        # Flag if the mouse position has found a colliding item
        foundOne = False
        # Check every menu item for collision with the mouse position
        for b in self.buttons:
            if b.rect.collidepoint(pos):
                foundOne = True
                # If this item wasn't already highlighted, do it
                if not (self.mouseover == b):
                    # Play the highlight sound & color that item red
                    self.ad.play(SOUND, "menu_hover", VOLUME_SOUND - 0.4)
                    self.mouseover = b
                    b.setColor(COLOR_TEXT_HIGHLIGHTED)
            else:
                # If it doesn't collide, set its color back to black
                b.setColor(COLOR_TEXT)
        # If every item was checked and not a single collision occured, set the highlighted object to None
        if not foundOne:
            self.mouseover = None
                
    # Method to be called from the view controller when it recognized a MouseClickEvent.
    # This checks if an item was highlighted (so the mouse is hovering over one)
    # and then prepares information on the selected item, if necessary.
    # Parameter:
    #   event   :   The pygame MOUSEBUTTONDOWN event
    # Returns:
    #   A two-item list. The first item is the index of the clicked-on menu item
    #   (those can be referred to with appropriate constants in src.constants;
    #   they start with MAIN_MENU_ITEM_). The second optional item contains the
    #   file name of a save file. This should only be appended if the "Load" button
    #   has been clicked and a save file has been chosen.
    #   If no item has been selected, this method returns None.
    def checkClick(self, event):
        return_list = None
        # If Left-Mouse-Click and an item is highlighted
        if event.button == 1 and self.mouseover is not None:
            self.ad.play(SOUND, "menu_select", VOLUME_SOUND - 0.4)
            return_list = []
            # Add the index of the clicked-on item depending on the current screen
            if self.loadmenu_open:
                # If the back button was clicked, change to MainMenu again by posting a ToggleEvent
                if self.mouseover == self.menu_backbutton:
                    GlobalServices.getEventManager().post(LoadMenuToggleEvent())
                else:
                    return_list.append(1)
                    return_list.append(self.mouseover[7])
            elif self.newgame_open:
                # If the back button was clicked, change to MainMenu again by posting a ToggleEvent
                if self.mouseover == self.menu_backbutton:
                    GlobalServices.getEventManager().post(NewGameToggleEvent())                
            else:
                return_list.append(self.buttons.index(self.mouseover))
        return return_list
        
    # Opens the load menu. This method also calculates the valid
    # save games to choose from when loading a game.
    def openLoadMenu(self):
        # TextRenderer handle
        tr = GlobalServices.getTextRenderer()
        # Get all directories in "saves" unfiltered first
        dirs = glob(os.path.join(PATH_SAVES, "*"))
        # Save the valid directories in this list:
        valid_dirs = []
        # Save the valid tuples (information on the save games) in this list:
        valid_tuples = []
        # Position attributes and increment variables or positioning
        start_pos = (80, 65)
        offset = (250, 80)
        x = 0
        y = 0
        # Validate these directories (check the files inside of them)
        for direction in dirs:
            delete = False
            name = os.path.basename(direction)
            path = os.path.join(direction, name)
            # A valid save game shelf consists of three data files and a screen shot thumbnail
            for ext in [".bak", ".dat", ".dir", ".png"]:
                file = "%s%s" % (path, ext)
                if not os.path.exists(file):
                    delete = True
                    break
            if not delete:
                valid_dirs.append((path, name))
        if len(valid_dirs) == 0:
            # If no valid directories are left, post a NoSavesFoundEvent to the Event Manager
            GlobalServices.getEventManager().post(NoSavesFoundEvent())
        else:
            # Delete the previous texts
            tr.deleteAll()
            # Reset the highlighted object
            self.mouseover = None
            # If there are some left, build the menu structure
            self.loadmenu_open = True
            # Sort the valid dirs by modification time first
            valid_dirs.sort(key=lambda x: os.path.getmtime("%s%s" % (x[0],".png")))
            valid_dirs.reverse()
            for d in valid_dirs:
                path = d[0]
                name = d[1]
                # Create pygame Surface object from the screenshot file
                screenshot = "%s%s" % (path, ".png")
                shot_surf = pygame.image.load(screenshot).convert()
                # Create Text surface from name
                name_surf = tr.writeAsSurface(name)
                # Format the modified time string and grab a surface for that as well
                mt = time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime(os.path.getmtime(screenshot)))
                mt_surf = tr.writeAsSurface(mt)
                # Construct positioning of the surfaces
                position_img   = (start_pos[0] + x*offset[0],\
                                  start_pos[1] + y*offset[1])
                rect_img = pygame.Rect(position_img, shot_surf.get_rect().size)
                position_name  = (position_img[0] + 100,\
                                  position_img[1] + 10)
                position_mtime = (position_name[0], position_name[1] + 20)
                # Construct the tuple
                new_tuple = (path, shot_surf, rect_img,\
                               name_surf, position_name,\
                               mt_surf, position_mtime, name)
                valid_tuples.append(new_tuple)
                # Increment the offset variables
                y += 1
                if (y % 5 == 0):
                    x += 1
                    y = 0
            self.loadmenu_saves = valid_tuples
    
    # Closes the load menu. Removes references to the opened files etc.
    def closeLoadMenu(self):
        self.loadmenu_open = False
        self.loadmenu_saves = []
        self.writeTexts()
        
    # Opens the new game dialog menu
    def openNewGame(self):
        # Reset the highlighted object
        self.mouseover = None
        # Init new game menu stuff
        self.newgame_open = True
        self.newgame_name = []
        GlobalServices.getTextRenderer().deleteAll()
    
    # Closes the new game dialog menu.
    def closeNewGame(self):
        self.newgame_open = False
        self.writeTexts()
    
    # Adds a character to the save game name.
    # Parameter:
    #   char    :   ASCII character to be added
    def addChar(self, char):
        if len(self.newgame_name) < 20:
            self.newgame_name.append(char)
            self._writeInput()
    
    # Removes the last character from the save game name.
    def remChar(self):
        if len(self.newgame_name) > 0:
            del self.newgame_name[-1]
            self._writeInput()
        
    # Returns the current save game character sequence.
    # Returns:
    #   A two-item tuple. First item is the index of the Begin
    #   button, the second is whatever the user has named his save game file
    def getChars(self):
        index = MAIN_MENU_ITEM_BEGIN
        name = "".join(self.newgame_name)
        return (index, name)
        
    # Helper function that updates the new game surface text.
    # It is called whenever the user entered something during the new game dialog.
    def _writeInput(self):
        self.newgame_surf = GlobalServices.getTextRenderer().writeAsSurface(\
                            "".join(self.newgame_name), COLOR_TEXT, FONTSTYLE_CAPTION)