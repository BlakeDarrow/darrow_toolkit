#-----------------------------------------------------#  
#   Imports
#       Might be some unnecessary imports
#-----------------------------------------------------#  
import bpy
import bgl
import gpu
import math
import getopt
import os
from pathlib import Path

from mathutils import Vector, Matrix
from bpy_extras.io_utils import (ImportHelper,
                                 ExportHelper,
                                 path_reference_mode,
                                 axis_conversion,
                                 )

from gpu_extras.batch import batch_for_shader
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
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
    
    def draw(self, context):
        
        layout = self.layout
        split=layout.split()
        col=split.column(align = True) 
        obj = context.object
        
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

                col.operator('clean.mesh')
                col.operator('shade.smooth')
                col.operator('apply.transforms')
                col.operator('apply.normals')
                               
#-----------------------------------------------------#  
#     handles export panel     
#-----------------------------------------------------#                    
class DarrowExportPanel(bpy.types.Panel):
    bl_label = "Exporter"
    bl_category = "Darrow Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_exportPanel"
    
    def draw(self, context):
        
        Var_prefix_bool = bpy.context.scene.useprefixBool
        Var_suffix_bool = bpy.context.scene.usecounterBool
        Var_custom_prefix = bpy.context.scene.PrefixOption
        obj = context.object
        
        if obj is not None:  
            layout = self.layout
            obj = context.scene

            box = layout.box()
            box.label(text = "Animation Export")
            split=box.split()
            split.prop(obj, 'isleafBool')
            split.prop(obj, 'allactionsBool')
        

            #layout.label(text = "Export Selected Mesh")
            box = layout.box()
            box.label(text = "FBX Exporter")
            box.operator('export_selected.darrow')
            
            split=box.split()
            split.prop(obj, 'useprefixBool')
            split.prop(obj, 'usecounterBool')

            #If use prefix is selected then these options show up
            if Var_prefix_bool == True: 
                box = layout.box()
                box.label(text = "Prefix Options")
                box.prop(obj, 'PrefixOption')
                #If the custom enum is selected these show up
                if Var_custom_prefix == 'OP2':
                    box.prop(context.scene, "custom_name_string", text="Prefix") 
            if Var_suffix_bool == True:
                box = layout.box()
                box.label(text = "Suffix Options")
                box.label(text = "Increase the suffix by (+1)")
                box.operator('reset.counter')
         
#-----------------------------------------------------#  
#     handles reseting the suffix counter      
#-----------------------------------------------------# 
class DarrowCounterReset(bpy.types.Operator):
    bl_idname = "reset.counter"
    bl_description = "Resets FBX suffix counter"
    bl_label = "Reset Suffix Counter"

    def execute(self, context):
        context.scene.counter = 0

        bpy.ops.auto.update()

        self.report({'INFO'}, "Set suffix count to 0")
        return {'FINISHED'} 
                    
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
    bl_description = "Apply all checklist functions"

    def execute(self, context):
        
        bpy.ops.shade.smooth()
        bpy.ops.apply.transforms()
        bpy.ops.apply.normals()
        bpy.ops.clean.mesh()

        self.report({'INFO'}, "Applied all checklist items")
        return {'FINISHED'}

