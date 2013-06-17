# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import PLAYER_MOVEMENT_ENABLED
from src.controller import GlobalServices
from src.interfaces import Storage
from src.model.EventTypes import MapChangeRequestEvent
from src.model.Timer import Timer
from src.model.scripts import rightwing, righthallway, atrium, mirrorhall, \
    librarydownstairs, libraryupstairs
from src.utilities import update_persistent_map_properties, set_property, \
    get_savegame
from src.view import OverlayFactory

# ScriptEngine.
# The motor behind the execution of script events
    
# ScriptsStorage.
# There is no need to instantiate this class from outside this module.
# It contains the callback methods for scripts. The only parameter is the tmxmap reference,
# so that overlay changes may be processed as well in that script. By calling
# ScriptEngine.run(Script), an associated method from this class instance is called.
# Script implementation methods always have these parameters:
#    obj    :    The Script object that is triggered upon calling
#    m      :    The Map object that belongs to this object
# The "script's way of teleporting" to another map uses other parameters described below
class ScriptsStorage(Storage):
    # Constructor
    def __init__(self):
        super(ScriptsStorage, self).__init__()
        self.teleport_in_progress = False
        
    # Righthallway.tmx
    def righthallway_dronesound(self, obj, m):
        righthallway.dronesound(self, obj, m)
        
    def righthallway_leftroomopening(self, obj, m):
        righthallway.leftroomopening(self, obj, m)
        
    # Rightwing.tmx
    def rightwing_powercutshort(self, obj, m):
        rightwing.powercutshort(self, obj, m)
        
    # Atrium.tmx
    def atrium_sfx(self, obj, m):
        atrium.sfx(self, obj, m)
        
    def atrium_scare(self, obj, m):
        atrium.scare(self, obj, m)
        
    # Mirrorhall.tmx
    def mirrorhall_murderscene(self, obj, m):
        mirrorhall.murderscene(self, obj, m)
        
    # Librarydownstairs.tmx
    def librarydownstairs_noise(self, obj, m):
        librarydownstairs.noise(self, obj, m)
        
    # Libraryupstairs.tmx
    def libraryupstairs_scare(self, obj, m):
        libraryupstairs.scare(self, obj, m)
        
    # Teleport method, called by every TeleportScript object.
    # The parameters for this one are different and contain the following:
    # Parameters:
    #    source        :    The tmxmap name to be teleported from
    #    target        :    The tmxmap name to be teleported to
    #    destination   :    Tuple of coordinates which describe the destination position
    def teleport(self, source, target, destination):
        self._go()
        self.teleport_in_progress = True
        set_property(PLAYER_MOVEMENT_ENABLED, False)
        
        # Save the state of the current map's properties to the persistent shelf
        # before teleporting to the new map
        update_persistent_map_properties(source, get_savegame())
        
        dur = 1000
        fadeout = OverlayFactory.create_animated_color((0,0,0), dur, 0, True, 0, 255)
        source.addOverlay(fadeout)
        self._wait(dur)
        source.rendering_enabled = False
        GlobalServices.getEventManager().post(MapChangeRequestEvent((target, destination)))
        
        set_property(PLAYER_MOVEMENT_ENABLED, True)
        source.removeOverlay(fadeout)
        
        self.teleport_in_progress = False
        self._halt()
    
# Global instance to store all script-callback methods
storage = ScriptsStorage()
# Dummy method handle for every script whose
# Tiled method handle parameter does not exist in the ScriptsStorage
dummymethod = lambda x,y: GlobalServices.getLogger().log(\
                             "This is not implemented in ScriptEngine.py")
cooldown = False

# Shutdown method sent by the Game object in case of a QuitEvent.
# It orders executing script threads to kill.
def shutdown():
    storage.interrupted = True
    storage.running = False
        
# Retrieves the storage object's method handle using a string name of the desired method.
# This is called by the Script class constructor upon initializing a Script object.
# Parameter:
#   methodname  :   The string method name to be retrieved
# Returns:
#   The method handle for that method, or the dummy method if it doesn't exist
def get(methodname):
    try:
        return getattr(storage, methodname)
    except AttributeError:
        # If the method could not be found, inform the logger to print it out and return a dummy method
        return dummymethod
        
def isCooldown():
    global cooldown
    return cooldown

def toggleCooldown(b):
    global cooldown
    cooldown = b
    
# Runs a script on the engine. This method ensures that other running interactions
# are stopped before executing the new one.
# Parameter:
#   script  :   The Script object to be executed
def run(script):
    if storage.teleport_in_progress or \
    isCooldown():
        return
    storage.object = script
    storage.running = True
    toggleCooldown(True)
    script.run()
    def cb():
        toggleCooldown(False)
    delaytimer = Timer(200, None, cb)
    delaytimer.start()

# Returns the current ScriptEngine status.
# Returns:
#   True, if a script is currently being executed, False otherwise    
def isRunning():
    return storage.running