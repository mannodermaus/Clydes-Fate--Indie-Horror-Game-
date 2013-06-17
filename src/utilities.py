# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from libs import tiledtmxloader
from libs.pyganim import pyganim
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PATH_GRAPHICS_TILES, DIRS, \
    DIRDICT, GLOBAL_OVERLAYS, GLOBAL_PROPERTIES, PATH_SAVES, CURRENT_SHELF_FILENAME, \
    CURRENT_SHELF
from src.model.MapProperties import MapProperties, SCRIPT, OBJECT, \
    TELEPORTSCRIPT, TELEPORTOBJECT
import math
import os
import pygame

# utilities.
# This module provides globally accessable helper methods
# that do all sorts of helpful stuff, such as conversion
# between tile and pixel units, creation of complex
# sprite animation dictionaries, distance measuring and
# directional calculations.
    
# Maps a given direction list to the corresponding string.
# Parameter:
#   dir :   Directional vector
# Returns:
#   A string representation of this direction
def direction_to_string(direction):
    ret = None
    # 8-way sprites
    if direction == [1,0]:
        ret = "right"
    elif direction == [1,-1]:
        ret = "up-right"
    elif direction == [0,-1]:
        ret = "up"
    elif direction == [-1,-1]:
        ret = "left-up"
    elif direction == [-1,0]:
        ret = "left"
    elif direction == [-1,1]:
        ret = "down-left"
    elif direction == [0,1]:
        ret = "down"
    elif direction == [1,1]:
        ret = "right-down"
    return ret

def string_to_direction(dirs):
    ret = ""
    if dirs == "right":
        ret = [1,0]
    elif dirs == "up-right":
        ret = [1,-1]
    elif dirs == "up":
        ret = [0,-1]
    elif dirs == "left-up":
        ret = [-1,-1]
    elif dirs == "left":
        ret = [-1,0]
    elif dirs == "down-left":
        ret = [-1,1]
    elif dirs == "down":
        ret = [0,1]
    elif dirs == "right-down":
        ret = [1,1]
    return ret
    
# Measures the distance between two points in whole-number pixel units
# Parameters:
#   p   :   Point 1
#   q   :   Point 2
# Returns:
#   The distance between p and q in pixels
def measure_distance(p, q):
    return int(math.fabs(math.hypot(q[0] - p[0], q[1] - p[1])))


# Adds an overlay to the list of global overlays
# Parameter:
#    o    :    The new Overlay to be added
def add_global_overlay(o):
    GLOBAL_OVERLAYS.append(o)
    
# Removes an overlay from the list of global overlays.
# This method is safe because it checks if this overlay
# exists in the list before attempting to remove it.
# Parameter:
#    o    :    The Overlay to be removed
def remove_global_overlay(o):
    if o in GLOBAL_OVERLAYS:
        GLOBAL_OVERLAYS.remove(o)
        
# Gets the list of global overlays
# Returns:
#    The list of global overlays
def get_global_overlays():
    return GLOBAL_OVERLAYS

# Sets the list of global overlays to the given new list
# Parameter:
#    olist    :    List of Overlay objects to be set as global overlays
def set_global_overlays(olist):
    for _ in range(len(GLOBAL_OVERLAYS)):
        GLOBAL_OVERLAYS.remove(GLOBAL_OVERLAYS[0])
    GLOBAL_OVERLAYS.extend(olist)
    
# Sets the value of a property to the given boolean value.
# Parameters:
#    key    :    The property to be changed
#    value  :    The new value for this property
def set_property(key, value):
    if key in GLOBAL_PROPERTIES.keys() and type(value) == bool:
        GLOBAL_PROPERTIES[key] = value
            
# Gets the value of a property.
# Parameter:
#    key    :    The property to retrieve the value from
# Returns:
#    The value for this property
def get_property(key):
    try:
        return GLOBAL_PROPERTIES[key]
    except KeyError:
        return None
        
