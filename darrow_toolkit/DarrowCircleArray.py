#-----------------------------------------------------#
#
#    Copyright (c) 2020-2022 Blake Darrow <contact@blakedarrow.com>
#
#    See the LICENSE file for your full rights.
#
#-----------------------------------------------------#
#   Imports
#-----------------------------------------------------#

import bpy
import math
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       )

#-----------------------------------------------------#
#     handles ui panel
#-----------------------------------------------------#

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
        settings = context.preferences.addons[__package__].preferences
        self.layout.prop(settings, 'advancedVertexBool', icon="SETTINGS", text="")

    def draw(self, context):
        settings = context.preferences.addons[__package__].preferences
        layout = self.layout
        obj = context.active_object
        objs = context.selected_objects
        Var_advancedBool = settings.advancedVertexBool
        xAxis = settings.xBool
        yAxis = settings.yBool
        zAxis = settings.zBool

        if obj is not None:
            if context.mode == 'OBJECT':
                
                col = layout.column(align=True)
                col.scale_y = 1.33
                col.prop(obj, 'arrayAmount', slider=True)

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
                col.operator('circle.array', icon="ONIONSKIN_ON",)

                if xAxis == False and yAxis == False and zAxis == False:
                    col.enabled = False
                elif len(objs) is not 0:
                    col.enabled = True
                else:
                    col.enabled = False

                if  Var_advancedBool == True:
                    box = layout.box()
                    col2 = box.column(align=False)
                    col2.label(text="Advanced")
                    col2.scale_y=1.2
                    col2.operator('clear.array', text="Delete Array", icon="TRASH")
                    if len(objs) is 0:
                        box.enabled = False
                    box.prop(settings, 'moveEmptyBool', toggle=False, text="Move empty to 'Empties'")
                    
#-----------------------------------------------------#
#     handles array
#-----------------------------------------------------#

class DarrowCircleArray(bpy.types.Operator):
    bl_idname = "circle.array"
    bl_description = "Move selected to world origin"
    bl_label = "Array Selected"
    bl_options = {"UNDO"}

    def execute(self, context):
        collectionFound = False
        obj = bpy.context.selected_objects[0]
        amt = context.object.arrayAmount
        settings = context.preferences.addons[__package__].preferences
        selected = bpy.context.selected_objects[0]
        empty_collection_name = "Darrow_Empties"
       
        for myCol in bpy.data.collections:
            if myCol.name == empty_collection_name:
                collectionFound = True
                break

        if collectionFound == False:
            col = bpy.data.collections.new(empty_collection_name)
            bpy.context.scene.collection.children.link(col)
            vlayer = bpy.context.scene.view_layers["View Layer"]
            vlayer.layer_collection.children[empty_collection_name].hide_viewport = True

        else:
            col = bpy.data.collections[empty_collection_name]

        bpy.context.scene.cursor.rotation_euler = (0, 0, 0)
        bpy.ops.object.transform_apply(
            location=True, rotation=True, scale=True)
        try:
            if bpy.context.object.modifiers["DarrowToolkitArray"].offset_object == None:
                modifier_to_remove = obj.modifiers.get("DarrowToolkitArray")
                obj.modifiers.remove(modifier_to_remove)
                context.object.linkedEmpty = "tmp"
                print("Resetting modifier")
        except:
            print("No modifier present")

        if context.object.linkedEmpty == "tmp":
            print("Creating array")
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD')
            bpy.context.object.empty_display_size = settings.emptySize
            empty = bpy.context.selected_objects[0]

        else:
            print("Array exists")
            vlayer = bpy.context.scene.view_layers["ViewLayer"]
            vlayer.layer_collection.children[empty_collection_name].hide_viewport = False
            empty = bpy.data.objects[context.object.linkedEmpty]

        bpy.ops.object.select_all(action='DESELECT')
        selected.select_set(state=True)
        context.view_layer.objects.active = selected
        context.object.linkedEmpty = empty.name
        array = False
        mod = bpy.context.object

        for modifier in mod.modifiers:
            if modifier.name == "DarrowToolkitArray":
                array = True
        
        if not array:
            modifier = obj.modifiers.new(
                name='DarrowToolkitArray', type='ARRAY')

            modifier.name = "DarrowToolkitArray"
            modifier.count = amt
            modifier.use_relative_offset = False
            modifier.use_object_offset = True
            modifier.offset_object = empty
        else:
            modifier_to_remove = obj.modifiers.get("DarrowToolkitArray")
            obj.modifiers.remove(modifier_to_remove)

            modifier = obj.modifiers.new(
                name='DarrowToolkitArray', type='ARRAY')

            modifier.name = "DarrowToolkitArray"
            modifier.count = amt
            modifier.use_relative_offset = False
            modifier.use_object_offset = True
            modifier.offset_object = empty
        
        modAmt = -1
        for mod in (obj.modifiers):
           modAmt = modAmt + 1

        bpy.ops.object.modifier_move_to_index(
            modifier="DarrowToolkitArray", index=modAmt)
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

        if settings.moveEmptyBool == True:
            empty.select_set(state=True)
            context.view_layer.objects.active = empty
            for coll in empty.users_collection:
                coll.objects.unlink(empty)

            col.objects.link(empty)
        else:
            for coll in empty.users_collection:
                coll.objects.unlink(empty)
            context.scene.collection.objects.link(empty)

        vlayer = bpy.context.scene.view_layers["ViewLayer"]
        vlayer.layer_collection.children[empty_collection_name].hide_viewport = True
        empty.select_set(state=False)
        selected.select_set(state=True)
        context.view_layer.objects.active = selected

        return {'FINISHED'}

#-----------------------------------------------------#
#     handles array
#-----------------------------------------------------#

class DarrowClearSelected(bpy.types.Operator):
    bl_idname = "clear.array"
    bl_description = "Move selected to world origin"
    bl_label = "Clear Selected"
    bl_options = {"UNDO"}

    def execute(self, context):
        obj = bpy.context.selected_objects[0]
        settings = context.preferences.addons[__package__].preferences
        selected = bpy.context.selected_objects[0]

        if not context.object.linkedEmpty == "tmp":
            empty = bpy.data.objects[context.object.linkedEmpty]
            context.object.linkedEmpty = empty.name
        else: 
            context.object.linkedEmpty == "tmp"

        bpy.ops.object.select_all(action='DESELECT')
        selected.select_set(state=True)
        context.view_layer.objects.active = selected

        mod = bpy.context.object

        for modifier in mod.modifiers:
            if modifier.name == "DarrowToolkitArray":
                modifier_to_remove = obj.modifiers.get("DarrowToolkitArray")
                obj.modifiers.remove(modifier_to_remove)

        if not context.object.linkedEmpty == "tmp":
            empty.select_set(state=True)
            selected.select_set(state=False)
            context.view_layer.objects.active = empty
            bpy.ops.object.delete()

        selected.select_set(state=True)
        context.view_layer.objects.active = selected
        context.object.linkedEmpty = "tmp"

        return {'FINISHED'}

#-----------------------------------------------------#
#   Registration classes
#-----------------------------------------------------#

classes = (DarrowCircleArray, DarrowToolPanel, DarrowClearSelected)

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
