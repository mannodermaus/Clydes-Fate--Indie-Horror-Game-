# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

import os
import pygame

# constants.
# This module provides global properties of every kind
# and therefore out-sources these values to their own module
# (avoiding system parameters and settings being scattered throughout
# actual source code).

# ===========================================
# Screen constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN_CENTER = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
# ===========================================

# ===========================================
# Name of the game and system constants
APP_NAME = "Clyde's Fate"
FPS = 60

POSITION_BOTTOM_SCREEN = (0, SCREEN_HEIGHT - 55)

DEFAULT_INTERACTION_DISTANCE = 80
FADEIN_TIME = 4000
FADEOUT_TIME = 3000

SOUND_STEP_INTERVAL = 300

VOLUME_MUSIC = 0.4
VOLUME_SOUND_AMBIENT = 0.3
VOLUME_SOUND = 0.8
# ===========================================

# ===========================================
# Image sizes
THUMBNAIL_SIZE = (90, 67)
# ===========================================

# ===========================================
# Asset file paths
_PATH_ASSETS = "assets"
PATH_GRAPHICS = os.path.join(_PATH_ASSETS, "graphics")
PATH_GRAPHICS_SPRITES = os.path.join(PATH_GRAPHICS, "sprites")
PATH_GRAPHICS_SPRITES_ITEMS = os.path.join(PATH_GRAPHICS_SPRITES, "items")
PATH_GRAPHICS_TILES = os.path.join(PATH_GRAPHICS, "tiles")
PATH_MAPS = os.path.join(_PATH_ASSETS, "maps")
PATH_MUSIC = os.path.join(_PATH_ASSETS, "music")
PATH_SOUNDS = os.path.join(_PATH_ASSETS, "sounds")
PATH_SAVES = "saves"
# ===========================================

# ===========================================
# Globally accessible properties
PLAYER_MOVEMENT_ENABLED = "player_movement_enabled"
MOUSE_HIGHLIGHT_ENABLED = "mouse_highlighting_enabled"
INVENTORY_OPEN_ENABLED = "inventory_open_enabled"
GAME_MENU_OPEN_ENABLED = "game_menu_open_enabled"
SAVE_ENABLED = "save_enabled"
FLASHLIGHT_MOVEMENT_ENABLED = "flashlight_movement_enabled"
CURRENTLY_PAUSING_FOR_CLICK = "currently_pausing_for_click"
CUTSCENE_RUNNING = "cutscene_running"
GLOBAL_PROPERTIES = {PLAYER_MOVEMENT_ENABLED:True,\
                     MOUSE_HIGHLIGHT_ENABLED:True,\
                     INVENTORY_OPEN_ENABLED:True,\
                     GAME_MENU_OPEN_ENABLED:True,\
                     SAVE_ENABLED:True,\
                     FLASHLIGHT_MOVEMENT_ENABLED:True,\
                     CURRENTLY_PAUSING_FOR_CLICK:False,\
                     CUTSCENE_RUNNING:False}
# ===========================================

# ===========================================
# Persistence
CURRENT_SHELF_FILENAME = [None, None]
CURRENT_SHELF = [{}]
SHELF_PERSISTENT_KEYS = ['player_position', 'current_map', 'player_inventory', 'current_sounds']

SHELF_KEY_PLAYERPOSITION = "player_position"
SHELF_KEY_CURRENTMAP = "current_map"
SHELF_KEY_CURRENTBGM = "current_bgm"
SHELF_KEYS = [SHELF_KEY_PLAYERPOSITION, SHELF_KEY_CURRENTMAP, SHELF_KEY_CURRENTBGM]
# ===========================================

# ===========================================
# Globally applicable visual overlays
GLOBAL_OVERLAYS = []
# ===========================================

# ===========================================
# Game states
STATE_MAIN_MENU = "game_state_main_menu"
STATE_GAME_MAP_LOADING = "game_state_map_loading"
STATE_GAME_RUNNING = "game_state_game_running"
STATE_GAME_PAUSED = "game_state_game_paused"
STATE_GAME_INVENTORY = "game_state_game_inventory"
STATE_GAME_MENU = "game_state_game_menu"
# ===========================================

# ===========================================
# Entity property lists
ENTITY_PROPERTIES = "health speed sprites".split()
ENTITY_ANIMATIONS = "walk-left walk-right walk-up walk-down".split()
# ===========================================

# ===========================================
# Lists of different kinds of Keys
KEYS_MOVEMENT   = [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s]
KEYS_CHARACTERS = [pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f,\
                   pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, \
                   pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r, \
                   pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, \
                   pygame.K_y, pygame.K_z, pygame.K_SPACE]
KEYS_NUMBERS    = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, \
                   pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
KEYS_DELETE     = [pygame.K_BACKSPACE, pygame.K_DELETE]
# ===========================================

