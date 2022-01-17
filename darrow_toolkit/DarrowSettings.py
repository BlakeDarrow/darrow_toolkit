#-----------------------------------------------------#  
#
#    Copyright (c) 2020-2021 Blake Darrow <contact@blakedarrow.com>
#
#    See the LICENSE file for your full rights.
#
#-----------------------------------------------------#  
#   Imports
#-----------------------------------------------------#  
import bpy
import sys
from bpy.props import StringProperty, IntProperty, BoolProperty, FloatProperty
from bpy.types import Operator, AddonPreferences
from . import addon_updater_ops

@addon_updater_ops.make_annotations
class DarrowAddonPreferences(AddonPreferences):
    bl_idname = __package__

    auto_check_update : BoolProperty(
        name = "Auto-check for Update",
        description = "If enabled, auto-check for updates using an interval",
        default = True,
    )

    updater_intrval_months : IntProperty(
        name='Months',
        description = "Number of months between checking for updates",
        default=3,
        min=0
    )
    updater_intrval_days : IntProperty(
        name='Days',
        description = "Number of days between checking for updates",
        default=0,
        min=0,
    )
    updater_intrval_hours : IntProperty(
        name='Hours',
        description = "Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )
    updater_intrval_minutes : IntProperty(
        name='Minutes',
        description = "Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )

    checklist_moduleBool : BoolProperty(
        name = "Tool Panel",
        default = True
    )

    export_moduleBool : BoolProperty(
        name = "Export Panel",
        default = True
    )

    library_moduleBool : BoolProperty(
        name = "Library Panel",
        default = True
    )
    
    array_moduleBool: BoolProperty(
        name="Array Panel",
        default=True
    )

    rgb_moduleBool : BoolProperty(
        name = "Vertex Panel",
        default = True
    )

    xBool : BoolProperty(
        name="X",
        description="Toggle X axis",
        default=False
    )
    yBool : BoolProperty(
        name="Y",
        description="Toggle Y axis",
        default=False
    )
    zBool : BoolProperty(
        name="Z",
        description="Toggle Z axis",
        default=True
    )


    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Toggle Menu Modules")
        split=box.split()
        split.prop(self, "checklist_moduleBool")
        split.prop(self, "rgb_moduleBool")
        split=box.split()
        split.prop(self, "export_moduleBool")
        split.prop(self, "library_moduleBool")
        split = box.split()
        split.prop(self, "array_moduleBool")

        addon_updater_ops.update_settings_ui(self,context)

#-----------------------------------------------------#  
#   Registration classes
#-----------------------------------------------------#  

classes = (DarrowAddonPreferences,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()