"""
Utilities for creating and navigating Blender collection/object hierarchies
expressed as filesystem-like paths (e.g. "SceneName/CollectionA/CollectionB").
"""

import logging
from pathlib import Path
from typing import Any, List, Union

import bpy
from bpy.types import Collection, Object, Scene

logger = logging.getLogger(__name__)


def create_hierarchy(path: str | Path) -> Collection:
    """
    Create a collection hierarchy matching the given path, creating any
    missing collections along the way. Returns the deepest (last) collection.

    The first part of the path must always be the name of an existing scene.
    """
    path = Path(path)

    scene_name = path.parts[0]
    if scene_name not in bpy.data.scenes:
        raise ValueError(f"Scene not found: {scene_name}")
    scene = bpy.data.scenes[scene_name]

    current_collection = scene.collection  # start at the scene's root collection
    collection_names = path.parts[1:]

    for depth, collection_name in enumerate(collection_names):
        existing_children = current_collection.children
        if collection_name in existing_children:
            current_collection = existing_children[collection_name]
            continue

        # A collection with this name may exist, but attached elsewhere in
        # the hierarchy. Since collection names are globally unique in
        # Blender, that would conflict with creating it here.
        if collection_name in bpy.data.collections:
            full_path = "/".join(collection_names[: depth + 1])
            raise ValueError(
                f"Cannot create collection '{collection_name}': it already exists elsewhere (expected at '{full_path}')"
            )

        logger.info("Creating collection: %s", "/".join(collection_names[: depth + 1]))
        new_collection = bpy.data.collections.new(collection_name)
        current_collection.children.link(new_collection)
        current_collection = new_collection

    return current_collection


def get_hierarchy_as_objects(obj: Any) -> List[Union[Scene, Collection, Object]]:
    if isinstance(obj, Collection):
        chain: List[Union[Scene, Collection, Object]] = [obj]
    else:
        parent_collection = obj.users_collection[0]
        chain = [parent_collection, obj]

    scene_collections = {scene.collection: scene for scene in bpy.data.scenes}
    all_collections = list(bpy.data.collections) + list(scene_collections.keys())

    # Walk upward, inserting parents, until we reach a scene's root collection.
    while chain[0] not in scene_collections:
        parent = next((col for col in all_collections if chain[0] in list(col.children)), None)
        if parent is None:
            raise ValueError(
                f"Could not find a parent for '{chain[0].name}' : "
                "hierarchy is broken or object is not linked to a scene."
            )
        chain.insert(0, parent)

    # Replace the root collection with its owning scene.
    chain[0] = scene_collections[chain[0]]
    return chain


def get_hierarchy_as_path(obj: Any) -> Path:
    chain = get_hierarchy_as_objects(obj)
    return _parts_to_path(chain)


def _parts_to_path(parts: List[Union[Scene, Collection, Object]]) -> Path:
    """Convert a list of hierarchy parts into a slash-separated Path."""
    return Path("/".join(part.name for part in parts))


def get_from_hierarchy(path: Union[str, Path]) -> Union[Collection, Object, Scene]:
    """Return the collection or object that exactly matches the given path."""
    path = Path(path)

    scene = bpy.data.scenes[path.parts[0]]
    if len(path.parts) == 1:
        return scene

    # All parts between the scene and the last one are collections.
    intermediate_names = path.parts[1:-1]
    collections = [scene.collection] + [bpy.data.collections[name] for name in intermediate_names]

    for parent, child in zip(collections, collections[1:]):
        if child not in list(parent.children):
            raise ValueError(f"Collection '{child.name}' is not a child of '{parent.name}'")

    item_name = path.parts[-1]
    parent_collection = collections[-1]

    collection_item = bpy.data.collections.get(item_name)
    if collection_item is not None:
        if collection_item not in list(parent_collection.children):
            raise ValueError(f"Collection '{item_name}' is not a child of '{parent_collection.name}'")
        return collection_item

    object_item = bpy.data.objects.get(item_name)
    if object_item is not None:
        if object_item not in list(parent_collection.objects):
            raise ValueError(f"Object '{item_name}' is not a child of '{parent_collection.name}'")
        return object_item

    raise ValueError(f"No item matches the provided path: {path}")
