#-----------------------------------------------------#  
#   Imports
#-----------------------------------------------------#  
import bpy
import addon_utils
import os
from os import walk
from bpy_extras.io_utils import ImportHelper
from bpy_extras.io_utils import ExportHelper
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       StringProperty,
                       EnumProperty,
                       PropertyGroup
                       )
  
#-----------------------------------------------------#  
#     handles checklist ui     
#-----------------------------------------------------#  
class DarrowDevPanel:
    bl_category = "Darrow Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_devPanel"

    @classmethod
    def poll(cls, context):
        return bpy.context.scene.library_moduleBool == True


class DarrowMainPanel(DarrowDevPanel, bpy.types.Panel):
    bl_label = "DarrowLibrary"
    bl_idname = "DARROW_PT_devPanel1"

    def draw(self, context):
        layout = self.layout
        split=layout.box()
        col=split.column(align = True)
        obj = context.object
        if obj is not None:
            col.label(text = "Add Mesh to Library")
            col.separator()
            col.operator('darrow.add_to_library')
            col.separator()
            col.separator()
        col.operator_menu_enum("object.property_darrow", "mesh_enum_prop", text="Geometry to import")
    
class DarrowSubPanel(DarrowDevPanel, bpy.types.Panel):
    bl_parent_id = "DARROW_PT_devPanel1"
    bl_label = "Current Geometry List"
    bl_idname = "DARROW_PT_devPanel2"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):

        layout = self.layout
        f = []
        addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
        meshpath = addonpath + "\mesh\\" #add folder with the custom mesh inside
        for (dirpath, dirnames, filenames) in walk(meshpath):
            f.extend(filenames)
            break

        for m in f:
            layout.label(text=m.replace('.fbx',''))

def mesh_items(scene, context):
    f = []
    addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
    meshpath = addonpath + "\mesh\\" #add folder with the custom mesh inside
    for (dirpath, dirnames, filenames) in walk(meshpath):
        f.extend(filenames)
        break

    meshNames = { i : f[i] for i in range(0, len(f) ) }

    items = []
    for name, name in meshNames.items():
        items.append((name, name, str(name)))  # name is used as identifier
    print(items)
    return items

class OBJECT_OT_mesh_library(bpy.types.Operator):
    bl_idname = "object.property_darrow"
    bl_label = "Import to scene"
    bl_options = {'REGISTER', 'UNDO'}

    mesh_enum_prop = bpy.props.EnumProperty(items=mesh_items)

    def execute(self, context):
        name = self.mesh_enum_prop
        addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
        meshpath = addonpath + "\mesh\\" #add folder with the custom mesh inside
        finalpath = meshpath + name #add name of custom mesh to the end

        bpy.ops.import_scene.fbx(filepath = finalpath) #import the mesh
        mesh_items(self,context)
        self.report({'INFO'}, f"{name}")
        return {'FINISHED'}

#-----------------------------------------------------#  
#    Add selected mesh to addon "mesh" folder
#-----------------------------------------------------#  

class DarrowAddMeshtoLibrary(Operator):
    bl_idname = "darrow.add_to_library"
    bl_label = "Add Selected to Library"
    filename_ext    = ".fbx";
    
    def execute(self, context):

        fbxname = bpy.context.view_layer.objects.active
        exportmeshName = bpy.path.clean_name(fbxname.name)
        addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
        meshpath = addonpath + "\mesh\\" #add folder with the custom mesh inside
        finalpath = meshpath + exportmeshName + ".fbx" #add name of selected mesh to the end

        bpy.ops.export_scene.fbx(filepath = finalpath)
        return {'FINISHED'}

#-----------------------------------------------------#  
#   Registration classes
#-----------------------------------------------------#  

classes = (DarrowMainPanel,DarrowSubPanel,DarrowAddMeshtoLibrary,OBJECT_OT_mesh_library)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.mesh_name = bpy.props.StringProperty(
        subtype="FILE_PATH"
    )

    bpy.types.Scene.library_list = bpy.props.StringProperty(
    
    )

    bpy.types.Scene.meshAdvancedBool = bpy.props.BoolProperty(
    name = "Advanced",
    default = True
    )

def unregister():
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()