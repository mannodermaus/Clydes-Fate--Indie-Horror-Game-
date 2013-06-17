# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import VOLUME_SOUND, COLOR_TEXT, VOLUME_SOUND_AMBIENT
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND
from src.model.EventTypes import ObjectHighlightedEvent
from src.view import OverlayFactory

def noise(storage, obj, m):
    storage._go()
    m.removeObject(obj)
    ad = GlobalServices.getAudioDevice()
    ad.play(SOUND, 'scare_whine_loop1', VOLUME_SOUND)
    storage._wait(1000)
    ad.play(SOUND, 'amb_guardian', VOLUME_SOUND_AMBIENT, -1, 3000)
    storage._wait(3000)
    ad.play(SOUND, 'scare_animal_squeal1', VOLUME_SOUND)
    storage._wait(4500)
    ad.play(SOUND, 'scare_tingeling_rev2', VOLUME_SOUND)
    storage._halt()

def painting(storage, obj, m):
    storage._go()
    if storage._playerInDistance(m.getPlayer().position, obj.rect, 150):
        tr = GlobalServices.getTextRenderer()
        storage._toggleCutscene(True)
        if storage._getData('library_officelever_pressed'):
            tr.write("There is red paint all over the picture.", 3)
            storage._wait(3000)
            tr.write("It seems to be the same kind of paint that was used for all those messages.", 3)
        else:
            tr.write("The statue in the center of this painting stands out. Its stare is unsettling.", 3)
            storage._wait(3000)
            tr.write("The title on the frame reads 'THE SOMNAMBULIST'.", 3)
        storage._toggleCutscene(False)
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
        y = 150
        ofs = 18
        tr.write("Marnie:",\
                 0, COLOR_TEXT, (100, y + (ofs*0)))
        tr.write("Last night, I caught Cly wandering around the house again.",\
                 0, COLOR_TEXT, (100, y + (ofs*2)))
        tr.write("He did not respond at all when I addressed him and asked what he was doing.",\
                 0, COLOR_TEXT, (100, y + (ofs*3)))
        tr.write("His eyed were wide open but he did not react at all. I put him back to bed.",\
                 0, COLOR_TEXT, (100, y + (ofs*4)))
        tr.write("The next morning, I asked him about the incident. He did not remember any of it,",\
                 0, COLOR_TEXT, (100, y + (ofs*6)))
        tr.write("although he claimed to be very tired that day.",\
                 0, COLOR_TEXT, (100, y + (ofs*7)))
        tr.write("This is the third time it happened when he slept over at our house.",\
                 0, COLOR_TEXT, (100, y + (ofs*8)))
        tr.write("I'm telling you, something is troubling this poor child.",\
                 0, COLOR_TEXT, (100, y + (ofs*9)))
        tr.write("Please, my dear, get this kid to the doctor.",\
                 0, COLOR_TEXT, (100, y + (ofs*10)))
        tr.write("- Harold",\
                 0, COLOR_TEXT, (100, y + (ofs*12)))
        
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
        
        if not storage._getData('library_notefound'):
            tr.write("Marnie...? My mother's name was Marnie.", 3)
            storage._wait(3000)
            tr.write("And Harold is my grandfather...", 3)
            storage._wait(3000)
            tr.write("They both vanished not too long ago.", 3)
            storage._wait(4500)
            tr.write("I feel strange.", 3)
            storage._setData('library_notefound', True)
        storage._toggleCutscene(False)
    storage._halt()
    
def message(storage, obj, m):
    storage._go()
    if storage._playerInDistance(m.getPlayer().position, obj.rect, 140):
        tr = GlobalServices.getTextRenderer()
        tr.write("'YOU DISGUST ME...'")
    
    storage._halt()