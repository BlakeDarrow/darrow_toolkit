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
class DarrowToolPanel(bpy.types.Panel):
    bl_label = "DarrowQ.O.L"
    bl_category = "Darrow Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_toolPanel"

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

        return settings.checklist_moduleBool == True
            #print("poll")

    def draw_header(self, context):
        settings = context.preferences.addons[__package__].preferences
        self.layout.prop(settings, 'advancedToolBool', icon="SETTINGS",text="")

    def draw(self, context):
        layout = self.layout
        objs = context.selected_objects
        obj = context.active_object
        settings = context.preferences.addons[__package__].preferences
        Var_compactBool = settings.advancedToolBool
        if obj is not None:
            split=layout.box()
            col = split.column(align=True)
            col.scale_y = 1.2
            obj = context.active_object
        
            if Var_compactBool == False:
                col.operator('set.wireframe',
                            text="Display Wireframe", icon="CUBE")
                if context.mode == 'OBJECT':
                    col.operator('move.origin', icon="OBJECT_ORIGIN")
                if context.mode == 'EDIT_MESH':
                    col.operator('set.origin', icon="PIVOT_CURSOR")
            
            if Var_compactBool == True:
                col.operator('set.wireframe', text="Display Wireframe", icon="CUBE")
                
                if context.mode == 'EDIT_MESH':
                    col.operator('set.origin', icon="PIVOT_CURSOR")
                if context.mode == 'OBJECT':
                    col.operator('move.origin', icon="OBJECT_ORIGIN")
                    col = split.column(align=True)
                    
                    col.scale_y = 1.2
                    col.operator('darrow.organize_menu',
                                 icon="OUTLINER_OB_GROUP_INSTANCE")
                    col.operator('clean.mesh', text = "Cleanup Mesh", icon="VERTEXSEL")
                    col.operator('shade.smooth', text = "Shade Smooth",icon="MOD_SMOOTH")
                    col.operator('apply.transforms', icon="CHECKMARK")
                    col.operator('apply.normals', icon="NORMALS_FACE")
                
                    col2 = split.column(align=True)
                    col2.scale_y = 1.2
                    col2.operator('set.empty_coll',icon="COLLECTION_NEW")
                    col2.operator('collapse.scene', icon="SORT_ASC")
                      
                    if len(objs) == 0:
                        col.enabled = False

                    else:
                        col.enabled = True

class CTO_OT_Dummy(bpy.types.Operator):
    bl_idname = "object.cto_dummy"
    bl_label = ""
    bl_description = "There is nothing here"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return False

    def execute(self, context):
        return {'FINISHED'}

