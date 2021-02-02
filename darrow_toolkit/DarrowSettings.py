#-----------------------------------------------------#  
#    Imports
#-----------------------------------------------------#  

import bpy
import sys
from bpy.types import Panel
import bl_ui
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import Operator, AddonPreferences


class DarrowAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    boolean = BoolProperty(
        #name="Example Boolean",
        #default=False,
        )

    def draw(self, context):
        layout = self.layout

        layout.label(text='Toggle specific modules')
        layout.prop(context.scene, 'hideCryptoBool')
        layout.operator("Hide.crypto")
        #layout.prop(self,"boolean")


class DarrowHideCrypto(bpy.types.Operator):
    bl_idname = "hide.crypto"
    bl_description = ""
    bl_label = "Update Modules"

    def execute(self, context):


        if bpy.context.scene.hideCryptoBool == True:
            print("true")
            #bpy.ops.wm.properties_remove(data_path = 'object', property = 'my_property')
            #darrow_toolkit.DarrowCrypto
            #bpy.types.DARROW_PT_cryptoPanel.remove(bpy.types.DARROW_PT_cryptoPanel.draw)
            bpy.utils.unregister_class(bpy.types.DARROW_PT_cryptoPanel)
            

        #else:
           # bpy.types.DARROW_PT_cryptoPanel.append(draw)

            #bpy.types.DARROW_PT_cryptoPanel.append(bpy.types.DARROW_PT_cryptoPanel.draw)
            #bpy.utils.register_class(bpy.types.DARROW_PT_cryptoPanel)
            #print("false")
        if bpy.context.scene.hideCryptoBool == False:
            bpy.utils.register_class(bpy.types.DARROW_PT_cryptoPanel)
            
        return {'FINISHED'}
#-----------------------------------------------------#  
#   Registration classes
#-----------------------------------------------------#  

classes = (DarrowAddonPreferences,DarrowHideCrypto)

def register():

    bpy.types.Scene.hideCryptoBool = bpy.props.BoolProperty(
    name = "Crypto Module",
    description = "Update crypto prices with interaction in toolkit items",
    default = False
    )

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()