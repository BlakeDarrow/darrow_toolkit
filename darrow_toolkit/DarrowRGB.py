#
#    Copyright (c) 2020-2021 Blake Darrow <contact@blakedarrow.com>
#
#    See the LICENSE file for your full rights.
#
#-----------------------------------------------------#  
#   Imports
#-----------------------------------------------------# 
 
import bpy
from .addon_updater_ops import get_user_preferences
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       )

#-----------------------------------------------------#         
#     handles panel if null  
#-----------------------------------------------------#  
class DarrowNullPanel(bpy.types.Panel):
    bl_label = ""
    bl_category = "Darrow Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_nullPanel"

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        for obj in bpy.context.selected_objects:
            if obj is not None: 
                #if obj.type =='MESH' : return True
                if obj.type =='EMPTY' : return True
                if obj.type =='CAMERA' : return True
                if obj.type =='LIGHT' : return True
                if obj.type =='CURVE' : return True
                if obj.type =='FONT' : return True
                if obj.type =='LATTICE' : return True
                if obj.type =='LIGHT_PROBE' : return True
                if obj.type =='IMAGE' : return True
                if obj.type =='SPEAKER' : return True

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.separator()
        box.label(text = "Please select only mesh(s)")
        box.separator()
  
#-----------------------------------------------------#  
#     handles ui     
#-----------------------------------------------------#  
class DarrowVertexPanel(bpy.types.Panel):
    bl_label = "DarrowVertex"
    bl_category = "Darrow Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_rgbPanel"

    @classmethod
    def poll(cls, context):
        settings = get_user_preferences(context)
        obj = context.active_object
        Var_displayBool = bpy.context.scene.vertexDisplayBool
        if(Var_displayBool == True):
            bpy.context.space_data.shading.color_type = 'VERTEX'
        else:
            bpy.context.space_data.shading.color_type = 'MATERIAL'
        if obj is not None: 
            obj = context.active_object
            objs = bpy.context.object.data
            for obj in bpy.context.selected_objects:
                if obj.type =='CURVE' : return False
                if obj.type =='FONT' : return False
                if obj.type =='CAMERA' : return False
                if obj.type =='LIGHT' : return False
                if obj.type =='LATTICE' : return False
                if obj.type =='LIGHT_PROBE' : return False
                if obj.type =='IMAGE' : return False
                if obj.type =='SPEAKER' : return False
        return settings.rgb_moduleBool == True

    def draw_header(self, context):
        layout = self.layout
        obj = context.scene
        self.layout.prop(obj, 'vertexDisplayBool', icon="SETTINGS",text="")

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scn = context.scene
    
        if obj is not None:  
            split=layout.box()
            row = split.row(align = True)
            row.operator('set.black')
            row.operator('set.white')
            
            row = split.row(align = True)
            row.operator('set.red')
            row.operator('set.green')
            row.operator('set.blue')

#-----------------------------------------------------#  
#     set Black color  
#-----------------------------------------------------#                 
class DarrowSetBlack(bpy.types.Operator):
    bl_idname = "set.black"
    bl_label = "Black"

    def execute(self, context):
        bpy.data.brushes["Draw"].color = (0, 0, 0)
        DarrowSetColor.execute(self,context)
        return {'FINISHED'} 
   
#-----------------------------------------------------#  
#     set White color  
#-----------------------------------------------------#                 
class DarrowSetWhite(bpy.types.Operator):
    bl_idname = "set.white"
    bl_label = "White"

    def execute(self, context):
        bpy.data.brushes["Draw"].color = (1, 1, 1)
        DarrowSetColor.execute(self,context)
        return {'FINISHED'} 
   
#-----------------------------------------------------#  
#     set Red color  
#-----------------------------------------------------#                 
class DarrowSetRed(bpy.types.Operator):
    bl_idname = "set.red"
    bl_label = "Red"

    def execute(self, context):
        bpy.data.brushes["Draw"].color = (1, 0, 0)
        DarrowSetColor.execute(self,context)
        return {'FINISHED'} 

#-----------------------------------------------------#  
#     set Green color  
#-----------------------------------------------------#                 
class DarrowSetGreen(bpy.types.Operator):
    bl_idname = "set.green"
    bl_label = "Green"

    def execute(self, context):
        bpy.data.brushes["Draw"].color = (0, 1, 0)
        DarrowSetColor.execute(self,context)
        return {'FINISHED'} 

#-----------------------------------------------------#  
#     set Blue color  
#-----------------------------------------------------#                 
class DarrowSetBlue(bpy.types.Operator):
    bl_idname = "set.blue"
    bl_label = "Blue"

    def execute(self, context):
        bpy.data.brushes["Draw"].color = (0, 0, 1)
        DarrowSetColor.execute(self,context)
        return {'FINISHED'} 
   
#-----------------------------------------------------#  
#     handles setting vertex color   
#-----------------------------------------------------#                 
class DarrowSetColor(bpy.types.Operator):
    bl_idname = "set.color"
    bl_label = "Set Color"

    def execute(self, context):
        current_mode = bpy.context.object.mode
        if current_mode == 'OBJECT':
            view_layer = bpy.context.view_layer
            obj_active = view_layer.objects.active
            selection = bpy.context.selected_objects
            bpy.ops.object.select_all(action='DESELECT')

            for obj in selection:
                view_layer.objects.active = obj
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.paint.vertex_paint_toggle()
                bpy.ops.paint.vertex_color_set()
                bpy.ops.object.mode_set(mode='OBJECT')
                obj.select_set(True)
    
        if current_mode == 'EDIT':
            view_layer = bpy.context.view_layer
            obj_active = view_layer.objects.active
            selection = bpy.context.selected_objects

            for obj in selection:
                view_layer.objects.active = obj
                bpy.ops.paint.vertex_paint_toggle()
                bpy.context.object.data.use_paint_mask = True
                bpy.ops.paint.vertex_color_set()
                bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'} 
    
#-----------------------------------------------------#  
#   Registration classes
#-----------------------------------------------------#  
classes = (DarrowSetBlack, DarrowSetWhite, DarrowSetRed, DarrowSetGreen, DarrowSetBlue, DarrowSetColor, DarrowNullPanel, DarrowVertexPanel)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.vertexDisplayBool = bpy.props.BoolProperty(
    name = "",
    description = "Toggle visabilty of vertex color",
    default = True
    )
def unregister():
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()