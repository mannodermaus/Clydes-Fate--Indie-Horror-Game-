# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.interfaces import Storage
from src.model import ObjectEngine
import pygame
import threading

# Clickable.
# Instances of this class represent an object in the game world
# which the player can interact with. Basically, the Tiled information on the Objects layer
# is encapsulated in this class. A Clickable object has a reference to a
# method found in ObjectEngine.py, which handles the behaviour of the clickable object
# with respect to the current game state and the information stored in
# the player's shelf, ergo, the things he already accomplished during
# his playthrough. The clickable's contents are being kept in a separate thread. Therefore
# the interaction with a clickable object does not stop the main render thread.
class Clickable:
    # Internal class ClickableThread.
    # Content manager for the encapsulated Clickable object.
    # Extends:
    #   threading.Thread
    class ClickableThread(threading.Thread):
        #Constructor
        # Parameters:
        #   o       :   The encapsulating Clickable object
        #   method  :   The method handle for the clickable's execution inside of ObjectEngine.py
        #   map     :   The map object to which this Clickable belongs
        def __init__(self, o, method, m):
            threading.Thread.__init__(self)
            self.object = o
            self.method = method
            self.map = m
        
        # Run method override, inherited by threading.Thread.
        # This method calls the method handle and orders the Clickable
        # to re-initialize the execution thread again, making it ready
        # for another go.
        def run(self):
            try:
                # Call the callback method
                self.method(self.object, self.map)
                # Afterwards, prepare for another run
                self.object._conclude()
            except Storage.Break:
                # A Storage.Break object is created when the game exits
                # while the callback is still being processed. Thus,
                # these are used to "kill" the thread's execution.
                pass
    # /CLASS
    
    # Constructor
    # Parameters:
    #   name        :   The name of the object in Tiled
    #   rect        :   The pygame Rect object that makes up the region of this object
    #                   (its boundaries are also defined in Tiled)
    #   callback    :   The callback method name (not function!)
    #                   to be retrieved from the ObjectEngine
    #   map         :   Map object that this clickable belongs to
    #   image       :   Pygame surface for this clickable (can be None; this is for "collectable" objects
    #                   like keys on the floor etc.)
    #   imagefile   :   String rep of the image
    #   blocked     :   True, if this clickable is not walkable by the player (default: False)
    def __init__(self, name, rect, methodname, m, image=None, imagefile=None, blocked=False):
        # Init attributes
        self.name = name
        self.rect = rect
        self.funcname = methodname
        self.blocked = blocked
        # Obtain the method handle from ObjectEngine
        self.callback = ObjectEngine.get(methodname)
        self.map = m
        self.image = image
        self.imagefile = imagefile
        # Prepare execution thread
        self._conclude()
        
    # Run method of the object. This is not overriding a Thread.run() method,
    # because a Clickable object does not extend threading.Thread! It is just named
    # that way to remind of the internal workings of this class.
    def run(self):
        # If the script's thread is not already running...
        if not self.running:
            # ...start it and set state to "running"
            self.thread.start()
            self.running = True
        else:
            self._conclude()
            self.run()
            
    # Sets the map reference for this Clickable object
    # Parameter:
    #    m    :    The Map object to be set
    def setMap(self, m):
        self.map = m
        self._conclude()
        
    # Change the image of this clickable object
    # Parameter:
    #    newimagefile    :    The new file path of the changed graphic.
    #                         If None is passed in, the current image is deleted
    #    keepcol         :    Boolean depicting if the object should maintain its collision aspect
    def changeImage(self, newimagefile, keepcol=False):
        if newimagefile is not None:
            self.imagefile = newimagefile
            self.image = pygame.image.load(newimagefile).convert_alpha()
        else:
            self.image = None
            self.imagefile = None
            
        if self.map is not None:
            self.map.changeSprite(self, keepcol)
        
    # Re-initialization of the clickable's thread object.
    def _conclude(self):
        self.thread = Clickable.ClickableThread(self, self.callback, self.map)
        self.running = False
        
    # Sets the blocked status of this Clickable object.
    # Parameter:
    #    b    :    Boolean to set the status to
    def setBlocked(self, b):
        self.blocked = b
        self.map.refreshCollisionLayer()
            
    # String representation of a Clickable object
    # Returns:
    #   Exactly that.
    def __repr__(self):
        return "(src.model.Clickable) '%s' (%s)" % (self.name, self.image)
        
    # Pickling a Clickable object
    # Returns:
    #   The modified dd of attributes to be pickled
    def __getstate__(self):
        # Copy the object's dd, delete the thread and callback method handle, and return that modified dd
        attrs = self.__dict__.copy()
        del attrs['callback']
        del attrs['thread']
        del attrs['image']
        del attrs['map']
        return attrs
        
    # Unpickling a Clickable object
    # Parameter:
    #   dd    :   The dd to be applied
    def __setstate__(self, dd):
        # Update the object's dd
        self.__dict__.update(dd)
        # Then, re-initialize the method handle and the object's execution thread
        self.callback = ObjectEngine.get(self.funcname)
        # Reload picture
        if self.imagefile is not None:
            self.image = pygame.image.load(self.imagefile).convert_alpha()
        else:
            self.image = None
        self.map = None
        self._conclude()
        
