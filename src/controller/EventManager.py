# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.controller import GlobalServices
from src.interfaces import Event
from weakref import WeakKeyDictionary

# Static instance
_instance = None

# EventManager.
# The central hub of the application's Model-View-Controller structure.
# The event manager manages a number of listeners to which he posts
# incoming events. On the other hand, every listener may produce those
# incoming events that are posted to the event manager, making it a
# broadcaster of messages and establisher of communication.
class EventManager:
    # Constructor
    def __init__(self):
        # Set-up the listeners as a Weak Key Dictionary
        # (therefore, unregistering becomes easier)
        self.listeners = WeakKeyDictionary()
        global _instance
        _instance = self
        
    # Register method for a listener.
    # Parameter:
    #   listener    :   Any object that wants to be notified of events.
    #                   If it does not provide a notify() method, therefore
    #                   not implementing the Listener interface, the event manager won't add it.
    def register(self, listener):
        # Make sure that the listener to be registered actually has a notify method
        if hasattr(listener, 'notify'):
            self.listeners[listener] = 1
    
    # Unregister method for a listener.
    # Parameter:
    #   listener    :   The listener object to be removed from the list of listeners.
    def unregister(self, listener):
        if listener in self.listeners.keys():
            del self.listeners[listener]
            
    # Post an event to all listeners known to the event manager
    # Parameter:
    #   event   :   The event to be posted.
    def post(self, event):
        # Check if it is an event or a subclass thereof, otherwise, don't post it
        if isinstance(event, Event):
            for listener in self.listeners.keys():
                listener.notify(event)
        else:
            GlobalServices.getLogger().log("Can't post this object: %s" % event)