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
import os
from pathlib import Path
import math
from bpy_extras.io_utils import (ImportHelper,
                                 ExportHelper,
                                 path_reference_mode,
                                 )
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       EnumProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       )

#-----------------------------------------------------#  
#     handles export panel     
#-----------------------------------------------------#                    
class DarrowExportPanel(bpy.types.Panel):
    bl_label = "DarrowFBX"
    bl_category = "Darrow Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_exportPanel"

    @classmethod
    def poll(cls, context):
        settings = context.preferences.addons[__package__].preferences
        obj = context.active_object
        preferences = context.preferences
        for obj in bpy.context.selected_objects:
            if obj.type =='CURVE' : return False
            if obj.type =='CAMERA' : return False
            if obj.type =='LIGHT' : return False
            if obj.type =='FONT' : return False
            if obj.type =='LATTICE' : return False
            if obj.type =='LIGHT_PROBE' : return False
            if obj.type =='IMAGE' : return False
            if obj.type =='SPEAKER' : return False

        return settings.export_moduleBool == True
            #print("poll")

    def draw_header(self, context):
        settings = context.preferences.addons[__package__].preferences
        layout = self.layout
        obj = context.scene
        self.layout.prop(settings, 'advancedExportBool', icon="SETTINGS",text="")

    def draw(self, context):
        settings = context.preferences.addons[__package__].preferences
        Var_prefix_bool = bpy.context.scene.useprefixBool
        Var_suffix_bool = bpy.context.scene.usecounterBool
        Var_custom_prefix = bpy.context.scene.PrefixOption
        Var_advanced_bool = settings.advancedExportBool
        Var_allowFBX = bpy.context.scene.fbxBool
        obj = context.object
        objs = context.selected_objects

        if context.mode == 'OBJECT':
            if obj is not None:  
                layout = self.layout
                obj = context.scene
                layout.prop(settings, 'exportPresets')

                if Var_advanced_bool ==True:
                    box = layout.box()
                    box.label(text = "Animation Options")
                    split=box.split()
                    split.prop(obj, 'isleafBool')
                    split.prop(obj, 'allactionsBool')
                    box = layout.box()
                    split=box.split()
                    split.prop(obj, 'collectionBool')
        
                box = layout.box()
                box.label(text = "FBX Exporter")
               
                if len(objs) is not 0: 
                    Var_allowFBX = True
                box.operator('export_selected.darrow', icon="EXPORT")
                if Var_allowFBX == False:
                    box.enabled = False 

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

        if context.mode == 'EDIT_MESH':
            layout = self.layout
        
#-----------------------------------------------------#  
#    Find selected parent collection
#-----------------------------------------------------#  
def get_parent_collection_names(collection, parent_names):
  for parent_collection in bpy.data.collections:
    if collection.name in parent_collection.children.keys():
      parent_names.append(parent_collection.name)
      get_parent_collection_names(parent_collection, parent_names)
      return

def turn_collection_hierarchy_into_path(obj):
    parent_collection = obj.users_collection[0]
    parent_names      = []
    parent_names.append(parent_collection.name)
    get_parent_collection_names(parent_collection, parent_names)
    parent_names.reverse()
    return '\\'.join(parent_names)

