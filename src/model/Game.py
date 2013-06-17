# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import STATE_MAIN_MENU, STATE_GAME_MAP_LOADING, \
    STATE_GAME_RUNNING, STATE_GAME_INVENTORY, PATH_SAVES, CURRENT_SHELF_FILENAME, \
    STATE_GAME_MENU
from src.controller import GlobalServices, ScriptEngine
from src.controller.GameHandlers import MainMenuGameHandler, MapLoadingHandler, \
    RunningGameHandler, InventoryGameHandler, GameMenuGameHandler
from src.interfaces import Listener
from src.model import MapFactory, ObjectEngine
from src.model.EventTypes import GameStateChangedEvent, MapChangedEvent, \
    FullscreenToggleEvent
from src.model.Player import Player
from src.model.Shadow import Shadow
from src.utilities import update_persistent_map_properties, get_global_overlays, \
    get_savegame, copy_to_shelve, reset_savegame
import os
import shelve
import shutil

# Game.
# The central hub of the applications logic processing. As many other controllers,
# the Game object listens to events posted by the EventManager, and also happily
# posts events to it as well. The Game object holds the game state, and notifies
# every other listener of changes of the game state. It also provides logic
# to persistently store or load from a saved game and holds general information about
# the game, such as the Player instance or the dictionary of Map objects, between which it
# can switch as pleased.
class Game(Listener):
    # Constructor
    # Parameter:
    #   evManager   :   EventManager instance to which events are posted to
    def __init__(self, evManager):
        Listener.__init__(self, evManager)
        self.currentmap = None
        # Destination tuple. This will be consumed after a teleport event has occured
        self.teleport_destination = None
        # Player object reference
        self.player = Player()
        # Shadow object reference
        self.shadow = Shadow()
        # State; initialized with "main menu" value
        self.state = STATE_MAIN_MENU
        self.changeHandler(self.state)
        # Broadcast the game state
        self.evManager.post(GameStateChangedEvent(self.state))
        
    # Listener interface implementation. This basically delegates the event handling
    # to the current Handler connected to the Game object in a given situation
    # Parameter:
    #   event   :   The event posted by the EventManager
    def notify(self, event):
        # Catch GameStateChanged events first, and change the current handler object accordingly
        if isinstance(event, GameStateChangedEvent):
            self.changeHandler(event.object)
        else:
            # If it is any other Event subclass object, let the handler deal with it
            self.handler.handle(event)
            
    # Change the handler working for this Game object according to the given state.
    # Parameter:
    #   state   :   The new game state
    def changeHandler(self, state):
        if state == STATE_MAIN_MENU:
            self.handler = MainMenuGameHandler(self)
        elif state == STATE_GAME_MAP_LOADING:
            self.handler = MapLoadingHandler(self)
        elif state == STATE_GAME_RUNNING:
            self.handler = RunningGameHandler(self)
        elif state == STATE_GAME_INVENTORY:
            self.handler = InventoryGameHandler(self)
        elif state == STATE_GAME_MENU:
            self.handler = GameMenuGameHandler(self)
        
    # Convenience method to delete a save game using the given file name
    # Parameter:
    #   name    :   The name of the save game to be deleted
    def deleteSavegame(self, name):
        path = os.path.join(PATH_SAVES, name)
        name = name.lower()
        dirs = [d.lower() for d in os.listdir(PATH_SAVES)]
        #print("delete %s from list" % name)
        #print(dirs)
        dele = False
        for d in dirs:
            if d == name:
                dele = True
        #print("in list? %s" % dele)
        # If this save game folder exists...
        if dele: 
            #...delete it!
            shutil.rmtree(path)
        
    # Save method that saves the current game state to the external shelf
    # of the current save game folder.
    # Parameter:
    #   disp    :   Boolean that toggles a text message to be displayed on screen,
    #               indicating a successful save process, if True. If False,
    #               saving still occurs, but the message is not displayed.
    def save(self, disp=False):                
        # Get the savegame data
        temp = get_savegame()
        # Open the "real" shelf (the one the player can load up again)!
        save = shelve.open(CURRENT_SHELF_FILENAME[0])
        
        # Save persistent data that needs to be stored in order to retrieve the game state.
        # All data that is used to do that is actually the player's current position,
        # the current map where this position applies, and the currently playing background
        # music.
        # Pre-defined keys for the dict
        save['player_position'] = self.player.position
        save['current_map'] = self.currentmap.properties['key_name']
        save['player_inventory'] = self.player.inventory
        save['current_sounds'] = GlobalServices.getAudioDevice().getPlayingSounds()
        
        temp['global_overlays'] = get_global_overlays()
        
        # Update the persistent map properties for the current map
        update_persistent_map_properties(self.currentmap, temp)
        # Copy the rest of the shelf data to the "correct" save file
        copy_to_shelve(temp, save)
        
        # Close the shelves again; that's it!
        save.close()
        
        if disp:
            # Display the optional success message using the TextRenderer module
            tr = GlobalServices.getTextRenderer()
            tr.write("Game saved.", 3)
            
    # Initializes the loading of a map using the MapFactory.
    # Parameter:
    #   name        :   The name of the map to be loaded
    def initMapLoading(self, name):
        # Check if there are MapProperties for this map by looking into the
        # savegame dict object.
        shelf = get_savegame()
        try:
            # Dictionary of saved map properties
            saveds = shelf['saved_maps']
            # Properties of this particular map
            properties = saveds[name]
        except KeyError:
            # No properties found
            properties = None
        # If this map hasn't been loaded yet, do so and place it inside the map dict
        if not MapFactory.mapAlreadyLoaded(name):
            # Map is loading. Change game state and notify other controllers
            # that a loading process is going on right now
            self.state = STATE_GAME_MAP_LOADING
            self.evManager.post(GameStateChangedEvent(self.state))
            
            MapFactory.loadMap(name, properties)
        else:
            # If it has already been loaded, change the map on your own
            # (no need for a 1-frame loading screen, amirite?)
            m = MapFactory.getMap(name)
            if properties is not None:
                m.setInteractives(properties.scripts, properties.objects)
            method = m.init_method
            self.changeMap(m, method)
                
    # Changes the map to the current Map object. This method is invoked whenever
    # the Game object handler receives a "MapLoadingDoneEvent". Then, the Game object
    # can change the necessary Map references and inform other controllers of the changed map!
    # Parameters:
    #   map             :   Map object to be switched to
    #   init_method     :   Method handle to the map's setup stuff, or None
    #   successload     :   Boolean depicting if the loading was successful.
    def changeMap(self, m, init_method=None, successload=True):
        # Set the teleport destination if there is one.
        # After that, change the map
        if successload:
            if self.teleport_destination is not None:
                self.player.setPosition(self.teleport_destination)
        self.teleport_destination = None
        # Set map reference and save the map in the dict
        self.currentmap = m
        # Add the player to the map
        self.currentmap.setPlayer(self.player)
        # Add the shadow to the map
        self.currentmap.setShadow(self.shadow)
        
        # Update the map objects' reference just in case
        for o in self.currentmap.objects:
            o.setMap(self.currentmap)
        for s in self.currentmap.scripts:
            s.setMap(self.currentmap)
        
        # Broadcast that the state is now "running"
        self.state = STATE_GAME_RUNNING
        self.evManager.post(GameStateChangedEvent(self.state))
        # Lastly, send a map changed event to get especially the view controller up-to-date
        self.evManager.post(MapChangedEvent(self.currentmap))
        # Address the map's setup method
        if init_method is not None:
            init_method(self.currentmap)
            
    # Checks if the window mode change can be done right now
    def fullscreenToggleRequest(self):
        if not (ScriptEngine.isRunning() and ObjectEngine.isRunning()):
            self.evManager.post(FullscreenToggleEvent())
            
    # This method switches back to the main menu. It is invoked
    # after the game is finished, or when the user selects the
    # corresponding menu item in the game menu
    def switchToMainMenu(self):
        # Pause all things
        GlobalServices.getAudioDevice().stopAll()
        # Close and delete the temporary shelf
        reset_savegame()
        # Delete the Map cache as well
        MapFactory.clearMaps()
        # Change state
        self.state = STATE_MAIN_MENU
        self.evManager.post(GameStateChangedEvent(self.state))