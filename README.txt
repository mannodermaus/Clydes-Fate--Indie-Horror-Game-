# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

This is my solution to assignment 6 in Prof. Shafae's class
"Introduction to Game Design and Production". I have implemented
a 2D tile-based horror game titled "Clyde's Fate" using PyGame.
The application includes all necessary libraries: Pyganim is
a helper library for convenient sprite animation access, Pytmxloader
is a helper library for TMX map file parsing. Both libraries have
been modified to be applicable to the game.

Overview and technical foundation:
- Model/View/Controller architecture
- Main patterns: Observer, Mediator, Singleton
- Collision detection
- Script and Interaction engines
- Audio service
- Sprite animation
- Persistent progress export using shelve
- Story-driven puzzle and game experience

Run:
From the command prompt, enter 'python run.py'.
There are no additional arguments.

Controls:
W,A,S,D - Move Clyde around
TAB - Open/Close inventory
F5 - Save progress
ALT+RETURN - Switch between Windowed/Fullscreen display
LMOUSE - Interact with highlighted objects

Known bugs:
- Display switching during script sequences or interactions may cause the game to continue running

References:
- http://inventwithpython.com/pyganim/
  Pyganim homepage
  
- http://code.google.com/p/pytmxloader/
  Pytmxloader homepage