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
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       )
#-----------------------------------------------------#         
#     handles ui panel 
#-----------------------------------------------------#  
class DarrowOrganizePanel(bpy.types.Panel):
    bl_label = "Scene Organizer"
    bl_category = "DarrowToolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_organizePanel"

    def draw_header(self, context):
       self.layout.label(text="",icon="LONGDISPLAY")

    def draw(self, context):
        split=self.layout
        col = split.column(align=True)
        col.scale_y = 1.33

        col.label(text="Display Options", icon="OPTIONS")
        col.operator('set.wireframe', text="Wireframe", icon="FILE_3D")
        row = col.row(align=True)
        row.operator('darrow.toggle_cutters',
                        text="Booleans", icon="MOD_BOOLEAN",)
        row.operator('darrow.toggle_empty', text="Empties", icon="EMPTY_AXIS")
        col.separator()
        col.label(text="Collection Sorting",icon="COLLECTION_NEW")
        row = col.row(align=True)
        row.operator('set.cutter_coll',text="Booleans", icon="MOD_BOOLEAN")
        row.operator('set.empty_coll',text="Empties", icon="EMPTY_AXIS")
        col.operator('collapse.scene', icon="SORT_ASC")
        col.separator()

def toggle_expand(context, state):
    area = next(a for a in context.screen.areas if a.type == 'OUTLINER')
    bpy.ops.outliner.show_hierarchy({'area': area}, 'INVOKE_DEFAULT')
    for i in range(state):
        bpy.ops.outliner.expanded_toggle({'area': area})
    area.tag_redraw()

#-----------------------------------------------------#
#    Toggle cutter visibility
#-----------------------------------------------------#
class DarrowToggleCutters(bpy.types.Operator):
    bl_label = "Toggle Cutters"
    bl_idname = "darrow.toggle_cutters"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Toggle the visabilty of boolean cutters."

    def execute(self, context):
        bpy.context.scene.cutterVis_Bool = not bpy.context.scene.cutterVis_Bool
        print(bpy.context.scene.cutterVis_Bool)
        for ob in bpy.data.objects:
            if ob.display_type == 'BOUNDS':
                ob.hide_viewport = bpy.context.scene.cutterVis_Bool
                ob.hide_viewport = not ob.hide_viewport
        return {'FINISHED'}
#
# -----------------------------------------------------#
#    Toggle empty visibility
#-----------------------------------------------------#
class DarrowToggleEmpty(bpy.types.Operator):
    bl_label = "Toggle Empty"
    bl_idname = "darrow.toggle_empty"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Toggle the visabilty of empties"

    def execute(self, context):
        bpy.context.scene.emptyVis_Bool = not bpy.context.scene.emptyVis_Bool
        print(bpy.context.scene.emptyVis_Bool)
        for ob in bpy.data.objects:
            if ob.type == 'EMPTY':
                ob.hide_viewport = bpy.context.scene.emptyVis_Bool
                ob.hide_viewport = not ob.hide_viewport
        return {'FINISHED'}

#-----------------------------------------------------#
#     Collapse outliner
#-----------------------------------------------------#
class DarrowCollapseOutliner(bpy.types.Operator):
    bl_label = "Collapse Outliner"
    bl_idname = "collapse.scene"
    bl_description = "Collapse all items in the outliner"

    def execute(self, context):
        toggle_expand(context, 2)
        return {'FINISHED'}

#-----------------------------------------------------#  
#     handles wireframe display   
#-----------------------------------------------------#                 
class DarrowWireframe(bpy.types.Operator):
    bl_idname = "set.wireframe"
    bl_description = "Display Wireframe Overlay Only"
    bl_label = "Toggle Wireframe"

    def execute(self, context):
        obj = context.active_object
        if bpy.context.scene.showWireframeBool == False:
            bpy.context.scene.showWireframeBool = True
            if obj is not None:
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
            if obj is not None:
                bpy.context.active_object.select_set(False)
            bpy.context.space_data.show_gizmo = True
            bpy.context.space_data.overlay.show_floor = True
            bpy.context.space_data.overlay.show_axis_y = True
            bpy.context.space_data.overlay.show_axis_x = True
            bpy.context.space_data.overlay.show_cursor = True
            bpy.context.space_data.overlay.show_object_origins = True
            bpy.context.space_data.overlay.show_wireframes = False

        self.report({'INFO'}, "Viewport Wireframe only")
        return {'FINISHED'} 
    
