# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import DEFAULT_INTERACTION_DISTANCE, SCREEN_WIDTH, \
    SCREEN_HEIGHT, PLAYER_MOVEMENT_ENABLED, MOUSE_HIGHLIGHT_ENABLED, \
    INVENTORY_OPEN_ENABLED, SAVE_ENABLED, CURRENTLY_PAUSING_FOR_CLICK, \
    CUTSCENE_RUNNING, FLASHLIGHT_MOVEMENT_ENABLED, PATH_GRAPHICS_SPRITES, \
    GAME_MENU_OPEN_ENABLED
from src.utilities import measure_distance, get_direction_from_point_to_point, \
    string_to_direction, set_property, get_property, get_savegame
import os
import pygame

# interfaces.
# This module defines multiple classes that provide interfaces for subclasses
# to implement, therefore establishing core method names that an implementing
# class should overwrite.

# Listener.
# Provides a notify() function to be called by the EventManager when events occur
class Listener:
    # Constructor
    # Parameter:
    #   evManager   :   EventManager instance
    def __init__(self, evManager):
        self.evManager = evManager
        
    # Notify method interface, called by the EventManager on the Listener
    # Parameter:
    #   event   :   Event posted by the EventManager
    def notify(self, event):
        from src.controller import GlobalServices
        GlobalServices.getLogger().log("no notify() implementation for object %s!" % self)
        
# Event.
# Basically a superclass for a container class representing an Event.
# An optional attribute may store additional information relevant for the listeners to deal with the event
class Event:
    # Constructor
    # Parameter:
    #   object  :   Additional specific information for the event
    def __init__(self, o=None):
        self.object = o
        
# ViewInterface.
# Provides a render() function to be called by the top-most View controller
class ViewInterface:
    # Cosntructor
    def __init__(self):
        pass
        
    # Render method interface
    # Parameter:
    #   screen  :   Surface to draw onto
    def render(self, screen):
        from src.controller import GlobalServices
        GlobalServices.getLogger().log("no render() implementation for object %s!" % self)
  
# LoggerInterface.
# Provides a log() function that knows how to write down different filtered output
class LoggerInterface:
    # Log method interface
    # Parameter:
    #   message :   String message to log
    def log(self, message):
        pass
        
    # Set filter method interface
    # Parameter:
    #   f  :   List of types that may be used in log()'s implementation to filter certain types of events
    def setFilter(self, f):
        pass

# Overlay.
# Provides a render() function that draws whatever the overlay is to the screen
class Overlay:
    # Constructor
    # Parameters:
    #   filename    :   Name of the overlay
    #   surf        :   Surface to use for drawing. This can be None if the
    #                   overlay's render() implementation handles drawing differently
    #   visible     :   Boolean describing if the overlay is to be considered during rendering or not
    #                   (if render() is overwritten, this flag must be included by hand again)
    #   flags       :   pygame blend function flags (see pygame.Surface docs for more)
    #   color       :   RGB color for solidcolor Overlays
    #   op          :   Opacity
    def __init__(self, filename, surf, visible=True, flags=0, color=None, op=255):
        self.name = filename
        self.surf = surf
        self.color = color
        self.op = op
        w,h = surf.get_size()
        self.rect = pygame.Rect(((SCREEN_WIDTH - w)/2, (SCREEN_HEIGHT - h)/2), surf.get_size())
        self.visible = visible
        self.flags = flags
        
    # Render method default implementation
    # Parameter:
    #   screen  :   The surface to draw onto
    #   active  :   Active state of the overlay. Can be used by subclasses
    #               to render a "static" version of the Overlay when False.
    #               True by default
    def render(self, screen, active=True):
        if self.visible:
            screen.blit(self.surf, self.rect, None, self.flags)
            
    # Change the opacity of this overlay (will only work if the surface does not
    # use per-pixel alpha (just like pygame usually does)
    # Parameter:
    #   opacity :   The new opacity (0: fully transparent, 255: fully opaque)
    def setOpacity(self, opacity):
        self.surf.set_alpha(opacity)
        self.op = opacity
        
    def __getstate__(self):
        dd = self.__dict__.copy()
        del dd['surf']
        return dd
    
    def __setstate__(self, dic):
        self.__dict__.update(dic)
        if self.name == "_solidcolor":
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.fill(self.color)
            s.set_alpha(self.op)
            self.surf = s
        else:
            self.surf = pygame.image.load(os.path.join(PATH_GRAPHICS_SPRITES, self.name)).convert_alpha()
        