# Sets the shelf to the one with the given name
# Parameter:
#    name    :    The file name of the shelf to be created
def set_shelf(name):
    dirname = os.path.join(PATH_SAVES, name)
    # Create a new folder inside of the "saves" dir, if there is no such savegame
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    CURRENT_SHELF_FILENAME[0] = os.path.join(dirname, name)

# Gets the dict for the current save game
# Returns:
#    Dict with persistent stuff
def get_savegame():
    return CURRENT_SHELF[0]

# Resets the dict for the current save game
def reset_savegame():
    CURRENT_SHELF[0] = {}
    
# Convert the given animations out of a sprite sheet image. This method
# takes a huge number of parameters that define the properties of the sprite sheet in detail.
# Parameters:
#   filename    :   The filename of the spritesheet
#   offset      :   A tuple containing the pixel offset of the first sprite
#   spritesize  :   A tuple containing the pixel size of each sprite
#   data        :   List of tuples (str, []) containing the necessary information about the animations
#                   that are to be extracted from the spritesheet. Example:
#                   ("walk-left", [0,1,2,3,4]) is a valid item in the 'data' parameter;
#                   it describes the indices of sprites to be used for an animation called "walk-left"
#   duration    :   The desired duration that every frame should last (in seconds)
# Returns:
#   A dict where the animation names serve as keys and the corresponding PygAnimation objects are the values
def spritesheet_to_animations(filename, offset, ssize, data, duration):
    # Load the spritesheet
    sheet = pygame.image.load(filename).convert_alpha()
    # Extract some properties out of it using the spritesize
    numrows = int((sheet.get_height() - offset[1]) / ssize[1])
    numcols = int((sheet.get_width() - offset[0]) / ssize[0])
    # Compute the sub rectangles for every single sprite with this
    subrects = [(offset[0] + ssize[0] * x, offset[1] + ssize[1] * y, ssize[0], ssize[1]) \
               for y in range(numrows) for x in range(numcols)]
    # Define the subimage loading function.
    # Parameter:
    #   rectanle    :   Four-component tuple containing the topleft point and the size of a rectangle
    #                   to be used to define the sub-image area that is to be returned
    # Returns:
    #   A TMXSprite of the spritesheet subregion that is depicted by the given rectangle
    def getImageAtRect(rectangle):
        rect = pygame.Rect(rectangle)
        subimage = pygame.Surface(rect.size, pygame.SRCALPHA)
        subimage.blit(sheet, (0, 0), rect)
        subimage = tiledtmxloader.helperspygame.SpriteLayer.Sprite(subimage, subimage.get_rect())
        return subimage
    # Use the loading function to retrieve every frame in the sheet and store it
    subimages = [getImageAtRect(r) for r in subrects]
    # Take the data tuple list and construct PygAnimations for every one
    animdict = {}
    for t in data:
        # Extract tuple
        animname = t[0]
        animnums = t[1]
        # Construct the frame tuples of the animation (PygAnimation requires
        # tuples of "Sprite, duration" in order to manage the duration of each frame)
        animframes = [(subimages[animnums[i]], duration) for i in range(len(animnums))]
        # Create a PygAnimation object and store it as a value in the dict
        animdict[animname] = pyganim.PygAnimation(animframes)
    return animdict

# Returns the topleft point that, when used in blitting, will render the given
# surface centered on the screen.
# Parameter:
#    surface    :    The pygame Surface object to be centered
# Returns:
#    Tuple of coordinates for the topleft point of the to-be-centered Surface
def center_image(surface):
    size = surface.get_rect().size
    return (SCREEN_WIDTH/2 - size[0]/2, SCREEN_HEIGHT/2 - size[1]/2)
    
# Returns the number string of the given key index according to pygame's constants.
# Parameter:
#    key    :    Pressed key's ASCII code
# Returns:
#    Modified version of that keycode
def force_number(key):
    return str(key - 48)
    
