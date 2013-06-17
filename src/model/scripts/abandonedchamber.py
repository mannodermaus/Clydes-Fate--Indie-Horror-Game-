# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.controller import GlobalServices

def canvas(storage, obj, m):
    storage._go()
    tr = GlobalServices.getTextRenderer()
    if storage._playerInDistance(m.getPlayer().position, obj.rect):
        storage._toggleCutscene(True)
        tr.write("Do these symbols contain a message?", 3)
        storage._toggleCutscene(False)
        storage._setData('lefthallway_scare_enabled', True)
    storage._halt()