#-----------------------------------------------------#
#    handles moving all Booleans's
#-----------------------------------------------------#
class DarrowSetCollectionCutter(bpy.types.Operator):
    bl_idname = "set.cutter_coll"
    bl_description = "Move all booleans to 'Darrow_Booleans' collection"
    bl_label = "Group All Booleans"

    def execute(self, context):
        collectionFound = False
        empty_collection_name = "Darrow_Booleans"
        old_obj = bpy.context.selected_objects
        scene = bpy.context.scene.objects

        bpy.ops.object.select_all(action='DESELECT')

        for myCol in bpy.data.collections:
            if myCol.name == empty_collection_name:
                collectionFound = True
                break

        bools = []
        for obj in scene:
            for mods in obj.modifiers:
                if mods.type == 'BOOLEAN':
                    bools.append(mods.object)

        if collectionFound == False and not len(bools) == 0:
                empty_collection = bpy.data.collections.new(empty_collection_name)
                bpy.context.scene.collection.children.link(empty_collection)
                bpy.data.collections[empty_collection_name].color_tag = 'COLOR_01'
                self.report({'INFO'}, "Moved all booleans")
        else:
            self.report({'WARNING'}, "No boolean cutters in scene to sort")
        
        for obj in bools:
            for coll in obj.users_collection:
                coll.objects.unlink(obj)
            bpy.data.collections[empty_collection_name].objects.link(obj)
 
       
        bpy.ops.object.select_all(action='DESELECT')

        for x in old_obj:     
            x.select_set(state=True)


        return {'FINISHED'}

#-----------------------------------------------------#
#    handles moving all empty's
#-----------------------------------------------------#
class DarrowSetCollection(bpy.types.Operator):
    bl_idname = "set.empty_coll"
    bl_description = "Move all empties to 'Darrow_Empties' collection"
    bl_label = "Group All Empties"

    def execute(self, context):
        collectionFound = False
        empty_collection_name = "Darrow_Empties"
        old_obj = bpy.context.selected_objects
        scene = bpy.context.scene.objects
        empties = []

        bpy.ops.object.select_all(action='DESELECT')
        for myCol in bpy.data.collections:
            if myCol.name == empty_collection_name:
                collectionFound = True
                break
        for obj in scene:
            if obj.type == "EMPTY":
                empties.append(obj)

        if collectionFound == False and not len(empties) == 0:
            empty_collection = bpy.data.collections.new(empty_collection_name)
            bpy.context.scene.collection.children.link(empty_collection)
            bpy.data.collections[empty_collection_name].color_tag = 'COLOR_01'
            self.report({'INFO'}, "Moved all empties")
        else:
            self.report({'WARNING'}, "No empties in scene to sort")
        
        for obj in empties:
            for coll in obj.users_collection:
                coll.objects.unlink(obj)
            bpy.data.collections[empty_collection_name].objects.link(obj)
      
        bpy.ops.object.select_all(action='DESELECT')

        for x in old_obj:     
            x.select_set(state=True)

       
        return {'FINISHED'}

#-----------------------------------------------------#  
#   Registration classes
#-----------------------------------------------------#
classes = (DarrowToggleEmpty,DarrowSetCollectionCutter,DarrowToggleCutters, DarrowCollapseOutliner, DarrowSetCollection, DarrowWireframe, DarrowOrganizePanel,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.cutterVis_Bool = bpy.props.BoolProperty(
        name="Vis Bool",
        description="Toggle visabilty of cutters",
        default=True
    )
    bpy.types.Scene.emptyVis_Bool = bpy.props.BoolProperty(
        name="Vis Bool",
        description="Toggle visabilty of empties",
        default=True
    )

    bpy.types.Scene.parentcoll_string = bpy.props.StringProperty(
            name="Name",
            description="Collection Name",
            default="Collection"
        )

    bpy.types.Scene.compactBool = bpy.props.BoolProperty(
    name = "Advanced",
    description = "Toggle Advanced Mode",
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