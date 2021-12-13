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
        settings = context.preferences.addons['darrow_toolkit'].preferences
        obj = context.active_object

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
        Var_displayBool = bpy.context.scene.vertexDisplayBool
        Var_viewportShading = bpy.context.space_data.shading.type
        self.layout.operator('set.display', icon="SETTINGS",text="", depress= Var_displayBool)
        if Var_viewportShading != 'SOLID':
            self.layout.enabled = False

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
#     handles setting shading display   
#-----------------------------------------------------#        
class DarrowSetDisplay(bpy.types.Operator):
    bl_idname = "set.display"
    bl_name = "Show Color"
    bl_label = "Toggle vertex color visability"
    """
    We have to have this class here to toggle the bool value,
    so that a user can still manualy change the shading method
    """
    def execute(self, context):
        Var_displayBool = bpy.context.scene.vertexDisplayBool
        Var_viewportShading = bpy.context.space_data.shading.type
    
        Var_displayBool = not Var_displayBool #Toggle bool value everytime this operator is called

        if Var_displayBool == True and Var_viewportShading == 'SOLID':
            bpy.context.space_data.shading.color_type = 'VERTEX'
        elif Var_viewportShading == 'SOLID':
            bpy.context.space_data.shading.color_type = 'MATERIAL'

        bpy.context.scene.vertexDisplayBool = Var_displayBool
        return {'FINISHED'}
    
#-----------------------------------------------------#  
#   Registration classes
#-----------------------------------------------------#  
classes = (DarrowNullPanel, DarrowVertexPanel,DarrowSetBlack, DarrowSetWhite, DarrowSetRed, DarrowSetGreen, DarrowSetBlue, DarrowSetColor, DarrowSetDisplay,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.vertexDisplayBool = bpy.props.BoolProperty(
    name = "",
    description = "Toggle visabilty of vertex color",
    default = False
    )
def unregister():
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()