# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import VOLUME_MUSIC, VOLUME_SOUND_AMBIENT, SCREEN_HEIGHT, \
    COLOR_TEXT, FONTSTYLE_CAPTION, VOLUME_SOUND, SAVE_ENABLED
from src.controller import GlobalServices
from src.controller.AudioDevice import MUSIC, SOUND
from src.model.EventTypes import MainMenuSwitchRequestEvent, \
    ObjectHighlightedEvent
from src.model.MapProperties import OBJECT
from src.utilities import conv_tile_pixel, remove_from_map, get_savegame, \
    set_property
from src.view import OverlayFactory
import pygame
import random

def init(storage, m):
    storage._go()
    storage._toggleCutscene(True)
    ad = GlobalServices.getAudioDevice()
    tr = GlobalServices.getTextRenderer()
    ad.stop(MUSIC, 5000)
    ad.stop(SOUND, 5000, 'amb_guardian')
    # Make the overlay
    darktrans = OverlayFactory.create_animated_color((20,0,0),\
                5000, 0, True, 0, 220)
    dark = OverlayFactory.create_by_color((20,0,0), 0, 220)
    fog = OverlayFactory.create("fog.png", pygame.BLEND_MULT)
    white = OverlayFactory.create("noise.png", pygame.BLEND_MULT)
    m.clearOverlays()
    m.addOverlay(darktrans)
    m.addOverlay(fog)
    
    player = m.getPlayer()
    shadow = m.getShadow()
    shadow.setPosition(conv_tile_pixel((8,10),m))
    
    player.setDirection([0,-1])
    player.halfSpeed()
    
    
    # Here be dragons
    storage._wait(5000)
    m.rendering_enabled = True
    m.addOverlay(dark)
    m.removeOverlay(darktrans)
    ad.play(MUSIC, 'bgm_4', VOLUME_MUSIC, -1)
    ad.play(SOUND, 'flashlight_toggle', VOLUME_SOUND)
    
    storage._wait(2000)
    tr.write("What is this place?", 3)
    storage._wait(3000)
    tr.write("It feels... strangely familiar.", 3)
    storage._wait(2000)
    ad.play(SOUND, 'noise', VOLUME_SOUND_AMBIENT + 0.3, -1)
    m.addOverlay(white)
    shadow.setVisible(True)
    storage._wait(300)
    m.removeOverlay(white)
    ad.stop(SOUND, 0, 'noise')
    shadow.setVisible(False)
    shadow.setPosition(conv_tile_pixel((8,12),m))
    storage._wait(1500)
    m.addOverlay(white)
    ad.play(SOUND, 'noise', VOLUME_SOUND_AMBIENT + 0.3, -1)
    shadow.setVisible(True)
    shadow.moveBy((0, 15), 500)
    storage._wait(450)
    m.removeOverlay(white)
    ad.stop(SOUND, 0, 'noise')
    shadow.setVisible(False)
    
    storage._toggleCutscene(False)
    set_property(SAVE_ENABLED, False)
    storage._halt()
    
