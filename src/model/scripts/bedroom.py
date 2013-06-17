# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import FADEIN_TIME, COLOR_TEXT, VOLUME_SOUND_AMBIENT, \
    VOLUME_MUSIC, COLOR_OBJECTIVE, VOLUME_SOUND, INVENTORY_ITEM_FLASHLIGHT, \
    COLOR_GOT_ITEM, PATH_GRAPHICS_TILES, POSITION_BOTTOM_SCREEN
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND, MUSIC
from src.model import ItemFactory
from src.model.MapProperties import OBJECT
from src.model.EventTypes import ObjectHighlightedEvent
from src.utilities import conv_tile_pixel, set_global_overlays, add_global_overlay,\
    remove_from_map, get_savegame
from src.view import OverlayFactory
import os
import pygame

def init(storage, m):
    storage._go()

    # Skip the intro if it has been played
    if storage._getData('bedroom_introduction_done'):
        m.rendering_enabled = True
        storage._halt()
        return
    
    # Introduction sequence
    storage._toggleCutscene(True)
    
    tr = GlobalServices.getTextRenderer()
    
    black = OverlayFactory.create_by_color((0,0,0), 0, 255)
    m.addOverlay(black)
    
    m.addAmbientSound(SOUND, "vind2", VOLUME_SOUND_AMBIENT, -1, FADEIN_TIME)
    storage._wait(5000)
    
    m.rendering_enabled = True
    
    starty = 200
    ofs = 18
    
    tr.write("...How long this has been going on?", 0, COLOR_TEXT, (200, starty))
    storage._wait(5000)
    tr.write("I have no idea, to be honest.", 0, COLOR_TEXT, (200, starty+ofs))
    storage._wait(5000)
    tr.write("It started right after I inherited my grandfather's mansion.",\
              0, COLOR_TEXT, (200, starty+ofs*2))
    storage._wait(5000)
    tr.deleteAll()
    storage._wait(2000)
    tr.write("This place is way too big for myself, so I have friends over on occasion.",\
              0, COLOR_TEXT, (200, starty))
    storage._wait(5000)
    tr.write("I really don't know why they keep messing with me,",\
              0, COLOR_TEXT, (200, starty+ofs))
    storage._wait(5000)
    tr.write("but whenever I wake up after they were over, everything is...",\
              0, COLOR_TEXT, (200, starty+ofs*2))
    storage._wait(3500)
    fadein = OverlayFactory.create_animated_color((0,0,0), 17500, 0, True, 255, 150)
    m.addOverlay(fadein)
    m.removeOverlay(black)
    m.addAmbientSound(MUSIC, "intro", VOLUME_MUSIC, -1, FADEIN_TIME)
    storage._wait(1500)
    tr.write("different.",\
              0, COLOR_TEXT, (200, starty+ofs*3))
    storage._wait(5000)
    tr.deleteAll()
    storage._wait(2000)
    tr.write(" They're coming over again tonight.",\
              0, COLOR_TEXT, (200, starty))
    storage._wait(5000)
    tr.write("I'll confront them with what they're doing to me.",\
              0, COLOR_TEXT, (200, starty+ofs))
    storage._wait(5000)
    tr.write("It bothers me, getting fooled all the time, by the ones I thought were my dearest.",\
              0, COLOR_TEXT, (200, starty+ofs*2))
    storage._wait(5000)
    fadein2 = OverlayFactory.create_animated_color((0,0,0), 2000, 0, True, 150, 0)
    m.switchOverlays([(fadein, fadein2)])
    m.addOverlay(fadein2)
    tr.deleteAll()
    
    storage._setData('bedroom_introduction_done', True)
    
    storage._wait(2000)
    
    tr.write("Meet the others downstairs.", 5, COLOR_OBJECTIVE)
    tr.write("[Press W,A,S,D to move. Click on highlighted objects when close to them to interact.]", 5, COLOR_OBJECTIVE,\
                 (0, POSITION_BOTTOM_SCREEN[1]+20))
    
    m.removeOverlay(fadein2)
    
    storage._toggleCutscene(False)
    
    storage._halt()
    
