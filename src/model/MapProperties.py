# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

# MapProperties.
# Holds a persistent state of a Map, ergo
# the objects and scripts that represent
# the current state of the Map.

# Constants for add/remove methods.
# When calling one of these methods,
# a constant parameter is provided to
# access a specific list of MapProperties.
SCRIPT = 1
OBJECT = 2
TELEPORTSCRIPT = 3
TELEPORTOBJECT = 4

class MapProperties:
    # Constructor
    # Parameter:
    #    m    :    The Map object whose properties are to be stored
    def __init__(self, m):
        self.objects = m.objects
        self.scripts = m.scripts
        
    # Returns one of the MapProperties' lists depending
    # on the constant that is passed into this method
    # Parameter:
    #    constant    :    A constant of this class depicting the
    #                     list to be returned
    # Returns:
    #    Either self.scripts or self.objects depending on the parameter
    def _getList(self, constant):
        items = []
        if constant in [SCRIPT, TELEPORTSCRIPT]:
            items = self.scripts
        elif constant in [OBJECT, TELEPORTOBJECT]:
            items = self.objects
        return items
        
    # Retrieves an object reference in the given list.
    # This is being called when MapProperties.remove()
    # is being passed in a string name of an object rather
    # than the object reference itself
    # Parameters:
    #    items    :    List to be checked
    #    name     :    Name to be checked in that list
    # Returns:
    #    The object reference that belongs to the name parameter
    def _getItemByName(self, items, name):
        for l in items:
            if l.name == name:
                return l
        return None
        
    # Returns an object of the MapProperties
    # Parameter:
    #    name    :    Name of the object to be retrieved
    # Returns:
    #    The object or None
    def get(self, name):
        obj = self._getItemByName(self.objects, name)
        if obj is not None:
            return obj
        obj = self._getItemByName(self.scripts, name)
        return obj
    
    # Updates an object of the MapProperties
    # Parameter:
    #    obj    :    Object to update
    def update(self, obj):
        name = obj.name
        for c in [OBJECT, SCRIPT]:
            l = self._getList(c)
            for item in l:
                if item.name == name:
                    self.remove(c, item)
                    self.add(c, obj)
                    return
        
    # Adds a new object to the MapProperties
    # Parameters:
    #    constant    :    Constant of this class depicting which list to use
    #    ref         :    Reference to the object to be added
    def add(self, constant, ref):
        items = self._getList(constant)
        # Add the object to the list
        items.append(ref)
        # Save persistent changes in 
    
    # Removes an object from a list of the MapProperties
    # Parameters:
    #    constant    :    Constant of this class depicting which list to use
    #    name_or_ref :    Name of the object to remove, or the reference to it
    def remove(self, constant, name_or_ref):
        items = self._getList(constant)
        # Get the reference of the object if just a string was passed in
        if type(name_or_ref) == str:
            ref = self._getItemByName(items, name_or_ref)
        else:
            ref = name_or_ref
        # Remove the object from the list
        if ref in items:
            items.remove(ref)
    
    # String representation of a MapProperties
    # Returns:
    #    String reference of this object
    def __repr__(self):
        return "MapProperties\n\tObjects: " + \
            str(self.objects) + "\n\tScripts:" + str(self.scripts)