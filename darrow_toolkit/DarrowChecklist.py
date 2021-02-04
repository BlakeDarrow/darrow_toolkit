#-----------------------------------------------------#  
#   Imports
#-----------------------------------------------------#  
import bpy
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       )
  
#-----------------------------------------------------#  
#     handles checklist ui     
#-----------------------------------------------------#  
class DarrowToolPanel(bpy.types.Panel):
    bl_label = "Checklist"
    bl_category = "Darrow Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_toolPanel"

    @classmethod
    def poll(cls, context):
        return bpy.context.scene.checklist_moduleBool == True
            #print("poll")

    def draw(self, context):
        
        layout = self.layout
        split=layout.split()
        col=split.column(align = True) 
        obj = context.object
        scn = context.scene
        
        if obj is not None:  
            #if bpy.context.object.hidetoolkitBool == False:

            col.label(text = "Viewport Display Options")
            col.operator('set.wireframe')
            col.operator('reset.wireframe')
            col.separator()
            col.label(text = "Object Origin")   
        
            if context.mode == 'EDIT_MESH':
                col.operator('set.origin')
                
            if context.mode == 'OBJECT':
                col.operator('move.origin')
                col.separator()
                #disabled "Apply All" button for orgin and move
                #col.operator('setsnap.origin')

                col.label(text = "Export Checklist")
                layout.operator('apply_all.darrow')

                
                #col.prop(scn, 'cleanmeshBool')
                #col.prop(scn, 'applytransformsBool')
                #col.prop(scn, 'shadesmoothBool')
                #col.prop(scn, 'normalsBool')

                col.operator('clean.mesh')
                col.operator('shade.smooth')
                col.operator('apply.transforms')
                col.operator('apply.normals')
                                                
#-----------------------------------------------------#  
#     handles wireframe display   
#-----------------------------------------------------#                 
class DarrowWireframe(bpy.types.Operator):
    bl_idname = "set.wireframe"
    bl_description = "Display Wireframe Overlay Only"
    bl_label = "Isolate Wireframe"

    def execute(self, context):
        bpy.context.active_object.select_set(False)
        bpy.context.space_data.show_gizmo = False
        bpy.context.space_data.overlay.show_floor = False
        bpy.context.space_data.overlay.show_axis_y = False
        bpy.context.space_data.overlay.show_axis_x = False
        bpy.context.space_data.overlay.show_cursor = False
        bpy.context.space_data.overlay.show_object_origins = False
        bpy.context.space_data.overlay.show_wireframes = True

        bpy.ops.auto.update()
        
        self.report({'INFO'}, "Viewport Wireframe only")
        return {'FINISHED'} 
    
#-----------------------------------------------------#  
#     handles reseting the wireframe display  
#-----------------------------------------------------#   
class DarrowWireframeReset(bpy.types.Operator):
    bl_idname = "reset.wireframe"
    bl_description = "Reset display overlays"
    bl_label = "Reset Overlay"

    def execute(self, context):
        bpy.context.active_object.select_set(False)
        bpy.context.space_data.show_gizmo = True
        bpy.context.space_data.overlay.show_floor = True
        bpy.context.space_data.overlay.show_axis_y = True
        bpy.context.space_data.overlay.show_axis_x = True
        bpy.context.space_data.overlay.show_cursor = True
        bpy.context.space_data.overlay.show_object_origins = True
        bpy.context.space_data.overlay.show_wireframes = False

        bpy.ops.auto.update()
    
        self.report({'INFO'}, "Reset viewport")
        return {'FINISHED'}   

#-----------------------------------------------------#  
#    Handles mesh clean up
#-----------------------------------------------------#  
class DarrowCleanMesh(bpy.types.Operator):
    bl_idname = "clean.mesh"
    bl_description = "Delete loose, remove doubles, and dissolve degenerate"
    bl_label = "Clean Mesh"

    def execute(self, context):
        if context.mode == 'OBJECT':
            bpy.ops.object.editmode_toggle()

        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete_loose()
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.dissolve_degenerate()
        bpy.ops.object.editmode_toggle()   
        bpy.ops.auto.update()     
        self.report({'INFO'}, "Mesh cleaned")
        return {'FINISHED'}

