# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import VOLUME_SOUND, PATH_GRAPHICS_TILES, \
    VOLUME_SOUND_AMBIENT, VOLUME_MUSIC
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND, MUSIC
from src.utilities import string_to_direction, conv_tile_pixel
from src.view import OverlayFactory
import os
import pygame


def init(storage, m):
    # If the scare hasn't been done yet and the player triggered
    # the abandoned room's canvas, this goes here
    storage._go()
    m.rendering_enabled = True
    if not storage._getData('lefthallway_scare_done') and\
       storage._getData('lefthallway_scare_enabled') and\
       not storage._getData('mirrorhall_murder_done'):
        
        # Scare
        storage._toggleCutscene(True)
        player = m.getPlayer()
        player.stopMoving()
        
        # Helper function for looking in a direction
        def face(direction):
            fl = m.getOverlay("_flashlight")
            fl.point(direction)
            player.setDirection(string_to_direction(direction))
            
        face("up")
        
        # Overlay creation
        ad = GlobalServices.getAudioDevice()
        fog = OverlayFactory.create("fog.png", pygame.BLEND_MULT)
        black = OverlayFactory.create_by_color((0, 0, 0), 0, 200)
        grad = OverlayFactory.create_animated_color((0,0,0),\
               3000, 0, True, 200, 0)
        
        ad.play(SOUND, '21_hole_loop', VOLUME_SOUND)
        ad.stop(MUSIC, 2000)
        ad.stop(SOUND, 2000, 'ambient_spooky')
        storage._wait(2000)
        
        # Show the figure
        ad.play(MUSIC, 'event1', VOLUME_MUSIC + 0.4)
        m.addOverlay(fog)
        shadow = m.getShadow()
        shadow.setPosition(conv_tile_pixel((41, 10), m))
        m.addOverlay(black)
        ad.play(SOUND, '27_spark1', VOLUME_SOUND)
        storage._wait(100)
        shadow.setVisible(True)
        m.removeOverlay(black)
        ad.play(SOUND, '27_spark2', VOLUME_SOUND)
        ad.play(SOUND, 'scare_wood_creak_scuf3', VOLUME_SOUND)
        shadow.moveBy((-30, 0), 2000)
        storage._wait(2000)
        shadow.moveBy((0, 1), 10)
        face("up-right")
        shadow.setVisible(False)
        storage._wait(250)
        face("up")
        storage._wait(100)
        shadow.setVisible(True)
        face("left-up")
        storage._wait(250)
        face("up")
        storage._wait(400)
        ad.play(SOUND, 'scare_wood_creak_walk2', VOLUME_SOUND)
        shadow.moveBy((0, -50), 4500)
        m.addOverlay(black)
        ad.play(SOUND, '27_spark4', VOLUME_SOUND)
        storage._wait(300)
        shadow.setVisible(False)
        m.removeOverlay(black)
        ad.play(SOUND, '27_spark3', VOLUME_SOUND)
        storage._wait(200)
        m.addOverlay(black)
        ad.play(SOUND, '27_spark4', VOLUME_SOUND)
        storage._wait(50)
        shadow.setVisible(True)
        m.removeOverlay(black)
        storage._wait(1450)
        ad.play(SOUND, 'general_chain_rattle2', VOLUME_SOUND)
        m.addOverlay(black)
        ad.play(SOUND, '27_spark1', VOLUME_SOUND)
        storage._wait(100)
        m.removeOverlay(black)
        ad.play(SOUND, '27_spark2', VOLUME_SOUND)
        storage._wait(200)
        m.addOverlay(black)
        ad.play(SOUND, '27_spark4', VOLUME_SOUND)
        storage._wait(50)
        shadow.setVisible(False)
        m.removeOverlay(black)
        ad.play(SOUND, '27_spark3', VOLUME_SOUND)
        storage._wait(390)
        m.addOverlay(black)
        ad.play(SOUND, '27_spark1', VOLUME_SOUND)
        storage._wait(200)
        shadow.setVisible(True)
        m.removeOverlay(black)
        ad.play(SOUND, '27_spark2', VOLUME_SOUND)
        storage._wait(777)
        m.removeOverlay(fog)
        m.addOverlay(black)
        ad.play(SOUND, '27_spark4', VOLUME_SOUND)
        storage._wait(500)
        shadow.setVisible(False)
        m.addOverlay(grad)
        m.removeOverlay(black)
        m.removeOverlay(fog)
        ad.play(SOUND, '27_spark3', VOLUME_SOUND)
        storage._wait(3000)
        m.removeOverlay(grad)
        ad.play(MUSIC, 'bgm_1', VOLUME_MUSIC, -1)
        ad.play(SOUND, 'ambient_spooky', VOLUME_SOUND_AMBIENT, -1, 2000)
        storage._setData('lefthallway_scare_done', True)
        storage._toggleCutscene(False)
    storage._halt()

