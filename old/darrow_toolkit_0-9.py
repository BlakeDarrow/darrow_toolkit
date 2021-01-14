#info for plugin
bl_info = {
    "name": "Darrow Toolkit",
    "author": "Blake Darrow",
    "version": (0, 9),
    "blender": (2, 90, 0),
    "location": "View3D > Sidebar > Darrow Toolkit",
    "description": "Toolkit to speed up common tasks.",
    "category": "Tools",
    "warning": "Still in development, might encounter bugs. Coin info taken from CoinMarketCap.com",
    "wiki_url": "https://github.com/BlakeDarrow/darrow_toolkit",
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
import requests
from pathlib import Path
from time import sleep

import urllib
from urllib import request

from urllib.request import urlopen

from html.parser import HTMLParser


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
#     handles Main ui     
#-----------------------------------------------------#  

class DarrowToolPanel(bpy.types.Panel):
    bl_label = "Darrow Toolkit"
    bl_category = "Darrow Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        
        layout = self.layout
        split=layout.split()
        col=split.column(align = True) 
        obj = context.object
        
        if obj is not None:
            
            #Variables for the bools and enums
            Var_prefix_bool = bpy.context.object.useprefixBool
            Var_suffix_bool = bpy.context.object.usecounterBool
            Var_custom_prefix = bpy.context.object.PrefixOption
            Var_use_alerts = bpy.context.object.usealertsBool
            Var_hidetools = bpy.types.Object.hidetoolkitBool
            
            if bpy.context.object.hidetoolkitBool == False:

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
                    layout.separator()
                    
                    col.operator('shade.smooth')
                    col.operator('apply.transforms')
                    col.operator('apply.normals')
                    
                    box = layout.box()
                    box.label(text = "FBX Exporter")
                    box.operator('export_selected.darrow')
                    
                    split=box.split()
                    split.prop(obj, 'useprefixBool')
                    split.prop(obj, 'usecounterBool')
                    layout.separator()
                    
                    if Var_suffix_bool == True:
                        box.label(text = "Increase the suffix by (+1)")
                        box.operator('reset.counter')
                        
                    #If use prefix is selected then these options show up
                    if Var_prefix_bool == True: 
                        layout.label(text = "Prefix Options")
                        box = layout.box()
                        box.prop(obj, 'PrefixOption')
                        #If the custom enum is selected these show up
                        if Var_custom_prefix == 'OP2':
                            
                            box.prop(context.scene, "my_string_prop", text="Prefix")    

                  
            split=layout.split()
            col=split.column(align = True)
            col.operator('get.prices')
            
            if bpy.context.object.showPricesBool == True:

                box = layout.box()
                box.separator()
                box.prop(context.scene, "btc_price")
                box.prop(context.scene, "eth_price")
                box.prop(context.scene, "xrp_price")
                box.label(text = "[ Refreshed every few minutes ]")
                split=box.split()
                split.operator('update.prices')
                split.operator('reset.prices')
                box.prop(obj, "hidetoolkitBool")
                box.prop(obj, "usealertsBool")
                
                if Var_use_alerts == True:
                    #box.label(text = "Price Notifications")
                    box.prop(context.scene, "btc_alert")
                    box.prop(context.scene, "eth_alert")
                    box.prop(context.scene, "xrp_alert")
             
            
class DarrowResetPrices(bpy.types.Operator):
    bl_idname = "reset.prices"
    bl_description = "Reset/restart all values"
    bl_label = "Reset"
    
    def execute(self, context):

        # resets url
        context.scene.btc_url = "null"
        context.scene.eth_url = "null"
        context.scene.xrp_url = "null"
        
        # print result
        print("url: Reset",context.scene.btc_url)
        print("url: Reset",context.scene.eth_url)
        print("url: Reset",context.scene.xrp_url)
        
        # resets price display
        context.scene.btc_price = "0.00"
        context.scene.eth_price = "0.00"
        context.scene.xrp_price = "0.00"
        
        # resets alerts
        context.scene.btc_alert = 25000
        context.scene.eth_alert = 500
        context.scene.xrp_alert = 0.35
        
        
        self.report({'INFO'}, "Prices Reset")
        return {'FINISHED'}


class DarrowUpdatePrices(bpy.types.Operator):
    bl_idname = "update.prices"
    bl_description = "Check for updated prices"
    bl_label = "Check Update"
    
    def execute(self, context):
        
        btc_url = context.scene.btc_url
        eth_url = context.scene.eth_url
        xrp_url = context.scene.xrp_url
   
#-----------------------------------------------------#  
#     Get bitcoin price from the internet    
#-----------------------------------------------------# 
        btc_url = 'https://coinmarketcap.com/'
        btc_response = urlopen(btc_url)
        #raw html code from url
        btc_rawstring = btc_response.read().decode('utf-8')
        #find these specific characters in the raw html. These are right before the price of bitcoin, so they are static
        btc_static = btc_rawstring.find('/currencies/bitcoin/markets/')
        #add a character buffer to get closer to price positions in raw string
        btc_buffer = 47
        #add the buffer to the static identifer to get the actual string start value for btc
        btc_startprice = btc_static + btc_buffer
        #add another buffer starting from the 'btc_startprice' to make sure we get the full price
        btc_endprice = btc_startprice + 10
        #get the actual price of btc by searching the raw string within these parameters
        btcprice = (btc_rawstring[btc_startprice:btc_endprice])
        #set global btc_price variable
        context.scene.btc_price = btcprice
#-----------------------------------------------------#  
#     Get Etherum price from the internet    
#-----------------------------------------------------#        
        eth_url = 'https://coinmarketcap.com/'
        eth_response = urlopen(eth_url)
        #raw html code from url
        eth_rawstring = eth_response.read().decode('utf-8')
        #find these specific characters in the raw html. These are right before the price of bitcoin, so they are static
        eth_static = eth_rawstring.find('/currencies/ethereum/markets/')
        #add a character buffer to get closer to price positions in raw string
        eth_buffer = 48
        #add the buffer to the static identifer to get the actual string start value for btc
        eth_startprice = eth_static + eth_buffer
        #add another buffer starting from the 'btc_startprice' to make sure we get the full price
        eth_endprice = eth_startprice + 9
        #get the actual price of btc by searching the raw string within these parameters
        ethprice = (eth_rawstring[eth_startprice:eth_endprice])
        #set global btc_price variable
        context.scene.eth_price = ethprice
#-----------------------------------------------------#  
#     Get Ripple price from the internet    
#-----------------------------------------------------#        
        xrp_url = 'https://coinmarketcap.com/'
        xrp_response = urlopen(xrp_url)
        #raw html code from url
        xrp_rawstring = xrp_response.read().decode('utf-8')
        #find these specific characters in the raw html. These are right before the price of bitcoin, so they are static
        xrp_static = xrp_rawstring.find('/currencies/xrp/markets/')
        #add a character buffer to get closer to price positions in raw string
        xrp_buffer = 43
        #add the buffer to the static identifer to get the actual string start value for btc
        xrp_startprice = xrp_static + xrp_buffer
        #add another buffer starting from the 'btc_startprice' to make sure we get the full price
        xrp_endprice = xrp_startprice + 7
        #get the actual price of btc by searching the raw string within these parameters
        xrpprice = (xrp_rawstring[xrp_startprice:xrp_endprice])
        #set global btc_price variable
        context.scene.xrp_price = xrpprice
        
#-----------------------------------------------------#  
#     Alerts
#-----------------------------------------------------#    

        # BTC Alerts
        btc_alert = context.scene.btc_alert
        btc_alert = float(btc_alert)
        
        btc_str_price = xrpprice.replace("$", '')
        btc_str_price = float(btc_str_price)
        
        
        # XRP Alerts 
        xrp_alert = context.scene.xrp_alert
        xrp_alert = float(xrp_alert)
        
        xrp_str_price = xrpprice.replace("$", '')
        xrp_str_price = float(xrp_str_price)

        print(xrp_str_price)
        print(xrp_alert)


        if bpy.context.object.usealertsBool == True:
            if (xrp_str_price <= xrp_alert):
                print("",)
                print("XRP UP")
            
        
        print("",)
        print("BTC:",btcprice)
        print("ETH:",ethprice)
        print("XRP:",xrpprice)

        print("url:",btc_url)
        print("url:",eth_url)
        print("url:",xrp_url)
    
        self.report({'INFO'}, "Prices Refreshed")
        return {'FINISHED'}

#-----------------------------------------------------#  
#     Show Crypto prices    
#-----------------------------------------------------#      
        
class DarrowGetPrices(bpy.types.Operator):
    bl_idname = "get.prices"
    bl_description = "Crypto prices from the internet"
    bl_label = "<---  Crypto Prices  --->"

    def execute(self, context):

        if bpy.context.object.showPricesBool == False:
            bpy.context.object.showPricesBool = True
        else:
            bpy.context.object.showPricesBool = False
        
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
    
        self.report({'INFO'}, "Reset viewport")
        return {'FINISHED'}   

#-----------------------------------------------------#  
#    Button to apply all transformations
#-----------------------------------------------------#  
class DarrowTransforms(bpy.types.Operator):
    bl_idname = "apply.transforms"
    bl_description = "Apply transformations to selected object"
    bl_label = "Apply Transforms"

    def execute(self, context):
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        self.report({'INFO'}, "Transforms applied")
        return {'FINISHED'}

#-----------------------------------------------------#  
#    Set Objects origin
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
        self.report({'INFO'}, "Selected is now origin")
        return {'FINISHED'}

#-----------------------------------------------------#  
#     Snap object to world center
#-----------------------------------------------------#   
class DarrowMoveOrigin(bpy.types.Operator):
    bl_idname = "move.origin"
    bl_description = "Move selected to world origin"
    bl_label = "Align to world"

    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
        self.report({'INFO'}, "Moved selected to object origin")
        return {'FINISHED'}

#-----------------------------------------------------#  
#    Set Objects origin and move to world origin
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
        return {'FINISHED'}

#-----------------------------------------------------#  
#     Button to apply outside calculated normals
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
        self.report({'INFO'}, "Normals calculated outside")
        return {'FINISHED'}
    
#-----------------------------------------------------#  
#     Button to smooth mesh
#-----------------------------------------------------#    
class DarrowSmooth(bpy.types.Operator):
    bl_idname = "shade.smooth"
    bl_label = "Smooth Object"
    bl_description = "Smooth the selected object"

    def execute(self, context):
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        self.report({'INFO'}, "Object smoothed")
        return {'FINISHED'}

#-----------------------------------------------------#  
#     Button to apply all checklisted items
#-----------------------------------------------------#         
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

#-----------------------------------------------------#  
#    Logic for exporting as FBX
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
        customprefix = bpy.context.scene.my_string_prop
        #get blend name
        blendName = bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend", "")
        #get fbx name
        name = bpy.path.clean_name(fbxname.name)
        #Variables for UI, like bools and enums
        Var_PrefixBool = bpy.context.object.useprefixBool
        Var_custom_prefix = bpy.context.object.PrefixOption
        Var_counterBool = bpy.context.object.usecounterBool
        
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
                #handles actual export    
                bpy.ops.export_scene.fbx(
                    filepath = saveLoc.replace('.fbx', '')+ ".fbx",
                    check_existing=True, 
                    axis_forward= '-Z', 
                    axis_up= 'Y', 
                    use_selection=True, 
                    global_scale=1, 
                    path_mode='AUTO')
                    
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
                check_existing=True, 
                axis_forward='-Z', 
                axis_up='Y', 
                use_selection=True, 
                global_scale=1, 
                path_mode='AUTO')
                
            self.report({'INFO'}, "Exported with mesh name")
        return {'FINISHED'}
    
    
