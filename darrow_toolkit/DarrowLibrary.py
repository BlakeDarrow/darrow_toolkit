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
from bpy.types import WindowManager
import addon_utils
import os
from platform import system as currentOS
import math
import random
import bpy.utils.previews
from mathutils import Vector, Matrix
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
from bpy.props import (
        StringProperty,
        EnumProperty,
    )

#-----------------------------------------------------#  
#   handles OS file broswer if Windows
#-----------------------------------------------------# 
class meshFolder(bpy.types.Operator):
    """Open the Mesh Folder in a file Browser"""
    bl_idname = "file.mesh_folder"
    bl_label = "Mesh"
    
    def execute(self, context):
        try :
            addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
            meshpath = addonpath + "\mesh\\" #add folder with the custom mesh inside
            os.makedirs(os.path.dirname(meshpath), exist_ok=True)
            path = meshpath
        except ValueError:
            self.report({'INFO'}, "No folder yet")
            return {'FINISHED'}
        bpy.ops.wm.path_open(filepath=path)
        return {'FINISHED'}

    def path(self):
        filepath = bpy.data.filepath
        relpath = bpy.path.relpath(filepath)
        path = filepath[0: -1 * (relpath.__len__() - 2)]
        return path

class renderFolder(bpy.types.Operator):
    """Open the Render Folder in a file Browser"""
    bl_idname = "file.thumbnail_folder"
    bl_label = "Thumbnails"
    
    def execute(self, context):
        try :
            addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
            meshpath = addonpath + "\\thumbnails\\" #add folder with the custom mesh inside
            os.makedirs(os.path.dirname(meshpath), exist_ok=True)
            path = meshpath
        except ValueError:
            self.report({'INFO'}, "No folder yet")
            return {'FINISHED'}
        
        bpy.ops.wm.path_open(filepath=path)
        return {'FINISHED'}

    def path(self):
        filepath = bpy.data.filepath
        relpath = bpy.path.relpath(filepath)
        path = filepath[0: -1 * (relpath.__len__() - 2)]
        return path

#-----------------------------------------------------#  
#   handles directory items
#-----------------------------------------------------# 
def enum_previews_from_directory_items(self, context):
    """EnumProperty callback"""
    enum_items = []

    if context is None:
        return enum_items

    wm = context.window_manager
    addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
    renderpath = addonpath + "\\thumbnails\\" #folder for renders
    directory = renderpath

    # Get the preview collection (defined in register func).
    pcoll = preview_collections["main"]

    if directory and os.path.exists(directory):
        # Scan the directory for png files
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            enum_items.append((name, name, name, thumb.icon_id, i))
    pcoll.my_previews = enum_items
    return pcoll.my_previews

#-----------------------------------------------------#  
#     handles  ui     
#-----------------------------------------------------#  
class DarrowDevPanel:
    bl_category = "Darrow Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_devPanel"

    @classmethod
    def poll(cls, context):
        settings = context.preferences.addons[__package__].preferences

        return settings.library_moduleBool == True