def switch(storage, obj, m, index):
    # (Extra "index" parameter depicts the # of the switch that was triggered
    # from 1 (far left) to 5 (far right))
    storage._go()
    if not storage._getData('lefthallway_puzzle_solved'):
        if storage._playerInDistance(m.getPlayer().position, obj.rect):
            ad = GlobalServices.getAudioDevice()
            # Initialize the persistent representation of this puzzle if it doesn't exist yet
            states = storage._getData('lefthallway_switches')
            if states is None:
                # -1: down, 0: middle, 1: up
                states = [0, 0, 0, 0, 0]
                
            # Change the state of the switch that was passed in
            # (subtract 1 from the index b/c computer scientists love to start at 0!)
            state = states[index-1]
            state += 1
            if state > 1:
                state = -1
            states[index-1] = state
            
            storage._setData('lefthallway_switches', states)
            
            # Change graphic for that switch
            if state == -1:
                image = 'switch_down.png'
            elif state == 0:
                image = 'switch_mid.png'
            else:
                image = 'switch_up.png'
            gfx = os.path.join(PATH_GRAPHICS_TILES, image)
            ad.play(SOUND, 'pull_switch', VOLUME_SOUND)
            obj.changeImage(gfx)
                
            # Solution to the switch puzzle (from left to right):
            # up down down up up
            # (The gender of the five people on the portrait
            # are mapped to the positioning of the switches.
            # The encoding of gender is hinted at in the abandoned chamber.)
            solution = [1, -1, -1, 1, 1]
            if states == solution:
                # Puzzle solved
                storage._toggleCutscene(True)
                ad.play(SOUND, 'doorstop3', VOLUME_SOUND)
                lastdir = m.getPlayer().getDirection()
                m.getPlayer().setDirection(string_to_direction("up-right"))
                storage._wait(250)
                ad.play(SOUND, '07_pick_lock', VOLUME_SOUND)
                storage._wait(500)
                tr = GlobalServices.getTextRenderer()
                tr.write("Something has happened. I think this is the correct combination.", 3)
                m.getPlayer().setDirection(string_to_direction(lastdir))
                storage._setData('lefthallway_puzzle_solved', True)
                storage._toggleCutscene(False)
    
    storage._halt()

def familyportrait(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        storage._toggleCutscene(True)
        if not storage._getData('lefthallway_portrait_intro'):
            tr.write("It is the portrait of a family that I don't know.", 4)
            storage._wait(4000)
            tr.write("Something about it seems strangely unsettling to me.", 4)
            storage._wait(4000)
        tr.write("A young boy frames each side of the portrait, with what seems to be a parent next to them.", 4)
        storage._wait(4000)
        tr.write("The girl in the middle looks sad.", 4)
        storage._toggleCutscene(False)
        storage._setData('lefthallway_portrait_intro', True)
    storage._halt()

def tpupperbalcony(storage, source, obj):
    storage._go()
    retval = False
    tr = GlobalServices.getTextRenderer()
    ad = GlobalServices.getAudioDevice()
    if storage._playerInDistance(source.getPlayer().position, obj.rect):
        ad.play(SOUND, "lockeddoor", VOLUME_SOUND)
        tr.write("The door won't budge.", 3)
    storage._halt()
    return retval

def tpmirrorhall(storage, source, obj):
    storage._go()
    retval = False
    if storage._playerInDistance(source.getPlayer().position, obj.rect):
        if storage._getData('mirrorhall_murder_done'):
            retval = True
        elif storage._getData('lefthallway_puzzle_solved'):
            ad = GlobalServices.getAudioDevice()
            ad.stop(MUSIC, 5000)
            ad.stop(SOUND, 5000, 'ambient_spooky')
            retval = True
        else:
            tr = GlobalServices.getTextRenderer()
            tr.write("This door seems to be locked with a mechanical lock.", 3)            
    storage._halt()
    return retval