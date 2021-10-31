#-----------------------------------------------------#  
#    Imports
#-----------------------------------------------------#  

import bpy
import sys
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import Operator, AddonPreferences
from . import addon_updater_ops

@addon_updater_ops.make_annotations
class DarrowAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        obj = context.scene
        box = layout.box()
        box.label(text='Turn off panels')
        split=box.split()
        split.prop(obj, 'checklist_moduleBool')
        split.prop(obj, 'export_moduleBool')
        split.prop(obj, 'library_moduleBool')
        split.prop(obj, 'rgb_moduleBool')

        addon_updater_ops.update_settings_ui(self,context)

    auto_check_update = bpy.props.BoolProperty(
        name = "Auto-check for Update",
        description = "If enabled, auto-check for updates using an interval",
        default = False,
    )
    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description = "Number of months between checking for updates",
        default=0,
        min=0
    )
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description = "Number of days between checking for updates",
        default=7,
        min=0,
    )
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description = "Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description = "Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )


#-----------------------------------------------------#  
#   Registration classes
#-----------------------------------------------------#  

classes = (DarrowAddonPreferences,)

def register():
    bpy.types.Scene.checklist_moduleBool = bpy.props.BoolProperty(
    name = "Tool Panel",
    description = "Turn on crypto panel",
    default = True
    )

    bpy.types.Scene.export_moduleBool = bpy.props.BoolProperty(
    name = "Export Panel",
    description = "Turn on export panel",
    default = True
    )

    bpy.types.Scene.library_moduleBool = bpy.props.BoolProperty(
    name = "Library Panel",
    description = "Turn on library panel",
    default = True
    )
    
    bpy.types.Scene.rgb_moduleBool = bpy.props.BoolProperty(
    name = "Vertex Panel",
    description = "Turn on vertex panel",
    default = True
    )

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()