# Storage.
# This serves as the base class for both the ScriptStorage and ObjectStorage objects
# in the respective Engine modules.
class Storage:
    # Internal class Break.
    # Break inducer. If the program is terminated/closed within a script's execution,
    # then the Script Engine raises one of these objects that are caught in Script.run()
    class Break(Exception):
        pass
        
    # Constructor
    def __init__(self):
        self.timestep = 100
        # Reference to the currently executing object
        self.object = None
        self.shelfopen = False
        self._halt()
        self._reset()
        
    # Reset function for the internal wait function
    def _reset(self):
        self.waiting = False
        self.interrupted = False
        self.killed = False
        self.i = 0
        
    # Start function.
    # Must be the first line of every interaction method callback
    def _go(self):
        self.running = True
        
    # Stop function.
    # Must be the last line of every interaction method callback
    def _halt(self):
        self.running = False
        if self.object is not None:
            self.object._conclude()
            self.object = None
    
    # Wait function for a thread's execution.
    # This is key in the execution of Scripts or Object interactions
    # Parameter:
    #   ms  :   The amount of milliseconds to wait
    def _wait(self, ms):
        self._reset()
        self.waiting = True
        # Loop
        while not(self.killed) and self.i < ms:
            # If someone interrupted from outside, raise a Break exception
            if self.interrupted:
                raise Storage.Break()
            pygame.time.wait(self.timestep)
            self.i += self.timestep
        self.waiting = False
        self.interrupted = False
        
    # Makes the player face the given Clickable or Script object
    # Parameters:
    #    player    :    Player reference
    #    obj       :    Object reference (Script or Clickable)
    def _faceObject(self, player, obj):
        directionstring = get_direction_from_point_to_point(\
                          player.currentsprite.rect.center, obj.rect.center)
        direction = string_to_direction(directionstring)
        player.setDirection(direction)
        
    # Toggles a cutscene. This means, it enables or disables
    # player movement, input etc. for the sake of non-interruptable sequences
    # Parameter:
    #    enabled    :    Boolean value. If True, player movement etc. will be blocked
    def _toggleCutscene(self, enabled):
        
        # Set the "CUTSCENE RUNNING" property to the given value.
        # Afterwards, invert the given value and therefore disable some things.
        set_property(CUTSCENE_RUNNING, enabled)
        
        # If this parameter is True, there is a cutscene
        # which DISABLES these properties. That's why
        # this next line makes sense
        enabled = not enabled
        
        set_property(PLAYER_MOVEMENT_ENABLED, enabled)
        set_property(MOUSE_HIGHLIGHT_ENABLED, enabled)
        set_property(INVENTORY_OPEN_ENABLED, enabled)
        set_property(GAME_MENU_OPEN_ENABLED, enabled)
        set_property(SAVE_ENABLED, enabled)
        set_property(FLASHLIGHT_MOVEMENT_ENABLED, enabled)
        
    # Pause function that pauses a thread's execution until
    # the InputController recognizes a MouseClickEvent.
    # This is useful for whenever an Object Interaction method
    # needs to pause execution, e.g. when the player has to read
    # a text or look at a picture.
    def _pauseUntilClick(self):
        # Set global property that enables the extra behaviour of InputController
        set_property(CURRENTLY_PAUSING_FOR_CLICK, True)
        self.waiting = True
        clicked = False
        while not clicked:
            if self.interrupted:
                raise Storage.Break()
            pygame.time.wait(self.timestep)
            # InputController re-sets this flag, so
            # this loop will notice when it changed
            if not get_property(CURRENTLY_PAUSING_FOR_CLICK):
                clicked = True
        self.waiting = False
            
    # Measures the distance between two points (in this context, the distance between
    # the player and the object's rectangle center) and returns True if this distance
    # is smaller or equal to the given threshold (in px). False is returned otherwise
    # Parameters:
    #   pos         :   Mouse position tuple
    #   rect        :   Pygame Rect whose center point is used for distance measuring
    #   threshold   :   A pixel distance threashold that needs to be "underpassed"
    # Returns:
    #   True if the distance between a point and the Rect's center point is smaller than the threshold,
    #   False otherwise.
    def _playerInDistance(self, pos, rect, threshold = DEFAULT_INTERACTION_DISTANCE):
        return measure_distance(pos, rect.center) <= threshold
        
    # Opens and returns the current save game shelf for access to persistent game data.
    # Returns:
    #   The temp shelf
    def _accessData(self):
        self.s = get_savegame()
        self.shelfopen = True
        
    # Sets a key/value pair inside of the shelf to be persistently stored.
    # Parameters:
    #   key     :   The key (string) under which to put the data in the shelf
    #   value   :   The value assigned to that key in the shelf
    def _setData(self, key, value):
        self._accessData()
        self.s[key] = value
        
    # Returns the value for a given key. This method
    # also catches KeyErrors, so it's safe to call it with
    # a key that's not inside of the shelf (it just returns None in that case)
    # Parameters:
    #   key :   The key to retrieve the corresponding data from
    # Returns:
    #   The data associated to the given key inside the shelf, or None if there is no such key
    def _getData(self, key):
        self._accessData()
        try:
            return self.s[key]
        except KeyError:
            return None