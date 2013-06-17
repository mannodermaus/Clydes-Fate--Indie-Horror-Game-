# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu
from src.constants import VOLUME_SOUND, PATH_GRAPHICS_TILES, COLOR_TEXT
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND
from src.model.EventTypes import ObjectHighlightedEvent
from src.model.MapProperties import OBJECT, TELEPORTOBJECT, SCRIPT
from src.utilities import add_to_map, get_savegame, conv_tile_pixel, \
    remove_object_from_map_properties, add_object_to_map_properties, \
    get_object_from_map_properties, update_object_in_map_properties, \
    string_to_direction
from src.view import OverlayFactory
import os
import pygame

def shelf(storage, obj, m):
    storage._go()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        tr = GlobalServices.getTextRenderer()
        storage._toggleCutscene(True)
        if storage._getData('library_relaxlever_pressed'):
            tr.write("The lever in the relaxation room seems to have moved the shelf.", 3)
        else:
            tr.write("This shelf looks just like the others in this room.", 3)
            storage._wait(3000)
            tr.write("However, the floor in front of this one is heavily scratched.", 3)
        storage._toggleCutscene(False)
    storage._halt()

def message(storage, obj, m):
    storage._go()
    if storage._playerInDistance(m.getPlayer().position, obj.rect, 140):
        tr = GlobalServices.getTextRenderer()
        tr.write("'IT IS I WHO SHALL LEAD YOU TO WHAT YOU DESERVE'", 3)
    storage._halt()

def officelever(storage, obj, m):
    storage._go()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        if not storage._getData('library_officelever_pressed'):
            storage._toggleCutscene(True)
            ad = GlobalServices.getAudioDevice()
            ad.play(SOUND, 'pull_switch', VOLUME_SOUND)
            
            # Change graphics for this lever
            downswitch = os.path.join(PATH_GRAPHICS_TILES,'switch_down.png')
            obj.changeImage(downswitch)
            
            # Grab the shelf in atrium.tmx and delete it
            remove_object_from_map_properties(get_savegame(), 'atrium',\
                                              OBJECT, 'mastershelf', True)
            
            # Add the TeleportClickable to that map
            from src.model.Clickable import TeleportClickable, Clickable
            tele = TeleportClickable('tpmasterroom',\
                                     pygame.Rect(conv_tile_pixel((24, 4), m),\
                                            conv_tile_pixel( (2, 3), m)),\
                                     None, 'atrium_tpmasterroom', 'doormove6',\
                                     'masterroom', 32*16, 35*16)
            add_object_to_map_properties(get_savegame(), 'atrium',\
                                         TELEPORTOBJECT, tele)
            
            # Add vandalized painting image
            painting = get_object_from_map_properties(get_savegame(), 'librarydownstairs','painting')
            vandalized = os.path.join(PATH_GRAPHICS_TILES, 'vandalizedpainting.png')
            painting.changeImage(vandalized)
            update_object_in_map_properties(get_savegame(), 'librarydownstairs', painting)
            
            # Add new wall texts on this map and librarydownstairs.tmx
            add_to_map(get_savegame(), OBJECT, 'libraryupstairs', 'message',\
               pygame.Rect(conv_tile_pixel((43,36), m), conv_tile_pixel((14,5), m)),\
               'libraryupstairs_message', 'message_3.png', True)
            
            # Add the scare script
            add_to_map(get_savegame(), SCRIPT, 'libraryupstairs', 'scare',\
                   pygame.Rect(conv_tile_pixel((38,14), m), conv_tile_pixel((1,6), m)),\
                   'libraryupstairs_scare')
            
            message4path = os.path.join(PATH_GRAPHICS_TILES, 'message_4.png')
            message4 = pygame.image.load(message4path).convert_alpha()
            othermsg = Clickable('message', pygame.Rect(conv_tile_pixel((22,18), m),\
                                 conv_tile_pixel((6,6), m)),\
                                 'librarydownstairs_message', None,
                                 message4, message4path)
            add_object_to_map_properties(get_savegame(), 'librarydownstairs',\
                                         OBJECT, othermsg)                                 
            
            # Toggle this event as "happened"
            storage._setData('library_officelever_pressed', True)
            
            storage._toggleCutscene(False)
        
    storage._halt()

