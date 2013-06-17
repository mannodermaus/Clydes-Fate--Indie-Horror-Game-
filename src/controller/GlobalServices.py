# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.controller.AudioDevice import AudioDevice
from src.interfaces import LoggerInterface, Listener
from src.view.TextRenderer import TextRenderer

# GlobalServices.
# This module provides services that can be accessed from any class that
# needs to access text rendering, audio playing, logging or event posting.
# These are the four services that are provided by this module.

# Logger
_logger = None
# Audio device
_audio = None
# Text renderer
_textrenderer = None
# Event manager
_evmanager = None
    
# Initialization method, invoked by main.py
# Parameter:
#    evManager    :    EventManager instance
def init(evManager):
    # Empty Logger implementation that is used per default
    # unless another Logger is passed into setLogger()
    # (this way, logging is "off" per default)
    class NullLogger(LoggerInterface, Listener):
        def log(self, message):
            pass
        def setFilter(self, filtered_types):
            pass
        def notify(self, event):
            pass
    global _logger, _evmanager
    _logger = NullLogger(evManager)
    _evmanager = evManager
    
# Retrieve EventManager instance.
# Returns:
#    EventManager
def getEventManager():
    global _evmanager
    return _evmanager

# Sets a new Logger.
# Parameter:
#    logger    :    The new Logger implementing the LoggerInterface to be used
def setLogger(logger):
    global _logger
    if isinstance(logger, LoggerInterface):
        _logger = logger
    
# Sets a new TextRenderer.
# Parameter:
#    tr    :    The new TextRenderer object
def setTextRenderer(tr):
    global _textrenderer
    if isinstance(tr, TextRenderer):
        _textrenderer = tr
    
# Sets a new AudioDevice.
# Parameter:
#    ad    :    The new AudioDevice object
def setAudioDevice(ad):
    global _audio
    if isinstance(ad, AudioDevice):
        _audio = ad
        
# Returns the current Logger.
# Returns:
#    The current logger
def getLogger():
    global _logger
    return _logger
    
# Returns the current TextRenderer.
# Returns:
#    The current text rendering object
def getTextRenderer():
    global _textrenderer
    return _textrenderer
    
# Returns the current AudioDevice.
# Returns:
#    The current audio playback device
def getAudioDevice():
    global _audio
    return _audio