# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import SCREEN_HEIGHT, SCREEN_WIDTH, APP_NAME, STATE_MAIN_MENU, \
    STATE_GAME_MAP_LOADING, STATE_GAME_RUNNING, STATE_GAME_INVENTORY, COLOR_BLACK, \
    COLOR_RED, VOLUME_SOUND, PATH_GRAPHICS, STATE_GAME_MENU
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND
from src.interfaces import Listener, ViewInterface
from src.model.EventTypes import GameStateChangedEvent, TickEvent, QuitEvent, \
    MouseMotionEvent, MouseClickEvent, MainMenuSelectionEvent, LoadMenuToggleEvent, \
    NewGameToggleEvent, CharAddEvent, CharDelEvent, CharEnteringCompleteEvent, \
    MapLoadingEvent, MapChangedEvent, ObjectHighlightedEvent, ObjectInteractionEvent, \
    SaveEvent, InventoryItemHighlightedEvent, NoSavesFoundEvent, \
    MainMenuSwitchRequestEvent, GameMenuToggleEvent, FullscreenToggleEvent
from src.view import GameView, MainMenuView, MapLoadingView
from src.view.TextRenderer import TextRenderer
import os
import pygame

# View.
# This class is the most "controller-y" the view component gets, but at the same time
# it is necessary to have a central access hub for other controllers when it comes
# to displaying things on the screen.
# The View controller manages an embodied object that also implements the ViewInterface
# and which describes a certain screen inside of the application. This object is called
# the "current view". Furthermore, this view controller holds the screen instance needed
# to render things for the user to see on a display.
# Implements:
#   Listener
#   ViewInterface
class View(Listener, ViewInterface):
    # Constructor
    # Parameter:
    #   evManager   :   Event Manager
    def __init__(self, evManager):
        Listener.__init__(self, evManager)
        # Set-up event handler
        self.handler = None
        # Setup the screen
        pygame.display.set_icon(pygame.image.load(\
                                os.path.join(PATH_GRAPHICS, "_appicon.ico")))
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fullscreen = False
        #self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN|pygame.HWSURFACE)
        pygame.display.set_caption(APP_NAME)
        # Init the text rendering module available to anyone in the GlobalServices module
        self.textRenderer = TextRenderer(self.screen)
        GlobalServices.setTextRenderer(self.textRenderer)
        # Keep track of this object's state
        self.state = None
        # Hold a Gameview instance
        self.gameview = None

    # Listener interface implementation
    # Parameter:
    #   event   :   The event that the event manager has received
    def notify(self, event):
        if isinstance(event, GameStateChangedEvent):
            self.changeHandler(event.object)
        else:
            self.handler.handle(event)

    # Handler change method. Any time the view controller is notified of a game state change event,
    # this method changes the controller's handler reference. This controller also changes its
    # currently displayed view to whatever the new game state requires. If the Game object tells
    # everyone that the state is now "GAME_RUNNING", this controller changes its current view to a GameView.
    # Parameter:
    #   state   :   The new state to which the handler is going to be set
    def changeHandler(self, state):
        # Clean-up pending text renderer messages
        self.textRenderer.deleteAll()
        # Now, change views and handler
        if state == STATE_MAIN_MENU:
            self.handler = MainMenuViewHandler(self)
            self.currentView = MainMenuView.MainMenuView()
        elif state == STATE_GAME_MAP_LOADING:
            self.handler = MapLoadingViewHandler(self)
            self.currentView = MapLoadingView.MapLoadingView()
        elif state == STATE_GAME_RUNNING:
            if not self.state in [STATE_GAME_INVENTORY, STATE_GAME_MENU]:
                if self.gameview is None:
                    self.gameview = GameView.GameView()
                self.currentView = self.gameview
            self.currentView.setHighlightedInventoryItem(None)
            self.handler = GameViewHandler(self)
            self.currentView.setInventoryDisplay(False)
            self.currentView.setGameMenuDisplay(False)
        elif state == STATE_GAME_MENU:
            self.handler = GameMenuViewHandler(self)
            self.currentView.setGameMenuDisplay(True)
        elif state == STATE_GAME_INVENTORY:
            self.handler = InventoryViewHandler(self)
            self.currentView.setHighlightedObject(None)
            self.currentView.setInventoryDisplay(True)
        # Keep track of the new state
        self.state = state

    # ViewInterface implementation
    # Parameter:
    #   screen  :   The surface to be drawn onto
    def render(self, screen):
        # Fill the screen with black
        screen.fill(COLOR_BLACK)
        # Tell the current view to draw itself on top of it
        if self.currentView is not None:
            self.currentView.render(screen)
        # Lastly, tell the text rendering module to render any pending text messages
        self.textRenderer.render()
        # Make the rendered image visible to the user
        pygame.display.flip()

    # This method toggles the pygame display
    # between Windowed and Fullscreen display
    def toggleFullscreen(self):
        # Flip the switch
        self.fullscreen = not self.fullscreen

        # Preserve old contents of the screen
        content = self.screen.convert()

        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN|pygame.HWSURFACE)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Blit old content to the new surface
        self.screen.blit(content, (0,0))

