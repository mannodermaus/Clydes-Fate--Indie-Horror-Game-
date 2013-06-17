# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from libs import tiledtmxloader
from src.constants import PATH_MAPS, PATH_GRAPHICS_TILES
from src.controller import GlobalServices
from src.model import ObjectEngine
from src.model.Clickable import Clickable, TeleportClickable
from src.model.EventTypes import MapLoadingDoneEvent, MapLoadingEvent, \
    MapLoadingFailedEvent
from src.model.Map import Map
from src.model.Script import Script, TeleportScript
import os
import pygame
import threading

# MapFactory.
# Factory class that is able to load up Map objects and also
# deal with unpickling Map objects.
# It uses the EventManager to post messages to every listener
# about the current state of the loading process.

# Dictionary of loaded maps held by the MapFactory.
# The getMap(key) method may be invoked to retrieve a Map object
# from the dictionary.
_MAPS = {}

# Retrieves a map from the loaded map dictionary
# Parameter:
#    key    :    The key name (file name) of the Map object
# Returns:
#    Reference to the Map object, or None if this key doesn't exist
def getMap(key):
    try:
        return _MAPS[key]
    except KeyError:
        return None
    
# Checks if the Map object for the given key has already been loaded.
# Parameter:
#    key    :    The key name (file name) to be looked for
# Returns:
#    True, if the Map object exists in the Map dictionary, False if not
def mapAlreadyLoaded(key):
    return (getMap(key) is not None)

