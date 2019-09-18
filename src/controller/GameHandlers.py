# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import COLOR_RED, MAIN_MENU_ITEM_BEGIN, MAIN_MENU_ITEM_LOAD, \
    MAIN_MENU_ITEM_SETTINGS, MAIN_MENU_ITEM_QUIT, FADEOUT_TIME, \
    CURRENT_SHELF_FILENAME, SHELF_PERSISTENT_KEYS, STATE_GAME_INVENTORY, \
    STATE_GAME_RUNNING, PLAYER_MOVEMENT_ENABLED, MOUSE_HIGHLIGHT_ENABLED, \
    INVENTORY_OPEN_ENABLED, SAVE_ENABLED, VOLUME_SOUND, STATE_GAME_MENU, \
    GAME_MENU_OPEN_ENABLED
from src.controller import GlobalServices, AudioDevice, ScriptEngine
from src.controller.AudioDevice import SOUND
from src.model import ObjectEngine
from src.model.EventTypes import MainMenuSelectionEvent, NoSavesFoundEvent, \
    NewGameToggleEvent, LoadMenuToggleEvent, QuitEvent, MapLoadingDoneEvent, \
    TickEvent, MouseMotionEvent, ObjectHighlightedEvent, MovementRequestEvent, \
    MovementDoneEvent, ObjectInteractionEvent, InventoryToggleEvent, \
    GameStateChangedEvent, SaveEvent, MapChangeRequestEvent, \
    InventoryItemHighlightedEvent, MapLoadingFailedEvent, MainMenuSwitchRequestEvent, \
    GameMenuToggleEvent, FullscreenToggleRequestEvent
from src.utilities import set_shelf, get_savegame, set_global_overlays, \
    get_property, copy_to_dict
import shelve


# GameHandlers.
# In this module, the handlers used by the Game object are defined.
# They have been outsourced because the Game object got a bit large.

# Base class for game handlers.
# This doesn't really do anything,
# but provides the interface for subclasses.
class GameHandler:
    # Constructor
    # Parameter:
    #   gh  :   Game object reference, so that a handler may post events to the EventManager
    def __init__(self, gh):
        self.gh = gh

    # Handle method. This does nothing, so a subclass has to implement event handling as necessary.
    # Parameter:
    #   event   :   The event posted by the EventManager, which was delegated to the
    #               game handler object to ... handle.
    def handle(self, event):
        pass


# Game Handler implementation for the main menu screen.
class MainMenuGameHandler(GameHandler):
    # Constructor
    # Parameter:
    #   gh  :   Game object reference, so that a handler may post events to the EventManager
    def __init__(self, gh):
        GameHandler.__init__(self, gh)

    # Handle method implementation.
    # This handler is particularly interested in MainMenuSelectionEvents,
    # because it is responsible for checking what was selected.
    # Parameter:
    #   event   :   The event posted by the Game object's EventManager reference
    def handle(self, event):
        if isinstance(event, FullscreenToggleRequestEvent):
            # Order the Game menu to check if that's possible
            self.gh.fullscreenToggleRequest()
        # Handle a selected item in the main menu
        if isinstance(event, MainMenuSelectionEvent):
            # Main Menu Items:
            self.handleMainMenuSelection(event.object)
        elif isinstance(event, NoSavesFoundEvent):
            # Delete the save folder again and output a "No loading blah" message
            GlobalServices.getTextRenderer().write("There are no saved games to be loaded.", 2, COLOR_RED)

    # Outsourced handle method for a main menu selection
    # Parameter:
    #   vals    :   Tuple of two items. The first one corresponds to one of the constants
    #               defined in src.constrants (starting with MAIN_MENU_ITEM_). The second
    #               one is only included when the load function had been selected. It
    #               contains the string file name of the save game that was selected for loading.
    #               This tuple is an empty list when the user goes back to the main menu
    #               from the load screen. In that case, this method does nothing.
    def handleMainMenuSelection(self, vals):
        if len(vals) == 0:
            return
        # Stop the music
        val = vals[0]
        if val == MAIN_MENU_ITEM_BEGIN:
            # If there is no second argument, toggle the new game input menu
            if len(vals) == 1:
                self.gh.evManager.post(NewGameToggleEvent())
            else:
                self.newgame(vals[1])
        elif val == MAIN_MENU_ITEM_LOAD:
            # If there is no second argument, toggle the load menu
            if len(vals) == 1:
                self.gh.evManager.post(LoadMenuToggleEvent())
            # Else, the user has selected a savegame. Load this then!
            else:
                self.load(vals[1])
        elif val == MAIN_MENU_ITEM_SETTINGS:
            GlobalServices.getTextRenderer().write("Settings are not available yet :(", 2, COLOR_RED)
        elif val == MAIN_MENU_ITEM_QUIT:
            self.gh.evManager.post(QuitEvent())

    # Initialize a new game
    # Parameter:
    #    name    :    The selected name for the playthrough entered by the user
    def newgame(self, name):
        # Delete the current shelf (if any)
        self.gh.deleteSavegame(name)
        # Create a shelf file handle using the given name
        set_shelf(name)
        # Initialize an empty dictionary for the saved map properties
        shelf = get_savegame()
        shelf['saved_maps'] = {}
        # Fadeout music
        GlobalServices.getAudioDevice().stop(AudioDevice.MUSIC, FADEOUT_TIME)
        # Set the player's start position
        self.gh.player.setPosition((240, 208))
        # Initialize the map loading of the first map
        self.gh.initMapLoading("bedroom")

    # Initialize the loading of a previously saved game, catching errors
    # that may occur if the save game does not actually exist.
    # Parameter:
    #   name    :   String file name of the save game to be loaded
    def load(self, name):
        # Point the shelf to be used to the additional argument
        set_shelf(name)
        # Open the save game shelf
        s = shelve.open(CURRENT_SHELF_FILENAME[0], "w")
        # Open the savegame dict
        s2 = get_savegame()
        # Set global overlays
        set_global_overlays(s['global_overlays'])
        # Copy shelf data to temp dict: exclude persistent stuff
        # that does not refer to "what the player has done gameplay-wise"
        copy_to_dict(s, s2, SHELF_PERSISTENT_KEYS)
        # Fadeout the (menu) music
        GlobalServices.getAudioDevice().stop(AudioDevice.MUSIC, FADEOUT_TIME)
        # Set persistently stored information like position and inventory
        self.gh.player.setPosition(s['player_position'])
        self.gh.player.setInventory(s['player_inventory'])
        # Re-play the saved ambient sounds and music
        GlobalServices.getAudioDevice().playList(s['current_sounds'])
        # Load the last map
        # Initialize the loading of testmap (for now)
        self.gh.initMapLoading(s['current_map'])
        # Finally, close the shelf again.
        s.close()


