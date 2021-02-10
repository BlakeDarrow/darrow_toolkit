#-----------------------------------------------------#  
#     Plugin information     
#-----------------------------------------------------#  
bl_info = {
    "name": "Darrow Toolkit",
    "author": "Blake Darrow",
    "version": (0, 11, 3),
    "blender": (2, 90, 0),
    "location": "View3D > Sidebar > Darrow Toolkit",
    "description": "Toolkit for efficient FBX exporting",
    "category": "Tools",
    #"warning": "Still in development. Coin info taken from CoinMarketCap.com",
    "wiki_url": "https://github.com/BlakeDarrow/darrow_toolkit",
    }
    
#-----------------------------------------------------#  
#     add all new scripts to this string    
#-----------------------------------------------------#   
modulesNames = ['DarrowCrypto', 'DarrowTools', 'DarrowSettings', 'DarrowExport']

#-----------------------------------------------------#  
#     imports    
#-----------------------------------------------------#  
import bpy
import sys
import importlib

#-----------------------------------------------------#  
#     create a dictonary for module names    
#-----------------------------------------------------# 
modulesFullNames = {}
for currentModuleName in modulesNames:
    modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))

#-----------------------------------------------------#  
#     import new modules to addon using full name from above    
#-----------------------------------------------------# 
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)

#-----------------------------------------------------#  
#     register the modules    
#-----------------------------------------------------# 

classes = ()

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()

#-----------------------------------------------------#  
#     unregister the modules    
#-----------------------------------------------------# 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()

if __name__ == "__main__":
    register()