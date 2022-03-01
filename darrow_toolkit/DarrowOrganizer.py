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

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        settings = context.preferences.addons[__package__].preferences

        if obj is not None: 
            obj = context.active_object
            objs = bpy.context.object.data

            for obj in bpy.context.selected_objects:
                if obj.type =='CURVE' : return False
                if obj.type =='FONT' : return False
                if obj.type =='CAMERA' : return False
                if obj.type =='LIGHT' : return False
                if obj.type =='LIGHT_PROBE' : return False
                if obj.type =='IMAGE' : return False
                if obj.type =='SPEAKER' : return False

        return settings.organizer_moduleBool == True
            #print("poll")

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if obj is not None:
            split=self.layout
            col = split.column(align=True)
            col.scale_y = 1.33
            obj = context.active_object
            col.operator('collapse.scene', icon="SORT_ASC")
            col.label(text="Display Options")
            row = col.row(align=True)
            row.operator('set.wireframe', text="Wireframe", icon="FILE_3D")
            row.operator('darrow.toggle_cutters',
                         text="Booleans", icon="MOD_BOOLEAN")
            col.separator()
            #col.label(text="Organize")
            col.operator('set.empty_coll',text="Group All Empties", icon="COLLECTION_NEW")
            col.operator('darrow.organize_menu',text="Organize Selected",icon="OUTLINER_OB_GROUP_INSTANCE")
            col.separator()

def toggle_expand(context, state):
    area = next(a for a in context.screen.areas if a.type == 'OUTLINER')
    bpy.ops.outliner.show_hierarchy({'area': area}, 'INVOKE_DEFAULT')
    for i in range(state):
        bpy.ops.outliner.expanded_toggle({'area': area})
    area.tag_redraw()

def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)

def parent_lookup(coll):
    parent_lookup = {}
    for coll in traverse_tree(coll):
        for c in coll.children.keys():
            parent_lookup.setdefault(c, coll)
    return parent_lookup

#-----------------------------------------------------#
#    Organize selected
#-----------------------------------------------------#
class DarrowOrganizeMenu(bpy.types.Operator):
    bl_label = "Organize Selected"
    bl_idname = "darrow.organize_menu"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(context.scene, "parentcoll_string")

    def execute(self, context):
        cutters = []
        cutters_parent = []
        linked = []
        selected = context.selected_objects[0]
        old_objs = bpy.context.selected_objects
        objs = bpy.context.selected_objects
        master_name = context.scene.parentcoll_string
        masterCollectionFound = False
        for myCol in bpy.data.collections:
            if myCol.name == master_name:
                masterCollectionFound = True
                break

        if masterCollectionFound == False:
            master_collection = bpy.data.collections.new(master_name)
            bpy.context.scene.collection.children.link(master_collection)
        else:
            master_collection = bpy.data.collections[master_name]
            
        for obj in objs:
            for mods in obj.modifiers:
                if mods.type == 'BOOLEAN':
                    cutters.append(mods.object)
                    cutters_parent.append(obj)
                    linked.append(obj)

                    for x in objs:
                        if x == mods.object:
                            objs.remove(mods.object)
        
        for obj in objs:
            for coll in obj.users_collection:
                coll.objects.unlink(obj)
            bpy.data.collections[master_name].objects.link(obj)
        
        for obj in cutters:
            for coll in obj.users_collection:
                coll.objects.unlink(obj)
            bpy.data.collections[master_name].objects.link(obj)
        used_cutters = []
        for obj in objs:
            for x in linked:
                if x == obj:
                    parent_name = obj.name + "_Parent"
                
                    parentCollectionFound = False
                    for myCol in bpy.data.collections:
                        if myCol.name == parent_name:
                            parentCollectionFound = True
                            break
                    if parentCollectionFound == False:
                        parent_collection = bpy.data.collections.new(parent_name)
                        bpy.context.scene.collection.children.link(parent_collection)
                    else:
                        parent_collection = bpy.data.collections[parent_name]
                    
                    for coll in obj.users_collection:
                        coll.objects.unlink(obj)
                    bpy.data.collections[parent_name].objects.link(obj)

                    """https://blender.stackexchange.com/a/172579"""
                    C = bpy.context
                    coll_scene = C.scene.collection
                    coll_parents = parent_lookup(coll_scene)
                    coll_target = coll_scene.children.get(master_collection.name)
                    active_coll = obj.users_collection[0]
                    active_coll_parent = coll_parents.get(active_coll.name)

                    if active_coll_parent:
                        active_coll_parent.children.unlink(active_coll)
                        coll_target.children.link(active_coll)

        for obj in cutters:
            C = bpy.context
            obj_i = cutters.index(obj)
            cutters_name = cutters_parent[obj_i].name + "_Cutters"
           
            cuttersCollectionFound = False
            for myCol in bpy.data.collections:
                if myCol.name == cutters_name:
                    cuttersCollectionFound = True
                    break
            if cuttersCollectionFound == False:
                cutters_collection = bpy.data.collections.new(cutters_name)
                bpy.context.scene.collection.children.link(cutters_collection)
            else:
                cutters_collection = bpy.data.collections[cutters_name]
            for coll in obj.users_collection:
                coll.objects.unlink(obj)
            bpy.data.collections[cutters_name].objects.link(obj)

            coll_scene = C.scene.collection
            coll_parents = parent_lookup(coll_scene)
            coll_target = cutters_parent[obj_i].users_collection[0]
            active_coll = obj.users_collection[0]
            active_coll_parent = coll_parents.get(active_coll.name)

            if active_coll_parent:
                active_coll_parent.children.unlink(active_coll)
                coll_target.children.link(active_coll)

        for x in old_objs:
            x.select_set(state=True)

        context.view_layer.objects.active = selected
        used_cutters.clear()
        cutters.clear()
        cutters_parent.clear()
        linked.clear()
        return {'FINISHED'}

