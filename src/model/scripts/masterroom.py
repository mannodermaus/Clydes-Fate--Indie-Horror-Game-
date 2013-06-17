# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import INVENTORY_ITEM_LADDER, VOLUME_SOUND, VOLUME_MUSIC, \
    PATH_GRAPHICS_TILES
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND, MUSIC
from src.model.EventTypes import ObjectHighlightedEvent
from src.model.MapProperties import OBJECT, TELEPORTOBJECT
from src.utilities import get_savegame, conv_tile_pixel, \
    remove_from_map, add_object_to_map_properties
import os
import pygame

def message(storage, obj, m):
    storage._go()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        tr = GlobalServices.getTextRenderer()
        tr.write("'TO THE ATTIC'", 3)
    storage._halt()
    
def ceilingdoor(storage, obj, m):
    storage._go()
    if storage._playerInDistance(m.getPlayer().position, obj.rect, 180):
        GlobalServices.getEventManager().post(ObjectHighlightedEvent(None))
        inv = m.getPlayer().inventory
        tr = GlobalServices.getTextRenderer()
        ad = GlobalServices.getAudioDevice()
        storage._toggleCutscene(True)
        if inv.containsName(INVENTORY_ITEM_LADDER):
            m.getPlayer().setPosition(conv_tile_pixel((9,15), m))
            # Add ladder to this map
            ad.play(SOUND, '05_attach_ladder', VOLUME_SOUND)
            from src.model.Clickable import TeleportClickable
            ladderpath = os.path.join(PATH_GRAPHICS_TILES, 'ladder_vertical.png')
            laddersurf = pygame.image.load(ladderpath).convert_alpha()            
            
            ladder = TeleportClickable('tpattic',\
                                     pygame.Rect(conv_tile_pixel((9, 7), m),\
                                            conv_tile_pixel( (2, 7), m)),\
                                     m, None, 'ladder_climb',\
                                     'attic', 8*16, 17*16, laddersurf,\
                                     ladderpath, True)
            add_object_to_map_properties(get_savegame(), 'masterroom',\
                                         TELEPORTOBJECT, ladder)
            remove_from_map(get_savegame(), OBJECT, 'masterroom', 'ceilingdoor')
            # Reset player blah
            inv.remove(inv.get(INVENTORY_ITEM_LADDER))
        else:
            tr.write("There is a loft hatch on the ceiling.", 3)
            storage._wait(3000)
            tr.write("I need something to get up there.", 3)
            if not storage._getData('masterroom_ladder_needed'):
                storage._wait(3000)
                ad.play(MUSIC, 'bgm_3', VOLUME_MUSIC, -1)
            storage._setData('masterroom_ladder_needed', True)
        storage._toggleCutscene(False)
    storage._halt()