# Copies the key/value pairs of a python dict to the shelf
# Parameter:
#   s       :   Dict object to get the stuff from
#   s2      :   The open shelve where the keys are being copied to
#   filter  :   List of keys that don't get applied to s2. This is optional
def copy_to_shelve(s, s2, f=[]):
    for k in s.keys():
        if not k in f:
            tempval = s[k]
            s2[k] = tempval
      
# Copies the key/value pairs of a shelve to a python dict
# Parameter:
#   s       :   shelve object to get the stuff from
#   s2      :   Dict to store the stuff into
#   filter  :   List of keys that don't get applied to s2. This is optional
def copy_to_dict(s, s2, f=[]):
    for k in s.dict.keys():
        tempkey = str(k, s.keyencoding)
        if not tempkey in f:
            tempval = s[tempkey]
            s2[tempkey] = tempval
      
# Create a new Sprite object from a file name.
# Parameters:
#   folder  :   The folder containing the image file (usually src.constants.PATH_GRAPHICS_SPRITES)
#   name    :   File name of the image including extension
# Returns:
#   A SpriteLayer.Sprite for this image
def create_sprite_from_file(folder, name):
    img = pygame.image.load(os.path.join(folder, name))
    rect = img.get_rect()
    return tiledtmxloader.helperspygame.SpriteLayer.Sprite(img, rect)

# Update the MapProperties object of the given map
# Parameters:
#    m    :    Map object to update the properties of
#    shelf:    Open shelf to be used. This method does not close the shelf.
def update_persistent_map_properties(m, shelf):
    name = m.properties['key_name']
    dic = shelf['saved_maps']
    properties = MapProperties(m)
    dic[name] = properties
    shelf['saved_maps'] = dic
    
# Adds an object to a map. Note that objects
# may only be removed from previously visited maps.
# Therefore, if no MapProperties entry exists for
# the map in question, this does not work.
# Parameters:
#    shelf    :    An open shelf to retrieve the
#                  data from. This method does not
#                  close the shelf itself.
#    constant :    A constant according to MapProperties constants
#    mapname  :    The key name of the map in question
#    name     :    The name of the object to be added
#    rect     :    The pygame Rect for this object
#    callback :    Callback method, interaction method
#    imagefile:    Optional: File name for the image to be used
#                  for this new object. This method adds
#                  the full path, so just use the filename
#                  e.g. "door.png" instead of "assets/graphics/..."
#    block    :    Boolean depicting if this object should be used in
#                  the collision detection (e.g. can the player walk over it?)
def add_to_map(shelf, constant, mapname, name, rect, callback, imagefile=None, block=False):
    # Local imports
    from src.model.Script import Script, TeleportScript
    from src.model.Clickable import Clickable, TeleportClickable
    from src.model import MapFactory
    
    mapref = MapFactory.getMap(mapname)
    image = None
    if constant == SCRIPT:
        ObjectClass = Script
    elif constant == TELEPORTSCRIPT:
        ObjectClass = TeleportScript
    elif constant in [OBJECT, TELEPORTOBJECT]:
        if imagefile is not None:
            imagefile = os.path.join(PATH_GRAPHICS_TILES, imagefile)
            image = pygame.image.load(imagefile).convert_alpha()
        if constant == OBJECT:
            ObjectClass = Clickable
        elif constant == TELEPORTOBJECT:
            ObjectClass = TeleportClickable
    
    c = ObjectClass(name, rect, callback, mapref, image, imagefile)
    
    if constant == OBJECT:
        if block:
            c.setBlocked(block)
            
    add_object_to_map_properties(shelf, mapname, constant, c)
    
# Adds an object to the persistent MapProperties.
# This way is the correct way to add an object to another map when
# in an interaction method.
# Parameters:
#    shelf       :    Shelf to be used for persistent access
#    key         :    The name of the map whose properties are to be updated
#    constant    :    Type constant
#    obj         :    Object to be added
def add_object_to_map_properties(shelf, key, constant, obj):
    dic = shelf['saved_maps']
    if key in dic:
        dic[key].add(constant, obj)
        shelf['saved_maps'] = dic
    # Try to add it to the actual Map object as well
    from src.model import MapFactory
    m = MapFactory.getMap(key)
    if m is not None:
        m.addObject(constant, obj)    
        
