import bpy

from .gui import MASALA_PT_mainPanel
from .operators import MASALA_OT_Assembler, MASALA_OT_Exporter, MASALA_OT_PreferenceTest
from .preferences import MasalaPreferences

bl_info = {
    "name": "Masala For Blender",
    "author": "Tristan Languebien @ Big Company",
    "description": "Modular asset creation framework based on AssetBlocks",
    "blender": (5, 1, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}

_classes = (
    MASALA_PT_mainPanel,
    MASALA_OT_Exporter,
    MASALA_OT_PreferenceTest,
    MasalaPreferences,
)


register, unregister = bpy.utils.register_classes_factory(classes=_classes)