# Base class for view handlers.
# Adready handles tick and quit events, so these don't have to be implemented in subclasses.
# (Still, implementing classes need not forget to call super.handle() in order for this to happen!)
class ViewHandler:
    # Constructor
    # Parameter:
    #   v   :   View reference, so that the view handler may access the event manager
    def __init__(self, v):
        self.v = v

    # Handler base method.
    # Parameter:
    #   event   :   The event that was registered by the event manager
    def handle(self, event):
        # TickEvent: Render the current view's state to the screen
        if isinstance(event, TickEvent):
            self.v.render(self.v.screen)
        # FullscreenToggleEvent: Change between Windowed and Fullscreen display
        elif isinstance(event, FullscreenToggleEvent):
            self.v.toggleFullscreen()
        # QuitEvent: Delete pending text messages in the text rendering module
        elif isinstance(event, QuitEvent):
            self.v.textRenderer.deleteAll()

# Main menu handler for the view controller.
# This handler handles input events from the input controller
# in relation to the main menu screen. Thus, it orders the MainMenuView
# to check if e.g. a mouse motion event has caused a button hover, or
# if a mouse click actually means something.
class MainMenuViewHandler(ViewHandler):
    # Constructor
    # Parameter:
    #   v   :   View reference
    def __init__(self, v):
        ViewHandler.__init__(self, v)
        # Load menu status
        self.loadmenu_open = False
        # New game menu status
        self.newgame_open = False

    # Handler implementation for main menu context.
    # Parameter:
    #   event   :   The event that was registered by the event manager
    def handle(self, event):
        # Handle tick and quit events first
        super(MainMenuViewHandler, self).handle(event)
        # Mouse motion events: Order the current view to check if a button was hovered over
        if isinstance(event, MouseMotionEvent):
            self.v.currentView.checkMotion(event.object.pos)
        # Mouse click event
        elif isinstance(event, MouseClickEvent):
            # Check if the user has clicked on an actual menu item.
            l = self.v.currentView.checkClick(event.object)
            # If the return value is not none, he actually has. Therefore, post the selection event!
            if l is not None:

                self.v.evManager.post(MainMenuSelectionEvent(l))
        # Load menu toggle event
        elif isinstance(event, LoadMenuToggleEvent):
            # Flip the status
            self.loadmenu_open = not self.loadmenu_open
            if self.loadmenu_open:
                self.v.currentView.openLoadMenu()
            else:
                self.v.currentView.closeLoadMenu()
        # New game menu toggle event
        elif isinstance(event, NewGameToggleEvent):
            # Flip the status
            self.newgame_open = not self.newgame_open
            if self.newgame_open:
                self.v.currentView.openNewGame()
            else:
                self.v.currentView.closeNewGame()
        # Adding a character to the save game name
        elif isinstance(event, CharAddEvent):
            GlobalServices.getAudioDevice().play(SOUND, "char_enter", VOLUME_SOUND)
            self.v.currentView.addChar(event.object)
        # Removing a character from the save game name
        elif isinstance(event, CharDelEvent):
            GlobalServices.getAudioDevice().play(SOUND, "char_enter", VOLUME_SOUND)
            self.v.currentView.remChar()
        # Submitting the current save game name
        elif isinstance(event, CharEnteringCompleteEvent):
            savegame = self.v.currentView.getChars()
            # If the save game name is empty, display error message
            if savegame[1] in ["", "_"]:
                GlobalServices.getTextRenderer().write("You must enter a name for your save game.", 3, COLOR_RED)
            else:
                GlobalServices.getAudioDevice().play(SOUND, "game_start", VOLUME_SOUND)
                self.v.evManager.post(MainMenuSelectionEvent(savegame))
        elif isinstance(event, NoSavesFoundEvent):
            self.loadmenu_open = False