class DarrowMainPanel(DarrowDevPanel, bpy.types.Panel):
    bl_label = "DarrowLibrary"
    bl_idname = "DARROW_PT_devPanel1"

    @classmethod
    def poll(cls, context):
        settings = context.preferences.addons[__package__].preferences
        obj = context.active_object
        for obj in bpy.context.selected_objects:
            if obj.type =='CURVE' : return False
            if obj.type =='CAMERA' : return False
            if obj.type =='LIGHT' : return False
            if obj.type =='FONT' : return False
            if obj.type =='LATTICE' : return False
            if obj.type =='LIGHT_PROBE' : return False
            if obj.type =='IMAGE' : return False
            if obj.type =='SPEAKER' : return False

        return settings.library_moduleBool == True
            #print("poll")

    def draw_header(self, context):
        settings = context.preferences.addons[__package__].preferences
        self.layout.prop(settings, 'advancedLibraryBool', icon="SETTINGS",text="")

    def draw(self, context):
        settings = context.preferences.addons[__package__].preferences
        getBool = bpy.context.scene.getBool
        addBool = bpy.context.scene.addBool
        nullBool = bpy.context.scene.nullBool
        folderBool = settings.advancedLibraryBool
    
        layout = self.layout
        wm = context.window_manager
        obj = context.object
        scn = context.scene

        if folderBool == True:
            box=layout.box()
            box.label(text = "Folder Locations", icon="FILE_FOLDER")
            box.scale_y = 1.2
            box=box.row(align = True)
            box.operator('file.mesh_folder',icon="FILE_PARENT")
            box.operator('file.thumbnail_folder')
            
        box=layout.box()
        box.label(text = "Select Operation", icon="MODIFIER")
        label_add = "Add" if getBool ^1 else "Add"
        label_get = "Get" if addBool ^1 else "Get"

        if getBool and addBool == True:
            getBool = False
            addBool = False
            advancedBool = False

            label_get = "select one"
            label_add = "select one"
        
        row = layout.row(align=True)
        row.scale_y = 2
        row.prop(scn, 'addBool',  toggle=True, text = label_add,icon="EXPORT")
        if getBool == True: 
            row.enabled = False

        row = layout.row(align=True)
        row.scale_y = 2
        row.prop(scn, 'getBool',  toggle=True, text = label_get,icon="IMPORT")
        if addBool == True:
            row.enabled = False 
        if addBool == True:
            if obj is not None:

                box=layout.box()
                box.label(text="Settings")
                box.prop(scn, 'autoCamGenBool')
                box.prop(scn, 'showWireframeRenderBool')

                box=layout.box()
                box= box.column(align = True)
                box.scale_y = 3
                box.operator('darrow.add_to_library', text = "Add to library", icon="EXPORT")
                row=layout.column(align = False)
                row.scale_y = 1
                row.prop(context.scene, "tag_name", text="Tag",icon="WORDWRAP_ON") 

        if getBool == True:
            layout = self.layout
            layout.label(text="Previews")
            row = layout.row()
            row.scale_y = .5
            row.template_icon_view(wm, "my_previews", show_labels = 1, scale = 18.5,scale_popup=5)
            row=layout.column(align = False)
            row.scale_y = 2.5
            row.operator_menu_enum("object.asset_library", "mesh_enum_prop", text="Get from library", icon="IMPORT")
            row=layout.column(align = False)
            row.scale_y = 1
            row.prop(scn, 'tag_enum_prop', text="Filter")

            #box=layout.box()
            #box.prop(scn, 'cursorLocBool')

        if obj is None and addBool == True:
            box=layout.box()
            box=box.column(align = True)
            box.label(text = "Please select a mesh")

