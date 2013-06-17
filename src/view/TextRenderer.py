# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import PATH_GRAPHICS, COLOR_TEXT, POSITION_BOTTOM_SCREEN, \
    FONTSTYLE_NORMAL, SCREEN_WIDTH
from src.model.Timer import Timer
import os
import pygame

# TextRenderer.
# This module provides a component that is able to write anything, anywhere on the screen.
# It is part of the GlobalServices access module and utilizes internal classes that are
# not needed by anyone outside of this class.
class TextRenderer():        
    # Constructor
    # Parameter:
    #   screen  :   The surface to be rendered onto
    def __init__(self, screen):
        # Set a screen reference
        self.screen = screen
        # Set-up the list of currently pending texts
        self.texts = []
        # Set-up three different styles to render text (different sizes etc.)
        TextRenderer._fontstyles = []
        TextRenderer._fontstyles.append(pygame.font.Font(os.path.join(PATH_GRAPHICS, "lydian.ttf"), 13))
        TextRenderer._fontstyles.append(pygame.font.Font(os.path.join(PATH_GRAPHICS, "lydian.ttf"), 17))
        f = pygame.font.Font(os.path.join(PATH_GRAPHICS, "lydian.ttf"), 30)
        f.set_bold(True)
        TextRenderer._fontstyles.append(f)
        
    # Render method called by the view controller.
    def render(self):
        # Every Text object knows how to render itself,
        # therefore just order them to do so.
        for text in self.texts:
            text.render()
            
    # Displays a new text on the screen. If the calling component
    # wants to keep a reference to the created object after its creation
    # (in order to process input on it or whatnot), it is returned at the end.
    # The text renderer itself keeps track of overlapping texts and deletes any
    # previously rendered text that collides with the new one. Therefore, each new text
    # has priority of the region it occupies.
    # Parameters:
    #   message     :   The string message to be displayed
    #   duration    :   The desired duration this text should last on screen, in seconds (default: 5).
    #                   If 0 is passed, the message won't be deleting itself after a certain amount of time.
    #   color       :   The desired RGBA color of the text (default: constants.COLOR_TEXT)
    #   position    :   The desired position tuple of the text (default: constants.POSITION_BOTTOM_SCREEN)
    #   fontstyle   :   The desired fontstyle of the text (default: TextRenderer.FONTSTYLE_NORMAL)
    #   center_hor  :   Boolean describing if the text is to be centered horizontally. Default: True
    # Returns:
    #   A reference to the created Text object
    def write(self, message, duration = 5, color = COLOR_TEXT, \
              position = POSITION_BOTTOM_SCREEN, fontstyle = FONTSTYLE_NORMAL, center_hor = True):
        # create the Text object
        try:
            obj = Text(message, duration*1000, position, color, self.screen, self._fontstyles[fontstyle], center_hor, self)
        except pygame.error:
            # When the fullscreen toggling is engaged at a time
            # where a Text is being rendered, this method fails to render.
            return
        # Check if the new object overlaps with one of the other currently drawn Text objects
        for o in self.texts:
            if obj.rect.colliderect(o.rect):
                # If so, delete that older texts
                o.delete()
        # Append the new text object to the list of texts
        self.texts.append(obj)
        # Return it
        return obj
        
    # Writes the given message to a pygame Surface and returns it.
    # Parameters:
    #   message     :   The string message to be written
    #   color       :   The RGBA color to be used for the text
    #   fontstyle   :   The fontstyle to be used
    # Returns:
    #    The rendered text as a pygame Surface object
    def writeAsSurface(self, message, color = COLOR_TEXT, fontstyle = FONTSTYLE_NORMAL):
        font = self._fontstyles[fontstyle]
        surf = font.render(str(message), True, color).convert_alpha()
        return surf
        
        
    # Delete the given text object from the list of texts.
    # Parameter:
    #   text    :   The Text object to be deleted
    def delete(self, text):
        if text in self.texts:
            self.texts.remove(text)
            
    # Deletes all text objects from the list
    def deleteAll(self):
        # Delete all open text threads        
        for _ in range(len(self.texts)):
            # Always access the first item
            # and repeat the process len(texts) times
            # to avoid iteration errors
            self.texts[0].delete()

# Text.
# This class holds a text object that can be drawn to the screen.
# It keeps track of its own state using a special timer that deletes
# the text if necessary.
class Text():
    # Internal class TextTimer.
    # This implementation of the Timer interface deletes the
    # text object after its duration has passed. If the user
    # exits the game while a text object is still being displayed,
    # the incoming quit event causes the view controller to kill all
    # text objects. Therefore, this interface is necessary.
    # Implements:
    #   Timer
    class TextTimer(Timer):
        # Constructor
        # Parameters:
        #   time    :   The time the associated object should last
        #   textobj :   Reference to that text object
        def __init__(self, time, textobj):
            self.textobj = textobj
            # Kill request switch that is toggled whenever the game exits early
            self.killrequest = False
            def killcheck():
                return self.killrequest == True
            Timer.__init__(self, time, killcheck)
                        
        # Timer implementation run method
        def run(self):
            # Run the timer, and afterwards, delete the text object
            Timer.run(self)
            self.textobj.delete()
    # /CLASS

    # Constructor of a text object
    # Parameters:
    #   text        :   String message to be displayed
    #   duration    :   Duration of the text in milliseconds
    #   position    :   Desired position of the text
    #   color       :   Desired color of the text
    #   screen      :   Surface on which the text is to be drawn
    #   font        :   Font to be used for drawing
    #   center      :   Boolean if the text should be centered horizontally
    #   tr          :   TextRenderer reference
    def __init__(self, text, duration, position, color, screen, font, center, tr):
        # Set all necessary parameters
        self._font = font
        self.text = text
        self.screen = screen
        self.setColor(color)
        pos = (SCREEN_WIDTH/2 - self.rendered.get_rect().width/2, position[1]) \
              if center else position
        self.position = pos
        self.rect = pygame.Rect(self.position, (self.rendered.get_rect().width, self.rendered.get_rect().height))
        self.tr = tr
        # If the duration is above 0, delete this text object using a TextTimer
        if (duration > 0):
            self.inf = False
            self.timer = Text.TextTimer(duration, self)
            self.timer.start()
        # Else, this object lasts forever (or until it collides with a more recent one)
        else:
            self.inf = True

    # Render method to draw the rendered text to the screen at the given position
    def render(self):
        self.screen.blit(self.rendered, self.position)
        
    # Delete the text and kill the timer if necessary
    def delete(self):
        if not self.inf:
            self.timer.killrequest = True
        self.tr.delete(self)
        
    # Set the color of the text
    # Parameter:
    #   color   :   The desired RGBA color
    def setColor(self, color):
        self.rendered = self._font.render(self.text, True, color).convert_alpha()
        
    # toString override for debugging purposes.
    # Returns:
    #   String representation of thie text object
    def __repr__(self):
        return "(src.view.TextRenderer.Text) '%s'" % self.text