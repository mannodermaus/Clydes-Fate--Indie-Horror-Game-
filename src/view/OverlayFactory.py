# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import PATH_GRAPHICS_SPRITES, SCREEN_WIDTH, SCREEN_HEIGHT, \
    SCREEN_CENTER, DIRS, FLASHLIGHT_MOVEMENT_ENABLED
from src.interfaces import Overlay
from src.utilities import get_direction_from_point_to_point, get_property
import os
import pygame
import time
        
# FlashlightOverlay.
# A special kind of graphical overlay for the screen.
# This overlay represents the flashlight that the player
# uses to see after the power goes out.
# Its render() method implements a direction-setter so
# that the flashlight adjusts itself to the mouse position
# on the screen.
class FlashlightOverlay(Overlay):
    # Constructor
    def __init__(self):
        # Load the flashlight images
        self.__loadimages()
        # Set the first direction to the first in the DIRS array (see src.constants)
        self.currentdir = DIRS[0]
        # Set the surface for this direction
        self.updateSurf()
        # Complete the initialization of an "ordinary overlay"
        Overlay.__init__(self, "_flashlight", self.surf)
        
    # Internal method that loads the pygame Surface objects for every direction
    # that the flashlight can be wielded in.
    def __loadimages(self):
        self.directions_surfs = {}
        for direction in DIRS:
            self.directions_surfs[direction] = pygame.image.load( \
                os.path.join(PATH_GRAPHICS_SPRITES, "flashlight", "flashlight_%s.png" % direction)).convert_alpha()
            self.directions_surfs[direction].set_alpha(200)
            
    # Forces the flashlight to point in the given direction.
    # If an illegal direction is passed, this method does not do anything.
    # Parameter:
    #    direction    :    A string of the direction where the flashlight should be pointed at.
    #                      Values are to be taken from src.constants.DIRS
    def point(self, direction):
        if direction in DIRS:
            self.currentdir = direction
            self.updateSurf()
        
    # Render method for this special overlay.
    # Parameters:
    #    screen    :    The surface to render onto
    #    active    :    Boolean indicating if this overlay is to be rendered "active"
    def render(self, screen, active=True):
        # If this overlay is active and the global property
        # for flashlight movement is enabled, determine a new
        # direction for the flashlight if necessary.
        if active and get_property(FLASHLIGHT_MOVEMENT_ENABLED):
            # Determine direction
            mpos = pygame.mouse.get_pos()
            newdir = get_direction_from_point_to_point(SCREEN_CENTER, mpos)
            # If this is a new direction, change it and the Surface
            if newdir is not self.currentdir:
                self.currentdir = newdir
                self.updateSurf()
        # Render
        Overlay.render(self, screen)
        
    # Updates the surface of this flashlight and re-sets
    # the surf attribute to the Surface of the current direction
    def updateSurf(self):
        self.surf = self.directions_surfs[self.currentdir]
        
    # Pickle method
    # Returns:
    #    Modified dict of this object's attributes
    def __getstate__(self):
        d = self.__dict__.copy()
        # Delete the current surface and the dictionary of saved surfaces
        # because those can't be pickled. Then return the dict
        del d['surf']
        del d['directions_surfs']
        return d
    
    # Unpickle method
    # Parameter:
    #    d    :    Dictionary to be used
    def __setstate__(self, d):
        self.__dict__.update(d)
        # Reload images and set the current surface
        self.__loadimages()
        self.updateSurf()
# /CLASS
        
# Create method for a FlashlightOverlay.
# Returns:
#    A new FlashlightOverlay object to be added to the screen
def create_flashlight():
    return FlashlightOverlay()
        
# Create method for an image overlay using a file.
# Parameters:
#    filename    :    Filename of the overlay, stored in assets/graphics/sprites
#    flags       :    pygame Blend Mode Flag that can optionally be passed in
# Returns:
#    An Overlay object with this image
def create(filename, flags=0):
    return Overlay(filename, pygame.image.load( \
        os.path.join(PATH_GRAPHICS_SPRITES, filename)), True, flags)
        
# Create method for a color overlay.
# Parameters:
#    color    :    (R,G,B) integer tuple depicting the color to be used
#    flags    :    pygame Blend Mode Flag that can optionally be passed in
#    opacity  :    Transparency of the image. This is only affecting the overlay
#                  if the standard Blend Mode is used
# Returns:
#    An Overlay of this color and transparency
def create_by_color(color, flags=0, opacity=255):
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    s.fill(color)
    s.set_alpha(opacity)
    return Overlay("_solidcolor", s, True, flags, color, opacity)
    
# Create method for an animated color overlay that interpolates
# between two transparencies.
# Parameters:
#    color        :    (R,G,B) integer tuple depicting the color to be used
#    duration     :    The time in milliseconds that it should take the
#                      overlay to complete its transparency transition
#    flags        :    pygame Blend Mode Flag
#    visible      :    Boolean to indicate if this overlay is to be displayed right away
#    start_opacity:    Transparency value at the start of the animation
#                      (0 = fully transparent; 255 = fully opaque)
#    stop_opacity :    Transparency value at the end of the animation
# Returns:
#    An AnimatedColorOverlay object
def create_animated_color(color, duration, flags=0, visible=True, start_opacity=255, stop_opacity=0):
    # AnimatedColorOverlay.
    # A special kind of graphical overlay for the screen
    # that interpolates between two transparency states
    # and updates itself.
    class AnimatedColorOverlay(Overlay):
        # Constructor.
        # Parameters:
        #    color        :    (R,G,B) integer tuple depicting the color to be used
        #    duration     :    The time in milliseconds that it should take the
        #                      overlay to complete its transparency transition
        #    flags        :    pygame Blend Mode Flag
        #    visible      :    Boolean to indicate if this overlay is to be displayed right away
        #    start_opacity:    Transparency value at the start of the animation
        #                      (0 = fully transparent; 255 = fully opaque)
        #    stop_opacity :    Transparency value at the end of the animation
        def __init__(self, color, duration, flags, visible=True, start_opacity=255, stop_opacity=0):
            # Set attributes and create the surface
            self.surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.fill(color)
            self.surf.set_alpha(start_opacity)
            self.start_opacity = start_opacity
            self.stop_opacity = stop_opacity
            self.color = color
            self.dur = duration
            # Setup start time (for animation)
            self.starttime = time.time()
            self.visible = visible
            self.animationfinished = False
            self.name = "_animatedcolor"
            self.flags = flags
            # Complete initialization process
            Overlay.__init__(self, self.name, self.surf, self.visible, self.flags)
            
        # Render method
        #    screen    :    Surface to render onto
        #    active    :    Boolean indicating if the overlay is to be rendered "in motion"
        def render(self, screen, active=True):
            if self.visible:
                # If the animation is not finished yet
                if not(self.animationfinished) and active:
                    # Calculate the current alpha transparency value
                    t = time.time()
                    dtms = int((t - self.starttime) * 1000)
                    # Linear mathematical function again!
                    alpha = int(((self.stop_opacity - self.start_opacity)/self.dur)\
                            * dtms) + self.start_opacity
                    # If the animation is over, stop it
                    if dtms > self.dur:
                        alpha = self.stop_opacity
                        self.animationfinished = True
                    # Set the transparency value
                    self.setOpacity(alpha)
                # Render to screen
                screen.blit(self.surf, (0, 0), None, self.flags)
            else:
                if not(self.animationfinished) and active:
                    self.starttime = time.time()
    # /CLASS
                    
    return AnimatedColorOverlay(color, duration, flags, visible, start_opacity, stop_opacity)