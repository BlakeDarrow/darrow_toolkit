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
from bpy.props import StringProperty, IntProperty, BoolProperty, FloatProperty, EnumProperty
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
        name = "Q.O.L Tools",
        default = True
    )

    export_moduleBool : BoolProperty(
        name = "FBX Exporter",
        default = True
    )

    library_moduleBool : BoolProperty(
        name = "Mesh Library",
        default = True
    )
    
    array_moduleBool: BoolProperty(
        name="Circular Array",
        default=True
    )

    rgb_moduleBool : BoolProperty(
        name = "Vertex Painter",
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
    emptySize : FloatProperty(
        name="Array Empty Display Size",
        description="Size of arrays' empty",
        default=0.25,
        soft_min=0,
        soft_max=1
    )
    exportPresets = EnumProperty(
        name="Preset",
        description="Animation Export Presets",
        items=[('OP1', "Unity", ""),
               ('OP2', "Unreal", ""),
               ],
        default='OP2'
    )
    advancedToolBool : BoolProperty(
        name="Advanced",
        description="Show advanced options",
        default=False
    )
    advancedVertexBool : BoolProperty(
        name="Advanced",
        description="Show advanced options",
        default=False
    )
    advancedCircleBool : BoolProperty(
        name="Advanced",
        description="Show advanced options",
        default=False
    )
    advancedExportBool : BoolProperty(
        name="Advanced",
        description="Show advanced options",
        default=False
    )
    advancedLibraryBool : BoolProperty(
        name="Advanced",
        description="Show advanced options",
        default=False
    )
    removeDoublesAmount : FloatProperty(
        name="Remove Doubles Amount",
        description="Threshold to Remove Doubles",
        default=0.02,
        soft_min=0,
        soft_max=2,
        precision=4
    )

    def draw(self, context):
        layout = self.layout
        col_1 = layout.box()
        col_1.label(text="Toggle Module Visablity and Advanced Display Options")
        col_1.scale_y = 1.1
        col_1 = col_1.split(factor=0.5)

        split = col_1.split(factor=0.1)
        panel = split.column(align=True)
        icon = split.column(align=True)

        col_2 = col_1.split(factor=1)
        split_2 = col_2.split(factor=0.9)
        icon_2 = split_2.column(align=True)
        panel_2 = split_2.column(align=True)
        panel.alignment = 'RIGHT'

        icon.prop(self, "checklist_moduleBool", toggle=True)
        panel.prop(self, "advancedToolBool", icon="SETTINGS", icon_only=True)

        icon_2.prop(self, "export_moduleBool", toggle=True)
        panel_2.prop(self, "advancedExportBool",icon="SETTINGS", icon_only=True)

        icon.prop(self, "rgb_moduleBool", toggle=True)
        panel.label(text="")
        
        icon_2.prop(self, "library_moduleBool", toggle=True)
        panel_2.prop(self, "advancedLibraryBool",icon="SETTINGS", icon_only=True)

        icon.prop(self, "array_moduleBool", toggle=True)
        panel.label(text="")
        
        box = layout.box()
        box.label(text="Default Module Properties")
        box.alignment = 'EXPAND'
        box.scale_y = 1.05
        box.prop(self, "exportPresets", text="Engine Export Preset")
        box.prop(self, "emptySize", text="Created Empty Size", slider=True)
        box.prop(self, "removeDoublesAmount", text="Remove Doubles Distance", slider=True)
        
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