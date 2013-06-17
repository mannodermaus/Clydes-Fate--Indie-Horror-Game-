# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import COLOR_TEXT, FONTSTYLE_NORMAL, FONTSTYLE_CAPTION, \
    INVENTORY_ITEM_STUDY_KEY, INVENTORY_ITEM_STORAGE_KEY, VOLUME_SOUND, \
    VOLUME_SOUND_AMBIENT, INVENTORY_ITEM_ATRIUM_KEY
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND
from src.model.MapProperties import SCRIPT
from src.utilities import remove_from_map, get_savegame
from src.view import OverlayFactory

def init(storage, m):
    storage._go()
    
    tr = GlobalServices.getTextRenderer()
    # Skip the credits if they played already
    if storage._getData('righthallway_introduction_done'):
        m.rendering_enabled = True
        storage._halt()
        return
        
    storage._setData('righthallway_introduction_done', True)
    
    m.rendering_enabled = True
    
    storage._wait(500)
    x = 450
    l = [tr.write("Story:", 5, COLOR_TEXT, (x, 360), FONTSTYLE_NORMAL, False),\
         tr.write("Anna Martje Geudert", 5, COLOR_TEXT, (x, 380), FONTSTYLE_CAPTION, False)]
    
    storage._wait(2500)
    
    for t in l:
        tr.delete(t)
    
    storage._wait(500)
    l = [tr.write("Graphics:", 5, COLOR_TEXT, (x, 300), FONTSTYLE_NORMAL, False),\
         tr.write("Celianna", 5, COLOR_TEXT, (x, 320), FONTSTYLE_CAPTION, False),\
         tr.write("Enterbrain", 5, COLOR_TEXT, (x, 350), FONTSTYLE_CAPTION, False),\
         tr.write("Kaz", 5, COLOR_TEXT, (x, 380), FONTSTYLE_CAPTION, False),\
         tr.write("Lunarea", 5, COLOR_TEXT, (x, 410), FONTSTYLE_CAPTION, False),\
         tr.write("Mack", 5, COLOR_TEXT, (x, 440), FONTSTYLE_CAPTION, False)]
    
    storage._wait(2500)
    
    for t in l:
        tr.delete(t)
    
    storage._wait(500)
    
    l = [tr.write("Sound & Music:", 5, COLOR_TEXT, (x, 360), FONTSTYLE_NORMAL, False),\
         tr.write("Marcel Schnelle", 5, COLOR_TEXT, (x, 380), FONTSTYLE_CAPTION, False),\
         tr.write("'Cry of Fear'", 5, COLOR_TEXT, (x, 410), FONTSTYLE_CAPTION, False),\
         tr.write("'Amnesia: The Dark Descent'", 5, COLOR_TEXT, (x, 440), FONTSTYLE_CAPTION, False)]
    
    storage._wait(2500)
    
    for t in l:
        tr.delete(t)
        
    storage._wait(500)
    
    l = [tr.write("Programming:", 5, COLOR_TEXT, (x, 360), FONTSTYLE_NORMAL, False),\
         tr.write("Marcel Schnelle", 5, COLOR_TEXT, (x, 380), FONTSTYLE_CAPTION, False)]
    
    storage._wait(2500)
    
    for t in l:
        tr.delete(t)
    
    storage._halt()
    
def dronesound(storage, obj, m):
    storage._go()
    if storage._getData('rightwing_powershortage'):
        remove_from_map(storage.s, SCRIPT, m.properties['key_name'], 'dronesound')
        ad = GlobalServices.getAudioDevice()
        
        ad.play(SOUND, 'drone', VOLUME_SOUND_AMBIENT, 0, 1500)
        black = OverlayFactory.create_by_color((0,0,0), 0, 255)
        
        storage._wait(3000)
        m.addOverlay(black)
        ad.play(SOUND, '27_spark3', VOLUME_SOUND)
        storage._wait(50)
        m.removeOverlay(black)
        ad.play(SOUND, '27_spark1', VOLUME_SOUND)
        storage._wait(100)
        m.addOverlay(black)
        ad.play(SOUND, '27_spark4', VOLUME_SOUND)
        storage._wait(50)
        m.removeOverlay(black)
        ad.play(SOUND, '27_spark2', VOLUME_SOUND)
        storage._wait(1750)
        m.addOverlay(black)
        ad.play(SOUND, '27_spark1', VOLUME_SOUND)
        storage._wait(100)
        m.removeOverlay(black)
        ad.play(SOUND, '27_spark3', VOLUME_SOUND)
    storage._halt()
    