# TeleportClickable.
# A special subclass of Clickable objects that have a convenient
# way to transition between maps.
class TeleportClickable(Clickable):
    # Internal class TeleportThread.
    # Content manager for the encapsulated TeleportClickable object.
    # Extends:
    #   threading.Thread
    class TeleportThread(threading.Thread):
        # Constructor
        # Parameters:
        #   object  :   The encapsulated Script object
        #   method  :   The ScriptEngine method to be executed in this thread
        #   map     :   The Map object that the encapsulated
        #               Script object is being held in
        def __init__(self, o, method, m):
            threading.Thread.__init__(self)
            self.object = o
            self.method = method
            self.map = m
            
        # Run method, inherited from threading.Thread.
        # This executes the callback method in ScriptEngine, and after
        # its execution, "concludes" the Script object, therefore preparing
        # it for another round of execution.
        def run(self):
            try:
                # Call the callback method
                self.method(self.map, self.object, \
                            self.object.target, self.object.destination)
                # Afterwards, prepare for another run
                self.object._conclude()
            except Storage.Break:
                # A Storage.Break object is created when the game exits
                # while the callback is still being processed. Thus,
                # these are used to "kill" the thread's execution.
                pass
                
    # /CLASS
    
    # Constructor
    # Parameters:
    #   name        :   The name of the object in Tiled
    #   rect        :   The pygame Rect object that makes up the region of this object
    #                   (its boundaries are also defined in Tiled)
    #   m           :   Map object that this clickable belongs to
    #   callback    :   The callback method name (not function!)
    #                   to be retrieved from the ObjectEngine
    #   sound       :   The sound that this TeleportClickable should
    #                   play when the transition is successful
    #   target_id   :   Name of the map to which this TeleportClickable should lead
    #   target_x    :   x position on the target map
    #   target_y    :   y position on the target map
    #   image       :   Pygame surface for this clickable (can be None; this is for "collectable" objects
    #                   like keys on the floor etc.)
    #   imagefile   :   String rep of the image
    #   blocked     :   True, if this clickable is not walkable by the player (default: False)
    
    def __init__(self, name, rect, m, callback,\
                 sound, target_id, target_x, target_y,\
                 image=None, imagefile=None, blocked=False):
        if callback is None:
            self.funcname = "teleport"
        else:
            self.funcname = callback
        # Init extra attributes
        self.target = target_id
        self.destination = (target_x, target_y)
        self.map = m
        self.sound = sound
        # Super constructor for proper initialization of the rest
        Clickable.__init__(self, name, rect, self.funcname, m, image, imagefile, blocked)
        # Prepare execution thread
        self._conclude()
        
        
    # Run method of the object. This is not overriding a Thread.run() method,
    # because a Clickable object does not extend threading.Thread! It is just named
    # that way to remind of the internal workings of this class.
    def run(self):
        # If the script's thread is not already running...
        if not self.running:
            # ...start it and set state to "running"
            self.thread.start()
            self.running = True
        else:
            self._conclude()
            self.run()
            
    # Re-initialization of the clickable's thread object.
    def _conclude(self):
        self.thread = TeleportClickable.TeleportThread(self, self.callback, self.map)
        self.running = False
            
    # String representation of a Clickable object
    # Returns:
    #   Exactly that.
    def __repr__(self):
        return "(src.model.TeleportClickable) '%s' (Destination: %s @ %d,%d)" %\
                (self.name, self.target, self.destination[0], self.destination[1])
                
