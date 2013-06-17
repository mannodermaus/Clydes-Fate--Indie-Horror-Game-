# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import VOLUME_SOUND, COLOR_TEXT, VOLUME_SOUND_AMBIENT, \
    INVENTORY_ITEM_LIBRARY_KEY
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND, MUSIC
from src.model.EventTypes import ObjectHighlightedEvent
from src.model.MapProperties import OBJECT
from src.utilities import conv_tile_pixel, string_to_direction, remove_from_map, \
    add_to_map, get_savegame
from src.view import OverlayFactory
import pygame

def sfx(storage, obj, m):
    storage._go()
    ad = GlobalServices.getAudioDevice()
    ad.play(SOUND, 'general_thunder2', VOLUME_SOUND)
    storage._wait(2400)
    ad.play(SOUND, 'general_thunder7', VOLUME_SOUND)
    m.removeObject(obj)
    storage._halt()
    
def hintnote(storage, obj, m):
    storage._go()
    
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        # Cutscene toggle: Disable user input
        storage._toggleCutscene(True)
        tr = GlobalServices.getTextRenderer()
        ad = GlobalServices.getAudioDevice()
        
        tr.deleteAll()
        
        # Overlays
        note = OverlayFactory.create("note_big.png")
        togray = OverlayFactory.create_animated_color((0,0,0), 1000, 0, True, 0, 200)
        m.addOverlay(note)
        m.addOverlay(togray)
        
        # Play sound
        ad.play(SOUND, 'journal_page', VOLUME_SOUND)
        
        # Text of the note
        y = 200
        ofs = 18
        tr.write("Claire:",\
                 0, COLOR_TEXT, (100, y + (ofs*0)))
        tr.write("You know that I had to seal the master's bedroom for a reason, right?",\
                 0, COLOR_TEXT, (100, y + (ofs*2)))
        tr.write("It is not at all because of personal disapproval or anything like that.",\
                 0, COLOR_TEXT, (100, y + (ofs*3)))
        tr.write("Please understand that it is for our own good, and safety.",\
                 0, COLOR_TEXT, (100, y + (ofs*4)))
        tr.write("Please do not try to unlock it. Trust me on this one.",\
                 0, COLOR_TEXT, (100, y + (ofs*5)))
        tr.write("- J",\
                 0, COLOR_TEXT, (100, y + (ofs*7)))
        
        # Wait for user input
        storage._pauseUntilClick()
        
        GlobalServices.getEventManager().post(ObjectHighlightedEvent(None))
        
        # Delete note overlay
        m.removeOverlay(note)
        m.removeOverlay(togray)
        # Play sound
        ad.play(SOUND, 'journal_page', VOLUME_SOUND)        
        # Delete texts
        tr.deleteAll()
        
        storage._toggleCutscene(False)
        
    storage._halt()
    
def message(storage, obj, m):
    storage._go()
    
    tr = GlobalServices.getTextRenderer()
    if storage._playerInDistance(m.getPlayer().position, obj.rect, 100):
        tr.write("'YOU KNOW WHAT YOU DID'", 3)
    
    storage._halt()
    
