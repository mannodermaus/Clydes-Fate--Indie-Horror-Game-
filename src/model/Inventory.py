# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from src.constants import INVENTORY_MAX_ITEMS, COLOR_TEXT, INVENTORY_ITEMS_DICT, \
    INVENTORY_ITEM_DEFAULT, COLOR_BLACK, FONTSTYLE_CAPTION, FONTSTYLE_NORMAL, PATH_GRAPHICS_SPRITES
from src.controller import GlobalServices
import math
import os
import pygame

# Inventory.
# Container class for InventoryItem objects that make up the stuff
# that the player keeps around in his inventory.
# This class provides convenient access to its items;
# it will also be pickled/unpickled upon save/load.
class Inventory:
    # Constructor
    def __init__(self):
        self.items = []
        # Load background image for the inventory
        self.loadBG()
        
    # Add an item to the inventory. This method detects if the given item already
    # exists in the player's possession: In this case, it does not add another Item
    # instance, but instead adds the quantity of the item to be added to the existing one!
    # Thus, 4 gold coins would not take up four inventory slots
    # Parameter:
    #   item    :   The InventoryItem to be added
    # Raises:
    #   InventoryFullException when the amount of items in the inventory has already
    #   reached INVENTORY_MAX_ITEMS (see src.constants)
    def add(self, item):
        if INVENTORY_MAX_ITEMS - len(self.items) == 0:
            raise InventoryFullException()
        if not self.containsName(item.name):
            # If this item is not already in the inventory, add it
            self.items.append(item)
            item.setInventory(self)
        else:
            # If it is already in there, take the quantity to be added and
            # add it to the existing Item object
            self.items[self._index(item.name)].addQty(item.qty)
    
    # Checks if a given item name belongs to an Item object in the inventory.
    # Parameter:
    #   name    :   The name to be used for checking
    #   qty     :   An optional minimum quantity that has to be held in possession
    #               for this method to return True. Default is 1
    # Returns:
    #   True, if an item is called the same as "name", False otherwise
    def containsName(self, name, qty=1):
        for i in self.items:
            if name == i.name:
                return i.qty >= qty
        return False
        
    # Internal method to retrieve the index of an item in the inventory by name
    # Parameter:
    #   name    :   The name to be looked for
    # Returns:
    #   The index inside of self.items corresponding to that item. This method
    #   returns -1 if it could not find the item at all, so it has first to be guaranteed
    #   that the desired item exists somewhere! If not, this method may cause trouble.
    def _index(self, name):
        for i in range(len(self.items)):
            item = self.items[i]
            if item.name == name:
                return i
        return -1
    
    # Removes an item completely from the inventory.
    # Parameter:
    #   item    :   The item to be removed
    def remove(self, item):
        if item in self.items:
            self.items.remove(item)
            
    # Retrieves an Item object from a given name.
    # Parameter:
    #   name    :   The name to be looked for
    # Returns:
    #   The Item instance of the associated Item object, or None if it couldn't be found
    def get(self, name):
        for i in self.items:
            if i.name == name:
                return i
        return None
        
    # Render method for drawing the inventory's contents to the given surface
    # Parameter:
    #   screen  :   The surface to draw onto
    def render(self, screen):
        # Draw a temp text
        GlobalServices.getTextRenderer().write("Inventory", 0, COLOR_TEXT,\
                                    (100,100), FONTSTYLE_CAPTION)
        # Draw background image
        screen.blit(self.bg, (0,0))
        # Order every item to draw itself properly on a 4x2 grid
        l = ((x,y) for y in range(2) for x in range(4))
        for i in self.items:
            i.render(screen, next(l))
        
    # Check if the given point collides with any item in the inventory.
    # Parameter:
    #   pos :   The position tuple to be checked against
    # Returns:
    #   The highlighted item, or None
    def checkForItemHighlight(self, pos):
        pos = pos.pos
        for i in self.items:
            if i.rect.collidepoint(pos):
                return i
        return None
    
    def loadBG(self):
        self.bg = pygame.image.load(os.path.join(PATH_GRAPHICS_SPRITES,\
                  "inventory_bg.png")).convert_alpha()
                  
    # String representation of an Inventory object
    # Returns:
    #   ...what do you think?
    def __repr__(self):
        return "(src.model.Inventory) INVENTORY contents: %s" % self.items
    
    # Pickle method
    # Returns:
    #    Modified dict of this object's attributes
    def __getstate__(self):
        d = self.__dict__.copy()
        # Delete background image reference
        del d["bg"]
        return d
    
    # Unpickle method
    # Parameter:
    #    d    :    The dict to be applied
    def __setstate__(self, d):
        # Update dict attributes
        self.__dict__.update(d)
        # Re-load bg image
        self.loadBG()
        