#-----------------------------------------------------#
#    Toggle cutter visibility
#-----------------------------------------------------#
class DarrowToggleCutters(bpy.types.Operator):
    bl_label = "Toggle Cutters"
    bl_idname = "darrow.toggle_cutters"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for ob in bpy.data.objects:
            if ob.display_type == 'BOUNDS':
                ob.hide_viewport = not ob.hide_viewport
        return {'FINISHED'}

#-----------------------------------------------------#
#     Collapse outliner
#-----------------------------------------------------#
class DarrowCollapseOutliner(bpy.types.Operator):
    bl_label = "Collapse Outliner"
    bl_idname = "collapse.scene"

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

        self.report({'INFO'}, "Viewport Wireframe only")
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

        bpy.ops.object.select_all(action='DESELECT')

        for myCol in bpy.data.collections:
            if myCol.name == empty_collection_name:
                collectionFound = True
                break

        if collectionFound == False:
            empty_collection = bpy.data.collections.new(empty_collection_name)
            bpy.context.scene.collection.children.link(empty_collection)
        
        for obj in scene:
            if obj.type == "EMPTY":
                for coll in obj.users_collection:
                    coll.objects.unlink(obj)
                bpy.data.collections[empty_collection_name].objects.link(obj)
                obj.hide_set(True)

        vlayer = bpy.context.scene.view_layers["View Layer"]
        vlayer.layer_collection.children[empty_collection_name].hide_viewport = True
        bpy.data.collections[empty_collection_name].color_tag = 'COLOR_01'
        bpy.ops.object.select_all(action='DESELECT')

        for x in old_obj:     
            x.select_set(state=True)

        self.report({'INFO'}, "Moved all empties")
        return {'FINISHED'}

#-----------------------------------------------------#  
#   Registration classes
#-----------------------------------------------------#
classes = (DarrowToggleCutters, DarrowOrganizeMenu, DarrowCollapseOutliner, DarrowSetCollection, DarrowWireframe, DarrowOrganizePanel,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

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