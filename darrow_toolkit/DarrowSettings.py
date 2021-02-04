#-----------------------------------------------------#  
#    Imports
#-----------------------------------------------------#  

import bpy
import sys
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import Operator, AddonPreferences

class DarrowAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        obj = context.scene

        layout.label(text='Toggle specific panels')
        layout.prop(obj, 'crypto_moduleBool')
        layout.prop(obj, 'checklist_moduleBool')
        layout.prop(obj, 'export_moduleBool')

#-----------------------------------------------------#  
#   Registration classes
#-----------------------------------------------------#  

classes = (DarrowAddonPreferences,)

def register():

    bpy.types.Scene.crypto_moduleBool = bpy.props.BoolProperty(
    name = "Crypto Panel",
    description = "Turn on crypto panel",
    default = False
    )

    bpy.types.Scene.checklist_moduleBool = bpy.props.BoolProperty(
    name = "Checklist Panel",
    description = "Turn on crypto panel",
    default = True
    )

    bpy.types.Scene.export_moduleBool = bpy.props.BoolProperty(
    name = "Crypto Panel",
    description = "Turn on crypto panel",
    default = True
    )

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()