#-----------------------------------------------------#  
#    handle apply transforms
#-----------------------------------------------------#  
class DarrowTransforms(bpy.types.Operator):
    bl_idname = "apply.transforms"
    bl_description = "Apply transformations to selected object"
    bl_label = "Apply Transforms"

    def execute(self, context):
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        bpy.ops.auto.update()

        self.report({'INFO'}, "Transforms applied")
        return {'FINISHED'}

#-----------------------------------------------------#  
#    Handles Objects origin
#-----------------------------------------------------#  
class DarrowSetOrigin(bpy.types.Operator):
    bl_idname = "set.origin"
    bl_description = "Set selected as object origin"
    bl_label = "Set Origin"

    def execute(self, context):
        if context.mode == 'OBJECT':
            bpy.ops.object.editmode_toggle()
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        bpy.ops.auto.update()

        self.report({'INFO'}, "Selected is now origin")
        return {'FINISHED'}

#-----------------------------------------------------#  
#     Handles snapping object to world center
#-----------------------------------------------------#   
class DarrowMoveOrigin(bpy.types.Operator):
    bl_idname = "move.origin"
    bl_description = "Move selected to world origin"
    bl_label = "Align to world"

    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

        bpy.ops.auto.update()

        self.report({'INFO'}, "Moved selected to object origin")
        return {'FINISHED'}

#-----------------------------------------------------#  
#    Handles setting Objects origin and move to world origin
#-----------------------------------------------------#   
class DarrowSetSnapOrigin(bpy.types.Operator):
    bl_idname = "setsnap.origin"
    bl_description = "Set selected as object origin and move to world origin"
    bl_label = "Apply All"

    def execute(self, context):
        if context.mode == 'OBJECT':
            bpy.ops.object.editmode_toggle()
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

        bpy.ops.auto.update()

        return {'FINISHED'}

#-----------------------------------------------------#  
#     Handles apply outside calculated normals
#-----------------------------------------------------#    
class DarrowNormals(bpy.types.Operator):
    bl_idname = "apply.normals"
    bl_description = "Calculate outside normals"
    bl_label = "Calculate Normals"

    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.editmode_toggle()

        bpy.ops.auto.update()

        self.report({'INFO'}, "Normals calculated outside")
        return {'FINISHED'}
    
#-----------------------------------------------------#  
#     Handles smooth mesh
#-----------------------------------------------------#    
class DarrowSmooth(bpy.types.Operator):
    bl_idname = "shade.smooth"
    bl_label = "Smooth Object"
    bl_description = "Smooth the selected object"

    def execute(self, context):
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True

        bpy.ops.auto.update()

        self.report({'INFO'}, "Object smoothed")
        return {'FINISHED'}

#-----------------------------------------------------#  
#     Handles 'apply all' checklisted items
#-----------------------------------------------------#         
class DarrowApply(bpy.types.Operator):
    bl_idname = "apply_all.darrow"
    bl_label = "Apply All"
    bl_description = "Apply all checklist functions, and prepare mesh for export"

    def execute(self, context):
        bpy.ops.shade.smooth()
        bpy.ops.apply.transforms()
        bpy.ops.apply.normals()
        bpy.ops.clean.mesh()

        self.report({'INFO'}, "Applied all checklist items")
        return {'FINISHED'}
 
#-----------------------------------------------------#  
#   Registration classes
#-----------------------------------------------------#  

classes = (DarrowApply, DarrowCleanMesh, DarrowWireframe, DarrowWireframeReset, DarrowSetOrigin, DarrowSetSnapOrigin, DarrowMoveOrigin, DarrowToolPanel, DarrowTransforms, DarrowNormals, DarrowSmooth,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
def unregister():
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()