# Load and prepare the map with the given file name.
# Parameter:
#   mapname       :    The string name of the map file. This does not need
#                      to include the complete path ("assets/maps...")! Only
#                      the file name without extension itself is necessary.
#   properties    :    MapProperties object to be applied to the loaded TMX map.
#                      This may be None. If it is, the needed information is
#                      also loaded from the TMX
def loadMap(mapname, properties):
    # Internal class MapLoadingThread.
    # A working thread used to load a map complete with interactive
    # objects and scripts. This runs in a thread so it does not
    # pause the main thread while reading the Tiled data.
    # Extends:
    #   threading.Thread
    class MapLoadingThread(threading.Thread):
        # Constructor
        # Parameter:
        #   name    :   The map name to be loaded without extension
        def __init__(self, name, properties):
            threading.Thread.__init__(self)
            self.name = name
            self.props = properties
            
        # Run method, inherited from threading.Thread,
        # that processes the actual loading of a map.
        def run(self):
            file_name = os.path.join(PATH_MAPS, "%s.tmx" % self.name)
            # Decode the map
            try:
                tilemap = tiledtmxloader.tmxreader.TileMapParser().parse_decode(file_name)
            except IOError:
                GlobalServices.getEventManager().post(MapLoadingFailedEvent(self.name))
                return
            tilemap.properties['file_name'] = file_name
            tilemap.properties['key_name'] = self.name
            # Post a loading event
            try:
                mapname = tilemap.properties['name']
            except KeyError:
                mapname = "<Map without a Name>"
            GlobalServices.getEventManager().post(MapLoadingEvent(mapname))
            # Load its resources
            resources = tiledtmxloader.helperspygame.ResourceLoaderPygame()
            resources.load(tilemap)
            # Create its layers
            layers = tiledtmxloader.helperspygame.get_layers_from_map(resources)
            # Prepare handles for collision and hero layers
            object_layers = [layer for layer in layers if layer.is_object_group]
            sprite_layers = [layer for layer in layers if not layer.is_object_group]
            cLayer = sprite_layers[-1]
            hLayer = [layer for layer in sprite_layers if layer.name == "hero"][0]
            clLayer= [layer for layer in sprite_layers if layer.name == "clickables"][0]
            # Deal with paralax layers
            paralaxLayers = [layer for layer in sprite_layers if layer.name == "paralax"]
            for p in paralaxLayers:
                p.set_layer_paralax_factor(float(p.properties["factor"]))
                
            # Create the Map object
            m = Map(tilemap.properties, cLayer, hLayer, clLayer, sprite_layers)
            
            # Setup the "interactives extraction"
            oLayer = [layer for layer in object_layers if layer.name == "objects"][0]
            
            # In case no properties are given to the MapFactory,
            # the objects and scripts information is parsed from the TMX map as well.
            if self.props is None:
                # Create distinct objects for scripts and clickables
                sLayer = [layer for layer in object_layers if layer.name == "scripts"][0]
                # Create interactive objects
                scripts = []
                objects = []
                for script in sLayer.objects:
                    name = script.name
                    rect = pygame.Rect(script.x, script.y, script.width, script.height)
                    # Fetch teleport scripts and add different things
                    if script.type == "teleport":
                        target = script.properties["target"]
                        dest_x = int(script.properties["x"]) * tilemap.tilewidth
                        dest_y = int(script.properties["y"]) * tilemap.tileheight
                        newscript = TeleportScript(name, rect, m, target, dest_x, dest_y)
                    # Fetch callback function from normal scripts
                    else:
                        callback = script.properties["func"]
                        newscript = Script(name, rect, callback, m)
                    scripts.append(newscript)
                    
                init_callback = None
                    
                for o in oLayer.objects:
                    # If there is an INIT object on the map, pass its callback along with
                    # the MapLoadingDoneEvent (an INIT event may setup initial things like
                    # ambient sounds etc.)
                    name = o.name
                    rect = pygame.Rect(o.x, o.y, o.width, o.height)
                    if (o.type == "init"):
                        init_callback = ObjectEngine.get(o.properties["func"])
                        continue
                    elif (o.type == "teleport"):
                        # Teleport Objects are most commonly found in the form of doors
                        # A teleport object may or may not have a func attribute. This
                        # extra callback can define altering behaviour (e.g. a door only
                        # opens once a certain key is aquired). If no func attribute is
                        # specified, the door basically opens every time
                        try:
                            callback = o.properties["func"]
                        except KeyError:
                            callback = None
                        try:
                            sound = o.properties["sound"]
                        except KeyError:
                            sound = None
                        target = o.properties["target"]
                        dest_x = int(o.properties["x"]) * tilemap.tilewidth
                        dest_y = int(o.properties["y"]) * tilemap.tileheight
                        newobject = TeleportClickable(name, rect, m, callback,\
                                                      sound, target, dest_x, dest_y)
                        
                    else:
                        callback = o.properties["func"]
                        try:
                            # Try to load the image property of this object
                            # (it will raise a KeyError if this is not the case;
                            # handle this error by setting both image and imagefile to None!)
                            imagefile = os.path.join(PATH_GRAPHICS_TILES, o.properties["image"])
                            image = pygame.image.load(imagefile).convert_alpha()
                        except KeyError:
                            imagefile = None
                            image = None
                        except pygame.error as e:
                            GlobalServices.getLogger().log(e)
                            imagefile = os.path.join(PATH_GRAPHICS_TILES, "defaulttile.png")
                            image = pygame.image.load(imagefile).convert_alpha()
                        try:
                            # Try to get the "block" attribute. If this is set in the object,
                            # this object prevents the player from walking on it
                            # (can be changed using setBlocked(bool) again)
                            blocked = o.properties["block"]
                            if blocked == "True":
                                blocked = True
                        except KeyError:
                            blocked = False
                        newobject = Clickable(name, rect, callback, m, image, imagefile, blocked)
                        
                    objects.append(newobject)
            # Else, there are pre-given properties for objects and scripts on that map.
            else:
                # Get the lists of objects/scripts from the MapProperties object
                scripts = self.props.scripts
                objects = self.props.objects
                # Update the objects' map reference
                for s in scripts:
                    s.setMap(m)
                for o in objects:
                    o.setMap(m)
                # In any case, set the init callback method if there is one.
                init_callback = None
                for o in oLayer.objects:
                    if o.type == "init":
                        init_callback = ObjectEngine.get(o.properties["func"])                        
                
            # Set the object and script objects for the map,
            # save it in the MapFactory's dict of loaded maps and return it
            m.setInteractives(scripts, objects)
            _MAPS[self.name] = m
            # Check the map's init method. If there is None,
            # set it to the default (ObjectEngine.global_inits)
            if init_callback is None:
                init_callback = ObjectEngine.get('global_inits')
            m.init_method = init_callback
            GlobalServices.getEventManager().post(MapLoadingDoneEvent([m, init_callback]))
    # /CLASS
    
    # Start loading process
    MapLoadingThread(mapname, properties).start()
    
# Clears all loaded maps
def clearMaps():
    _MAPS.clear()