# Handler for the Game object that becomes active during the MapFactory's
# loading process. Its only purpose basically is to handle an event that
# indicates that the MapFactory is done loading, so... yeah, not the
# most overloaded handler, I guess.
class MapLoadingHandler(GameHandler):
    # Constructor
    # Parameter:
    #   gh  :   Game object reference, so that a handler may post events to the EventManager
    def __init__(self, gh):
        GameHandler.__init__(self, gh)

    # Handle method implementation
    # Parameter:
    #   event   :   The event posted by the EventManager
    def handle(self, event):
        # Catch MapLoadingDoneEvents and notify the Game object
        # to change the current map to the event's object.
        if isinstance(event, MapLoadingDoneEvent):
            map_object = event.object[0]
            callback = None
            if len(event.object) > 1:
                callback = event.object[1]
            self.gh.changeMap(map_object, callback)
        # Catch MapLoadingFailedEvents and write out to the screen
        # that this particular map doesn't exist (yet)
        elif isinstance(event, MapLoadingFailedEvent):
            self.gh.currentmap.rendering_enabled = True
            self.gh.changeMap(self.gh.currentmap, None, False)
            GlobalServices.getTextRenderer().write("Couldn't load %s.tmx" % event.object, 4)


# Handler for the Game object's events during the running game.
# This event is responsible for ordering the player to start or stop moving
# when it recognizes TickEvents. It also orders other controllers to check
# stuff when it receives input events (mouse movements) and interact with objects.
class RunningGameHandler(GameHandler):
    # Constructor
    # Parameter:
    #   gh  :   Game object reference, so that a handler may post events to the EventManager
    def __init__(self, gh):
        GameHandler.__init__(self, gh)

    # Handle method implementation.
    # Parameter:
    #   event   :   The event posted by the EventManager
    def handle(self, event):
        # TickEvent: Update player sprites, handle collision detection,
        # check for player-script collision, process other logic...
        if isinstance(event, TickEvent):
            # Update entities
            self.gh.player.update()
            self.gh.shadow.update(event.object)
            if self.gh.player.moving:
                if (self.gh.currentmap is not None):
                    # Player-Map collision detection
                    coll_result = self.gh.currentmap.isWalkable(self.gh.player, self.gh.player.facing)
                    self.gh.player.move(coll_result, event.object)
                    # Player-Script collision detection
                    script_result = self.gh.currentmap.checkForScriptToggle(self.gh.player)
                    if script_result is not None:
                        ScriptEngine.run(script_result)
        # FullscreenToggleRequestEvent
        elif isinstance(event, FullscreenToggleRequestEvent):
            # Order the Game menu to check if that's possible
            self.gh.fullscreenToggleRequest()
        # QuitEvent: Shutdown the Engine objects (killing running interaction threads)
        elif isinstance(event, QuitEvent):
            # Shutdown the engine objects
            ScriptEngine.shutdown()
            ObjectEngine.shutdown()
        # MouseMotionEvent: Order the map to check if the moved mouse has highlighted a clickable object
        elif isinstance(event, MouseMotionEvent):
            # Check for enabled highlighting
            if get_property(MOUSE_HIGHLIGHT_ENABLED):
                # Check for object highlighting
                obj = self.gh.currentmap.checkForObjectHighlight(event.object)
                self.gh.evManager.post(ObjectHighlightedEvent(obj))
        # MovementRequestEvent: Order the player to start moving and point him in the desired direction
        elif isinstance(event, MovementRequestEvent):
            if get_property(PLAYER_MOVEMENT_ENABLED):
                # Player has started moving
                self.gh.player.startMoving()
                self.gh.player.setDirection(event.object)
        # MovementDoneEvent: Order the player to stop moving
        elif isinstance(event, MovementDoneEvent):
            self.gh.player.stopMoving()
        # ObjectInteractionEvent: Order the Object Engine to interact with the event's object
        elif isinstance(event, ObjectInteractionEvent):
            ObjectEngine.interact(event.object)
        # InventoryToggleEvent: Order the opening of the inventory dialog
        elif isinstance(event, InventoryToggleEvent):
            # Open inventory if no script or object execution is running right now
            if get_property(INVENTORY_OPEN_ENABLED):
                # Stop the player
                self.gh.player.stopMoving()
                # Play a sound for inventory toggling
                GlobalServices.getAudioDevice().play(SOUND, "journal_open", VOLUME_SOUND)
                # Change game state
                self.gh.state = STATE_GAME_INVENTORY
                self.gh.evManager.post(GameStateChangedEvent(self.gh.state))
        elif isinstance(event, GameMenuToggleEvent):
            if get_property(GAME_MENU_OPEN_ENABLED):
                # Open game menu! First, stop the player
                self.gh.player.stopMoving()
                # Change game state
                self.gh.state = STATE_GAME_MENU
                self.gh.evManager.post(GameStateChangedEvent(self.gh.state))
        # SaveEvent: Initialize the save process
        elif isinstance(event, SaveEvent):
            if get_property(SAVE_ENABLED):
                # Save the state (the True parameter orders the TextRenderer to display a message as well)
                self.gh.save(True)
        # MapChangeRequestEvent: When the user has triggered a teleport to another map,
        # the ScriptEngine posts this event to the EventManager
        elif isinstance(event, MapChangeRequestEvent):
            # Stop moving the player
            self.gh.player.stopMoving()
            # Unpack event information
            map_object = event.object[0]
            destination = event.object[1]
            # Init loading with the map and save the dest position
            self.gh.teleport_destination = destination
            self.gh.initMapLoading(map_object)
        # MainMenuSwitchRequestEvent: After the game is finished
        elif isinstance(event, MainMenuSwitchRequestEvent):
            self.gh.switchToMainMenu()