def bed(storage, obj, m):
    storage._go()
        
    tr = GlobalServices.getTextRenderer()
    ad = GlobalServices.getAudioDevice()
    player = m.getPlayer()
    storage._faceObject(player, obj)
    
    if storage._playerInDistance(player.position, obj.rect):
        if storage._getData('bedroom_bedscare_done'):
            tr.write("There is no way I'll be able to sleep with this going on.", 3)
            
        elif storage._getData('entrancenote_obtained'):
            storage._toggleCutscene(True)
            GlobalServices.getEventManager().post(ObjectHighlightedEvent(None))
            tr.write("I am not imagining these things.", 3)
            storage._wait(3000)
            tr.write("...am I?", 3)
            storage._wait(3000)
            if storage._getData('leftwing_debrisfound'):
                tr.write("The blocked path in the Left Wing...", 3)
                storage._wait(3000)
                tr.write("I didn't put that stuff there.", 3)
                storage._wait(3000)
            storage._wait(1000)
            player.setDirection([1,0])
            tr.write("I need some sleep.", 3)
            storage._wait(3000)
            togray = OverlayFactory.create_animated_color((0,0,0), 4500, 0, True, 0, 255)
            m.addOverlay(togray)
            ad.stop(MUSIC, 4500)
            ad.stop(SOUND, 4500, 'vind2')
            ad.play(SOUND, 'ambient_spooky', VOLUME_SOUND_AMBIENT, -1, 4500)
            storage._wait(6000)
            
            starty = 200
            ofs = 18
            tr.write("When I think about it, I guess it's no wonder my friends turned on me.",\
                     0, COLOR_TEXT, (200, starty))
            storage._wait(4000)
            tr.write("After all, whenever one of them stayed overnight,",\
                     0, COLOR_TEXT, (200, starty + ofs))
            storage._wait(2000)
            tr.write("nothing weird ever happened the next morning.",\
                     0, COLOR_TEXT, (200, starty + (ofs * 2)))
            storage._wait(3000)
            tr.deleteAll()
            storage._wait(1000)
            starty = 214
            tr.write("I'm afraid.",\
                     0, COLOR_TEXT, (200, starty))
            storage._wait(4000)
            tr.write("Let's hope that I can settle this tomorrow.",\
                     0, COLOR_TEXT, (200, starty + ofs))
            storage._wait(1500)
            
            bed1 = os.path.join(PATH_GRAPHICS_TILES,'bed_clyde_eyesclosed.png')
            obj.changeImage(bed1)
            player.setVisible(False)
                        
            ad.play(SOUND, 'drone', VOLUME_SOUND)
            ad.play(SOUND, 'elec', VOLUME_SOUND)
            red = OverlayFactory.create_by_color((178, 10, 5), 0, 60)
            black = OverlayFactory.create_by_color((0, 0, 0), 0, 255)
            fog = OverlayFactory.create('fog.png', pygame.BLEND_MULT)
            add_global_overlay(fog)
            m.addOverlay(fog)
            tr.deleteAll()
            storage._wait(1500)
            ad.play(SOUND, 'insanity_bug3', VOLUME_SOUND_AMBIENT - 0.1, -1, 1500)
            m.removeOverlay(togray)
            storage._wait(400)
            ad.play(SOUND, 'general_thunder2', VOLUME_SOUND)
            ad.play(SOUND, 'insanity_monster_roar02', VOLUME_SOUND)
            storage._wait(400)
            ad.play(SOUND, '27_spark2', VOLUME_SOUND)
            m.addOverlay(red)
            m.addOverlay(black)
            storage._wait(300)
            
            
            ad.play(SOUND, '27_spark4', VOLUME_SOUND)
            m.removeOverlay(black)
            storage._wait(1000)
            m.removeOverlay(red)
            
            ad.play(SOUND, '27_spark2', VOLUME_SOUND)
            m.addOverlay(black)
            storage._wait(500)
            
            # Anderes Ich hier einfügen
            shadow = m.getShadow()
            shadow.setPosition(conv_tile_pixel((13, 15), m))
            shadow.setVisible(True)
            
            ad.play(SOUND, '27_spark4', VOLUME_SOUND)
            m.removeOverlay(black)
            storage._wait(300)
            
            bed2 = os.path.join(PATH_GRAPHICS_TILES,'bed_clyde_eyesopen.png')
            obj.changeImage(bed2)
            
            m.addOverlay(red)
            shadow.setVisible(False)
            for _ in range(3):
                ad.play(SOUND, '27_spark1', VOLUME_SOUND)
                m.addOverlay(black)
                storage._wait(750)
                m.removeOverlay(black)
                ad.play(SOUND, '27_spark3', VOLUME_SOUND)
                storage._wait(100)
            ad.play(MUSIC, 'bgm_1', VOLUME_MUSIC, -1)
            m.removeOverlay(red)
            grey = OverlayFactory.create_by_color((0, 0, 0), 0, 180)
            m.addOverlay(grey)
            ad.play(SOUND, '27_spark2', VOLUME_SOUND)
            storage._wait(100)
            ad.play(SOUND, '27_spark3', VOLUME_SOUND)
            ad.play(SOUND, 'insanity_monster_roar01', VOLUME_SOUND)
            
            obj.changeImage(None, True)
            
            player.setDirection([-1,1])
            player.setVisible(True)
            
            m.removeOverlay(black)
            storage._wait(2000)
            tr.write("What was that?!", 3)
            storage._wait(3000)
            ad.play(SOUND, 'scare_breath', VOLUME_SOUND)
            tr.write("Did it... happen again?", 3)
            storage._wait(3000)
            tr.write("The power's out completely now.", 3)
            storage._wait(4500)
            player.setDirection([-1,-1])
            tr.write("I better grab my flashlight from the table if I decide to go out.", 3)
            storage._wait(4000)
            tr.deleteAll()
            storage._wait(500)
            player.setDirection([-1,0])
            
            ad.play(SOUND, 'general_thunder2', VOLUME_SOUND)
            tr.write("Grab the flashlight and head out.", 5, COLOR_OBJECTIVE)
            tr.write("[Press F5 to save your progress.]", 3, COLOR_OBJECTIVE,\
                 (0, POSITION_BOTTOM_SCREEN[1]+20))
            # 'Toggled this cutscene' switch
            storage._setData('bedroom_bedscare_done', True)
            
            storage._toggleCutscene(False)
        else:
            tr.write("My bed used to be so comfortable. I don't sleep very well at the moment.", 5)
    else:
        tr.write("My bed. I can't reach it from here.", 3)
        
    storage._halt()
    