def worldmap(storage, obj, m):
    storage._go()
    
    tr = GlobalServices.getTextRenderer()

    if storage._getData('righthallway_introduction_done'):
        if storage._playerInDistance(m.getPlayer().position, obj.rect, 100):
            storage._toggleCutscene(True)
            tr.write("This map has always been a trasure to my old man.", 3)
            storage._wait(3000)
            tr.write("I never understood why he admired it so much.", 3)
            storage._toggleCutscene(False)
    
    storage._halt()
    
def tpguestroom(storage, m, obj):
    storage._go()
    
    tr = GlobalServices.getTextRenderer()
    ad = GlobalServices.getAudioDevice()
    retval = False
    
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        if storage._getData('flashlight_obtained'):
            retval = True
        else:
            ad.play(SOUND, "lockeddoor", VOLUME_SOUND)
            tr.write("The door seems jammed.", 3)
        
    storage._halt()
    return retval
    
def tpatrium(storage, m, obj):
    storage._go()
    ad = GlobalServices.getAudioDevice()
    
    tr = GlobalServices.getTextRenderer()
    retval = False
    
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        # Key
        if storage._getData('atrium_open'):
            retval = True
        else:
            inventory = m.getPlayer().inventory
            if inventory.containsName(INVENTORY_ITEM_ATRIUM_KEY):
                storage._toggleCutscene(True)
                
                ad.play(SOUND, "pick_key", VOLUME_SOUND)
                tr.write("I can use the atrium key here.", 3)
                storage._wait(3000)
                
                key = inventory.get(INVENTORY_ITEM_ATRIUM_KEY)
                key.subQty(1)
                storage._setData('atrium_open', True)
                
                storage._toggleCutscene(False)
                retval = True
                
            else:
                ad.play(SOUND, "lockeddoor", VOLUME_SOUND)
                tr.write("The door to the atrium... it's locked? That's weird, it shouldn't be.", 3)
            
    storage._halt()
    return retval
    
def tpstorage(storage, m, obj):
    storage._go()
    
    tr = GlobalServices.getTextRenderer()
    ad = GlobalServices.getAudioDevice()
    inv = m.getPlayer().inventory
    
    retval = False
    
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        if storage._getData('storage_open'):
            retval = True
        elif inv.containsName(INVENTORY_ITEM_STORAGE_KEY):
            storage._toggleCutscene(True)
            
            ad.play(SOUND, "keypickup", VOLUME_SOUND)
            tr.write("I can use the storage key here.", 3)
            storage._wait(3000)
            
            key = inv.get(INVENTORY_ITEM_STORAGE_KEY)
            key.subQty(1)
            storage._setData('storage_open', True)
            
            storage._toggleCutscene(False)
            retval = True
        else:
            ad.play(SOUND, "lockeddoor", VOLUME_SOUND)
            tr.write("The storage has been locked for as long as I can remember. I have never been in there.", 4)
            retval = False
    
    storage._halt()
    return retval

def tpstudy(storage, m, obj):
    storage._go()
    
    tr = GlobalServices.getTextRenderer()
    ad = GlobalServices.getAudioDevice()
    inv = m.getPlayer().inventory
    
    retval = False
    
    if not storage._getData('righthallway_introduction_done'):
        retval = False
    elif storage._playerInDistance(m.getPlayer().position, obj.rect):
        if storage._getData('study_open'):
            retval = True
        elif inv.containsName(INVENTORY_ITEM_STUDY_KEY):
            
            storage._toggleCutscene(True)
            
            ad.play(SOUND, "keypickup", VOLUME_SOUND)
            tr.write("The study key fits into the lock.", 2)
            storage._wait(2000)
            
            key = inv.get(INVENTORY_ITEM_STUDY_KEY)
            key.subQty(1)
            storage._setData('study_open', True)
            
            storage._toggleCutscene(False)
            
            retval = True
        else:
            ad.play(SOUND, "lockeddoor", VOLUME_SOUND)
            tr.write("This door leads to the study room. It is locked.", 4)
            retval = False
    
    storage._halt()
    return retval

def leftroomopening(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    ad = GlobalServices.getAudioDevice()
    if storage._getData('flashlight_obtained'):
        m.getPlayer().stopMoving()
        storage._toggleCutscene(True)
        
        ad.play(SOUND, 'doorclose', VOLUME_SOUND_AMBIENT)
        
        storage._wait(1000)
        
        tr.write("That noise came from across the hallway. Was it a door opening?", 3)
        
        storage._wait(1500)
        
        remove_from_map(get_savegame(), SCRIPT, 'righthallway', 'righthallway_leftroomopening')
        
        storage._toggleCutscene(False)
    storage._halt()