# Handler for the Game object's events for when the inventory is open.
class InventoryGameHandler(GameHandler):
    # Constructor
    # Parameter:
    #   gh  :   Game object reference, so that a handler may post events to the EventManager
    def __init__(self, gh):
        GameHandler.__init__(self, gh)

    # Handle method implementation.
    # Parameter:
    #    event    :    The event posted by the EventManager
    def handle(self, event):
        # FullscreenToggleRequestEvent
        if isinstance(event, FullscreenToggleRequestEvent):
            # Order the Game menu to check if that's possible
            self.gh.fullscreenToggleRequest()
        # InventoryToggleEvent: Order the closing of the inventory dialog
        elif isinstance(event, InventoryToggleEvent):
            GlobalServices.getAudioDevice().play(SOUND, "journal_close", VOLUME_SOUND)
            # Change game state
            self.gh.state = STATE_GAME_RUNNING
            self.gh.evManager.post(GameStateChangedEvent(self.gh.state))
        # MouseMotionEvent: Check with the inventory if the mouse has highlighted an item
        elif isinstance(event, MouseMotionEvent):
            item = self.gh.player.inventory.checkForItemHighlight(event.object)
            self.gh.evManager.post(InventoryItemHighlightedEvent(item))


# Handler for the Game object's events for when the game menu is open
class GameMenuGameHandler(GameHandler):
    # Constructor
    # Parameter:
    #   gh  :   Game object reference, so that a handler may post events to the EventManager
    def __init__(self, gh):
        GameHandler.__init__(self, gh)

    # Handle method implementation.
    # Parameter:
    #    event    :    The event posted by the EventManager
    def handle(self, event):
        # FullscreenToggleRequestEvent
        if isinstance(event, FullscreenToggleRequestEvent):
            # Order the Game menu to check if that's possible
            self.gh.fullscreenToggleRequest()
        elif isinstance(event, GameMenuToggleEvent):
            # Change game state
            self.gh.state = STATE_GAME_RUNNING
            self.gh.evManager.post(GameStateChangedEvent(self.gh.state))
        # MainMenuSwitchRequestEvent: When the user selected
        # the "Back to Main Menu" text
        elif isinstance(event, MainMenuSwitchRequestEvent):
            self.gh.switchToMainMenu()