def bookshelf(storage, obj, m):
    storage._go()
        
    tr = GlobalServices.getTextRenderer()
    
    storage._faceObject(m.getPlayer(), obj)
    
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        storage._toggleCutscene(True)
        tr.write("It is full of old books, most of which I haven't even touched once since I got here.", 3)
        storage._wait(3000)
        tr.write("These may have been useful to my grand-dad, but that was another time.", 3)
        storage._toggleCutscene(False)
    else:
        tr.write("I can't reach that from here.")
        
    storage._halt()
    
def flashlight(storage, obj, m):
    storage._go()
    
    tr = GlobalServices.getTextRenderer()
    ad = GlobalServices.getAudioDevice()
    
    storage._faceObject(m.getPlayer(), obj)
    
    if not storage._playerInDistance(m.getPlayer().position, obj.rect):
        tr.write("I can't reach that from here.", 3)
    else:
        # Bed scare sequence done
        if storage._getData('bedroom_bedscare_done'):
            # Add the flashlight to the inventory
            m.getPlayer().inventory.add(\
                          ItemFactory.create(INVENTORY_ITEM_FLASHLIGHT, 1))
            ad.play(SOUND, 'pick_item', VOLUME_SOUND)
            tr.write("Got 'Flashlight'", 3, COLOR_GOT_ITEM)
            # Delete the note from the map
            m.removeObject(obj)
            remove_from_map(get_savegame(), OBJECT, 'bedroom', 'bedroom_flashlight')
            # Set a flag that this script was executed
            storage._setData('flashlight_obtained', True)        
            # Add the global flashlight overlay, deleting the others
            flashlight = OverlayFactory.create_flashlight()
            set_global_overlays([flashlight])
            # Add the overlay to this map, too
            m.clearOverlays()
            m.addOverlay(flashlight)
            ad.play(SOUND, 'flashlight_toggle', VOLUME_SOUND)
            ad.stop(SOUND, 1500, 'insanity_bug3')
        else:
            storage._toggleCutscene(True)
            tr.write("Sometimes I need my flashlight when the power tends to get all freaky.", 3)
            storage._wait(3000)
            tr.write("I don't know if that's because the mansion is just old or haunted, though.", 3)
            storage._toggleCutscene(False)
    
    storage._halt()
    
def tprhallway(storage, m, obj):
    storage._go()
    
    tr = GlobalServices.getTextRenderer()
    
    # This door works in most cases when the player is in range
    retval = False
    
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        # If the bed scare occured but the player hasn't picked up the flashlight,
        # this door doesn't work
        if storage._getData('bedroom_bedscare_done') and \
        not storage._getData('flashlight_obtained'):
            tr.write("I better grab my flashlight from the table before I get out.", 4)
            retval = False
        else:
            retval = True
    
    storage._halt()
    return retval

def closet(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    if not storage._playerInDistance(m.getPlayer().position, obj.rect):
        tr.write("I can't reach that from here.", 3)
    else:
        tr.write("My closet of random stuff. Nothing of interest here.", 3)
    storage._halt()