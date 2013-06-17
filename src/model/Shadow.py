# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from libs.pyganim import pyganim
from src.model import EntityFactory
from src.utilities import get_direction_from_point_to_point, direction_to_string
import pygame

# Shadow.
# The "antagonist" of the game. This class is similar
# to Player.py, but differs in some aspects such as movement input.
class Shadow:
    # Constructor
    def __init__(self):
        # Setup the shadow's properties using the EntityFactory
        self.properties = EntityFactory.createShadowProperties()
        self.sprites = self.properties["sprites"]
        self.conductor = pyganim.PygConductor(self.sprites)
        self.position = (300, 300)
        self.coll_rect = pygame.Rect((0,0), (25, 10))
        # Setup initial direction
        self.moving = False
        self.direction = None
        self.position = (300, 300)
        self.setDirection([0,1])
        self.resetMovementVars()
        # Setup initial sprite
        self.currentsprite = None
        self.updateSprite()
        self.walk_starttime = 0
        self.walk_curtime = 0
        # Visibility
        self.visible = False
        
    # Sets the visibility of the Shadow. It's False by default,
    # but if a cutscene needs the shadow to be visible, flip
    # the switch!
    # Parameter:
    #    b    :    Boolean depicting if the shadow should be rendered or not
    def setVisible(self, b):
        self.visible = b
        
    # Returns if the shadow is visible at the moment or not
    # Returns:
    #    True, if the shadow is visible, False otherwise
    def isVisible(self):
        return self.visible
        
    # Sets the position of the shadow
    # Parameter:
    #    pos    :    Positional tuple to use as the position
    def setPosition(self, pos):
        self.position = pos
        self.resetMovementVars()
        
    # Sets the direction of the shadow
    # Parameter:
    #    direction    :    Vector for direction
    def setDirection(self, direction):
        self.direction = direction_to_string(direction)
        
    # Resets the movement-related variables of Shadow.
    def resetMovementVars(self):
        self.currentMoveDestination = None
        self.cmStartPos = None
        self.cmDestPos = None
        self.cmDestTime = 0
        self.cmCurTime = 0
        self.moving = False
        
    # Moves the shadow by a given vector ina given time
    # Parameter:
    #    vector    :    The vector to move from the shadow's initial position
    #    dur       :    Duration in milliseconds that it takes the shadow
    #                   to move the vector's distance
    def moveBy(self, vector, dur):
        # Re-position the shadow if the last movement is still present
        if self.cmDestPos is not None:
            self.position = self.cmDestPos
        # Now reset and re-setup
        self.resetMovementVars()
        # Calculate starting and finishing points for this movement
        self.cmStartPos = self.position
        self.cmDestPos = (self.position[0] + vector[0],\
                          self.position[1] + vector[1])
        self.cmDestTime = dur
        self.cmCurTime = 0
        
        # Set the facing of the sprite
        self.direction = get_direction_from_point_to_point(\
                         self.currentsprite.rect.center, self.cmDestPos)
        
        # Enable moving status
        self.moving = True

    # Update method for the shadow
    # Parameter:
    #    fps    :    FPS time in milliseconds since the last tick
    def update(self, fps):
        if not self.visible:
            return
        if self.moving:
            self.conductor.play()
            # Use the inverse of the fps as milliseconds input
            # to the two linear mathematical functions that
            # interpolate between the current move's start
            # and end points.
            self.cmCurTime += (1000/fps)
            # y = mx + n
            self.position = (((self.cmDestPos[0] - self.cmStartPos[0])/self.cmDestTime)*\
                              self.cmCurTime + self.cmStartPos[0],\
                              ((self.cmDestPos[1] - self.cmStartPos[1])/self.cmDestTime)*\
                              self.cmCurTime + self.cmStartPos[1])
            self.updateSprite()
            # If the movement's time has passed,
            # end the movement here.
            if self.cmCurTime >= self.cmDestTime:
                self.position = self.cmDestPos
                self.resetMovementVars()
        else:
            self.conductor.stop()
            self.updateSprite(True)
    
    # Updates the sprite for the Player
    # Parameter:
    #    standingFrame    :    Boolean that depicts if the "still frame"
    #                          of the animation should be used (= True), or if
    #                          the animation should be in motion (= False)    
    def updateSprite(self, standingFrame=False):
        if not standingFrame:
            self.currentsprite = self.sprites["walk-%s" % self.direction].getCurrentFrame()
        else:
            self.currentsprite = self.sprites["walk-%s" % self.direction].getFrame(1)
        self.currentsprite.rect.midbottom = (self.position[0], self.position[1])