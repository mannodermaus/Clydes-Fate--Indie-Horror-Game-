# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import PLAYER_MOVEMENT_ENABLED
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND
from src.interfaces import Storage
from src.model.EventTypes import MapChangeRequestEvent, ObjectHighlightedEvent
from src.model.scripts import bedroom, righthallway, mainhall, leftwing, \
    guestroom, atrium, lefthallway, abandonedchamber, mirrorhall, librarydownstairs, \
    libraryupstairs, rightwing, masterroom, attic
from src.utilities import update_persistent_map_properties, get_global_overlays, \
    set_property, get_savegame
from src.view import OverlayFactory

# ObjectEngine.
# Hugely important module of the application, as the interactions
# between any clickable object in the game causes this engine to
# be notified. The engine then initializes the interaction and calls
# the appropriate function inside the central ObjectStorage object.
# This function then delegates the call other modules that belong to the maps
# (see src.model.scripts), but this is the starting point.

# ObjectStorage.
# Singleton-ish object that holds the callback
# methods for all the interactive objects.
class ObjectStorage(Storage):
    # Constructor
    def __init__(self):
        super(ObjectStorage, self).__init__()
        
    # Global overlays initialization method.
    # There is a global list of overlays that are applied to every map
    # upon entering. The two main reasons for this are Flashlight Overlays
    # and Darkened Screens. When a Map object does not provide an INIT object,
    # this method is called anyway to init the correct display of the map
    # Parameters:
    #    m            :    The map object whose overlays are about to be set
    #    handlerAv    :    Boolean switch depicting if there is another init method
    #                      to initialize the map. This is false by default
    def global_inits(self, m, handlerAv=False):
        GlobalServices.getEventManager().post(ObjectHighlightedEvent(None))
        # Check if the current global overlays are already equivalent to the map's ones
        if m.overlays != get_global_overlays():
            # Remove overlays
            m.clearOverlays()
            # Add global overlays
            for o in get_global_overlays():
                m.addOverlay(o)
            m.flushOverlayQueue()
        # If no other handler init method is attached to this init,
        # this method does the enabling of map rendering (so that you can see stuff)
        if not handlerAv:
            m.rendering_enabled = True
        
    # Bedroom.tmx
    def init_bedroom(self, m):
        self.global_inits(m, True)
        bedroom.init(self, m)
        
    def bedroom_bed(self, obj, m):
        bedroom.bed(self, obj, m)
        
    def bedroom_bookshelf(self, obj, m):
        bedroom.bookshelf(self, obj, m)
        
    def bedroom_closet(self, obj, m):
        bedroom.closet(self, obj, m)
        
    def bedroom_flashlight(self, obj, m):
        bedroom.flashlight(self, obj, m)
        
    def bedroom_tprhallway(self, source, obj, target, destination):
        success = bedroom.tprhallway(self, source, obj)
        if success:
            self.teleport(source, obj, target, destination)     
        
    # Rightwing.tmx
    def rightwing_ladder(self, obj, m):
        rightwing.ladder(self, obj, m)
    
    # Righthallway.tmx
    def init_righthallway(self, m):
        self.global_inits(m, True)
        righthallway.init(self, m)
        
    def righthallway_worldmap(self, obj, m):
        righthallway.worldmap(self, obj, m)
        
    def righthallway_tp_atrium(self, source, obj, target, destination):
        success = righthallway.tpatrium(self, source, obj)
        if success:
            self.teleport(source, obj, target, destination)
        
    def righthallway_tp_storageroom(self, source, obj, target, destination):
        success = righthallway.tpstorage(self, source, obj)
        if success:
            self.teleport(source, obj, target, destination)
            
    def righthallway_tp_guestroom(self, source, obj, target, destination):
        success = righthallway.tpguestroom(self, source, obj)
        if success:
            self.teleport(source, obj, target, destination)
            
    def righthallway_tp_study(self, source, obj, target, destination):
        success = righthallway.tpstudy(self, source, obj)
        if success:
            self.teleport(source, obj, target, destination)
            
    # Mainhall.tmx
    def mainhall_entrancenote(self, obj, m):
        mainhall.entrancenote(self, obj, m)
        
    def mainhall_paintingd(self, obj, m):
        mainhall.paintingd(self, obj, m)
        
    def mainhall_paintingr(self, obj, m):
        mainhall.paintingr(self, obj, m)
        
    def mainhall_paintingl(self, obj, m):
        mainhall.paintingl(self, obj, m)
        
    def mainhall_closetl(self, obj, m):
        mainhall.closetl(self, obj, m)
        
    def mainhall_closetr(self, obj, m):
        mainhall.closetr(self, obj, m)
        
    def mainhall_bookshelf(self, obj, m):
        mainhall.bookshelf(self, obj, m)
        
    def mainhall_piano(self, obj, m):
        mainhall.piano(self, obj, m)
        
    def mainhall_tpoutside(self, source, obj, target, destination):
        success = mainhall.tpoutside(self, source, obj)
        if success:
            self.teleport(source, obj, target, destination)
        
    # Leftwing.tmx
    def leftwing_blockingdebris(self, obj, m):
        leftwing.blockingdebris(self, obj, m)
        
    def leftwing_note(self, obj, m):
        leftwing.note(self, obj, m)
        
    # Guestroom.tmx
    def guestroom_keyshelf(self, obj, m):
        guestroom.keyshelf(self, obj, m)
        
    def guestroom_switch(self, obj, m):
        guestroom.switch(self, obj, m)
        
    # Atrium.tmx        
    def atrium_hintnote(self, obj, m):
        atrium.hintnote(self, obj, m)
        
    def atrium_message(self, obj, m):
        atrium.message(self, obj, m)
        
    def atrium_blockingshelf(self, obj, m):
        atrium.blockingshelf(self, obj, m)
        
    def atrium_mastershelf(self, obj, m):
        atrium.mastershelf(self, obj, m)
        
    def atrium_tplibrary(self, source, obj, target, destination):
        success = atrium.tplibrary(self, source, obj)
        if success:
            self.teleport(source, obj, target, destination)
        
    def atrium_tpmasterroom(self, source, obj, target, destination):
        success= atrium.tpmasterroom(self, source, obj)
        if success:
            self.teleport(source, obj, target, destination)
    
    # Lefthallway.tmx
    def init_lefthallway(self, m):
        self.global_inits(m, True)
        lefthallway.init(self, m)
        
    def lefthallway_switch1(self, obj, m):
        lefthallway.switch(self, obj, m, 1)
        
    def lefthallway_switch2(self, obj, m):
        lefthallway.switch(self, obj, m, 2)
        
    def lefthallway_switch3(self, obj, m):
        lefthallway.switch(self, obj, m, 3)
        
    def lefthallway_switch4(self, obj, m):
        lefthallway.switch(self, obj, m, 4)
        
    def lefthallway_switch5(self, obj, m):
        lefthallway.switch(self, obj, m, 5)
        
    def lefthallway_familyportrait(self, obj, m):
        lefthallway.familyportrait(self, obj, m)
        
    def lefthallway_tpupperbalcony(self, source, obj, target, destination):
        success = lefthallway.tpupperbalcony(self, source, obj)
        if success:
            self.teleport(source, obj, target, destination)
        
    def lefthallway_tpmirrorhall(self, source, obj, target, destination):
        success = lefthallway.tpmirrorhall(self, source, obj)
        if success:
            self.teleport(source, obj, target, destination)
            
    # Abandonedchamber.tmx
    def abandonedchamber_canvas(self, obj, m):
        abandonedchamber.canvas(self, obj, m)
        
    # Mirrorhall.tmx
    def mirrorhall_claire(self, obj, m):
        mirrorhall.claire(self, obj, m)
        
    def mirrorhall_librarykey(self, obj, m):
        mirrorhall.librarykey(self, obj, m)
        
    def mirrorhall_message(self, obj, m):
        mirrorhall.message(self, obj, m)
        
    # Librarydownstairs.tmx
    def librarydownstairs_painting(self, obj, m):
        librarydownstairs.painting(self, obj, m)
        
    def librarydownstairs_note(self, obj, m):
        librarydownstairs.note(self, obj, m)
        
    def librarydownstairs_message(self, obj, m):
        librarydownstairs.message(self, obj, m)
        
    # Libraryupstairs.tmx
    def libraryupstairs_shelf(self, obj, m):
        libraryupstairs.shelf(self, obj, m)
        
    def libraryupstairs_officelever(self, obj, m):
        libraryupstairs.officelever(self, obj, m)
        
    def libraryupstairs_officenote(self, obj, m):
        libraryupstairs.officenote(self, obj, m)
        
    def libraryupstairs_relaxlever(self, obj, m):
        libraryupstairs.relaxlever(self, obj, m)
        
    def libraryupstairs_relaxnote(self, obj, m):
        libraryupstairs.relaxnote(self, obj, m)
        
    def libraryupstairs_message(self, obj, m):
        libraryupstairs.message(self, obj, m)
        
    # Masterroom.tmx
    def masterroom_ceilingdoor(self, obj, m):
        masterroom.ceilingdoor(self, obj, m)
        
    def masterroom_message(self, obj, m):
        masterroom.message(self, obj, m)     
    
    # Attic.tmx
    def init_attic(self, m):
        self.global_inits(m, True)
        attic.init(self, m)
        
    def attic_door(self, obj, m):
        attic.door(self, obj, m)
        
    def attic_photo(self, obj, m):
        attic.photo(self, obj, m)
        
    def attic_hand(self, obj, m):
        attic.hand(self, obj, m)
        
    def attic_pencil(self, obj, m):
        attic.pencil(self, obj, m)
        
    def attic_gun(self, obj, m):
        attic.gun(self, obj, m)
        
    def attic_note(self, obj, m):
        attic.note(self, obj, m)
        
    # Teleport method, called by every TeleportClickable object (even
    # if there is specific callback behaviour beforehand).
    # The parameters for this one are different and contain the following:
    # Parameters:
    #    source        :    The m name to be teleported from
    #    obj           :    TeleportClickable object
    #    target        :    The map name to be teleported to
    #    destination   :    Tuple of coordinates which describe the destination position
    def teleport(self, source, obj, target, destination):
        self._go()
        
        if self._playerInDistance(source.getPlayer().position, obj.rect):
            # Play the sound of this TeleportClickable object
            # (if there is one; could be a door squeaking etc)
            if hasattr(obj, 'sound'):
                GlobalServices.getAudioDevice().play(SOUND, obj.sound, 0.8)
            
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
            
            source.removeOverlay(fadeout)
            source.flushOverlayQueue()
            set_property(PLAYER_MOVEMENT_ENABLED, True)
            self.teleport_in_progress = False
            
        self._halt()
        