def door(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        tr.write("The hatch won't open.", 3)
    storage._halt()
    
_lastitem = [None, 0]
    
def photo(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    if storage._playerInDistance(m.getPlayer().position, obj.rect, 100):
        _lastitem[0] = "photo"
        _lastitem[1] += 1
        storage._toggleCutscene(True)
        if not storage._getData('attic_photoseen'):
            tr.write("I know this photo. It was taken two years ago.", 3)
            storage._wait(3000)
            
        photo = OverlayFactory.create("photo.png", 0)
        m.addOverlay(photo, 0)
        
        tr.write("My family... everyone has been crossed out with the same red paint I've seen everywhere.", 4)
        
        storage._pauseUntilClick()
        
        m.removeOverlay(photo)
        storage._toggleCutscene(False)
        set_property(SAVE_ENABLED, False)
        storage._setData('attic_photoseen', True)
    storage._halt()
    checkEnding(storage, m)
    
def hand(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        _lastitem[0] = "hand"
        _lastitem[1] += 1
        storage._toggleCutscene(True)
        if not storage._getData('attic_handseen'):
            tr.write("There is an imprint of a hand on the wall, drained in paint.", 3)
            storage._wait(3000)
            tr.deleteAll()
            storage._wait(1500)
        tr.write("...My right hand is a perfect match to the imprint.", 3)
        storage._toggleCutscene(False)
        set_property(SAVE_ENABLED, False)
        storage._setData('attic_handseen', True)
    storage._halt()
    checkEnding(storage, m)
    
def pencil(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        _lastitem[0] = "pencil"
        _lastitem[1] += 1
        storage._toggleCutscene(True)
        if not storage._getData('attic_pencilseen'):
            tr.write("What appears to be a red marker lies on the table.", 3)
            storage._wait(3000)
        tr.write("The messages surely have been written using this marker.", 3)
        storage._toggleCutscene(False)
        set_property(SAVE_ENABLED, False)
        storage._setData('attic_pencilseen', True)
    storage._halt()
    checkEnding(storage, m)
    
def gun(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        _lastitem[0] = "gun"
        _lastitem[1] += 1
        storage._toggleCutscene(True)
        if not storage._getData('attic_handseen'):
            tr.write("In the center of the table's surface, there is a handgun.", 3)
            storage._wait(3000)
            tr.write("It looks like it has been used several times.", 3)
        else:
            tr.write("The handgun looks like it has been used several times.", 3)
        storage._toggleCutscene(False)
        set_property(SAVE_ENABLED, False)
        storage._setData('attic_gunseen', True)
    storage._halt()
    checkEnding(storage, m)
    
def note(storage, obj, m):
    storage._go()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        _lastitem[0] = "note"
        _lastitem[1] += 1
        storage._toggleCutscene(True)
        ad = GlobalServices.getAudioDevice()
        # Overlays
        note = OverlayFactory.create("note_big.png")
        text = OverlayFactory.create("lastnote.png")
        m.addOverlay(note)
        m.addOverlay(text)
        
        # Play sound
        ad.play(SOUND, 'journal_page', VOLUME_SOUND)
        
        # Wait for user input
        storage._pauseUntilClick()
        
        # Delete note overlay
        m.removeOverlay(note)
        m.removeOverlay(text)
        # Play sound
        ad.play(SOUND, 'journal_page', VOLUME_SOUND) 
        storage._toggleCutscene(False)
        set_property(SAVE_ENABLED, False)
        storage._setData('attic_noteseen', True)
    storage._halt()
    checkEnding(storage, m)
    
def checkEnding(storage, m):
    storage._go()
    ad = GlobalServices.getAudioDevice()
    ad.stop(SOUND, 0, 'insanity_ear_ring')
    ad.play(SOUND, 'insanity_ear_ring', (0.02*_lastitem[1]), -1, 0)
    # Check if the ending has been reached
    if  storage._getData('attic_photoseen')\
    and storage._getData('attic_handseen')\
    and storage._getData('attic_noteseen')\
    and storage._getData('attic_gunseen')\
    and storage._getData('attic_pencilseen'):
        storage._halt()
        ending(storage, m)
    else:
        # Add a random scare if necessary
        if _lastitem[1] % 2 == 0:
            white = OverlayFactory.create("noise.png", pygame.BLEND_MULT)
            storage._wait(1000)
            shadow = m.getShadow()
            shadow.setPosition(conv_tile_pixel((random.randrange(3,12),\
                                                random.randrange(7,11)),m))
            m.addOverlay(white)
            shadow.setVisible(True)
            ad.play(SOUND, 'noise', VOLUME_SOUND + 0.1, -1)
            storage._wait(300)
            m.removeOverlay(white)
            ad.stop(SOUND, 0, 'noise')
            shadow.setVisible(False)
        storage._halt()
    
def ending(storage, m):
    storage._go()
    GlobalServices.getEventManager().post(ObjectHighlightedEvent(None))
    storage._toggleCutscene(True)
    storage._wait(3000)
    white = OverlayFactory.create("noise.png", pygame.BLEND_MULT)
    def static(ms):
        m.addOverlay(white)
        ad.play(SOUND, 'noise', VOLUME_SOUND + 0.1, -1)
        storage._wait(ms)
        m.removeOverlay(white)
        ad.stop(SOUND, 0, 'noise')
    tr = GlobalServices.getTextRenderer()
    ad = GlobalServices.getAudioDevice()
    tr.write("W-w-what am I supposed to do now?", 3)
    storage._wait(1400)
    static(340)
    storage._wait(1600)
    tr.write("I lose track of the sharp edges around me...", 3)
    storage._wait(2000)
    towhite = OverlayFactory.create_animated_color((255,255,255),\
              1000, 0, True, 0, 255)
    m.addOverlay(towhite)
    storage._wait(1500)
    player = m.getPlayer()
    player.setPosition(conv_tile_pixel((8,9), m))
    player.setAnimation("kneel")
    storage._wait(400)
    fadeout = OverlayFactory.create_animated_color((255,255,255),\
              1000, 0, True, 255, 0)
    m.addOverlay(fadeout)
    m.removeOverlay(towhite)
    storage._wait(3000)
    tr.write("Did I...", 3)
    player.setAnimation("walk")
    storage._wait(800)
    static(200)
    storage._wait(600)
    static(40)
    storage._wait(600)
    static(1000)
    storage._wait(2500)
    player.setDirection([0,-1])
    storage._wait(500)
    tr.write("It was... me..?", 3)
    storage._wait(1000)
    static(500)
    storage._wait(3000)
    static(100)
    storage._wait(1000)
    ad.play(SOUND, 'pick_item', VOLUME_SOUND)
    remove_from_map(get_savegame(), OBJECT, 'attic', 'gun')
    tr.write("I should...", 3)
    storage._wait(3000)
    toblack = OverlayFactory.create_animated_color((0,0,0), 2500, 0, True, 0, 255)
    m.addOverlay(toblack)
    ad.stop(SOUND, 2750, 'insanity_ear_ring')
    ad.stop(MUSIC, 2750)
    storage._wait(3500)
    ad.play(SOUND, 'gun_cock', VOLUME_SOUND)
    storage._wait(3500)
    storage._halt()
    rollCredits(storage, m)
    
def rollCredits(storage, m):
    storage._go()
    m.rendering_enabled = False
    m.clearOverlays()
    ad = GlobalServices.getAudioDevice()
    tr = GlobalServices.getTextRenderer()
    x = 125
    pos = SCREEN_HEIGHT/2
    ofs = 28
    ad.play(MUSIC, 'credits', VOLUME_MUSIC + 0.1)
    tl = OverlayFactory.create("title.png", 0)
    m.addOverlay(tl)
    storage._wait(5000)
    m.removeOverlay(tl)
    storage._wait(1000)
    tr.write("Created by Marcel Schnelle", 0, COLOR_TEXT, (x, pos + ofs*0), FONTSTYLE_CAPTION, False)
    tr.write("at California State University, Fullerton", 0, COLOR_TEXT, (x, pos + ofs*1), FONTSTYLE_CAPTION, False)
    tr.write("for 'Introduction to Game Design & Production'", 0, COLOR_TEXT, (x, pos + ofs*2), FONTSTYLE_CAPTION, False)
    tr.write("(Fall 2012)", 0, COLOR_TEXT, (x, pos + ofs*3), FONTSTYLE_CAPTION, False)
    storage._wait(10000)
    tr.deleteAll()
    storage._wait(1000)
    tr.write("Story by Anna Martje Geudert", 0, COLOR_TEXT, (x, pos + ofs*0), FONTSTYLE_CAPTION, False)
    storage._wait(5000)
    tr.deleteAll()
    storage._wait(1000)
    tr.write("Resources gathered from", 0, COLOR_TEXT, (x, pos + ofs*0), FONTSTYLE_CAPTION, False)
    tr.write("Celianna", 0, COLOR_TEXT, (x, pos + ofs*1), FONTSTYLE_CAPTION, False)
    tr.write("Enterbrain", 0, COLOR_TEXT, (x, pos + ofs*2), FONTSTYLE_CAPTION, False)
    tr.write("Kaz", 0, COLOR_TEXT, (x, pos + ofs*3), FONTSTYLE_CAPTION, False)
    tr.write("Lunarea", 0, COLOR_TEXT, (x, pos + ofs*4), FONTSTYLE_CAPTION, False)
    tr.write("Mack", 0, COLOR_TEXT, (x, pos + ofs*5), FONTSTYLE_CAPTION, False)
    storage._wait(10000)
    tr.deleteAll()
    storage._wait(1000)
    tr.write("And the games", 0, COLOR_TEXT, (x, pos + ofs*0), FONTSTYLE_CAPTION, False)
    tr.write("'Cry of Fear'", 0, COLOR_TEXT, (x, pos + ofs*1), FONTSTYLE_CAPTION, False)
    tr.write("'Amnesia: The Dark Descent'", 0, COLOR_TEXT, (x, pos + ofs*2), FONTSTYLE_CAPTION, False)
    storage._wait(7500)
    tr.deleteAll()
    storage._wait(1000)
    tr.write("Inspired by", 0, COLOR_TEXT, (x, pos + ofs*0), FONTSTYLE_CAPTION, False)
    tr.write("Mark Fischbach", 0, COLOR_TEXT, (x, pos + ofs*1), FONTSTYLE_CAPTION, False)
    storage._wait(7500)
    tr.deleteAll()
    storage._wait(1000)
    tr.write("Thanks for playing!", 0, COLOR_TEXT, (x, pos + ofs*0), FONTSTYLE_CAPTION, False)
    ad.stop(MUSIC, 7500)
    storage._wait(7500)
    tr.deleteAll()
    storage._wait(2000)
    storage._halt()
    GlobalServices.getEventManager().post(MainMenuSwitchRequestEvent())