# Map loading handler for the view controller.
# This handler is not used at the moment
class MapLoadingViewHandler(ViewHandler):
    def __init__(self, v):
        ViewHandler.__init__(self, v)

    # Handler implementation for map loading context.
    # Parameter:
    #   event   :   The event that was registered by the event manager
    def handle(self, event):
        super(MapLoadingViewHandler, self).handle(event)
        if isinstance(event, MapLoadingEvent):
            # Get map name and display it...
            name = event.object
            self.v.currentView.setName(name)

# Game handler for the view controller.
# This handler is responsible for notifying the current GameView
# when a map change request has been made, or an object in the map
# has been highlighted by the user's mouse.
class GameViewHandler(ViewHandler):
    # Constructor
    # Parameter:
    #   v   :   View reference
    def __init__(self, v):
        ViewHandler.__init__(self, v)

    # Handler implementation for main game context.
    # Parameter:
    #   event   :   The event that was registered by the event manager
    def handle(self, event):
        # Handle tick and quit events first
        super(GameViewHandler, self).handle(event)
        # Map changed event: Order the current view to change the rendered map
        if isinstance(event, MapChangedEvent):
            self.v.currentView.setCurrentMap(event.object)
        # Object highlighted event: Notify the view to render the appropriate rectangle for the highlighted object
        elif isinstance(event, ObjectHighlightedEvent):
            self.v.currentView.setHighlightedObject(event.object)
        # Mouse click event. Check if the user has clicked on a region of interest
        elif isinstance(event, MouseClickEvent):
            # Get the clicked-on object
            clickedobj = self.v.currentView.getHighlightedObject()
            # If it is not none, post an object interaction event, so that the
            # ObjectEngine may execute the object's behaviour
            if clickedobj is not None:
                GlobalServices.getAudioDevice().play(SOUND, "object_click", VOLUME_SOUND)
                self.v.evManager.post(ObjectInteractionEvent(clickedobj))
        # Save event. Order the current view (GameView) to capture a screenshot and save
        # it in the current save game's folder
        elif isinstance(event, SaveEvent):
            self.v.currentView.saveScreenshot()


# Inventory handler for the view controller.
# This handler is responsible for determining mouse movement and clicks
# when the inventory box is opened.
class InventoryViewHandler(ViewHandler):
    # Constructor
    # Parameter:
    #   v   :   View reference
    def __init__(self, v):
        ViewHandler.__init__(self, v)
        self.itemtext = None

    # Handler implementation for main game context.
    # Parameter:
    #   event   :   The event that was registered by the event manager
    def handle(self, event):
        # Handle tick and quit events first
        super(InventoryViewHandler, self).handle(event)
        # Inventory Item Highlighted Event. Delegate the potentially highlighted object to the current view
        if isinstance(event, InventoryItemHighlightedEvent):
            item = event.object
            self.v.currentView.setHighlightedInventoryItem(item)
            # If an inventory item was highlighted, display the item's description
            if item is not None:
                self.itemtext = GlobalServices.getTextRenderer().write(item.desc, 0)
            else:
                # If no inventory item was highlighted, check if there was a description text and delete it
                if self.itemtext is not None:
                    self.itemtext.delete()
                    self.itemtext = None
        elif isinstance(event, MouseClickEvent):
            pass

# Game menu handler for the view controller.
# This handler is responsible for determining mouse movement and clicks
# when the game menu is opened.
class GameMenuViewHandler(ViewHandler):
    # Constructor
    # Parameter:
    #   v   :   View reference
    def __init__(self, v):
        ViewHandler.__init__(self, v)
        self.selected = None

    # Handler implementation for main game context.
    # Parameter:
    #   event   :   The event that was registered by the event manager
    def handle(self, event):
        # Handle tick and quit events first
        super(GameMenuViewHandler, self).handle(event)
        # MouseMotionEvent: Check with the game menu
        # if the mouse has highlighted a menu item
        if isinstance(event, MouseMotionEvent):
            found = self.v.currentView.checkForGameMenuHighlight(event.object.pos)
            if found is not None \
            and found != self.selected:
                GlobalServices.getAudioDevice().play(\
                    SOUND, "menu_hover", VOLUME_SOUND - 0.4)
                self.selected = found
        # MouseMotionEvent: Check with the game menu
        # if the mouse has highlighted a menu item
        if isinstance(event, MouseClickEvent):
            if self.selected is not None:
                GlobalServices.getAudioDevice().play(\
                    SOUND, "menu_select", VOLUME_SOUND - 0.4)
            if self.selected == 1:
                GlobalServices.getTextRenderer().deleteAll()
                self.v.evManager.post(GameMenuToggleEvent())
            elif self.selected == 2:
                self.v.evManager.post(MainMenuSwitchRequestEvent())