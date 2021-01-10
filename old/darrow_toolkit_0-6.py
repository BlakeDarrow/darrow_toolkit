#info for plugin
bl_info = {
    "name": "Darrow Toolkit",
    "author": "Blake Darrow",
    "version": (0, 6),
    "blender": (2, 90, 0),
    "location": "View3D > Sidebar > Darrow Toolkit",
    "description": "Darrow Toolkit",
    "category": "Tools"
    }
#-----------------------------------------------------#  
#	Imports
#-----------------------------------------------------#  
import bpy
import bgl
import gpu
import math
import getopt
import os

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
#-----------------------------------------------------#  

#main panel menu logic
class DarrowToolPanel(bpy.types.Panel):
    bl_label = "Darrow Toolkit"
    bl_category = "Darrow Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        split=layout.split()
        col=split.column(align = True)
        
        if obj is not None:
            # Actual panel buttons and logic
            col.label(text = "Object Origin")
            if context.mode == 'EDIT_MESH':
                 col.operator('set.origin')
            
            if context.mode == 'OBJECT':
                col.operator('move.origin')
                col.separator()
                #disabled "Apply All" button for orgin and move
                #col.operator('setsnap.origin')
            col.separator()
            if context.mode == 'OBJECT':
                col.label(text = "Export Checklist")
                layout.operator('apply_all.darrow')
                
            if context.mode == 'OBJECT':
                col.operator('shade.smooth')
                col.operator('apply.transforms')
                col.operator('apply.normals')
            layout.separator()
            box = layout.box()

            box.label(text = "Export as FBX")
            box.operator('export_selected.darrow')
            box.prop(obj, 'useprefixBool')
            
            #Variables for the bools and enums
            Var_prefix_bool = bpy.context.object.useprefixBool
            Var_custom_prefix = bpy.context.object.PrefixOption

            #If use prefix is selected then these options show up
            if Var_prefix_bool == True:   
                box.prop(obj, 'PrefixOption')
                #If the custom enum is selected these show up
                if Var_custom_prefix == 'OP2':
                    box.prop(context.scene, "my_string_prop", text="Prefix")
          
#Button to apply all transformations
class DarrowTransforms(bpy.types.Operator):
    bl_idname = "apply.transforms"
    bl_description = "Apply transformations to selected object"
    bl_label = "Apply Transforms"

    def execute(self, context):
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        self.report({'INFO'}, "Transforms applied")
        return {'FINISHED'}
    
#Set Objects origin
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
        self.report({'INFO'}, "Selected is now origin")
        return {'FINISHED'}
    
#Snap object to world center
class DarrowMoveOrigin(bpy.types.Operator):
    bl_idname = "move.origin"
    bl_description = "Move selected to world origin"
    bl_label = "Align to world"

    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        self.report({'INFO'}, "Moved selected to object origin")
        return {'FINISHED'}
    
#Set Objects origin and move to world origin
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
        return {'FINISHED'}

#Button to apply outside calculated normals
class DarrowNormals(bpy.types.Operator):
    bl_idname = "apply.normals"
    bl_description = "Calculate outside normals"
    bl_label = "Calculate Normals"

    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.editmode_toggle()
        self.report({'INFO'}, "Normals calculated outside")
        return {'FINISHED'}
    
#Button to smooth mesh
class DarrowSmooth(bpy.types.Operator):
    bl_idname = "shade.smooth"
    bl_label = "Smooth Object"
    bl_description = "Smooth the selected object"

    def execute(self, context):
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        self.report({'INFO'}, "Object smoothed")
        return {'FINISHED'}
        
#Button to apply all checklisted items
class DarrowApply(bpy.types.Operator):
    bl_idname = "apply_all.darrow"
    bl_label = "Apply All"
    bl_description = "Apply all checklist functions"

    def execute(self, context):
        
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
        if context.mode == 'OBJECT':
            bpy.ops.object.editmode_toggle()
            
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.editmode_toggle()
        self.report({'INFO'}, "Applied transforms, smoothed mesh, and calculated normals")
        return {'FINISHED'}
   
