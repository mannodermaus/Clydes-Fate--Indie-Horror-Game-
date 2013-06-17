# CS 386
# Introduction to Game Design and Production
# Assignment 6: Final Game Project
# by Marcel Schnelle
# mschnelle@csu.fullerton.edu

from libs.tiledtmxloader.helperspygame import SpriteLayer
from src.constants import FADEOUT_TIME, VOLUME_SOUND
from src.controller import GlobalServices
from src.controller.AudioDevice import SOUND
from src.model.MapProperties import SCRIPT, TELEPORTSCRIPT, OBJECT, \
    TELEPORTOBJECT
import math

# Map.
# Wrapper class for a TMX TileMap describing a "room"
# of the game. This class also has several convenience methods
# to access different properties such as scripts, objects
# and layers. This class also implements collision detection for entities
# and itself, and is called by the Game object to e.g. check
# if the player can walk somewhere.
class Map:
    # Constructor.
    # Parameters:
    #    properties    :    Dictionary of Tiled properties
    #    cLayer        :    Collision layer
    #    hLayer        :    Sprite layer on which the hero is put
    #    clLayer       :    Sprite layer on which obtainable items are put
    #    sprite_layers :    All other sprite layers
    def __init__(self, properties, cLayer, hLayer, clLayer, sprite_layers):
        self.highlighted_object = None
        self.properties = properties
        self.renderer = None
        self.init_method = None
        self._cLayer = cLayer
        self._hLayer = hLayer
        self._clickablesLayer = clLayer
        self.sprite_layers = sprite_layers
        self.scripts = None
        self.objects = None
        self.player = None
        self.shadow = None
        self.entities = []
        self.overlays = []
        self._overlayqueue = []
        self.deleting = False
        self.ambient_sounds = []
        self.rendering_enabled = False
        
    # Sets the interactive objects and scripts to this map.
    # Parameters:
    #    scripts    :    List of Script objects
    #    objects    :    List of Clickable objects
    def setInteractives(self, scripts, objects):
        self.scripts = scripts
        self.objects = objects
        # Every object that has an image property is added
        # to the list of entities using addSprite()
        for o in self.objects:
            if o.image is not None:
                self.removeSprite(o)
                self.addSprite(o, SpriteLayer.Sprite(o.image, o.rect.copy()))
        
    # Sets the Player reference of this Map
    # Parameter:
    #    player    :    Player object
    def setPlayer(self, player):
        self.player = player
        
    # Gets the Player reference of this Map
    # Returns:
    #    The Player object
    def getPlayer(self):
        return self.player
    
    # Sets the Shadow reference of this Map
    # Parameter:
    #    shadow    :    Shadow object
    def setShadow(self, shadow):
        self.shadow = shadow
        
    # Gets the Shadow reference of this Map
    # Returns:
    #    The Shadow object
    def getShadow(self):
        return self.shadow
    
    # Insert an overlay into the list of overlays, using the queue
    # that is processed at the end of a render cycle.
    # Parameters:
    #   o   :   The overlay to be added to the list
    #   i   :   The index ("priority") of the overlay, basically determining the position of the overlay in the list.
    #           The lower the index, the earlier the overlay will be drawn to the screen.
    #           Default value is -1, meaning theat this overlay will be drawn on top of each already existing one
    def addOverlay(self, o, i=-1):
        self._overlayqueue.append((o, True, i))
        
    # Remove an overlay from the list of overlays,
    # using the queue that is processed at the end of a render cycle.
    # Parameter:
    #    o    :    The Overlay object to be removed
    def removeOverlay(self, overlay):
        self._overlayqueue.append((overlay, False))
        
    # Clears the list of overlays for this map
    def clearOverlays(self):
        for o in self.overlays:
            self.removeOverlay(o)
        
    # Switches two overlays of this Map for seamless transition between two Overlays.
    # Parameter:
    #    overlays    :    Two-item list of Overlay objects
    def switchOverlays(self, overlays):
        for item in overlays:
            o1 = item[0]
            o2 = item[1]
            self._overlayqueue.append((o2, True, -1))
            self._overlayqueue.append((o1, False))
        
    # Get an overlay from the list of overlays by name.
    # Parameter:
    #    name    :    The name of the overlay
    # Returns:
    #    The Overlay reference or None if there is no such Overlay
    def getOverlay(self, name):
        for o in self.overlays:
            if o.name == name:
                return o
        return None
    
    # Flushes the overlay queue, working through it
    # and adding or removing the Overlay objects to this Map.
    # At the end of this method, the queue will be empty.
    def flushOverlayQueue(self):
        # Check if an overlay has to be removed or added
        for o in self._overlayqueue:
            # True: Insert the overlay into the list
            if o[1]:
                if o[2] != -1:
                    self.overlays.insert(o[2], o[0])
                else:
                    self.overlays.append(o[0])
            # False: remove it from the list
            else:
                if o[0] in self.overlays:
                    self.overlays.remove(o[0])
            self._overlayqueue.remove(o)
        
    # Adds a sprite to the list of entities that are rendered
    # on top of the static sprite layers.
    # Parameters:
    #    o        :    The Clickable object to add the sprite for
    #    sprite   :    The Sprite object
    def addSprite(self, o, sprite):
        # Center the sprite first
        wi,hi = sprite.image.get_size()
        wr,hr = sprite.rect.size
        centered = sprite.rect.move((wr-wi)/2, (hr-hi)/2)
        sprite.rect = centered
        # Append the sprite to the list of entities and refresh the collision layer
        self.entities.append((o, sprite))
        self.refreshCollisionLayer()
        
    # Removes a sprite from the list of entities
    # Parameter:
    #    o              :    The Clickable object whose sprite is to be removed
    #    keepblocked    :    Boolean depicting if the object should be "deleted" in terms of collision. Default is False
    def removeSprite(self, o, keepblocked=False):
        found = None
        for e in self.entities:
            if o == e[0]:
                o.blocked = keepblocked
                found = e
                break
        self.refreshCollisionLayer()
        if found is not None:
            self.entities.remove(found)
                
    # Changes the sprite for the given Clickable object.
    # Used to update a Clickable sprite
    # Parameter:
    #    o          :    The Clickable object whose sprite is to be updated
    #    keepcol    :    Boolean depicting if the object should maintain its collision aspect
    def changeSprite(self, o, keepcol):
        self.removeSprite(o, keepcol)
        if o.image is not None:
            self.addSprite(o, SpriteLayer.Sprite(o.image, o.rect.copy()))
                
    # Adds an object to the list of scripts or objects,
    # depending on what was passed into the method.
    # Parameters:
    #    kind    :    Type constant for o
    #    o       :    Object
    def addObject(self, kind, o):
        if kind in [SCRIPT, TELEPORTSCRIPT]:
            self.scripts.append(o)
        elif kind in [OBJECT, TELEPORTOBJECT]:
            self.objects.append(o)
            if o.image is not None:
                self.addSprite(o, SpriteLayer.Sprite(o.image, o.rect.copy()))
    # Removes an object from either the list of scripts or objects,
    # depending on what was fed into the method. This method is harsher
    # than removeSprite() because it also removes the object's reference
    # in the respective list
    # Parameter:
    #    o              :    The Clickable or Script object to be removed
    #    keepblocked    :    Boolean if the collision area of this
    #                        object should remain blocked
    def removeObject(self, o, keepblocked = False):
        if type(o) == str:
            obj = self.getObjectByName(o)
            o = obj
        if o in self.objects:
            self.objects.remove(o)
        elif o in self.scripts:
            self.scripts.remove(o)
        self.removeSprite(o, keepblocked)
        self.highlighted_object = None
        
    # Gets an object by name from either the list of scripts or objects,
    # depending on what was fed into the method. Make sure that there
    # are no duplicate names on the map.
    # Parameter:
    #    name    :    The name of the Clickable or Script to be retrieved
    # Returns:
    #    This Clickable or Script object, or None if it couldn't be found.
    def getObjectByName(self, name):
        for i in self.objects:
            if i.name == name:
                return i
        for i in self.scripts:
            if i.name == name:
                return i
        return None
        
    # Adds an ambient sound to the list of ambient sounds on this map.
    # Parameters:
    #    kind    :    SOUND or MUSIC according to src.controller.AudioDevice
    #    key     :    Name of the sound or music file
    #    vol     :    Volume of the sound from 0.0 to 1.0
    #    loop    :    Loop or number of repetitions
    #    fadein  :    Time in milliseconds that this sound should fade in with
    def addAmbientSound(self, kind, key, vol, loop, fadein):
        item = (kind, [key, vol, loop, fadein])
        self.ambient_sounds.append(item)
        GlobalServices.getAudioDevice().play(kind, key, vol, loop, fadein)
        
    # Removes an ambient sound from the list of ambient sounds.
    # Parameter:
    #    key    :    The name of the sound to be removed.
    #                If multiple instances of this key exist,
    #                all are deleted.
    def removeAmbientSound(self, key):
        for s in self.ambient_sounds:
            if key == s[1][0]:
                GlobalServices.getAudioDevice().stop(s[0], FADEOUT_TIME, s[1][0])
                self.ambient_sounds.remove(s)
                
    # Starts all ambient sounds
    def startAmbientSounds(self):
        for s in self.ambient_sounds:
            kind = s[0]
            key = s[1][0]
            vol = s[1][1]
            loop = s[1][2]
            fadein = s[1][3]
            GlobalServices.getAudioDevice().play(kind, key, vol, loop, fadein)
        
    # Refreshes the collision layer. This is called when a sprite
    # of a Clickable object is added or removed. If this Clickable
    # has got the "blocked" flag set to True, the respective tiles
    # on the map are set to the sprite, allowing the collision detection
    # to detect these objects.
    def refreshCollisionLayer(self):
        for o in self.entities:
            r = o[0].rect
            x = int(r[0] // self._cLayer.tilewidth)
            y = int(r[1] // self._cLayer.tileheight)
            w = int(r.width // self._cLayer.tilewidth)
            h = int(r.height // self._cLayer.tileheight)
            if o[0].blocked:
                put = o[1]
            else:
                put = None
            for yo in range(h):
                for xo in range(w):
                    self._cLayer.content2D[y + yo][x + xo] = put
    
    # Render method for the map.
    # Parameters:
    #    renderer    :    The Renderer passed in from the GameView
    #    screen      :    The surface to render onto
    def renderMap(self, renderer, screen):
        if not self.rendering_enabled:
            return
        
        # Keep the renderer reference
        self.renderer = renderer
        # Update the camera
        renderer.set_camera_position(self.player.currentsprite.rect.centerx,\
                                     self.player.currentsprite.rect.centery)
        # Update player and shadow sprites
        self._hLayer.clear_sprites()
        if self.player.isVisible():
            self._hLayer.add_sprite(self.player.currentsprite)
        if self.shadow.isVisible():
            self._hLayer.add_sprite(self.shadow.currentsprite)
        # Update clickable sprites
        self._clickablesLayer.clear_sprites()
        for e in self.entities:
            self._clickablesLayer.add_sprite(e[1])
        # Render the map layers one by one
        for sprite_layer in self.sprite_layers:
            renderer.render_layer(screen, sprite_layer)
            
    # Render method for the map's overlays.
    # Parameters:
    #    renderer    :    Renderer passed in from the GameView
    #    screen      :    The surface to render onto
    #    active      :    Boolean depicting if the overlays should be rendered "active"
    def renderOverlays(self, renderer, screen, active=True):
        if not self.deleting:
            for overlay in self.overlays:
                overlay.render(screen, active)
        self.flushOverlayQueue()
            
    # Collision detection. Given an entity and a desired direction, this method computes
    # whether this movement is doable or not, or if it can be altered to be converted into
    # a valid direction.
    # Parameters:
    #   entity      :   The entity to be checked. Should provide position and currentsprite attributes
    #   direction   :   A two-entry list of the desired direction as defined in utilities.direction_to_string()
    # Returns:
    #   A two-entry list of a valid direction the entity can go in
    #   or None, if movement in that direction is not possible.
    def isWalkable(self, entity, direction):
        # Save some variables: Player position, entity's rect (for collision) and a vertical offset for checking
        pos = entity.position
        rect = entity.currentsprite.rect
        ox = 8
        
        # Check method: Returns true, if the tile belonging to the given coordinates rx,ry in this direction is walkable.
        def check(direction, rx, ry):
            tile_x = int(rx // self._cLayer.tilewidth) + direction[0]
            tile_y = int((pos[1] + ry)/2 // self._cLayer.tileheight) + direction[1]
            tile = self._cLayer.content2D[tile_y][tile_x]
            if tile is None or not tile.rect.colliderect(rect):
                return True
            return False
        
        # Horizontal or vertical movement: If the direction vector has only one component (e.g. [1,0] for "to the right"),
        # we know that this is a horizontal or vertical movement request. Check this using the vector's sum with math.fabs
        if int(math.fabs(direction[0]) + math.fabs(direction[1])) == 1:
            # Vertical movement needs extra checking (because the sprite's "shoulders" may overlap with a wall, but
            # the entity's point of reference is actually on a walkable tile. This behaviour is unwanted, therefore
            # we shift the point of reference to the left and to the right checking again!)
            if (direction[0] == 0):
                if (check(direction, rect.center[0] - ox, rect.center[1]) \
                and check(direction, rect.center[0] + ox, rect.center[1])):
                    return direction
            # For horizontal movement, just check in front of the hero, that's fine. (The rect objects are perfectly aligned)
            elif check(direction, rect.center[0], rect.center[1]):
                return direction
                
        # Diagonal movement: We need to check other adjacent tiles as well!
        else:
            # Result variable where the resulting direction is stored in
            result = None
            # Define other tiles to be checked (the ones next to the entity in each dimension)
            positions = ((0, direction[1]), (direction[0], 0))
            # Test diagonal first!
            if check(direction, rect.center[0], rect.center[1]):
                # Diagonal tile is walkable!
                result = direction
                # Test horizontal and vertical as well.
                # If any of these don't work, xor the result and return them at last.
                # With this xor technique, we manage to get the entity to "slide" along a wall
                # in a valid direction and not get stuck immediately.
                for p in positions:
                    if not check(p, rect.center[0], rect.center[1]):
                        result = (result[0] ^ p[0], result[1] ^ p[1])  
            else:
                # Diagonal tile is not walkable: Check if the horizontal or vertical tiles are.
                # If yes, walk that direction!
                if (check(positions[0], rect.center[0], rect.center[1])  \
                and not check(positions[1], rect.center[0], rect.center[1])):
                    result = positions[0]
                elif (not check(positions[0], rect.center[0], rect.center[1]) \
                and check(positions[1], rect.center[0], rect.center[1])):
                    result = positions[1]
            return result
        # Should be unreachable
        return None
            
    # Checks the list of objects on the Map for potential collision
    # with the current mouse position. This is invoked by the Game
    # object if it received a MouseMotionEvent. This method
    # translates the mouse position into world coordinates and
    # checks if it collides with any Clickable's rectangle.
    # Parameter:
    #    mouseevent    :    The mouse event sent by the InputController,
    #                       which can be asked for mouse position
    # Returns:
    #    The reference to the highlighted object if a collision occured,
    #    None otherwise.
    def checkForObjectHighlight(self, mouseevent):
        if self.renderer is not None:
            # Translate into world coordinates
            mpos = mouseevent.pos
            wcoords = self.renderer.get_world_pos(self._cLayer, mpos[0], mpos[1])
            # Check for collision with Clickable objects
            for obj in self.objects:
                if (obj.rect.collidepoint(wcoords)):
                    # If the found object is not already the highlighted one,
                    # play a "hover" sound effect and return the object.
                    # (This way, the sound only plays once instead of infinitely)
                    if obj is not self.highlighted_object:
                        GlobalServices.getAudioDevice().play(SOUND, "object_hover", VOLUME_SOUND)
                        self.highlighted_object = obj
                    return obj
        self.highlighted_object = None
        return None
        
    # Checks the list of scripts if any of its contents have been triggered
    # by the player.
    # Parameter:
    #    player    :    The player object
    # Returns:
    #    Reference to the Script object that collides with the player's position,
    #    or None if no script collides with the player's position
    def checkForScriptToggle(self, player):
        for script in self.scripts:
            if (script.rect.collidepoint(player.position)):
                return script
        return None
                
    # toString method to represent the Map object via the logger
    # Returns:
    #    Convenient string representation of the Map object
    def __repr__(self):
        return "(src.model.Map) '%s' (File: %s)" % (self.properties['name'], self.properties['file_name'])

    # equals method to compare two Map objects
    # Parameter:
    #    other    :    Other object to compare it tp
    # Returns:
    #    True, if the file names of both objects are equal,
    #    False otherwise.
    def __eq__(self, other):
        if other is None:
            return False
        elif isinstance(other, Map):
            return self.properties['file_name'] == other.properties['file_name']
        else:
            return False