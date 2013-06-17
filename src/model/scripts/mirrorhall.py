# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import VOLUME_MUSIC, VOLUME_SOUND, VOLUME_SOUND_AMBIENT, \
    COLOR_GOT_ITEM, INVENTORY_ITEM_LIBRARY_KEY
from src.controller import GlobalServices
from src.controller.AudioDevice import MUSIC, SOUND
from src.model import ItemFactory
from src.model.EventTypes import ObjectHighlightedEvent
from src.model.MapProperties import OBJECT
from src.utilities import string_to_direction, conv_tile_pixel, remove_from_map, \
    add_to_map, get_savegame
from src.view import OverlayFactory
import pygame

def claire(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        storage._faceObject(m.getPlayer(), obj)
        if not storage._getData('mirrorhall_clairefound'):
            storage._toggleCutscene(True)
            tr.write("Wait... I remember this girl.", 3)
            storage._wait(3000)
            tr.write("She was my cousin's step-sister, Claire.", 3)
            storage._wait(3000)
            tr.write("Didn't my parents tell me she died in an accident?", 3)
            storage._wait(3000)
        tr.write("How come I couldn't recognize her? What led this... thing to take her life?", 3)
        storage._toggleCutscene(False)
        storage._setData('mirrorhall_clairefound', True)
    storage._halt()
    
def librarykey(storage, obj, m):
    storage._go()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        tr = GlobalServices.getTextRenderer()
        ad = GlobalServices.getAudioDevice()
        ad.play(SOUND, 'pick_key', VOLUME_SOUND)
        tr.write("Got 'Library Key'", 3, COLOR_GOT_ITEM)
        m.getPlayer().inventory.add(ItemFactory.create(INVENTORY_ITEM_LIBRARY_KEY, 1))
        remove_from_map(get_savegame(), OBJECT, 'mirrorhall', 'librarykey')
        storage._setData('librarykey_obtained', True)
    storage._halt()
        
def murderscene(storage, obj, m):
    storage._go()
    
    if not storage._getData('mirrorhall_murder_done'):
        GlobalServices.getEventManager().post(ObjectHighlightedEvent(None))
        player = m.getPlayer()
        player.stopMoving()
        storage._toggleCutscene(True)
        shadow = m.getShadow()
        shadow.setPosition(conv_tile_pixel((24, 17), m))
        tr = GlobalServices.getTextRenderer()
        ad = GlobalServices.getAudioDevice()
        
        fog = OverlayFactory.create("fog.png", pygame.BLEND_MULT)
        nolight = OverlayFactory.create("nolighting.png", 0)
        
        fl = m.getOverlay("_flashlight")
        # Helper function for looking in a direction
        def face(direction):
            fl.point(direction)
            player.setDirection(string_to_direction(direction))
            
        face("up")
        ad.play(MUSIC, 'event2', VOLUME_MUSIC)
        tr.write("Huh?", 0.5)
        storage._wait(500)
        ad.play(SOUND, 'insanity_whisper03', VOLUME_SOUND)
        storage._wait(250)
        m.addOverlay(fog)
        shadow.setVisible(True)
        shadow.moveBy((-60,0), 3750)
        ad.play(SOUND, 'scare_wood_creak_walk2', VOLUME_SOUND)
        storage._wait(750)
        tr.write("What the hell are you!?", 2)
        storage._wait(1500)
        tr.write("ANSWER ME!! Why did you kill this girl?!", 3)
        storage._wait(1500)
        ad.stop(MUSIC, 10)
        shadow.moveBy((0,70), 1000)
        ad.play(SOUND, 'scare_wood_creak_scuf3', VOLUME_SOUND)
        ad.play(SOUND, 'fb_sfx_19_false_dead01', VOLUME_SOUND - 0.1)
        towhite = OverlayFactory.create_animated_color((255,255,255), 1000, 0, True, 0, 255)
        m.addOverlay(towhite)
        ad.play(SOUND, 'insanity_ear_ring', VOLUME_SOUND_AMBIENT - 0.2, -1, 1000)
        storage._wait(1000)
        ad.play(SOUND, '21_scream10', VOLUME_SOUND - 0.4)
        m.removeOverlay(fog)
        shadow.setVisible(False)
        
        add_to_map(storage.s, OBJECT, 'mirrorhall', 'message',\
                   pygame.Rect(conv_tile_pixel((11,22), m), conv_tile_pixel((4,4), m)),\
                   'mirrorhall_message', 'message_2.png', True)
        
        player.setAnimation("lie_eyesclosed")
        
        storage._wait(5500)
        ad.stop(SOUND, 5000, 'insanity_ear_ring')
        m.removeOverlay(fl)
        totrans = OverlayFactory.create_animated_color((255,255,255), 5500, 0, True, 255, 0)
        m.addOverlay(totrans)
        m.addOverlay(nolight, 0)
        m.removeOverlay(towhite)
        ad.stop(SOUND, 5000, 'fb_sfx_19_false_dead01')
        ad.play(SOUND, '24_amb_noise', VOLUME_SOUND_AMBIENT, -1, 1000)
        storage._wait(6500)
        
        player.setAnimation("lie_eyesopen")
        storage._wait(1000)
        player.setAnimation("lie_eyesclosed")
        storage._wait(400)
        player.setAnimation("lie_eyesopen")
        storage._wait(500)
        player.setAnimation("lie_eyesclosed")
        storage._wait(100)
        player.setAnimation("lie_eyesopen")
        storage._wait(2000)
        player.setAnimation("kneel")
        tr.write("Did I... did I pass out?", 3)
        storage._wait(1500)
        
        player.setAnimation("walk")
        face("down")
        
        storage._wait(4000)
        
        ad.play(SOUND, 'flashlight_toggle', VOLUME_SOUND)
        m.addOverlay(fl)
        m.removeOverlay(nolight)
        m.removeOverlay(totrans)
        face("left-up")
        storage._wait(1000)
        face("up-right")
        storage._wait(500)
        face("down")
        storage._wait(250)
        face("down-left")
        storage._wait(300)
        face("left")
        storage._wait(750)
        face("left-up")
        storage._wait(300)
        face("up")
        storage._wait(400)
        tr.write("My head hurts so badly. Everything's a blur...", 3)
        storage._wait(3000)
        ad.stop(SOUND, 3000, '24_amb_noise')
        storage._wait(3000)
        ad.play(MUSIC, 'bgm_2', VOLUME_MUSIC, -1, 2000)
        storage._setData('mirrorhall_murder_done', True)
        storage._toggleCutscene(False)
    
    storage._halt()
    
def message(storage, obj, m):
    storage._go()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        tr = GlobalServices.getTextRenderer()
        tr.write("'STAY AWAKE'", 3)
    storage._halt()