#-----------------------------------------------------#  
#    Handles Thumbnail Creation
#-----------------------------------------------------#  
class DarrowThumbnail(bpy.types.Operator):
    bl_idname= "darrow.create_thumbnail"
    bl_label = "Generate Thumbnail"

    def execute(self, context):
        print("execute")

        fbxname = bpy.context.view_layer.objects.active
        name = fbxname.name
        print(name)

        if bpy.context.scene.autoCamGenBool == True:
            camera_data = bpy.data.cameras.new(name='Thumbnail_Camera_Darrow')
            camera_object = bpy.data.objects.new('Thumbnail_Camera_Darrow', camera_data)
            bpy.context.scene.collection.objects.link(camera_object)

            cam = camera_object
            target = bpy.context.view_layer.objects.active

            dist = target.dimensions * 2.5
            cam.location = dist
            bpy.context.scene.render.resolution_x = 1080
            bpy.context.scene.render.resolution_y = 1080

            constraint = cam.constraints.new(type='TRACK_TO')
            constraint2 = cam.constraints.new(type='LIMIT_DISTANCE')
            
            constraint.target = target
            constraint2.target = target
            constraint2.limit_mode = 'LIMITDIST_OUTSIDE'
            constraint2.distance = 5

            bpy.context.view_layer.objects.active = cam
            bpy.ops.view3d.object_as_camera()
            target.select_set(state=False)
        else:
            fbxname.select_set(state=False)

        addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
        meshpath = addonpath + "\\thumbnails\\" #folder for renders

        if bpy.context.scene.showWireframeRenderBool == True:
            bpy.context.space_data.show_gizmo = False
            bpy.context.space_data.overlay.show_floor = False
            bpy.context.space_data.overlay.show_axis_y = False
            bpy.context.space_data.overlay.show_axis_x = False
            bpy.context.space_data.overlay.show_cursor = False
            bpy.context.space_data.overlay.show_object_origins = False
            #bpy.context.space_data.overlay.show_wireframes = True

        print(bpy.context.scene.showWireframeRenderBool)
        bpy.context.scene.render.filepath = meshpath + name + ".jpg"
        #bpy.ops.render.render(write_still = True)
        bpy.ops.render.opengl(write_still = True)
        if bpy.context.scene.autoCamGenBool == True:
            bpy.data.objects.remove(cam)
        else:
            print("no auto camera")

        if bpy.context.scene.showWireframeRenderBool == True:
            bpy.context.space_data.show_gizmo = True
            bpy.context.space_data.overlay.show_floor = True
            bpy.context.space_data.overlay.show_axis_y = True
            bpy.context.space_data.overlay.show_axis_x = True
            bpy.context.space_data.overlay.show_cursor = True
            bpy.context.space_data.overlay.show_object_origins = True
            #bpy.context.space_data.overlay.show_wireframes = False

        fbxname.select_set(state=True)
        return {'FINISHED'}

#-----------------------------------------------------#  
#    Returns a dict of all mesh with unique identifier
#-----------------------------------------------------#  
def mesh_items(scene, context):
    f = []

    currentTag = bpy.context.scene.tag_enum_prop
    addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
    meshpath = addonpath + "\mesh\\" + currentTag #add folder with the custom mesh inside

    for (dirpath, dirnames, filenames) in walk(meshpath):
        f.extend(filenames)
        break

    meshNames = { i : f[i] for i in range(0, len(f) ) }

    items = []
    for name, name in meshNames.items():
        items.append((name, name, str(name)))  # name is used as identifier
    print(items)
    return items

def tag_items(scene,context):
    tags = []
    addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
    meshpath = addonpath + "\mesh\\" #add folder with the custom mesh inside
    os.chdir(meshpath)

    foldernames= os.listdir (".") # get all files' and folders' names in the current directory
    for name in foldernames: # loop through all the files and folders
        if os.path.isdir(os.path.join(os.path.abspath("."), name)): # check whether the current object is a folder or not
            tags.append(name)
    tagData = { i : tags[i] for i in range(0, len(tags) ) }

    folders = []
    for name, name in tagData.items():
        folders.append((name, name, str(name)))  # name is used as identifier
    print(folders)
    return folders

#-----------------------------------------------------#  
#    Get mesh from library
#-----------------------------------------------------#  
class OBJECT_OT_mesh_library(bpy.types.Operator):
    """Get mesh from current library"""
    bl_idname = "object.asset_library"
    bl_label = "Import to scene"
    bl_options = {'REGISTER', 'UNDO'}

    mesh_enum_prop : bpy.props.EnumProperty(items=mesh_items, description="Mesh to import")
    
    def execute(self, context):
        print("Hello world")
        name = self.mesh_enum_prop
        currentTag = bpy.context.scene.tag_enum_prop
        print(name)
  
        addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
        meshpath = addonpath + "\mesh\\" #add folder with the custom mesh inside
        
        tagpath = meshpath + currentTag + "\\"

        finalpath = tagpath + name #add name of custom mesh to the end
        print(finalpath)

        cursorLocBool = bpy.context.scene.cursorLocBool

        bpy.ops.import_scene.fbx(filepath = finalpath) #import the selected mesh
        if cursorLocBool == True:
            bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

        mesh_items(self,context) #update enum list of assets
        self.report({'INFO'}, f"{name}")
        return {'FINISHED'}