# Global instance to store all script-callback methods
storage = ObjectStorage()
# Dummy method. When (by accident) an interaction is not implemented,
# the application doesn't crash, but instead uses this method that
# does nothing but notify the logger that a method is missing.
dummymethod = lambda x,y,z=0,w=0: GlobalServices.getLogger().log(\
                                  "This is not implemented in ObjectEngine.py")
        
# Shutdown method sent by game object in case of QuitEvent
def shutdown():
    storage.interrupted = True
    storage.running = False
        
# Returns the method handle to the script name's callback,
# or causes the logger to print out a warning message.
# Parameter:
#    methodname    :    String name of the method to retrieve
#                       (according to the object's "func" parameter in the TMX map)
# Returns:
#    Method handle to this method in the ObjectStorage object
def get(methodname):
    try:
        return getattr(storage, methodname)
    except AttributeError as e:
        # If the method could not be found, inform the
        # logger to print it out and return a dummy method
        GlobalServices.getLogger().log(e)
        return dummymethod
        
# Runs the interaction of an object on the engine.
# This method ensures that other running interactions
# are stopped before executing the new one.
# Parameter:
#    o  :   The Clickable object to be executed
def interact(o):
    storage.object = o
    storage.running = True
    o.run()
    
# Returns the current ObjectEngine status.
# Returns:
#   True, if an interaction is currently being executed, False otherwise    
def isRunning():
    return storage.running