def extend_transfo_pop_up(self, context):
    layout = self.layout
    row = layout.row(align=False)
    row.operator(DarrowClearOrientation.bl_idname, icon='TRASH')
    row.operator(CTO_OT_Dummy.bl_idname, icon='BLANK1', emboss=False)

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
                context.object.type == 'MESH' and
                len(context.object.data.uv_layers) > 0)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(context.scene, "parentcoll_string")
        #col.prop(context.scene, 'keepParentBool')
        #col.prop(context.scene, 'collapseBool')
        #these are not working properly

    def execute(self, context): #NEED TO CHECK IF COLLECTION HAS ALREADY BEEN CREATED
        selected = context.selected_objects[0]
        old_coll = selected.users_collection[0]
        old_objs = bpy.context.selected_objects
        objs = bpy.context.selected_objects
        master_name = context.scene.parentcoll_string
        master_collection = bpy.data.collections.new(master_name)
        bpy.context.scene.collection.children.link(master_collection)
        cutters = []
        cutters_parent = []
        linked = []

        for obj in objs:
            for mods in obj.modifiers:
                if mods.type == 'BOOLEAN':
                    if not cutters.__contains__(mods.object):
                        cutters.append(mods.object)
                    if not cutters_parent.__contains__(obj):
                        cutters_parent.append(obj)
                    if not linked.__contains__(obj):
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

        for obj in objs:
            for x in linked:
                if x == obj:
                    parent_name = obj.name
                    parent_collection = bpy.data.collections.new(parent_name)
                    bpy.context.scene.collection.children.link(parent_collection)
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
            cutters_collection = bpy.data.collections.new(cutters_name)
            bpy.context.scene.collection.children.link(cutters_collection)
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
        
        Var_keepParent_bool = bpy.context.scene.keepParentBool
        if Var_keepParent_bool == True: # NOT WORKING REALLY
            for obj in old_objs:
                C = bpy.context
                coll_scene = C.scene.collection
                coll_parents = parent_lookup(coll_scene)
                coll_target = coll_scene.children.get(master_collection.name)
                active_coll = obj.users_collection[0]
                active_coll_parent = coll_parents.get(active_coll.name)

                if active_coll_parent:
                    active_coll_parent.children.unlink(active_coll)
                    coll_target.children.link(active_coll)

        for x in old_objs:
            x.select_set(state=True)

        context.view_layer.objects.active = selected

        if bpy.context.scene.collapseBool == True:
            area = next(a for a in context.screen.areas if a.type == 'OUTLINER')
            bpy.ops.outliner.show_hierarchy({'area': area}, 'INVOKE_DEFAULT')
            for i in range(2):
                bpy.ops.outliner.expanded_toggle({'area': area})
            area.tag_redraw()
        return {'FINISHED'}

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
#     Collapse outliner
#-----------------------------------------------------#
class DarrowCollapseOutliner(bpy.types.Operator):
    bl_label = "Collapse Outliner"
    bl_idname = "collapse.scene"

    def execute(self, context):
        toggle_expand(context, 2)
        return {'FINISHED'}

#-----------------------------------------------------#
#     handles Orientation 
#-----------------------------------------------------#
class DarrowClearOrientation(bpy.types.Operator):
    bl_idname = "clear.orientation"
    bl_description = "clear.orientation"
    bl_label = "Cleanup"

    def execute(self, context):
        try:
            bpy.context.scene.transform_orientation_slots[0].type = ""
        except Exception as inst:
            transforms = str(inst).split(
                "in")[1][3:-2].replace("', '", " ").split()
            for type in transforms[6:]:
                try:
                    bpy.context.scene.transform_orientation_slots[0].type = type
                    bpy.ops.transform.delete_orientation()
                except Exception as e:
                    pass
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
#    handles mesh clean up
#-----------------------------------------------------#  
class DarrowCleanMesh(bpy.types.Operator):
    bl_idname = "clean.mesh"
    bl_description = "Delete loose, remove doubles, and dissolve degenerate"
    bl_label = "Clean Mesh"

    def execute(self, context):
        settings = context.preferences.addons[__package__].preferences
        objs = context.selected_objects
        if len(objs) != 0: 
            if context.mode == 'OBJECT':
                bpy.ops.object.editmode_toggle()

            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.delete_loose()
            bpy.ops.mesh.remove_doubles(threshold=settings.removeDoublesAmount)
            bpy.ops.mesh.dissolve_degenerate()
            bpy.ops.object.editmode_toggle()   
            self.report({'INFO'}, "Mesh cleaned")
        else:
            self.report({'INFO'}, "None Selected")
        return {'FINISHED'}

#-----------------------------------------------------#  
#    handle apply transforms
#-----------------------------------------------------#  
class DarrowTransforms(bpy.types.Operator):
    bl_idname = "apply.transforms"
    bl_description = "Apply transformations to selected object"
    bl_label = "Apply Transforms"
    bl_options = {"UNDO"}

    def execute(self, context):
        objs = context.selected_objects
        if len(objs) != 0: 
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=True)
            bpy.ops.object.transform_apply(location=True,rotation=True, scale=True)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            self.report({'INFO'}, "Transforms applied")
        else:
            self.report({'INFO'}, "None Selected")
        return {'FINISHED'}

