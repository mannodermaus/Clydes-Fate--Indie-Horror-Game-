from src.constants import PATH_GRAPHICS_TILES, VOLUME_SOUND, COLOR_GOT_ITEM, \
    INVENTORY_ITEM_ATRIUM_KEY
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND
from src.model import ItemFactory
import os

def keyshelf(storage, obj, m):
    storage._go()
    
    tr = GlobalServices.getTextRenderer()
    ad = GlobalServices.getAudioDevice()
    
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        # If the player has got the key
        if storage._getData('atriumkey_obtained'):
            tr.write("Nothing of interest.", 3)
        # If the player has pressed the switch
        elif storage._getData('guestroom_switch_pressed'):
            storage._toggleCutscene(True)
            tr.write("That lever has moved the wooden canvas.", 3)
            storage._wait(3000)
            tr.write("A small compartment containing a pale key was revealed.", 3)
            storage._wait(3000)
            emptyshelf = os.path.join(PATH_GRAPHICS_TILES,'shelf_taken.png')
            obj.changeImage(emptyshelf, True)
            ad.play(SOUND, 'pick_key', VOLUME_SOUND)
            tr.write("Got 'Atrium Key'", 3, COLOR_GOT_ITEM)
            m.getPlayer().inventory.add(ItemFactory.create(\
                                        INVENTORY_ITEM_ATRIUM_KEY, 1))
            storage._setData('atriumkey_obtained', True)
            storage._toggleCutscene(False)
            
        # Otherwise
        else:
            storage._toggleCutscene(True)
            tr.write("This is a weird bookshelf.", 3)
            storage._wait(3000)
            tr.write("The \"books\" are actually painted on top of a wooden canvas.", 3)
            storage._wait(3000)
            tr.write("There are hinges on the sides, but I can't move the front.", 3)
            storage._setData('guestroom_foundshelf', True)
            storage._toggleCutscene(False)
    else:
        tr.write("I can't reach that from here.", 3)        
    
    storage._halt()

def switch(storage, obj, m):
    storage._go()
    
    tr = GlobalServices.getTextRenderer()
    ad = GlobalServices.getAudioDevice()
    
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        if storage._getData('guestroom_switch_pressed'):
            tr.write("I pulled the lever. It won't budge now.", 3)
        else:
            storage._toggleCutscene(True)
            tr.write("It's... a lever?", 3)
            storage._wait(3000)
            if storage._getData('guestroom_foundshelf'):
                tr.write("Does this do something with the hinges on that bookshelf?", 3)
                storage._wait(3000)
            ad.play(SOUND, 'pull_switch', VOLUME_SOUND)
            # Change graphics
            downswitch = os.path.join(PATH_GRAPHICS_TILES,'switch_down.png')
            obj.changeImage(downswitch)
            shelfchange = os.path.join(PATH_GRAPHICS_TILES,'shelf_atriumkey_inside.png')
            shelf_object = m.getObjectByName('keyshelf')
            shelf_object.changeImage(shelfchange, True)
            ad.play(SOUND, 'shelf', VOLUME_SOUND)
            
            storage._setData('guestroom_switch_pressed', True)
            storage._toggleCutscene(False)
    else:
        tr.write("I can't reach that from here.", 3) 
    storage._halt()