#-----------------------------------------------------#  
#    Add mesh to library
#-----------------------------------------------------#  
class DarrowAddMeshtoLibrary(Operator):
    """Add selected mesh to the library using the current tag"""
    bl_idname = "darrow.add_to_library"
    bl_label = "Add Selected to Library"
    filename_ext    = ".fbx";
    
    def execute(self, context):
        objs = context.selected_objects
        if len(objs) is not 0: 
            tagString = bpy.context.scene.tag_name #if this is null, no folder is created
            fbxname = bpy.context.view_layer.objects.active
            exportmeshName = bpy.path.clean_name(fbxname.name)
            addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
            tryPath = addonpath + "\mesh\\"
            meshpath = addonpath + "\mesh\\" #add folder with the custom mesh inside
            os.makedirs(os.path.dirname(meshpath), exist_ok=True)
            finalpath = meshpath + tagString + "\\"+ exportmeshName + ".fbx" #add name of selected mesh to the end

            os.chdir(meshpath)
            try:
                os.mkdir(tagString)
            except:
                print("tag folder already created")

            bpy.ops.export_scene.fbx(
            filepath = finalpath,
            use_selection=True,
                )

            DarrowThumbnail.execute(self,context)
        else:
            self.report({'INFO'}, "None Selected")
        return {'FINISHED'}

#-----------------------------------------------------#  
#   Registration classes
#-----------------------------------------------------#  
preview_collections = {}
classes = (DarrowMainPanel,DarrowThumbnail, DarrowAddMeshtoLibrary,OBJECT_OT_mesh_library,meshFolder,renderFolder)

def register():
#-----------------------------------------------------#  
#-----------------------------------------------------# 
    WindowManager.my_previews = EnumProperty(
        items=enum_previews_from_directory_items,

    )
    pcoll = bpy.utils.previews.new()
    pcoll.my_previews = ()
    preview_collections["main"] = pcoll
#-----------------------------------------------------#  
#-----------------------------------------------------# 

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.tag_enum_prop = bpy.props.EnumProperty(
        items=tag_items, 
        description="Tag to show",
        name="",
        )

    bpy.types.Scene.mesh_name = bpy.props.StringProperty(
        subtype="FILE_PATH",
    )

    bpy.types.Scene.tag_name = bpy.props.StringProperty(
        name = "",
        description = "Master",
        default = "Master"
    )

    bpy.types.Scene.cursorLocBool = bpy.props.BoolProperty(
        default = True,
        name = "Spawn at Cursor Location"
    )

    bpy.types.Scene.showWireframeRenderBool = bpy.props.BoolProperty(
        default = True,
        name = "Hide Overlays in Thumbnail"
    )
    
    bpy.types.Scene.library_list = bpy.props.StringProperty(
    
    )


    bpy.types.Scene.autoCamGenBool = bpy.props.BoolProperty(
    name = "Generate Thumbnail Camera",
    default = True,
    description = "Generate camera for thumbnail automatically(limited)"
    )

    bpy.types.Scene.getBool = bpy.props.BoolProperty(
    name = "Get bool",
    default = False,
    description="Get mesh overlay"
    )

    bpy.types.Scene.addBool = bpy.props.BoolProperty(
    name = "Add bool",
    default = False,
    description="Add mesh overlay"
    )

    bpy.types.Scene.nullBool = bpy.props.BoolProperty(
    name = "",
    default = False
    )

def unregister():

    del WindowManager.my_previews

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()