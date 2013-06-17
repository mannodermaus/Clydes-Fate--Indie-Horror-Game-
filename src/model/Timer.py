# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

import threading
import pygame

# Timer.
# Helper class that implements a custom killable timer.
# This is most prominently used by src.view.TextRenderer.Text objects
# that can kill themselves after the timer has run out
class Timer(threading.Thread):
    # Constructor
    # Parameters:
    #    time    :    Time in milliseconds that the timer should run
    #    killfunc:    Kill function that can be passed in optionally.
    #                 This is a way to provide another condition that
    #                 may kill the timer early. Killfunc should be
    #                 a method that returns a boolean value depending
    #                 on whatever condition. Default is a method
    #                 that always returns False
    #    callback:    Callback function that is called when
    #                 the timer is done
    def __init__(self, time, killfunc = None, callback = lambda: 0):
        threading.Thread.__init__(self)
        if killfunc is None:
            killfunc = lambda: False
        self.timegoal = time
        self.timestep = 10
        self.i = 0
        self.killed = False
        self.killfunc = killfunc
        self.callback = callback
        
    # Runs the timer
    def run(self):
        while not self.killed and self.i < self.timegoal:
            # Kill function check:
            if self.killfunc():
                self.killed = True
                break
            pygame.time.wait(self.timestep)
            self.i += self.timestep
        self.callback()
