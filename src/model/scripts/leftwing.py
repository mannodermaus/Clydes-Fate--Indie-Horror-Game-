# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import VOLUME_SOUND, COLOR_TEXT
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND
from src.model.EventTypes import ObjectHighlightedEvent
from src.view import OverlayFactory


def blockingdebris(storage, obj, m):
    storage._go()
    
    tr = GlobalServices.getTextRenderer()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        tr.write("The path is blocked by several shelves that weren't here before.", 3)
        storage._setData('leftwing_debrisfound', True)

    storage._halt()
    
def note(storage, obj, m):
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
        y = 140
        ofs = 18
        tr.write("Who would have done something like this?!",\
                 0, COLOR_TEXT, (100, y + (ofs*0)))
        tr.write("My little girl... you shouldn't have had to suffer through this.",\
                 0, COLOR_TEXT, (100, y + (ofs*1)))
        tr.write("After I found your lifeless body, I took it to your most favourite place.",\
                 0, COLOR_TEXT, (100, y + (ofs*2)))
        tr.write("Surely you will find peace among there.",\
                 0, COLOR_TEXT, (100, y + (ofs*3)))
        tr.write("I looked at your picture today.",\
                 0, COLOR_TEXT, (100, y + (ofs*5)))
        tr.write("I do not know if it is just me, but your mother's expression changed.",\
                 0, COLOR_TEXT, (100, y + (ofs*6)))
        tr.write("There she sits, to your right, and what appears to be a sole tear runs down her cheek.",\
                 0, COLOR_TEXT, (100, y + (ofs*7)))
        tr.write("Can a painting feel emotions?",\
                 0, COLOR_TEXT, (100, y + (ofs*9)))
        tr.write("Now I am surely being silly.",\
                 0, COLOR_TEXT, (100, y + (ofs*10)))
        tr.write("I will miss you, big sister.",\
                 0, COLOR_TEXT, (100, y + (ofs*11)))
        tr.write("- J",\
                 0, COLOR_TEXT, (100, y + (ofs*13)))
        
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