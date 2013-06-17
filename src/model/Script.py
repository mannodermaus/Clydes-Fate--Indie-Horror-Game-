# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.interfaces import Storage
import threading

# Script.
# Instances of this class represent a script event that happens on the
# map they are part of. Basically, the Tiled information on the Scripts layer
# is encapsulated in this class. A Script object has a reference to a
# method found in ScriptEngine.py, which handles the execution of this script.
# The script's contents are being kept in a separate thread. Therefore
# an executing script does not stop the main render thread.
class Script:
    # Internal class ScriptThread.
    # Content manager for the encapsulated Script object.
    # Extends:
    #   threading.Thread
    class ScriptThread(threading.Thread):
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
                self.method(self.object, self.map)
                # Afterwards, prepare for another run
                self.object._conclude()
            except Storage.Break:
                # A Storage.Break object is created when the game exits
                # while the callback is still being processed. Thus,
                # these are used to "kill" the thread's execution.
                pass
    # /CLASS
        
    # Constructor of Script objects.
    # Parameters:
    #   name    :   The name of the script in Tiled
    #   rect    :   The pygame Rect object that makes up the region
    #               where the script is triggered when colliding with the player
    #   callback:   The callback method name (not function!)
    #               to be retrieved from the ScriptEngine
    #   map     :   Map object that this script belongs to
    def __init__(self, name, rect, callback, m, _1=0, _2=0):
        # Init attributes
        self.name = name
        self.rect = rect
        self.methodname = callback
        self.map = m
        # Get the actual method handle from the string name
        from src.controller import ScriptEngine
        self.callback = ScriptEngine.get(callback)
        # Init the execution thread
        self._conclude()
        
    # Run method of the script. This is not overriding a Thread.run() method,
    # because a Script object does not extend threading.Thread! It is just named
    # that way to remind of the internal workings of this class.
    def run(self):
        # If the script's thread is not already running...
        if not self.running:
            # Start it, and set it to "running"
            self.thread.start()
            self.running = True
            
    # Sets the map reference for this Clickable object
    # Parameter:
    #    m    :    The Map object to be set
    def setMap(self, m):
        self.map = m
        self._conclude()
        
    # Re-initialization of the script's thread object.
    def _conclude(self):
        self.thread = Script.ScriptThread(self, self.callback, self.map)
        self.running = False
            
    # String representation of a Script object
    # Returns:
    #   Exactly that.
    def __repr__(self):
        return "(src.model.Script) '%s' (Interaction method: %s())" % (self.name, self.methodname)
        
    # Pickling a Script object
    # Returns:
    #   The modified dict of attributes to be pickled
    def __getstate__(self):
        # Copy the object's dict, delete the thread and callback method handle, and return that modified dict
        attrs = self.__dict__.copy()
        del attrs['callback']
        del attrs['thread']
        del attrs['map']
        return attrs
        
    # Unpickling a Script object
    # Parameter:
    #   dict    :   The dict to be applied
    def __setstate__(self, dd):
        # Update the object's dict
        self.__dict__.update(dd)
        # Then, re-initialize the method handle and the object's execution thread
        from src.controller import ScriptEngine
        self.callback = ScriptEngine.get(self.methodname)
        self.map = None
        self._conclude()
        
class TeleportScript(Script):
    # Internal class TeleportThread.
    # Content manager for the encapsulated TeleportScript object.
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
                self.method(self.map, self.object.target, self.object.destination)
                # Afterwards, prepare for another run
                self.object._conclude()
            except Storage.Break:
                # A Storage.Break object is created when the game exits
                # while the callback is still being processed. Thus,
                # these are used to "kill" the thread's execution.
                pass
    # /CLASS
    # Constructor of TeleportScript objects.
    # Parameters:
    #   name        :   The name of the script in Tiled
    #   rect        :   The pygame Rect object that makes up the region
    #                   where the script is triggered when colliding with the player
    #   map         :   Map object that this script belongs to
    #   target_id   :   Name of the map that this teleport will bring the player to
    #   target_x    :   x coordinate in pixel of the destination
    #   target_y    :   y coordinate in pixel of the destination
    def __init__(self, name, rect, m, target_id, target_x, target_y):
        Script.__init__(self, name, rect, "teleport", m)
        # Init extra attributes
        self.target = target_id
        self.destination = (target_x, target_y)
        # Init the execution thread
        self._conclude()
            
    # Re-initialization of the script's thread object.
    def _conclude(self):
        self.thread = TeleportScript.TeleportThread(self, self.callback, self.map)
        self.running = False
               
    # String representation of a Script object
    # Returns:
    #   Exactly that.
    def __repr__(self):
        return "(src.model.TeleportScript) '%s' (Destination: %s @ %d,%d)" %\
                (self.name, self.target, self.destination[0], self.destination[1])