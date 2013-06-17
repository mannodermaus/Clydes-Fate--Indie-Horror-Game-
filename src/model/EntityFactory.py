# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import PATH_GRAPHICS_SPRITES
from src.model.Inventory import Inventory
from src.utilities import spritesheet_to_animations
import os

# EntityFactory.
# This helper class provides methods for the creation of
# the Player entity and the ominous "Shadow" that pops up
# at random points during gameplay.

# Creates the properties of the Player object
# and returns it in a convenient fashion. This method is invoked
# during the Player's constructor.
# Returns:
#    A Python dict containing the properties that
#    a Player needs, i.e. movement speed, inventory
#    and sprite animations.
def createPlayerProperties():
    properties = {}
    properties["pps"] = 100
    properties["inventory"] = Inventory()    
    anim_data = [("walk-down" , [0,1,2,1]), ("walk-left", [3,4,5,4]), \
                ("walk-right", [6,7,8,7]), ("walk-up"  , [9,10,11,10]), \
                ("walk-down-left" , [12,13,14,13]), ("walk-right-down", [15,16,17,16]), \
                ("walk-left-up", [18,19,20,19]), ("walk-up-right"  , [21,22,23,22]), \
                ("lie_eyesopen", [25]), ("lie_eyesclosed", [24]), ("kneel", [26])]
    properties["sprites"] = spritesheet_to_animations(os.path.join(PATH_GRAPHICS_SPRITES, \
                            "clyde.png"), (0,0), (32,32), anim_data, 0.25)
    return properties

# Creates the properties of the Shadow object
# and returns it in a convenient fashion. This method is invoked
# during the Shadow's constructor.
# Returns:
#    A Python dict containing the properties
#    of the Shadow, basically just the sprite animations.
def createShadowProperties():
    properties = {}
    anim_data = [("walk-down" , [0,1,2,1]), ("walk-left", [3,4,5,4]), \
                ("walk-right", [6,7,8,7]), ("walk-up"  , [9,10,11,10]), \
                ("walk-down-left" , [12,13,14,13]), ("walk-right-down", [15,16,17,16]), \
                ("walk-left-up", [18,19,20,19]), ("walk-up-right"  , [21,22,23,22])]
    properties["sprites"] = spritesheet_to_animations(os.path.join(PATH_GRAPHICS_SPRITES, \
                            "shadow.png"), (0,0), (32,32), anim_data, 0.75)
    return properties