#-----------------------------------------------------#  
#    Handles logic for exporting as FBX
#-----------------------------------------------------#
class DarrowExportFBX(bpy.types.Operator, ExportHelper):
    bl_idname = "export_selected.darrow"
    bl_label = 'Export Selected'
    bl_description = "Export selected as FBX using mesh name"
    bl_options = {'PRESET'}
    filename_ext    = ".fbx";

    """ 
    This class needs massive amounts of refactoring. Very slow.
    """

    def execute(self, context):
        settings = context.preferences.addons[__package__].preferences
        objs = context.selected_objects
        if len(objs) is not 0: 
            C = bpy.context
            fbxname = bpy.context.view_layer.objects.active
            #get fbx name
            name = bpy.path.clean_name(fbxname.name)
            Var_collectionBool = bpy.context.scene.collectionBool
            
            # Find amount of objects in selection
            amt = len(C.selected_objects)
            one = 1

            obj = bpy.context.view_layer.objects.active
            parent_coll = turn_collection_hierarchy_into_path(obj)

            if (Var_collectionBool == True) and (amt > one):
                fbxname = parent_coll
                name = bpy.path.clean_name(fbxname)
                print(name)
                print("MORE THAN 1 MESH, SELECTED. USING COLLECTION NAME TO EXPORT")

            bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=True)
            #option to show in exporter
            path_mode = path_reference_mode
            #get the name of the active object
            #get string of custom prefix user input
            customprefix = bpy.context.scene.custom_name_string

            #get blend name
            blendName = bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend", "")
        
            #Variables for UI, like bools and enums

            Var_actionsBool = bpy.context.scene.allactionsBool
            Var_leafBool = bpy.context.scene.isleafBool
            Var_PrefixBool = bpy.context.scene.useprefixBool
            Var_custom_prefix = bpy.context.scene.PrefixOption
            Var_presets =settings.exportPresets
            Var_counterBool = bpy.context.scene.usecounterBool
            
            if Var_presets == 'OP1':
                if (amt > one):
                    Var_axisUp = 'Y'
                    Var_axisForward = 'X'
                    Var_scale = 1
                    print("more than one, not rotating")
                else:
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                    bpy.context.active_object.rotation_euler[0] = math.radians(-90)
                    print("rotated -90")
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                    print("rotations applied")
                    bpy.context.active_object.rotation_euler[0] = math.radians(90)
                    print("rotated 90")
                    Var_axisUp = 'Y'
                    Var_axisForward = 'X'
                    Var_scale = 1
                    print("rotating")
                print("Unity Exporter")

            if Var_presets == 'OP2':
                Var_axisUp = 'Z'
                Var_axisForward = '-Y'
                Var_scale = 1
                print("Unreal Exporter")

            Var_nlaBool = False
            Var_forcestartkey = False

            if Var_presets == 'OP1':
                Var_leafBool = False
                Var_actionsBool = False
                Var_nlaBool = False
                Var_forcestartkey = False
                print("Unity Vars")

            if Var_presets == 'OP2':
                Var_nlaBool = False
                Var_leafBool = False
                Var_actionsBool = False
                Var_forcestartkey = True
                print("Unreal Vars")

            #get the counter and add "1" to it, only when bool is checked
            if Var_counterBool == True:
                context.scene.counter += 1
                count = context.scene.counter
                count = str(count)
                Var_exportnumber = "_" + count
            
            #If "Use Prefix" box selected, the 2 prefix options will show up in the enum
            # Hopefull these vars (deteremined in advanced panel) will overwrite all presets 
            Var_actionsBool = bpy.context.scene.allactionsBool
            Var_leafBool = bpy.context.scene.isleafBool
            
            if Var_PrefixBool == True:
                print("USED PREFIX")

            #if ".blend enum" is selected, the object will export with custom prefix + mesh name
                if Var_custom_prefix == 'OP1':
                    
                    if not bpy.data.is_saved:
                            raise Exception("Blend file is not saved")
                            print("SAVE YOUR FILE")
                    
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
                        bake_anim_use_nla_strips = Var_nlaBool,
                        bake_anim_force_startend_keying = Var_forcestartkey,
                        check_existing=True, 
                        axis_forward= Var_axisForward, 
                        axis_up= Var_axisUp, 
                        use_selection=True, 
                        global_scale= Var_scale, 
                        path_mode='AUTO')

                    #print(Var_actionsBool)
                    #print(Var_leafBool)
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
                                
                    if not bpy.data.is_saved:
                        saveLoc = self.filepath.replace("untitled","") + customname
                    else:
                        saveLoc = self.filepath.replace(blendName,'') + customname  
                        
                    #print(saveLoc)
                    #export logic
                    bpy.ops.export_scene.fbx(
                        filepath = saveLoc.replace(".fbx", '')+ ".fbx",
                        use_mesh_modifiers=True,
                        bake_anim_use_all_actions = Var_actionsBool,
                        add_leaf_bones = Var_leafBool,
                        bake_anim_use_nla_strips = Var_nlaBool,
                        bake_anim_force_startend_keying = Var_forcestartkey,
                        check_existing=True, 
                        axis_forward= Var_axisForward, 
                        axis_up= Var_axisUp, 
                        use_selection=True, 
                        global_scale= Var_scale, 
                        path_mode='AUTO')
                    #print(Var_actionsBool)
                    #print(Var_leafBool)
                    self.report({'INFO'}, "Exported with custom prefix and mesh name")
                else:
                    print("No Prefix Defined", context.mode)

            #If the user does not check "use prefix" the object will be exported as the mesh name only
            #this is the default "export selected" button
            else:
                #print("DID NOT USE PREFIX")
                #If the "export counter" bool is true then we add the counter varable to the end of the save location
                if Var_counterBool == True:
                    if not bpy.data.is_saved:
                        #raise Exception("Blend file is not saved")
                        saveLoc = self.filepath.replace("untitled","") + name + Var_exportnumber
                    else:
                        saveLoc = self.filepath.replace(blendName,"") + name + Var_exportnumber  
                    
                else:
                    saveLoc = self.filepath.replace(blendName,"") + name
                    
                    if not bpy.data.is_saved:
                        #raise Exception("Blend file is not saved")
                        saveLoc = self.filepath.replace("untitled","") + name
                    print("SAVE YOUR FILE")

                bpy.ops.export_scene.fbx(
                    filepath = saveLoc.replace('.fbx', '')+  ".fbx",
                    use_selection=True, 
                    use_mesh_modifiers=True,
                    bake_anim_use_all_actions = Var_actionsBool,
                    add_leaf_bones = Var_leafBool,
                    bake_anim_use_nla_strips = Var_nlaBool,
                    bake_anim_force_startend_keying = Var_forcestartkey,
                    check_existing=True, 
                    axis_forward=Var_axisForward, 
                    axis_up= Var_axisUp, 
                    global_scale= Var_scale, 
                    path_mode='AUTO')
                #print(saveLoc)  
                #print(Var_actionsBool)
                #print(Var_leafBool)
                self.report({'INFO'}, "Exported with mesh name")

            if Var_presets == 'OP1':
                if (amt > one):
                    print("more than one, not rotating")
                else:
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                    print("applied rotations")
                    print("OBJ should be nack to normal")
        else:
            self.report({'INFO'}, "None Selected")

        return {'FINISHED'}
   
#-----------------------------------------------------#  
#     handles reseting the suffix counter      
#-----------------------------------------------------# 
class DarrowCounterReset(bpy.types.Operator):
    bl_idname = "reset.counter"
    bl_description = "Resets FBX suffix counter"
    bl_label = "Reset Suffix Counter"

    def execute(self, context):
        context.scene.counter = 0

        self.report({'INFO'}, "Set suffix count to 0")
        return {'FINISHED'} 
  
classes = (DarrowExportPanel, DarrowExportFBX, DarrowCounterReset)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

   
    bpy.types.Scene.fbxBool = bpy.props.BoolProperty()

    bpy.types.Scene.collectionBool = bpy.props.BoolProperty(
    name = "Multi-object smart naming",
    description = "Use the parent collection name when exporting more than 1 object",
    default = True
    )

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