# ===========================================
# Colors and styles
COLOR_HIGHLIGHTED_OBJECT = (192, 188, 24, 255)
COLOR_TEXT = (180, 194, 197, 255)
COLOR_TEXT_HIGHLIGHTED = (252, 30, 55, 255)
COLOR_BLACK = (0,0,0,255)
COLOR_GOT_ITEM = (150, 147, 10, 255)
COLOR_OBJECTIVE = (40, 155, 100, 255)
COLOR_RED = (255,0,0)

FONTSTYLE_NORMAL = 0
FONTSTYLE_CAPTION = 1
FONTSTYLE_LOGO = 2
# ===========================================

# ===========================================
# Main menu item indices
MAIN_MENU_ITEM_BEGIN = 0
MAIN_MENU_ITEM_LOAD = 1
MAIN_MENU_ITEM_QUIT = 2
MAIN_MENU_ITEM_SETTINGS = 3
# ===========================================


# ===========================================    
# Constants for directional determination
DIRS = "left left-up up up-right right right-down down down-left".split()
DIRDICT = {}
DIRDICT[DIRS[0]] = [-2.8, -2.9, -3.0, -3.1,  3.1,  3.0,  2.9,  2.8]
DIRDICT[DIRS[1]] = [-2.7, -2.6, -2.5, -2.4, -2.3, -2.2, -2.1, -2.0]
DIRDICT[DIRS[2]] = [-1.9, -1.8, -1.7, -1.6, -1.5, -1.4, -1.3, -1.2]
DIRDICT[DIRS[3]] = [-1.1, -1.0, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4]
DIRDICT[DIRS[4]] = [-0.3, -0.2, -0.1,  0.0,  0.1,  0.2,  0.3,  0.4]
DIRDICT[DIRS[5]] = [ 0.5,  0.6,  0.7,  0.8,  0.9,  1.0,  1.1,  1.2]
DIRDICT[DIRS[6]] = [ 1.3,  1.4,  1.5,  1.6,  1.7,  1.8,  1.9,  2.0]
DIRDICT[DIRS[7]] = [ 2.1,  2.2,  2.3,  2.4,  2.5,  2.6,  2.7,  2.8]
# ===========================================
    
# ===========================================
# Inventory constants
INVENTORY_MAX_ITEMS = 8
INVENTORY_ITEM_DEFAULT = "Default"
INVENTORY_ITEM_OLD_KEY = "Old Key"
INVENTORY_ITEM_KNIFE = "Knife"
INVENTORY_ITEM_STUDY_KEY = "Study Key"
INVENTORY_ITEM_STORAGE_KEY = "Storage Key"
INVENTORY_ITEM_ENTRANCE_NOTE = "Entrance Note"
INVENTORY_ITEM_FLASHLIGHT = "Flashlight"
INVENTORY_ITEM_ATRIUM_KEY = "Atrium Key"
INVENTORY_ITEM_LIBRARY_KEY = "Library Key"
INVENTORY_ITEM_LADDER = "Ladder"

__d__ = lambda x: os.path.join(PATH_GRAPHICS_SPRITES_ITEMS, x)

INVENTORY_ITEMS_DICT = {INVENTORY_ITEM_DEFAULT      :   {"desc":"An indistinguishable object of some sorts.",\
                                                         "image":__d__("default.png")},\
                        INVENTORY_ITEM_OLD_KEY      :   {"desc":"A rusty key that smells like fish.",\
                                                         "image":__d__("old_key.png")},\
                        INVENTORY_ITEM_KNIFE        :   {"desc":"A stained iron knife with a crooked blade.",\
                                                         "image":__d__("datknife.png")},\
                        INVENTORY_ITEM_STUDY_KEY    :   {"desc":"A sophisticated key with a blue sapphire emblem. It belongs to the study room upstairs.",\
                                                         "image":__d__("studykey.png")},\
                        INVENTORY_ITEM_STORAGE_KEY  :   {"desc":"A rusty iron key with water stains. The name tag reads 'STORAGE'.",\
                                                         "image":__d__("storagekey.png")},\
                        INVENTORY_ITEM_ENTRANCE_NOTE:   {"desc":"A note from my buddies who have forsaken me.",\
                                                         "image":__d__("note.png")},\
                        INVENTORY_ITEM_FLASHLIGHT   :   {"desc":"My handy flashlight.",\
                                                         "image":__d__("flashlight.png")},\
                        INVENTORY_ITEM_ATRIUM_KEY   :   {"desc":"A pale white key with a little ruby. 'ATRIUM' is engraved on it.",\
                                                         "image":__d__("atriumkey.png")},\
                        INVENTORY_ITEM_LIBRARY_KEY  :   {"desc":"A heavy key, used to unlock a solid wood door.",\
                                                         "image":__d__("librarykey.png")},\
                        INVENTORY_ITEM_LADDER       :   {"desc":"An oak ladder, about 6 feet tall.",\
                                                         "image":__d__("ladder.png")}
                        }
# ===========================================