# Removes an object from the persistent MapProperties.
# Parameters:
#    shelf       :    Shelf to be used for persistent access
#    key         :    The name of the map whose properties are to be updated
#    constant    :    Type constant
#    obj         :    Object to be removed
#    keepblocked :    Boolean depicting if the area of the object should remain blocked
def remove_object_from_map_properties(shelf, key, constant, obj, keepblocked=False):
    dic = shelf['saved_maps']
    # Try to remove it from the actual Map object first (this way, sprites get removed)
    from src.model import MapFactory
    m = MapFactory.getMap(key)
    if m is not None:
        m.removeObject(obj, keepblocked)
        
    # Remove it from the map properties
    if key in dic:
        dic[key].remove(constant, obj)
        shelf['saved_maps'] = dic

# Retrieves an object from the persistent MapProperties.
# Parameters:
#    shelf       :    Shelf to be used for persistent access
#    key         :    The name of the map whose properties are to be updated
#    name        :    Name of the object to be retrieved
# Returns:
#    Reference to that object, or None
def get_object_from_map_properties(shelf, key, name):
    dic = shelf['saved_maps']
    if key in dic:
        return dic[key].get(name)
    return None

# Updates an object in the persistent MapProperties.
# Parameters:
#    shelf    :    Shelf to use
#    mname    :    Map name
#    obj      :    Object to update
def update_object_in_map_properties(shelf, mname, obj):
    dic = shelf['saved_maps']
    if mname in dic:
        dic[mname].update(obj)
        shelf['saved_maps'] = dic

# Removes an object from a map. Note that objects
# may only be removed from previously visited maps.
# Therefore, if no MapProperties entry exists for
# the map in question, this does not work.
# Parameters:
#    shelf    :    An open shelf to retrieve the
#                  data from. This method does not
#                  close the shelf itself.
#    constant :    A constant according to MapProperties constants
#    mapname  :    The key name of the map in question
#    name     :    The name of the object to be removed
def remove_from_map(shelf, constant, mapname, name):
    # Local import
    from src.model import MapFactory
    
    # This part is relevant when a script removes an object
    # on the map where it is on itself.
    m = MapFactory.getMap(mapname)
    if m is not None:
        ref = m.getObjectByName(name)
        m.removeObject(ref)
        
    # Delete the entry in the map's MapProperties
    dic = shelf['saved_maps']
    if mapname in dic:
        dic[mapname].remove(constant, name)
        shelf['saved_maps'] = dic
        
# This method calculates the general direction from pos1 to pos2.
# The return values are expressed as a two-item list depicting
# the direction, e.g. [1,0] = RIGHT, [0,-1] = UP and so on.
# This method is used to:
# - Determine the direction of the player's flashlight
# - Face the player towards an object he clicked on
# Parameters:
#    pos1    :    First point (e.g. the player position)
#    pos2    :    Second point (e.g. the mouse position)
# Returns:
#    A two-item list in the form [x,y] with x,y e [-1;0;1]
def get_direction_from_point_to_point(pos1, pos2):
    x,y = pos2[0] - pos1[0], pos2[1] - pos1[1]
    rounded = round(math.atan2(y,x), 1)
    for direction in DIRS:
        if rounded in DIRDICT[direction]:
            return direction
        
# Converts a position in Tiled-Tile-Coordinates to pixel coordinates
# Parameters:
#    tilepoint    :    Two-item point of tile coordinates
#    mapref       :    Map object whose tilewidth and tileheight constants are used
# Returns:
#    The pixel coordinates for tilepoint
def conv_tile_pixel(tilepoint, mapref):
    tw = mapref._cLayer.tilewidth
    th = mapref._cLayer.tileheight
    return (tilepoint[0] * tw, tilepoint[1] * th)