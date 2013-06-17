# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.interfaces import Listener, LoggerInterface, Event

# Logger.
# This is an implementation of the LoggerInterface
# that uses the main console as the output device for logged messages.
# Implements:
#    LoggerInterface
#    Listener
class Logger(Listener, LoggerInterface):
    # Constructor
    # Parameter:
    #    evManager    :    EventManager
    def __init__(self, evManager):
        Listener.__init__(self, evManager)
        # Initialize the filter using "every" Event
        self.filter = [Event]
        
    # Applies a new filter to this logger.
    # Parameter:
    #    eventtypes    :    List of types (subclasses of Event)
    #                       whose messages are being logged
    def setFilter(self, eventtypes):
        self.filter = eventtypes
        
    # Logs a message.
    # Parameter:
    #    message    :    The message to be logged
    def log(self, message):
        print("LOGGER: %s" % message)
        
    # Listener method implementation invoked
    # by the EventManager whenever it posts an event
    # Parameter:
    #    event    :    Event posted by the EventManager
    def notify(self, event):
        # If the event's type is part of the current filter, log it
        for the_type in self.filter:
            if isinstance(event, the_type):
                print("LOGGER: Identified %s" % (event.__class__.__name__))
                if event.object is not None:
                    print("        Object: " + str(event.object))
                break