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
 
class DarrowToolPanel(bpy.types.Panel):
    bl_label = "DarrowTools"
    bl_category = "Darrow Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_toolPanel"

    @classmethod
    def poll(cls, context):
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

        return bpy.context.scene.checklist_moduleBool == True
            #print("poll")

    def draw_header(self, context):
        layout = self.layout
        obj = context.scene
        self.layout.prop(obj, 'compactBool')

    def draw(self, context):
        
        layout = self.layout
        split=layout.split()
        col=split.column(align = True) 
        obj = context.object
        scn = context.scene
        Var_compactBool = bpy.context.scene.compactBool
    
        if obj is not None:  

            if Var_compactBool == True:
                 
                if context.mode == 'OBJECT':
                    col.operator('set.wireframe', text="Toggle Wireframe")
                    col.operator('apply_all.darrow', text="Prepare for Export")
                
                if context.mode == 'EDIT_MESH':
                    col.separator()
                    col.operator('set.origin')
                
            if Var_compactBool == False:
                col.label(text = "Additional Options")
                #col.label(text = "Viewport Display")
                col.operator('set.wireframe')
                #col.separator()
                #col.label(text = "Object Origin") 
                
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
    bl_label = "Toggle Wireframe"

    def execute(self, context):

        if bpy.context.scene.showWireframeBool == False:
            bpy.context.scene.showWireframeBool = True

            bpy.context.active_object.select_set(False)
            bpy.context.space_data.show_gizmo = False
            bpy.context.space_data.overlay.show_floor = False
            bpy.context.space_data.overlay.show_axis_y = False
            bpy.context.space_data.overlay.show_axis_x = False
            bpy.context.space_data.overlay.show_cursor = False
            bpy.context.space_data.overlay.show_object_origins = False
            bpy.context.space_data.overlay.show_wireframes = True
        else:
            bpy.context.scene.showWireframeBool = False

            bpy.context.active_object.select_set(False)
            bpy.context.space_data.show_gizmo = True
            bpy.context.space_data.overlay.show_floor = True
            bpy.context.space_data.overlay.show_axis_y = True
            bpy.context.space_data.overlay.show_axis_x = True
            bpy.context.space_data.overlay.show_cursor = True
            bpy.context.space_data.overlay.show_object_origins = True
            bpy.context.space_data.overlay.show_wireframes = False

        bpy.ops.auto.update()
        
        self.report({'INFO'}, "Viewport Wireframe only")
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
        bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=True)
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
    bl_label = "Move to Origin"

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
    bl_label = "Move to origin"

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
    bl_description = "Apply all checklist functions, and prepare mesh for export(not be compatable with animations)"

    def execute(self, context):

        bpy.ops.shade.smooth()
        bpy.ops.move.origin()
        bpy.ops.apply.transforms()
        bpy.ops.apply.normals()
        bpy.ops.clean.mesh()
        bpy.ops.move.origin()

        self.report({'INFO'}, "Applied all checklist items")
        return {'FINISHED'}
 
#-----------------------------------------------------#  
#   Registration classes
#-----------------------------------------------------#  

classes = (DarrowApply, DarrowCleanMesh, DarrowWireframe, DarrowSetOrigin, DarrowSetSnapOrigin, DarrowMoveOrigin, DarrowNullPanel, DarrowToolPanel, DarrowTransforms, DarrowNormals, DarrowSmooth,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.compactBool = bpy.props.BoolProperty(
    name = "Compact",
    description = "Toggle Compact Mode",
    default = False
    )

    bpy.types.Scene.showWireframeBool = bpy.props.BoolProperty(
    name = "Toggle Wireframe",
    description = "Toggle visabilty of wireframe mode",
    default = False
    )

def unregister():
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()