#-----------------------------------------------------#  
#    handles Objects origin
#-----------------------------------------------------#  
class DarrowSetOrigin(bpy.types.Operator):
    bl_idname = "set.origin"
    bl_description = "Set selected as object origin"
    bl_label = "Set Origin"

    def execute(self, context):
        objs = context.selected_objects
        if len(objs) != 0: 
            if context.mode == 'OBJECT':
                bpy.ops.object.editmode_toggle()
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            self.report({'INFO'}, "Selected is now origin")
        else:
            self.report({'INFO'}, "None Selected")
        return {'FINISHED'}

#-----------------------------------------------------#  
#     handles snapping object to world center
#-----------------------------------------------------#   
class DarrowMoveOrigin(bpy.types.Operator):
    bl_idname = "move.origin"
    bl_description = "Move selected to world origin"
    bl_label = "Move to Origin"

    def execute(self, context):
        objs = context.selected_objects
        if len(objs) != 0: 
            bpy.ops.view3d.snap_cursor_to_center()
            bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
            self.report({'INFO'}, "Moved selected to object origin")
        else:
            self.report({'INFO'}, "None Selected")
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
#     handles apply outside calculated normals
#-----------------------------------------------------#    
class DarrowNormals(bpy.types.Operator):
    bl_idname = "apply.normals"
    bl_description = "Calculate outside normals"
    bl_label = "Calculate Normals"

    def execute(self, context):
        objs = context.selected_objects
        if len(objs) != 0: 
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.editmode_toggle()
            self.report({'INFO'}, "Normals calculated outside")
        else:
            self.report({'INFO'}, "None Selected")
        return {'FINISHED'}
    
#-----------------------------------------------------#  
#     handles smooth mesh
#-----------------------------------------------------#    
class DarrowSmooth(bpy.types.Operator):
    bl_idname = "shade.smooth"
    bl_label = "Smooth Object"
    bl_description = "Smooth the selected object"

    def execute(self, context):
        objs = context.selected_objects
        if len(objs) != 0: 
            bpy.ops.object.shade_smooth()
            bpy.context.object.data.use_auto_smooth = True
            bpy.context.object.data.auto_smooth_angle = 3.14159

            self.report({'INFO'}, "Object smoothed to 180")
        else:
            self.report({'INFO'}, "None Selected")
        return {'FINISHED'}

#-----------------------------------------------------#  
#   Registration classes
#-----------------------------------------------------#  
classes = (DarrowOrganizeMenu, DarrowCollapseOutliner, DarrowSetCollection, CTO_OT_Dummy, DarrowClearOrientation, DarrowCleanMesh,
           DarrowWireframe, DarrowSetOrigin, DarrowMoveOrigin, DarrowToolPanel, DarrowTransforms, DarrowNormals, DarrowSmooth,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.parentcoll_string = bpy.props.StringProperty(
            name="Name",
            description="Collection Name",
            default="Collection"
        )

    bpy.types.VIEW3D_PT_transform_orientations.append(extend_transfo_pop_up)

    bpy.types.Scene.compactBool = bpy.props.BoolProperty(
    name = "Advanced",
    description = "Toggle Advanced Mode",
    default = False
    )

    bpy.types.Scene.keepParentBool = bpy.props.BoolProperty(
        name="Remember parent collection",
        description="Toggle",
        default=False
    )
    bpy.types.Scene.collapseBool = bpy.props.BoolProperty(
        name="Collapse outliner",
        description="Toggle",
        default=False
    )

    bpy.types.Scene.showWireframeBool = bpy.props.BoolProperty(
    name = "Toggle Wireframe",
    description = "Toggle visabilty of wireframe mode",
    default = False
    )

def unregister():
    bpy.types.VIEW3D_PT_transform_orientations.remove(extend_transfo_pop_up)
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()