def relaxlever(storage, obj, m):
    storage._go()
    if not storage._getData('library_relaxlever_pressed')\
    and storage._playerInDistance(m.getPlayer().position, obj.rect):
        ad = GlobalServices.getAudioDevice()
        ad.play(SOUND, 'pull_switch', VOLUME_SOUND)
        # Change graphics
        downswitch = os.path.join(PATH_GRAPHICS_TILES,'switch_down.png')
        obj.changeImage(downswitch)
        shelf = m.getObjectByName('shelf')
        ad.play(SOUND, 'shelf', VOLUME_SOUND)
        # Re-position the shelf
        m.removeObject(shelf, True)
        
        add_to_map(get_savegame(), OBJECT, 'libraryupstairs', 'shelf',\
                   pygame.Rect(conv_tile_pixel((47,10), m), conv_tile_pixel((4,6), m)),\
                   'libraryupstairs_shelf', 'bigshelf_four.png', True)
        
        # Add the next lever (that was behind the moved shelf)
        add_to_map(get_savegame(), OBJECT, 'libraryupstairs', 'officelever',\
                   pygame.Rect(conv_tile_pixel((45,11), m), conv_tile_pixel((1,2), m)),\
                   'libraryupstairs_officelever', 'switch_up.png', True)
        
        storage._accessData()
        storage._setData('library_relaxlever_pressed', True)
    storage._halt()
    
def scare(storage, obj, m):
    storage._go()
    player = m.getPlayer()
    shadow = m.getShadow()
    ad = GlobalServices.getAudioDevice()
    fl = m.getOverlay("_flashlight")
    player.stopMoving()
    storage._toggleCutscene(True)
    # Helper function for looking in a direction
    def face(direction):
        fl.point(direction)
        player.setDirection(string_to_direction(direction))
        
    face("left")
    
    fog = OverlayFactory.create("fog.png", pygame.BLEND_MULT)
    black = OverlayFactory.create_by_color((0,0,0), 0, 255)
    red = OverlayFactory.create_by_color((200,0,0), 0, 40)
    m.addOverlay(fog)
    m.addOverlay(red)
    # Show shadow
    shadow.setPosition(conv_tile_pixel((31,17), m))
    ad.play(SOUND, '27_orb_implode', VOLUME_SOUND + 0.1)
    ad.play(SOUND, 'scare_male_terrified5', VOLUME_SOUND)
    shadow.setVisible(True)
    storage._wait(1100)
    shadow.moveBy((-70,0), 3000)
    storage._wait(1900)
    ad.play(SOUND, 'insanity_whisper03', VOLUME_SOUND)
    m.addOverlay(black)
    ad.play(SOUND, '27_spark2', VOLUME_SOUND)
    storage._wait(300)
    m.removeOverlay(fog)
    m.removeOverlay(red)
    shadow.setVisible(False)
    m.removeOverlay(black)
    ad.play(SOUND, '27_spark4', VOLUME_SOUND)
    storage._wait(2000)
    
    # Delete script
    m.removeObject(obj)
    
    storage._toggleCutscene(False)
    storage._halt()

def officenote(storage, obj, m):
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
        tr.write("The doctor's said that everything is going to be fine.",\
                 0, COLOR_TEXT, (100, y + (ofs*0)))
        tr.write("I won't give my offspring away only because your senile self",\
                 0, COLOR_TEXT, (100, y + (ofs*1)))
        tr.write("blames everything on him! How dare you speak those insults!",\
                 0, COLOR_TEXT, (100, y + (ofs*2)))
        tr.write("Cly has NOTHING to do with any of the disappearances of our family.",\
                 0, COLOR_TEXT, (100, y + (ofs*3)))
        tr.write("I mean, God, why do you keep saying that?! Haven't you heard",\
                 0, COLOR_TEXT, (100, y + (ofs*4)))
        tr.write("the inspector's words? He's innocent!",\
                 0, COLOR_TEXT, (100, y + (ofs*5)))
        tr.write("I took your key to where you wrongfully locked my son, you monster.",\
                 0, COLOR_TEXT, (100, y + (ofs*7)))
        tr.write("This will be hard to forgive, father.",\
                 0, COLOR_TEXT, (100, y + (ofs*8)))
        tr.write("- M",\
                 0, COLOR_TEXT, (100, y + (ofs*10)))
        
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

def relaxnote(storage, obj, m):
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
        tr.write("This boy is getting out of hand!",\
                 0, COLOR_TEXT, (100, y + (ofs*0)))
        tr.write("He seems to be less and less certifiably sane, to put it in fancy terms.",\
                 0, COLOR_TEXT, (100, y + (ofs*2)))
        tr.write("I have locked him in his room after what he did to aunt Sophie.",\
                 0, COLOR_TEXT, (100, y + (ofs*3)))
        tr.write("This has nothing to do with bad manners anymore, Marnie!",\
                 0, COLOR_TEXT, (100, y + (ofs*4)))
        tr.write("The child is vile and struck by evil, I tell you. Why won't you listen to me, Marnie?",\
                 0, COLOR_TEXT, (100, y + (ofs*5)))
        tr.write("This, this is not your child anymore. Please be reasonable and get help.",\
                 0, COLOR_TEXT, (100, y + (ofs*6)))
        tr.write("- Harold",\
                 0, COLOR_TEXT, (100, y + (ofs*8)))
        
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