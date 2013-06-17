# scripts.
# In this package, the interaction methods for all objects in the game
# are stored, separated in different modules representing a Map.
# The parameters vary in relation to the kind of object interaction
# that takes place in there.
# "Clickable" objects that the player can click on using his mouse:
#    storage    :    The ObjectStorage or ScriptStorage object
#    obj        :    Object that was clicked on
#    m          :    Map that the object belongs to
# "TeleportClickable" objects that are used for "conditional teleports",
# e.g. a locked door that can be opened using a key, etc. These
# methods also have a return value! If a TeleportClickable method
# returns True, the map transition worked, if not, it didn't:
#    storage    :    The ObjectStorage or ScriptStorage object
#    m          :    Map that the object belongs to
#    obj        :    Object that was clicked on
# Init methods that are the first thing to be executed upon entering a Map:
#    storage    :    The ObjectStorage or ScriptStorage object
#    m          :    Map whose init method this is

# Get persistent value:
#     storage._getData(key)
# Set persistent value:
#     storage._setData(key, value)
# Add an item:
#     m.getPlayer().inventory.add(ItemFactory.create(key, qty))
# Check for an item:
#    if m.getPlayer().inventory.containsName(key, [qty])
# Remove an item:
#    m.getPlayer().inventory.remove(key)
#    OR:
#    item = m.getPlayer().inventory.get(key)
#    item.subQty(qty)
# One-time objects that delete themselves
#     m.removeObject(obj)
#     GlobalServices.getEventManager().post(ObjectHighlightedEvent(None))
# Look towards an object
#     storage._faceObject(m.getPlayer(), obj)
# Add object to map:
#     add_to_map(get_savegame(), OBJECT, mapname, name, rect, callback, imagefile)
# Remove object from map:
#     remove_from_map(get_savegame(), SCRIPT, mapname, name)
# Change an object's image:
#     obj.changeImage(newimagefile)
# Distance check:
#     if storage._playerInDistance(m.getPlayer().position, obj.rect)
# Get global property:
#     get_property(key)
# Set global property:
#     set_property(key, value)