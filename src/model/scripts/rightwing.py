# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import VOLUME_SOUND, INVENTORY_ITEM_LADDER, COLOR_GOT_ITEM
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND
from src.model import ItemFactory
from src.model.EventTypes import ObjectHighlightedEvent
from src.model.MapProperties import SCRIPT, OBJECT
from src.utilities import remove_from_map, get_savegame, add_global_overlay
from src.view import OverlayFactory

def ladder(storage, obj, m):
    storage._go()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        tr = GlobalServices.getTextRenderer()
        ad = GlobalServices.getAudioDevice()
        if storage._getData('masterroom_ladder_needed'):
            storage._toggleCutscene(True)
            tr.write("This ladder should get me up through that loft hatch.", 3)
            storage._wait(3000)
            inv = m.getPlayer().inventory
            inv.add(ItemFactory.create(INVENTORY_ITEM_LADDER, 1))
            remove_from_map(get_savegame(), OBJECT, 'rightwing', 'ladder')
            ad.play(SOUND, 'pick_item', VOLUME_SOUND)
            tr.write("Got 'Ladder'", 3, COLOR_GOT_ITEM)
            storage._toggleCutscene(False)
            GlobalServices.getEventManager().post(ObjectHighlightedEvent(None))
        else:
            tr.write("There is a ladder on the ground. I have no purpose for that right now.", 3)
    storage._halt()

def powercutshort(storage, obj, m):
    storage._go()
    ad = GlobalServices.getAudioDevice()
    tr = GlobalServices.getTextRenderer()
    
    if storage._getData('entrancenote_obtained')\
    and not storage._getData('rightwing_powershortage'):
        storage._toggleCutscene(True)
        p = m.getPlayer()
        p.stopMoving()
        storage._setData('rightwing_powershortage', True)
        
        ad.play(SOUND, 'drone', VOLUME_SOUND)
        ad.play(SOUND, 'elec', VOLUME_SOUND)
        
        black = OverlayFactory.create_by_color((0,0,0), 0, 255)
        m.addOverlay(black)
        storage._wait(1000)
        
        m.removeOverlay(black)
        ad.play(SOUND, '27_spark1', VOLUME_SOUND)
        storage._wait(100)
        m.addOverlay(black)
        storage._wait(1500)
        
        m.removeOverlay(black)
        ad.play(SOUND, '27_spark2', VOLUME_SOUND)
        storage._wait(50)
        m.addOverlay(black)
        storage._wait(20)
        m.removeOverlay(black)
        ad.play(SOUND, '27_spark4', VOLUME_SOUND)
        storage._wait(30)
        m.addOverlay(black)
        storage._wait(50)
        ad.play(SOUND, '27_spark3', VOLUME_SOUND)
        m.removeOverlay(black)
        storage._wait(400)
        m.addOverlay(black)
        storage._wait(20)
        m.removeOverlay(black)
        ad.play(SOUND, '27_spark4', VOLUME_SOUND)
        storage._wait(30)
        m.addOverlay(black)
        ad.play(SOUND, '27_spark3', VOLUME_SOUND)
        storage._wait(50)
        fadein = OverlayFactory.create_animated_color((0,0,0), 3000, 0, True, 255, 155)
        storage._wait(600)
        m.removeOverlay(black)
        m.addOverlay(fadein)
        
        storage._wait(3000)
        
        tr.write("What was that? A... power shortage?", 3)
        storage._wait(500)
        p.setDirection([1,0])
        storage._wait(500)
        p.setDirection([1,1])
        storage._wait(500)
        p.setDirection([-1,0])
        storage._wait(500)
        p.setDirection([1,0])
        storage._wait(500)
        p.setDirection([0,-1])
        storage._wait(500)
        tr.write("Keep going, Clyde... it's nothing.", 3)
        remove_from_map(get_savegame(), SCRIPT, 'rightwing', 'rightwing_powercutshort')
        add_global_overlay(OverlayFactory.create_by_color((0,0,0), 0, 155))
        storage._toggleCutscene(False)
        
    storage._halt()