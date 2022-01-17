#-----------------------------------------------------#
#
#    Copyright (c) 2020-2021 Blake Darrow <contact@blakedarrow.com>
#
#    See the LICENSE file for your full rights.
#
#-----------------------------------------------------#
#   Imports
#-----------------------------------------------------#
from cgitb import enable
from email.policy import default
from mathutils import Euler
import bpy
import math
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       )


#-----------------------------------------------------#
#     handles ui panel
#-----------------------------------------------------#

# Need to create a distance slider?
# parent empty


class DarrowToolPanel(bpy.types.Panel):
    bl_label = "DarrowCircleArray"
    bl_category = "Darrow Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_arrayPanel"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        settings = context.preferences.addons[__package__].preferences
        if obj is not None:
            obj = context.active_object
            objs = bpy.context.object.data

            for obj in bpy.context.selected_objects:
                if obj.type == 'CURVE':
                    return False
                if obj.type == 'FONT':
                    return False
                if obj.type == 'CAMERA':
                    return False
                if obj.type == 'LIGHT':
                    return False
                if obj.type == 'LATTICE':
                    return False
                if obj.type == 'LIGHT_PROBE':
                    return False
                if obj.type == 'IMAGE':
                    return False
                if obj.type == 'SPEAKER':
                    return False

        return settings.array_moduleBool == True

    def draw_header(self, context):
        layout = self.layout
        obj = context.scene
        #self.layout.prop(obj, 'compactBool', icon="SETTINGS", text="")

    def draw(self, context):
        settings = context.preferences.addons[__package__].preferences
        layout = self.layout
        obj = context.active_object
        scn = context.scene
        Var_compactBool = bpy.context.scene.compactBool
        xAxis = settings.xBool
        yAxis = settings.yBool
        zAxis = settings.zBool

        if obj is not None:
            objs = context.selected_objects

            col = layout.column(align=True)
            col.scale_y = 1.33
            col.prop(obj, 'arrayAmount',slider=True)
            #if len(objs) is not 0 and context.scene.compactBool == True:
               #col.prop(obj, 'stepAmount', slider=True)

            row = layout.row(align=True)
            split = row.split(align=True)
            split.prop(settings, 'xBool', toggle=True)

            if yAxis == True:
                split.enabled = False
            if zAxis == True:
                split.enabled = False

            split = row.split(align=True)
            split.prop(settings, 'yBool', toggle=True)
            if xAxis == True:
                split.enabled = False
            if zAxis == True:
                split.enabled = False

            split = row.split(align=True)
            split.prop(settings, 'zBool', toggle=True)
            if xAxis == True:
                split.enabled = False
            if yAxis == True:
                split.enabled = False
            
            col = layout.column(align=True)
            col.scale_y = 1.5
            col.operator('circle.array')

            if len(objs) is not 0:
                col.enabled = True
            else:
                col.enabled = False

#---------------------------------------------------#
#     handles array
#-----------------------------------------------------#
def update_func(self, context):
    obj = bpy.context.selected_objects[0]
    if not obj.modifiers:
        print("no modifiers")
    else:
        bpy.context.object.modifiers["Array"].count = context.object.stepAmount

def update_func_create(self, context):
    context.object.stepAmount = context.object.arrayAmount

class DarrowCircleArray(bpy.types.Operator):
    bl_idname = "circle.array"
    bl_description = "Move selected to world origin"
    bl_label = "Array Selected"
    bl_options = {"UNDO"}
    
    def execute(self, context):
        bpy.context.scene.cursor.rotation_euler = (0,0,0)

        amt = context.object.arrayAmount
        settings = context.preferences.addons[__package__].preferences
        selected = bpy.context.selected_objects[0]
        bpy.ops.object.transform_apply(
            location=True, rotation=True, scale=True)

        if context.object.linkedEmpty == "tmp":
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD')
            empty = bpy.context.selected_objects[0]
            
        else:
            empty = bpy.data.objects[context.object.linkedEmpty]

        bpy.ops.object.select_all(action='DESELECT')
        selected.select_set(state=True)
        context.view_layer.objects.active = selected
        context.object.linkedEmpty = empty.name

        obj = bpy.context.selected_objects[0]
        if not obj.modifiers:
            bpy.ops.object.modifier_add(type='ARRAY')
            bpy.context.object.modifiers["Array"].count = amt
            bpy.context.object.modifiers["Array"].use_relative_offset = False
            bpy.context.object.modifiers["Array"].use_object_offset = True
            bpy.context.object.modifiers["Array"].offset_object = empty
        else:
            modifier_to_remove = obj.modifiers.get("Array")
            obj.modifiers.remove(modifier_to_remove)
            bpy.ops.object.modifier_add(type='ARRAY')
            bpy.context.object.modifiers["Array"].count = amt
            bpy.context.object.modifiers["Array"].use_relative_offset = False
            bpy.context.object.modifiers["Array"].use_object_offset = True
            bpy.context.object.modifiers["Array"].offset_object = empty
        
        bpy.ops.object.select_all(action='DESELECT')
        empty.select_set(state=True)
        selected.select_set(state=False)
        context.view_layer.objects.active = empty
        bpy.ops.object.transform_apply(
            location=True, rotation=True, scale=True)
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        if settings.xBool == True:
            axis = 'X'
        if settings.yBool == True:
            axis = 'Y'
        if settings.zBool == True:
            axis = 'Z'
        rotation = 360 / amt
        print(rotation)
        value = math.radians(rotation)
        bpy.ops.transform.rotate(
            value=value, orient_axis=axis, orient_type='GLOBAL',)
        bpy.ops.object.select_all(action='DESELECT')
        empty.select_set(state=False)
        selected.select_set(state=True) 
        context.view_layer.objects.active = selected
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

        empty.select_set(state=True)
        selected.select_set(state=True) 
        context.view_layer.objects.active = selected
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        bpy.ops.object.select_all(action='DESELECT')
        empty.select_set(state=False)
        selected.select_set(state=True)
        context.view_layer.objects.active = selected

        return {'FINISHED'}

#-----------------------------------------------------#
#   Registration classes
#-----------------------------------------------------#

classes = (DarrowCircleArray, DarrowToolPanel,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.linkedEmpty = bpy.props.StringProperty(
        default="tmp"
    )

    bpy.types.Object.arrayAmount = bpy.props.IntProperty(
        name="Amount",
        description="Amount",
        default=5,
        step=1,
        soft_max=30,
        soft_min=1,
        #update=update_func_create
    )

    bpy.types.Object.stepAmount = bpy.props.IntProperty(
        name="Step",
        description="Step",
        default=5,
        step=100,
        soft_max=30,
        soft_min=1,
        #update=update_func
    )

    bpy.types.Scene.compactBool = bpy.props.BoolProperty(
        name="Advanced",
        description="Toggle Advanced Mode",
        default=False
    )


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
