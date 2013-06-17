# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.interfaces import Event

# EventTypes.
# In this module, the different types of messages that are common
# in the application are defined. Most of these are simply three-liner
# classes, however it is important to be able to distinguish different
# messages not only by properties, but also by class name (at least to me it is).

# FullscreenToggleRequestEvent.
# Posted by the InputController when Alt+Enter
# is pressed. Causes the Game object to check if that's possible at the moment
class FullscreenToggleRequestEvent(Event):
    def __init__(self):
        Event.__init__(self)
        
# FullscreenToggleEvent.
# Posted by the Game object when a fullscreen toggle request
# is successful
class FullscreenToggleEvent(Event):
    def __init__(self):
        Event.__init__(self)
        
# TickEvent.
# Posted by the TickController each frame. It causes input handling,
# view rendering and controller stuff.
# The TickEvent's object is the elapsed time since the last call in milliseconds.
class TickEvent(Event):
    def __init__(self, dt):
        Event.__init__(self, dt)
        
# MouseMotionEvent.
# Posted by the InputController whenever it recognizes a movement of the mouse.
# The MouseMotionEvent's object is the actual pygame MOUSEMOTION event to be used
# to determine information on the event.
class MouseMotionEvent(Event):
    def __init__(self, event):
        Event.__init__(self, event)

# MouseClickEvent.
# Posted by the InputController whenever it recognizes a mouse click.
# The MouseClickEvent's object is the actual pygame MOUSEBUTTONDOWN event.
class MouseClickEvent(Event):
    def __init__(self, event):
        Event.__init__(self, event)
        
# ObjectHighlightedEvent.
# Posted by the Game object whenever it was able to get a highlighted object from
# the current Map instance after a mouse click has occured.
# The ObjectHighlightedEvent's object is a reference to the highlighted object.
class ObjectHighlightedEvent(Event):
    def __init__(self, obj):
        Event.__init__(self, obj)
        
# InventoryItemHighlightedEvent.
# Posted by the Game object whenever it was able to get a highlighted menu item
# from the player's Inventory object after a mouse click has occured.
# The InventoryItemHighlightedEvent's object is a reference to the highlighted object.
class InventoryItemHighlightedEvent(Event):
    def __init__(self, obj):
        Event.__init__(self, obj)
    
# QuitEvent.
# Posted by the InputController whenever the user has pressed Escape in the main menu,
# or by the Game object if the user has selected "Exit" from the main menu.
class QuitEvent(Event):
    def __init__(self):
        Event.__init__(self)
        
# MovementRequestEvent.
# Posted by the InputController whenever it detected KEYDOWN events corresponding
# to any of the movement keys. The MovementRequestEvent's object is a two-dimensional
# vector containing the desired movement in the form [x,y] with x,y e [-1, 0, 1].
class MovementRequestEvent(Event):
    def __init__(self, keys):
        Event.__init__(self, keys)
        
# MovementDoneEvent.
# Posted by the InputController whenever a preceding movement has finished (when the user
# has stopped pressing movement keys).
class MovementDoneEvent(Event):
    def __init__(self):
        Event.__init__(self)
        
# MapChangeRequestEvent.
# Posted by the ScriptEngine whenever a teleport script is attempting
# to change the current map (like, if the player enters a new room).
# The MapChangeRequestEvent's object is a tuple of two items.
# The first one is the string name of the map to be loaded,
# the second one is the destination position of the teleport script
# (a tuple of x,y coordinates where the player is to be placed after teleporting).
class MapChangeRequestEvent(Event):
    def __init__(self, map_and_pos):
        Event.__init__(self, map_and_pos)
        
# MapLoadingEvent.
# Posted by the MapFactory whenever a new map is going to be loaded.
# The MapLoadingEvent's object is the string name of the map that is loading.
class MapLoadingEvent(Event):
    def __init__(self, mapname):
        Event.__init__(self, mapname)
        
# MapLoadingDoneEvent.
# Posted by the MapFactory whenever a map is loaded successfully.
# The MapLoadingDoneEvent's object is a tuple of three items, the first
# being the loaded Map object, the second parameter is optional
# and may contain the method handle to  the map's initialization object in ObjectEngine.py
class MapLoadingDoneEvent(Event):
    def __init__(self, mapAndOverlays):
        Event.__init__(self, mapAndOverlays)
        