def scare(storage, obj, m):
    storage._go()
    
    ad = GlobalServices.getAudioDevice()
    tr = GlobalServices.getTextRenderer()
    
    storage._toggleCutscene(True)
    
    # Force the flashlight to point to the right
    player = m.getPlayer()
    player.stopMoving()
    
    fl = m.getOverlay("_flashlight")
    # Helper function for looking in a direction
    def face(direction):
        fl.point(direction)
        player.setDirection(string_to_direction(direction))
        
    face("right")
    
    # Overlay creation
    red = OverlayFactory.create_by_color((170, 0, 0), 0, 50)
    black = OverlayFactory.create_by_color((0, 0, 0), 0, 210)
        
    # Show the figure
    ad.play(SOUND, 'scare_wood_creak_walk2', VOLUME_SOUND)
    ad.play(SOUND, '24_amb_noise', VOLUME_SOUND_AMBIENT, -1)
    shadow = m.getShadow()
    shadow.setPosition(conv_tile_pixel((43, 8), m))
    m.addOverlay(red)
    shadow.setVisible(True)
    shadow.moveBy((0, 100), 5000)
    
    storage._wait(1000)
    
    ad.stop(SOUND, 0, '24_amb_noise')
    ad.play(SOUND, '27_spark3', VOLUME_SOUND)
    ad.play(SOUND, 'scare_tingeling', VOLUME_SOUND, 0, 1000)
    m.addOverlay(black)
    m.removeOverlay(red)
    shadow.setVisible(False)
    shadow.setPosition(conv_tile_pixel((43, 14), m))
    
    storage._wait(2000)
    
    ad.play(SOUND, 'scare_wood_creak_walk3', VOLUME_SOUND)
    ad.play(SOUND, 'insanity_baby_cry2', VOLUME_SOUND)
    ad.play(SOUND, '27_orb_implode', VOLUME_SOUND)
    ad.play(SOUND, '24_amb_noise', VOLUME_SOUND_AMBIENT, -1)
    m.addOverlay(red)
    m.removeOverlay(black)
    shadow.setVisible(True)
    shadow.moveBy((-75, 0), 7500)
    
    storage._wait(2500)
    
    ad.stop(SOUND, 1750, '24_amb_noise')
    ad.play(SOUND, '27_spark4', VOLUME_SOUND)
    ad.play(SOUND, 'scare_male_terrified5', VOLUME_SOUND)
    m.addOverlay(black)
    m.removeOverlay(red)
    shadow.setVisible(False)
    
    add_to_map(get_savegame(), OBJECT, 'atrium', 'message',\
               pygame.Rect(conv_tile_pixel((29,7), m), conv_tile_pixel((8,4), m)),\
               'atrium_message', 'message_1.png', True)
    
    storage._wait(1000)
    
    m.removeOverlay(black)
    tr.write("What in the world was that thing?!", 2)
    face("left")
    storage._wait(250)
    face("up-right")
    storage._wait(250)
    face("right")
    storage._wait(100)
    face("right-down")
    storage._wait(250)
    face("right")
    storage._wait(1150)
    tr.write("Where did it go?", 2)
    storage._wait(2000)
    face("up")
    tr.write("Did it write... this?", 3)
    storage._wait(3000)
    face("right")
    
    m.removeObject(obj)
    storage._toggleCutscene(False)
    
    remove_from_map(get_savegame(), OBJECT, 'atrium', 'blockingshelf')
    storage._setData('atrium_scaredone', True)
    add_to_map(get_savegame(), OBJECT, 'atrium', 'blockingshelf',\
               pygame.Rect(conv_tile_pixel((11,25), m), conv_tile_pixel((2,8), m)),\
               'atrium_blockingshelf', 'bigshelf_right.png', True)
    
    storage._halt()
    
def blockingshelf(storage, obj, m):
    storage._go()
    
    tr = GlobalServices.getTextRenderer()
    if storage._playerInDistance(m.getPlayer().position, obj.rect, 100):
        if storage._getData('atrium_scaredone'):
            if storage._getData('atrium_blockshelffound'):
                tr.write("Why is this shelf moved now?", 3)
            else:
                tr.write("A shelf, filled with historical books.", 3)
        else:
            tr.write("A huge shelf is blocking the path to the left hallway.", 3)
            storage._setData('atrium_blockshelffound', True)
    
    storage._halt()

def mastershelf(storage, obj, m):
    storage._go()
    
    tr = GlobalServices.getTextRenderer()
    if storage._playerInDistance(m.getPlayer().position, obj.rect, 100):
        storage._toggleCutscene(True)
        tr.write("This shelf contains books about all sorts of alchemy.", 3)
        storage._wait(3000)
        tr.write("A slight breeze comes in from behind the shelf.", 3)
        storage._toggleCutscene(False)
    
    storage._halt()

def tplibrary(storage, m, obj):
    storage._go()
    
    retval = False
    tr = GlobalServices.getTextRenderer()
    ad = GlobalServices.getAudioDevice()
    
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        if storage._getData('library_open'):
            retval = True
        else:
            inventory = m.getPlayer().inventory
            if inventory.containsName(INVENTORY_ITEM_LIBRARY_KEY):
                storage._toggleCutscene(True)
                ad.play(SOUND, "pick_key", VOLUME_SOUND)
                tr.write("The library key fits into the lock.", 3)
                storage._wait(3000)
                
                key = inventory.get(INVENTORY_ITEM_LIBRARY_KEY)
                key.subQty(1)
                storage._setData('library_open', True)
                
                storage._toggleCutscene(False)
                retval = True
            else:
                ad.play(SOUND, "lockeddoor", VOLUME_SOUND)
                tr.write("The door is locked. 'Library' is spelt on the door frame.", 3)
    
    storage._halt()
    return retval

def tpmasterroom(storage, m, obj):
    storage._go()
    retval = True
    
    if not storage._getData('atrium_masterroom_firstentered'):
        storage._toggleCutscene(True)
        tr = GlobalServices.getTextRenderer()
        tr.write("The lever in the library has moved the shelf out of the way.", 3)
        storage._wait(3000)
        tr.write("This means that I can enter the master office.", 3)
        storage._wait(3000)
        tr.write("I'm barely awake right now. What does all of this mean?", 3)
        storage._wait(3000)
        m.getPlayer().setDirection([0,1])
        m.getOverlay("_flashlight").point("down")
        tr.deleteAll()
        storage._wait(2000)
        m.getPlayer().setDirection([0,-1])
        m.getOverlay("_flashlight").point("up")
        tr.write("...", 3)
        storage._wait(3000)
        storage._toggleCutscene(False)
        ad = GlobalServices.getAudioDevice()
        ad.stop(MUSIC, 5000)
        storage._setData('atrium_masterroom_firstentered', True)
    storage._halt()
    return retval