# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import PATH_SOUNDS, PATH_MUSIC, FADEIN_TIME, VOLUME_SOUND
import os
import pygame

# Constants for Sound or Music access,
# passed in for AudioDevice.play() and AudioDevice.stop()
SOUND = 1
MUSIC = 2

# AudioDevice.
# This class is being used in a Singleton-ish way,
# because the only instance of this class is being held
# in src.controller.GlobalServices and is accessed by
# asking the GlobalServices object.
class AudioDevice:
    # Constructor
    def __init__(self):
        # Dictionary containing sfx objects with unique keys
        self._sounds = {}
        # Current music to be played back
        self._music = None
        # Playing status of the music track
        self._musicPlaying = False
        # Logger
        from src.controller import GlobalServices
        self._logger = GlobalServices.getLogger()
        # List of sounds that are consistently playing
        self._soundlist = []
        # List of sound extensions
        self._soundexts = [".wav", ".ogg", ".mp3"]
        
    # Retrieves a Sound object from the list of
    # cached sound effects. If it doesn't exist,
    # it is created and stored in this list.
    # Parameter:
    #    key    :    The name of the sound to retrieve
    # Returns:
    #    The Sound object for that key, retrieved from
    #    the list of sounds. This method raises a pygame Error
    #    if none of the allowed extensions pointed to a valid
    #    file on the file system.
    def getSound(self, key):
        match = False
        if not key in self._sounds:
            # Go through the allowed extensions for sound files.
            for e in self._soundexts:
                sound_path = os.path.join(PATH_SOUNDS, "%s%s" % (key, e))
                try:
                    # Try loading this sound with this extension
                    if os.path.exists(sound_path):
                        self._sounds[key] = pygame.mixer.Sound(sound_path)
                        # If that worked, we have our match
                        match = True
                except pygame.error as e:
                    print("Cannot load '{}': {}".format(sound_path, e))
                    # If this sound couldn't be loaded with this extension,
                    # it's probably because that wasn't the right extension.
                    # Just keep on going and try other extensions
                    continue
            # If no match was found at all, raise an error
            # stating that this sound file doesn't exist at all.
            if not match:
                raise pygame.error()
        return self._sounds[key]
    
    # Loads the music for the given key into pygame's
    # music mixer. Due to the nature of that module,
    # this method does not return a Music object, but instead
    # buffers the new music into memory.
    # Parameter:
    #    key    :    Name of the music to load
    def loadMusic(self, key):
        match = False
        for e in self._soundexts:
            music_path = os.path.join(PATH_MUSIC, "%s%s" % (key, e))
            try:
                # Try loading this music with this extension
                if os.path.exists(music_path):
                    pygame.mixer.music.load(music_path)
                    match = True
            except pygame.error as e:
                print("Cannot load '{}': {}".format(music_path, e))
                # If this sound couldn't be loaded with this extension,
                # it's probably because that wasn't the right extension.
                # Just keep on going and try other extensions
                continue
        # If no match was found at all, raise an error
        # stating that this sound file doesn't exist at all.
        if not match:
            raise pygame.error()
    
    # Using pygame's mixer module, this method plays back the given sound
    # with all the provided properties.
    # Parameters:
    #    kind    :    Type constant SOUND or MUSIC
    #    key     :    The name of the audio file without extension
    #    volume  :    The desired volume for the sound
    #    loop    :    Numbers of repetition this sound should make.
    #                 (0 = no loop, -1 = infinite loop)
    #    fadein  :    Fade-in time for the sound to reach full volume
    #                 (only works for SOUND, though) in milliseconds
    def play(self, kind, key, volume=1.0, loop=0, fadein=0):
        if key is None:
            return        
        if kind == SOUND:
            try:
                sound = self.getSound(key)
                sound.set_volume(volume)
                sound.play(loop, 0, fadein)
                if loop == -1:
                    self._soundlist.append((SOUND, key, volume, loop, fadein))
            except pygame.error:
                self._logger.log("%s is not a valid sound key." % key)
        elif kind == MUSIC:
            if not self._music == key:
                if self._musicPlaying:
                    self.stop(MUSIC, 1000)
                self._music = key
                try:
                    self.loadMusic(key)
                    pygame.mixer.music.set_volume(volume)
                    pygame.mixer.music.play(loop)
                    if not (MUSIC, key) in self._soundlist:
                        self._soundlist.append((MUSIC, key, volume, loop, fadein))
                    self._musicPlaying = True
                except pygame.error as e:
                    self._logger.log("Music '{}' can't be loaded: {}".format(key, e))
                
    # Stops the given audio file and removes it from the list
    # of currently playing sound effects.
    # Paramaters:
    #    kind        :    Type constant SOUND or MUSIC
    #    fadeouttime :    Time in milliseconds that it should take the sound
    #                     to go completely silent
    #    key         :    The name of the sound to stop. If kind == "MUSIC",
    #                     this doesn't need to be passed in
    def stop(self, kind, fadeouttime=-1, key=""):
        if kind == SOUND:
            sound = self.getSound(key)
            if fadeouttime != -1:
                sound.fadeout(fadeouttime)
            else:
                sound.stop()
        elif kind == MUSIC and self._musicPlaying:
            # When stopping MUSIC, the key is usually not being passed in.
            # Because of this, grab the current BGM
            key = self.getCurrentBGM()
            if fadeouttime != -1:
                pygame.mixer.music.fadeout(fadeouttime)
            self._musicPlaying = False
        self.removeFromList(key)
            
    # Returns the state of the given sound as "playing" or not
    # Parameters:
    #    kind    :    Type constant SOUND or MUSIC
    #    key     :    The name of the sound without extension
    # Returns:
    #    True, if this sound is currently being played back, False otherwise
    def isPlaying(self, kind, key):
        for f in self._soundlist:
            if f[0] == SOUND and f[1] == key:
                return True
        return False
    
    # Removes the given sound for the key from the sound list
    # Parameter:
    #    key    :    The name of the sound without extension
    def removeFromList(self, key):
        for f in self._soundlist:
            if f[1] == key:
                self._soundlist.remove(f)
                
            
    # Retrieve the current background music played back through
    # pygame's mixer.music module.
    # Returns:
    #    The name of the currently playing music, or None if none is playing
    def getCurrentBGM(self):
        if self._musicPlaying:
            return self._music
        return None
        
    # Retrieve the list of currently playing sounds
    # Returns:
    #    The list of currently playing sounds
    def getPlayingSounds(self):
        return self._soundlist
        
    # Plays back a list of sounds at once
    # Parameter:
    #    l    :    List of sound files; an element in
    #              the list has to have specific properties
    #              described below
    def playList(self, l):
        for t in l:
            # t[0] : The kind of sound (SOUND, MUSIC)
            kind = t[0]
            # t[1] : The key of sound (file name)
            key = t[1]
            # t[2] : The volume (optional)
            try:
                vol = t[2]
            except IndexError:
                vol = VOLUME_SOUND
            # t[3] : Looping (optional)
            try:
                loop = t[3]
            except IndexError:
                loop = 0
            # t[4] : Fade-in in ms (optional)
            try:
                fadein = t[4]
            except IndexError:
                fadein = FADEIN_TIME
            self.play(kind, key, vol, loop, fadein)
            
    # Stops all playing sounds.
    def stopAll(self):
        for _ in range(len(self._soundlist)):
            item = self._soundlist[0]
            kind = item[0]
            key = item[1]
            self.stop(kind, 1000, key)