# MapLoadingFailedEvent.
# Posted by the MapFactory when the map name to be loaded does not exist.
# The MapLoadingFailedEvent's object is the string name of the
# non-existing map.
class MapLoadingFailedEvent(Event):
    def __init__(self, name):
        Event.__init__(self, name)
        
# MapChangedEvent.
# Posted by the Game object when it switched the current map.
# The MapChangedEvent's object is the reference to the new Map object to be used.
class MapChangedEvent(Event):
    def __init__(self, newmap):
        Event.__init__(self, newmap)
        
# GameStateChangedEvent.
# Posted by the Game object whenever its own state changes. It notifies the listeners
# about important changes in the application state, so that they can adjust their event handlers
# and stay up-to-date with the Game object. The GameStateChangedEvent's object is a string constant
# found in src.constants (those starting with "STATE_").
class GameStateChangedEvent(Event):
    def __init__(self, newstate):
        Event.__init__(self, newstate)
        
# MainMenuSelectionEvent.
# Posted by the MainMenuViewHandler whenever the user successfully selected
# a menu item in the main menu screen. The MainMenuSelectionEvent's object is
# a tuple of two items. The first one describes the action that was selected
# according to src.constants integer constants (those starting with "MAIN_MENU_ITEM_").
# The second one is a string depicting the name of the selected save game to be loaded up.
# This second argument is only passed along if the user clicked on the Load button.
class MainMenuSelectionEvent(Event):
    def __init__(self, value):
        Event.__init__(self, value)
        
# ObjectInteractionEvent.
# Posted by the GameViewHandler whenever a mouse click during the running game collided
# with the rectangle of an interaction object on the map. The ObjectInteractionEvent's object
# is a reference to the clicked-on object, to be passed over to the ObjectEngine by the Game object.
class ObjectInteractionEvent(Event):
    def __init__(self, obj):
        Event.__init__(self, obj)
        
# SaveEvent.
# Posted by the InputController when the user has pressed the save shortcut during a running game.
class SaveEvent(Event):
    def __init__(self):
        Event.__init__(self)
        
# NoSavesFoundEvent.
# Posted by the MainMenuView when every possible directory in the saves folder
# is no valid save game to be loaded from.
class NoSavesFoundEvent(Event):
    def __init__(self):
        Event.__init__(self)
        
# NewGameToggleEvent.
# Posted by the Game object when it received a MainMenuSelectionEvent aiming for the
# Begin button on the main menu. This event will be caught by both the InputController
# and the View controller in order to adjust the input handling and display of the
# newly input save game name
class NewGameToggleEvent(Event):
    def __init__(self):
        Event.__init__(self)
        
# CharAddEvent.
# Posted by the InputController during the new game input dialog.
# The CharAddEvent's object is the unicode character to be added to the save game name
class CharAddEvent(Event):
    def __init__(self, char):
        Event.__init__(self, char)
        
# CharDelEvent.
# Posted by the InputController during the new game input dialog.
class CharDelEvent(Event):
    def __init__(self):
        Event.__init__(self)
        
# CharEnteringCompleteEvent.
# Posted by the InputController during the new game input dialog, when the user hits enter to submit his save game name.
class CharEnteringCompleteEvent(Event):
    def __init__(self):
        Event.__init__(self)
        
# LoadMenuToggleEvent.
# Posted by the Game object when it received a MainMenuSelectionEvent aiming for the
# Load button on the main menu screen. This event will be caught by the View controller
# to toggle the display of the Loading screen (where the player can choose from a
# previously saved game)
class LoadMenuToggleEvent(Event):
    def __init__(self):
        Event.__init__(self)
        
# InventoryToggleEvent.
# Posted by the InputController when the user pressed the Tab key during gameplay. It causes
# the Game object to order the opening or closing of the inventory dialog box, depending on
# whether it was closed or opened before.
class InventoryToggleEvent(Event):
    def __init__(self):
        Event.__init__(self)
        
# GameMenuToggleEvent.
# Posted by the InputController when the user pressed the Esc key during gameplay. It causes
# the Game object to order the opening or closing of the game menu, depending on
# whether it was closed or opened before (and only if the inventory
# screen is not up at the moment).
class GameMenuToggleEvent(Event):
    def __init__(self):
        Event.__init__(self)
        
# MainMenuSwitchRequestEvent.
# Posted by the InputController when the escape key was pressed during gameplay.
# Also posted after the game has finished.
class MainMenuSwitchRequestEvent(Event):
    def __init__(self):
        Event.__init__(self)