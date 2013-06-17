# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from libs.pyganim import pyganim
from src.constants import VOLUME_SOUND
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND
from src.model import EntityFactory
from src.utilities import direction_to_string
import pygame
import random

# Player.
# Player representation for Clyde,
# the main protagonist of the applciation.
class Player():
    # Constructor
    def __init__(self):
        # Setup the player properties using the EntityFactory
        self.properties = EntityFactory.createPlayerProperties()
        self.sprites = self.properties["sprites"]
        self.conductor = pyganim.PygConductor(self.sprites)
        # Pixels to move per second for this player
        self.pps = self.properties["pps"]
        # Speedlock equals 1 if it is disabled, and 0.5 if it's on
        self.speedlock = 1
        self.inventory = self.properties["inventory"]
        self.position = (300, 300)
        self.coll_rect = pygame.Rect((0,0), (25, 10))
        # Setup initial direction
        self.moving = False
        self.facing = None
        self.direction = None
        self.animation = None
        self.setFacing([0,1])
        self.setDirection([0,1])
        # Setup initial sprite
        self.setAnimation("walk")
        self.currentsprite = None
        self.updateSprite()
        self.visible = True
        self.walk_starttime = 0
        self.walk_curtime = 0
        
    # Internal method to check if a step sound should be played
    # at the current point in "walk time"
    # Parameter:
    #    fps    :    FPS time in milliseconds since the last tick
    def _checkSound(self, fps):
        if self.walk_curtime >= int(fps * 0.55):
            self.walk_starttime = 0
            self.walk_curtime = 0
            self._playStepSound()
            
    # Internal method that plays a randomized step sound
    def _playStepSound(self):
        i = random.randrange(1, 6)
        GlobalServices.getAudioDevice().play(SOUND,\
                "step_run_rock%d" % i, VOLUME_SOUND)
            
    # Sets the visibility of the Player. It's True by default,
    # but if a cutscene needs the player to be invisible, flip
    # the switch!
    # Parameter:
    #    b    :    Boolean depicting if the player should be rendered or not
    def setVisible(self, b):
        self.visible = b
        
    # Returns if the player is visible at the moment or not
    # Returns:
    #    True, if the player is visible, False otherwise
    def isVisible(self):
        return self.visible
            
    # Moves the player. This is called by the RunningGameHandler
    # Parameters:
    #    direction    :    Vector depicting the direction to go to
    #    fps          :    FPS time in milliseconds since the last tick
    def move(self, direction, fps):
        if direction is not None:
            self.walk_curtime += 1
            # Play step sound
            self.setAnimation("walk")
            self._checkSound(fps)
            self.startMoving()
            
            # Move Clyde 100 px per second, therefore
            # determine timestep according to fps
            speed = (self.pps / fps) * self.speedlock;
            
            self.position = (self.position[0] + direction[0] * speed, \
                             self.position[1] + direction[1] * speed)
        else:
            self.stopMoving()
        
    # Starts moving the sprite of the Player
    def startMoving(self):
        if not self.moving:
            self._playStepSound()
            self.setAnimation("walk")
            self.moving = True
        
    # Stops the movement of the Player's sprite
    def stopMoving(self):
        self.moving = False
        
    # Sets the position of the player
    # Parameter:
    #    pos    :    Positional tuple to set the player's position to
    def setPosition(self, pos):
        self.position = pos
        
    # Returns the current direction the player goes to
    # Returns:
    #    Current direction as vector
    def getDirection(self):
        return self.direction
    
    # Sets the facing of the Player sprite (the direction in which he looks)
    # Parameter:
    #    d    :    Vector representing the direction to be facing
    def setFacing(self, d):
        self.facing = d
        
    # Sets a new direction of the player
    # Parameter:
    #    d    : Vector representing the direction
    def setDirection(self, d):
        self.setFacing(d)
        if d != [0,0]:
            self.direction = direction_to_string(self.facing)
        self.setAnimation("walk")
        
    # Sets the inventory reference for the player
    # Parameter:
    #    inv    :    Inventory reference
    def setInventory(self, inv):
        self.inventory = inv
        
    # Changes the speed of the player
    # Parameter:
    #    speed    :    Speed to set the player's movement to
    def halfSpeed(self):
        self.speedlock = 0.5
        
    # Restores the speed of the player to normal
    def restoreSpeed(self):
        self.speedlock = 1
        
    # Updates the player's status
    def update(self):
        if self.moving:
            self.conductor.play()
            self.updateSprite()
        else:
            self.conductor.stop()
            self.updateSprite(True)
            self.walk_starttime = 0
            self.walk_curtime = 0
        
    # Sets the animation of the Player's sprite
    # Parameter:
    #    key    :    The new animation to be used
    def setAnimation(self, key):
        if key == "walk":            
            self.animation = "walk-%s" % self.direction
            self.defFrame = 1
        else:
            self.animation = key
            self.defFrame = 0
            
    # Updates the sprite for the Player
    # Parameter:
    #    standingFrame    :    Boolean that depicts if the "still frame"
    #                          of the animation should be used (= True), or if
    #                          the animation should be in motion (= False)
    def updateSprite(self, standingFrame=False):
        if not standingFrame:
            self.currentsprite = self.sprites[self.animation].getCurrentFrame()
        else:
            self.currentsprite = self.sprites[self.animation].getFrame(self.defFrame)
        self.currentsprite.rect.midbottom = (self.position[0], self.position[1])