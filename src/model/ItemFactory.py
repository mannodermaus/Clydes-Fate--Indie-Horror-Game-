# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.model.Inventory import InventoryItem
from src.constants import INVENTORY_ITEMS_DICT

# ItemFactory.
# This is a little helper class that is able to create an
# InventoryItem instance using a provided name and quantity.
# Therefore, there is no need to get global properties involved.
# Instead, just call ItemFactory.create() and retrieve the InventoryItem.

# Creates an InventoryItem
# Parameters:
#    name    :    String name of the item to create using
#                 the desired constant for the item in src.constants
#                 (starting with INVENTORY_ITEM_)
#    qty     :    Desired quantity with which the item should be initialized
# Returns:
#    The constructed InventoryItem, ready to use
def create(name, qty):
    data = INVENTORY_ITEMS_DICT[name]
    item = InventoryItem(name, data["desc"], data["image"], qty)
    return item