#-----------------------------------------------------#  
#    Handles logic for exporting as FBX
#-----------------------------------------------------#  
class DarrowExportFBX(bpy.types.Operator, ExportHelper):
    bl_idname = "export_selected.darrow"
    bl_label = 'Export Selected'
    bl_description = "Export selected as FBX using mesh name"
    bl_options = {'PRESET'}
    filename_ext    = ".fbx";
    check_extension = True
    
    #meat of exporting the FBX
    def execute(self, context):
        
        #option to show in exporter
        path_mode = path_reference_mode
        #get the name of the active object
        fbxname = bpy.context.view_layer.objects.active
        #get string of custom prefix user input
        customprefix = bpy.context.scene.custom_name_string
        #get blend name
        blendName = bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend", "")
        #get fbx name
        name = bpy.path.clean_name(fbxname.name)
        #Variables for UI, like bools and enums
        Var_actionsBool = bpy.context.scene.allactionsBool
        Var_leafBool = bpy.context.scene.isleafBool
        Var_PrefixBool = bpy.context.scene.useprefixBool
        Var_custom_prefix = bpy.context.scene.PrefixOption
        Var_counterBool = bpy.context.scene.usecounterBool

        
        #get the counter and add "1" to it, only when bool is checked
        if Var_counterBool == True:
            context.scene.counter += 1
            count = context.scene.counter
            count = str(count)
            Var_exportnumber = "_" + count
        
        #If "Use Prefix" box selected, the 2 prefix options will show up in the enum
        if not bpy.data.is_saved:
                raise Exception("Blend file is not saved")
                print("SAVE YOUR FILE")
        
        if Var_PrefixBool == True:
            print("USED PREFIX")

        #if ".blend enum" is selected, the object will export with custom prefix + mesh name
            if Var_custom_prefix == 'OP1':
                #If the "export counter" bool is true then we add the counter varable to the end of the save location          
                if Var_counterBool == True:
                    saveLoc = self.filepath + "_" + name + Var_exportnumber
                    self.report({'INFO'}, "Added Counter to the end of mesh") 
                else: 
                    saveLoc = self.filepath + "_" + name
                print(saveLoc)
                #handles actual export    
                bpy.ops.export_scene.fbx(
                    filepath = saveLoc.replace('.fbx', '')+ ".fbx",
                    use_mesh_modifiers=True,
                    bake_anim_use_all_actions = Var_actionsBool,
                    add_leaf_bones = Var_leafBool,
                    check_existing=True, 
                    axis_forward= '-Z', 
                    axis_up= 'Y', 
                    use_selection=True, 
                    global_scale=1, 
                    path_mode='AUTO')
                print(Var_actionsBool)
                print(Var_leafBool)
                self.report({'INFO'}, "Exported with .blend prefix and mesh name") 
                return {'FINISHED'}
            else:
                print("No Prefix Defined", context.mode)

        #If use "custom" enum is selected, the object will export with custom prefix + mesh name
            if Var_custom_prefix == 'OP2':
                #If the "export counter" bool is true then we add the counter varable to the end of the save location
                if Var_counterBool == True:
                    customname = customprefix + "_" + name + Var_exportnumber
                else:
                    customname = customprefix + "_" + name
                saveLoc = self.filepath.replace(blendName,'') + customname  
                print(saveLoc)
                #export logic
                bpy.ops.export_scene.fbx(
                    filepath = saveLoc.replace(".fbx", '')+ ".fbx",
                    use_mesh_modifiers=True,
                    bake_anim_use_all_actions = Var_actionsBool,
                    add_leaf_bones = Var_leafBool,
                    check_existing=True, 
                    axis_forward='-Z', 
                    axis_up='Y', 
                    use_selection=True, 
                    global_scale=1, 
                    path_mode='AUTO')
                print(Var_actionsBool)
                print(Var_leafBool)
                self.report({'INFO'}, "Exported with custom prefix and mesh name")
            else:
                print("No Prefix Defined", context.mode)

        #If the user does not check "use prefix" the object will be exported as the mesh name only
        #this is the default "export selected" button
        else:
            print("DID NOT USE PREFIX")
            #If the "export counter" bool is true then we add the counter varable to the end of the save location
            if Var_counterBool == True:
                saveLoc = self.filepath.replace(blendName,"") + name + Var_exportnumber
            else:
                saveLoc = self.filepath.replace(blendName,"") + name
                
            if not bpy.data.is_saved:
                raise Exception("Blend file is not saved")
                print("SAVE YOUR FILE")
                
            else:
                bpy.ops.export_scene.fbx(
                filepath = saveLoc.replace('.fbx', '')+  ".fbx",
                use_mesh_modifiers=True,
                bake_anim_use_all_actions = Var_actionsBool,
                add_leaf_bones = Var_leafBool,
                check_existing=True, 
                axis_forward='-Z', 
                axis_up='Y', 
                use_selection=True, 
                global_scale=1, 
                path_mode='AUTO')
            print(saveLoc)  
            print(Var_actionsBool)
            print(Var_leafBool)
            self.report({'INFO'}, "Exported with mesh name")
        return {'FINISHED'}
    
#-----------------------------------------------------#  
#   Registration classes
#-----------------------------------------------------#  

classes = (DarrowCounterReset, DarrowApply, DarrowCleanMesh, DarrowWireframe, DarrowWireframeReset, DarrowSetOrigin, DarrowSetSnapOrigin, DarrowMoveOrigin, DarrowExportFBX, DarrowToolPanel, DarrowExportPanel, DarrowTransforms, DarrowNormals, DarrowSmooth,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
          

    bpy.types.Scene.allactionsBool = bpy.props.BoolProperty(
    name = "All actions",
    description = "Export each action separated separately",
    default = False
    )

    bpy.types.Scene.isleafBool = bpy.props.BoolProperty(
    name = "Leaf bones",
    description = "Exporting using leaf bones",
    default = False
    )

    bpy.types.Scene.useprefixBool = bpy.props.BoolProperty(
    name = "Use Prefix",
    description = "Export selected object with custom text as a prefix",
    default = False
    )

    bpy.types.Scene.usecounterBool = bpy.props.BoolProperty(
    name = "Use Suffix",
    description = "Count exports and use as suffex",
    default = False
    )
    
    bpy.types.Scene.custom_name_string = bpy.props.StringProperty(
    name = "",
    description = "Custom Prefix",
    default = "Assets"
    )

    bpy.types.Scene.counter = bpy.props.IntProperty(
    default = 0
    )
    
    bpy.types.Scene.PrefixOption = bpy.props.EnumProperty(
    name="",
    description="Apply Data to attribute.",
    items=[('OP1', ".blend", ""),
           ('OP2', "custom", ""),
        ]
    )

def unregister():
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()