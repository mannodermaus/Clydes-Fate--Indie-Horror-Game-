# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import COLOR_TEXT, INVENTORY_ITEM_ENTRANCE_NOTE, \
    COLOR_GOT_ITEM, VOLUME_SOUND, VOLUME_MUSIC, COLOR_OBJECTIVE, \
    POSITION_BOTTOM_SCREEN
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND, MUSIC
from src.model import ItemFactory
from src.model.EventTypes import ObjectHighlightedEvent
from src.view import OverlayFactory

# Copy this for more action
def __hull(storage, obj, m):
    storage._go()
    
    storage._halt()


def entrancenote(storage, obj, m):
    storage._go()
    
    storage._faceObject(m.getPlayer(), obj)
    tr = GlobalServices.getTextRenderer()
    
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        # Cutscene toggle: Disable user input
        storage._toggleCutscene(True)
        ad = GlobalServices.getAudioDevice()
        
        tr.write("There is a note on the ground.", 3)
        storage._wait(3000)
        tr.write("Did someone slide this under the entrance door?", 3)
        storage._wait(4000)
        tr.deleteAll()
        
        # Overlays
        note = OverlayFactory.create("note_big.png")
        togray = OverlayFactory.create_animated_color((0,0,0), 1000, 0, True, 0, 200)
        m.addOverlay(note)
        m.addOverlay(togray)
        
        # Play sound
        ad.play(SOUND, 'journal_page', VOLUME_SOUND)
        
        # Text of the note
        y = 120
        ofs = 18
        tr.write("Clyde,", 0, COLOR_TEXT, (100, y))
        tr.write("you know we like you. However, you kinda freak us out, dude.",\
                 0, COLOR_TEXT, (100, y + (ofs*2)))
        tr.write("We have grown sick of your accusations and want to give you some time",\
                 0, COLOR_TEXT, (100, y + (ofs*3)))
        tr.write("for yourself to sort things out and get your mind straight.",\
                 0, COLOR_TEXT, (100, y + (ofs*4)))
        tr.write("Why would you keep blaming us for shit that's obviously not real?",\
                 0, COLOR_TEXT, (100, y + (ofs*6)))
        tr.write("What good would it do us if we, like you said we do, 'keep changing things in the house'?",\
                 0, COLOR_TEXT, (100, y + (ofs*7)))
        tr.write("Never ever has any of us witnessed anything suspicious when we gave in",\
                 0, COLOR_TEXT, (100, y + (ofs*8)))
        tr.write("to your begging us to stay overnight. What, are you frightened of your",\
                 0, COLOR_TEXT, (100, y + (ofs*9)))
        tr.write("grandpa's house and see spooky things that aren't even there?",\
                 0, COLOR_TEXT, (100, y + (ofs*10)))
        tr.write("We don't want to say this, but we ain't gonna stay for tonight.",\
                 0, COLOR_TEXT, (100, y + (ofs*11)))
        tr.write("Get it together, man.",\
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
        # Fadeout music
        ad.stop(MUSIC, 12000)
        ad.stop(SOUND, 12000, 'vind2')
        # More text
        tr.write("Did they...?", 3)
        storage._wait(4000)
        tr.write("They have forsaken me.", 3)
        storage._wait(4000)
        tr.write("I didn't want to upset them... it's just...", 3)
        storage._wait(4000)
        tr.write("I am NOT making this up. Something is wrong here.", 3)
        storage._wait(4000)
        tr.deleteAll()
        storage._wait(1000)
        m.getPlayer().setDirection([0,-1])
        tr.write("I feel dizzy. I should get back to bed.", 3)
        storage._wait(4000)
        storage._faceObject(m.getPlayer(), obj)
        # Delete texts
        tr.deleteAll()
        # Add the note to the inventory
        m.getPlayer().inventory.add(\
                      ItemFactory.create(INVENTORY_ITEM_ENTRANCE_NOTE, 1))
        ad.play(SOUND, 'pick_paper', VOLUME_SOUND)
        tr.write("Got 'Note (Forsaken Friends)'", 3, COLOR_GOT_ITEM)
        tr.write("[Press TAB to access your possessions.]", 3, COLOR_OBJECTIVE,\
                 (0, POSITION_BOTTOM_SCREEN[1]+20))
        
        
        # Delete the note from the map
        m.removeObject(obj)
        # Set a flag that this script was executed
        storage._setData('entrancenote_obtained', True)
        # End cutscene
        storage._toggleCutscene(False)
        # Play a new BGM
        ad.play(MUSIC, 'ambienceloop', VOLUME_MUSIC, -1)
    else:
        tr.write("Is that a note on the ground?", 3)
    storage._halt()

def paintingd(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    storage._faceObject(m.getPlayer(), obj)
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        tr.write("These are two paintings of my grandparents in their prime.", 3)
    else:
        tr.write("I can't reach that from here.", 3)
    storage._halt()

def paintingr(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    storage._faceObject(m.getPlayer(), obj)
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        storage._toggleCutscene(True)
        tr.write("A dusty painting. Something is written on the frame...", 3)
        storage._wait(3000)
        tr.write("'CLAIRE'", 3)
        storage._toggleCutscene(False)
    else:
        tr.write("I can't reach that from here.", 3)
    
    storage._halt()

def paintingl(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    storage._faceObject(m.getPlayer(), obj)
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        storage._toggleCutscene(True)
        tr.write("A pretty painting of a sunset.", 3)
        storage._wait(3000)
        tr.write("The signature on the bottom right suggests it was drawn by one of my ancestors.", 3)
        storage._toggleCutscene(False)
    else:
        tr.write("I can't reach that from here.", 3)
    
    storage._halt()

def closetl(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    storage._faceObject(m.getPlayer(), obj)
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        storage._toggleCutscene(True)
        tr.write("A closet with all sorts of cutlery.", 3)
        storage._wait(3000)
        tr.write("There are several oddly shaped glasses in there.", 3)
        storage._toggleCutscene(False)
    else:
        tr.write("I can't reach that from here.", 3)
    
    storage._halt()

def closetr(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    storage._faceObject(m.getPlayer(), obj)
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        tr.write("An empty closet. Nothing of interest here.", 3)       
    else:
        tr.write("I can't reach that from here.", 3)
    
    storage._halt()

def piano(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    storage._faceObject(m.getPlayer(), obj)
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        storage._toggleCutscene(True)
        tr.write("I remember my aunt playing on the piano all the time.", 3)
        storage._wait(3000)
        tr.write("The keys have gotten a little dusty.", 3)        
        storage._toggleCutscene(False)
    else:
        tr.write("I can't reach that from here.", 3)
    storage._halt()

def bookshelf(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    storage._faceObject(m.getPlayer(), obj)
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        storage._toggleCutscene(True)
        tr.write("All sorts of literature are stored in this bookshelf.", 3)
        storage._wait(3000)
        tr.write("Nothing seems particularly interesting to me, though.", 3)
        storage._toggleCutscene(False)        
    else:
        tr.write("I can't reach that from here.", 3)
    
    storage._halt()

def tpoutside(storage, m, obj):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    storage._faceObject(m.getPlayer(), obj)
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        tr.write("The main entrance door is shut.", 3)
        if storage._getData('entrancenote_obtained'):
            storage._toggleCutscene(True)
            storage._wait(3000)
            tr.write("That note must have been slipped under the door. A small breeze comes in from there.", 3)
            storage._toggleCutscene(False)
    else:
        tr.write("I can't reach that from here.", 3)
    
    storage._halt()
    return False