#Logic for exporting as FBX
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
        name = bpy.path.clean_name(fbxname.name)

        #Variables for UI, like bools and enums
        Var_PrefixBool = bpy.context.object.useprefixBool
        Var_custom_prefix = bpy.context.object.PrefixOption
        
        #If "Use Prefix" box selected, the 2 prefix options will show up in the enum
        if not bpy.data.is_saved:
                raise Exception("Blend file is not saved")
                print("SAVE YOUR FILE")
        
        if Var_PrefixBool == True:
            print("USED PREFIX")
                  
        #if Use Custom Prefix 1 is selected, the object will export with custom prefix + mesh name
            if Var_custom_prefix == 'OP1':
                saveLoc = self.filepath + "_" + name
                bpy.ops.export_scene.fbx(
                    filepath = saveLoc.replace('.fbx', '')+ ".fbx",
                    check_existing=True, 
                    axis_forward='-Z', 
                    axis_up='Y', 
                    use_selection=True, 
                    global_scale=1, 
                    path_mode='AUTO')
                    
                self.report({'INFO'}, "Exported with .blend prefix and mesh name") 
                return {'FINISHED'}
            else:
                print("No Prefix Defined", context.mode)

        #If Use Custom Prefix 2 is selected, the object will export with custom prefix + mesh name
            if Var_custom_prefix == 'OP2':
                #Variables for prefix naming
                customprefix = bpy.context.scene.my_string_prop
                customname = customprefix + "_" + name
                blendName = bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend", "")
                saveLoc = self.filepath.replace(blendName,'') + customname
                #export logic
                bpy.ops.export_scene.fbx(
                    filepath = saveLoc.replace(".fbx", '')+ ".fbx",
                    check_existing=True, 
                    axis_forward='-Z', 
                    axis_up='Y', 
                    use_selection=True, 
                    global_scale=1, 
                    path_mode='AUTO')
                    
                self.report({'INFO'}, "Exported with custom prefix and mesh name")
            else:
                print("No Prefix Defined", context.mode)

        #If the user does not check "use prefix" the object will be exported as the mesh name only
        #this is the default "export selected" button
        else:
            print("DID NOT USE PREFIX")
            #To export with a relative 
            blendName = bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend", "")
            saveLoc = self.filepath.replace(blendName,"") + name
            if not bpy.data.is_saved:
                raise Exception("Blend file is not saved")
                print("SAVE YOUR FILE")
                
            else:
                bpy.ops.export_scene.fbx(
                filepath = saveLoc.replace('.fbx', '')+  ".fbx",
                check_existing=True, 
                axis_forward='-Z', 
                axis_up='Y', 
                use_selection=True, 
                global_scale=1, 
                path_mode='AUTO')
            self.report({'INFO'}, "Exported with mesh name")
        return {'FINISHED'}
    
#-----------------------------------------------------#  
#	Registration classes
#-----------------------------------------------------#  

def register():
    
    bpy.utils.register_class(DarrowApply)
    bpy.utils.register_class(DarrowSetOrigin)
    bpy.utils.register_class(DarrowSetSnapOrigin)    
    bpy.utils.register_class(DarrowMoveOrigin)
    bpy.utils.register_class(DarrowExportFBX)
    bpy.utils.register_class(DarrowToolPanel)
    bpy.utils.register_class(DarrowTransforms)
    bpy.utils.register_class(DarrowNormals)
    bpy.utils.register_class(DarrowSmooth)

    
    bpy.types.Object.useprefixBool = BoolProperty(
    name = "Use Prefix",
    description = "Export selected object with custom text as a prefix",
    default = False
    )

    bpy.types.Scene.my_string_prop = bpy.props.StringProperty(
    name = "",
    description = "Custom Prefix",
    default = "Assets"
    )
    
    bpy.types.Object.PrefixOption = EnumProperty(
    name="",
    description="Apply Data to attribute.",
    items=[('OP1', ".blend", ""),
           ('OP2', "custom", ""),
        ]
    )
    
def unregister():
    
    bpy.utils.unregister_class(DarrowApply)
    bpy.utils.unregister_class(DarrowSetOrigin)
    bpy.utils.unregister_class(DarrowSetSnapOrigin) 
    bpy.utils.unregister_class(DarrowMoveOrigin)
    bpy.utils.unregister_class(DarrowToolPanel)
    bpy.utils.unregister_class(DarrowTransforms)
    bpy.utils.unregister_class(DarrowNormals)
    bpy.utils.unregister_class(DarrowSmooth)
    bpy.utils.unregister_class(DarrowExportFBX)

if __name__ == "__main__":
    register()