# InventoryItem.
# An instance of this class represents an item inside of the player's inventory.
# It is prepared to be pickled.
class InventoryItem:
    # Constructor
    # Parameters:
    #   name    :   String name of the item. Stored in src.constants (ITEM_*[0])
    #   desc    :   String description of the item. Stored in src.constants (ITEM_*[1])
    #   picname :   File name of the item's picture
    #   picsurf :   Surface of the item's picture
    #   qty     :   Quantity of the item (default: 1)
    def __init__(self, name, desc, picname, qty=1):
        self.name = name
        self.desc = desc
        self.picname = picname
        self.pic_surf = None
        self.dim = 48
        self.position = (0,0)
        self.updatePicSurf()
        self.updateRect()
        self.qty = qty
        self.qty_surf = None
        self.inventory = None
        self.updateQtySurf()
        
    # Updates the surface for the icon of this inventory item
    def updatePicSurf(self):
        try:
            self.pic_surf = pygame.image.load(self.picname).convert_alpha()
        except pygame.error:
            default = INVENTORY_ITEMS_DICT[INVENTORY_ITEM_DEFAULT]["image"]
            self.pic_surf = pygame.image.load(default).convert_alpha()
        # Set the dimension of the image and the rect
        self.dim = self.pic_surf.get_rect().width
        
    # Updates the surface for the quantify of this inventory item
    def updateQtySurf(self):
        self.qty_surf = GlobalServices.getTextRenderer().writeAsSurface( \
                        self.qty, COLOR_BLACK, FONTSTYLE_NORMAL)
        
    # Updates the Rect area of this inventory item
    def updateRect(self):
        self.rect  = pygame.Rect(self.position, (self.dim, self.dim))
        
    # Internal operator method that changes the quantity
    # of this item. Does not need to be called
    # by anybody but other methods of this class. Instead,
    # call addQty() or subQty()
    # Parameter:
    #    a    :    Amount to be added or subtracted from this item's quantity
    def _op(self, a):
        self.qty = int(self.qty + a)
        self.updateQtySurf()
    
    # Adds an integer amount to the quantity of this item.
    # Parameter:
    #    qty    :    Amount to be added to this item
    def addQty(self, qty):
        qty = math.fabs(qty)
        self._op(qty)
        
    # Subtract an integer amount from the quantity of this item.
    # This method automatically removes this item from the inventory
    # if the quantity to be subtracted reduces the amount to zero,
    # ergo "the item is gone".
    # Parameter:
    #    qty    :    Amount to be subtracted from this item
    def subQty(self, qty):
        qty = -qty if qty > 0 else qty
        self._op(qty)
        # Removes the item in case of reducing the amount to zero
        if self.qty <= 0 and self.inventory is not None:
            self.inventory.remove(self)
            
    # Sets the inventory reference of this item
    # Parameter:
    #    inv    :    Inventory object
    def setInventory(self, inv):
        self.inventory = inv
        
    # Renders a visual representation of this item.
    # Parameters:
    #    surf    :    Surface to blit the item onto
    #    i       :    Index of this item (used for positioning)
    def render(self, surf, i):
        self.position = (200 + i[0] * self.dim, 200 + i[1] * self.dim)
        self.updateRect()
        # Blit the surface
        surf.blit(self.pic_surf, self.position)
        # Blit the quantity on top
        surf.blit(self.qty_surf, self.position)
        
    # String representation of an inventory item.
    # Returns:
    #    String representation of this item
    def __repr__(self):
        return "(%d) '%s'" % (self.qty, self.name)
        
    # Pickle method
    # Returns:
    #    Modified dict of attributes for this item
    def __getstate__(self):
        dd = self.__dict__.copy()
        # Remove pygame Surface objects
        del dd["qty_surf"]
        del dd["pic_surf"]
        # Return the adjusted dict
        return dd
        
    # Unpickle method
    # Parameter:
    #    dd    :    Dict to be applied to the object
    def __setstate__(self, dd):
        self.__dict__.update(dd)
        # Create the Surface objects again
        self.updatePicSurf()
        self.updateQtySurf()
        
# InventoryFullException.
# Raised by Inventory.add() when the maximum capacity of items
# has been reached and someone tries to add another item
class InventoryFullException(Exception):
    pass