#-----------------------------------------------------#  
#     Crypto Price Menu      
#-----------------------------------------------------#                   
class DarrowPriceMenu(bpy.types.Menu):
    bl_label = "Cryptocurrency Prices"
    bl_idname = "Darrow.PriceMenu"
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "btc_price")
        
        #bpy.ops.wm.call_menu(name=DarrowPriceMenu.bl_idname)
 
    
#-----------------------------------------------------#  
#	Registration classes
#-----------------------------------------------------#  

def register():
    bpy.utils.register_class(DarrowCounterReset)
    bpy.utils.register_class(DarrowApply)
    bpy.utils.register_class(DarrowWireframe)
    bpy.utils.register_class(DarrowWireframeReset)
    bpy.utils.register_class(DarrowSetOrigin)
    bpy.utils.register_class(DarrowSetSnapOrigin)    
    bpy.utils.register_class(DarrowMoveOrigin)
    bpy.utils.register_class(DarrowExportFBX)
    bpy.utils.register_class(DarrowToolPanel)
    bpy.utils.register_class(DarrowTransforms)
    bpy.utils.register_class(DarrowNormals)
    bpy.utils.register_class(DarrowSmooth)
    bpy.utils.register_class(DarrowGetPrices)
    bpy.utils.register_class(DarrowPriceMenu)
    bpy.utils.register_class(DarrowUpdatePrices)
    bpy.utils.register_class(DarrowResetPrices)


    bpy.types.Object.usealertsBool = BoolProperty(
    name = "Turn on price alerts",
    description = "Price alerts toggle",
    default = False
    )
    
    bpy.types.Object.hidetoolkitBool = BoolProperty(
    name = "Crypto mode",
    description = "Hide additional tools",
    default = False
    )

    bpy.types.Object.useprefixBool = BoolProperty(
    name = "Use Prefix",
    description = "Export selected object with custom text as a prefix",
    default = False
    )

    bpy.types.Object.usecounterBool = BoolProperty(
    name = "Use Suffix",
    description = "Count exports and use as suffex",
    default = False
    )
    
    bpy.types.Object.showPricesBool = BoolProperty(
    name = "Show Crypto Prices",
    description = "Toggle visabilty of crypto prices",
    default = False
    )
    
    bpy.types.Scene.my_string_prop = bpy.props.StringProperty(
    name = "",
    description = "Custom Prefix",
    default = "Assets"
    )
    
    bpy.types.Scene.counter = bpy.props.IntProperty(
    default = 0
    )
    
    bpy.types.Scene.btc_price = bpy.props.StringProperty(
    name = "BTC",
    description = "Current price of Bitcoin",
    )
    
    bpy.types.Scene.eth_price = bpy.props.StringProperty(
    name = "ETH",
    description = "Current price of Ethereum"
    )
    
    bpy.types.Scene.xrp_price = bpy.props.StringProperty(
    name = "XRP",
    description = "Current price of Ripple",
    )
    
    bpy.types.Scene.btc_url = bpy.props.StringProperty(
    name = "BTC URL",
    description = "",
    )
    
    bpy.types.Scene.eth_url = bpy.props.StringProperty(
    name = "ETH URL",
    description = "",
    )
    
    bpy.types.Scene.xrp_url = bpy.props.StringProperty(
    name = "xrp URL",
    description = "",
    )
    
    
    bpy.types.Scene.btc_alert = bpy.props.FloatProperty(
    name = "BTC <",
    )
    
    bpy.types.Scene.eth_alert = bpy.props.FloatProperty(
    name = "ETH <",
    )
    
    bpy.types.Scene.xrp_alert = bpy.props.FloatProperty(
    name = "XRP <",
    )
    
    bpy.types.Object.PrefixOption = EnumProperty(
    name="",
    description="Apply Data to attribute.",
    items=[('OP1', ".blend", ""),
           ('OP2', "custom", ""),
        ]
    )
    
def unregister():
    
    bpy.utils.unregister_class(DarrowCounterReset)
    bpy.utils.unregister_class(DarrowApply)
    bpy.utils.runegister_class(DarrowWireframeReset)
    bpy.utils.runegister_class(DarrowWireframe)
    bpy.utils.unregister_class(DarrowSetOrigin)
    bpy.utils.unregister_class(DarrowSetSnapOrigin) 
    bpy.utils.unregister_class(DarrowMoveOrigin)
    bpy.utils.unregister_class(DarrowToolPanel)
    bpy.utils.unregister_class(DarrowTransforms)
    bpy.utils.unregister_class(DarrowNormals)
    bpy.utils.unregister_class(DarrowSmooth)
    bpy.utils.unregister_class(DarrowExportFBX)
    bpy.utils.unregister_class(DarrowGetPrices)

if __name__ == "__main__":
    register()