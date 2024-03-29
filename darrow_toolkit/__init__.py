#-----------------------------------------------------#  
#    License
#-----------------------------------------------------#  
#    MIT License
#
#    Copyright (c) 2020-2022 Blake Darrow <contact@blakedarrow.com>
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.
#
#-----------------------------------------------------#  
#     Plugin information     
#-----------------------------------------------------#  
bl_info = {
    "name": "Darrow Toolkit",
    "author": "Blake Darrow",
    "version": (0, 16, 8),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Darrow Toolkit",
    "description": "Custom toolkit for efficient FBX exporting, circular array, Q.O.L improvements, and external mesh libraries",
    "category": "Tools",
    "wiki_url": "https://docs.darrow.tools/en/latest/index.html",
    }
    
#-----------------------------------------------------#  
#     add all new scripts to this string    
#-----------------------------------------------------#   

if __package__ != "darrow_toolkit":
    sys.modules["darrow_toolkit"] = sys.modules[__package__]

modulesNames = ['DarrowTools', 'DarrowRGB', 'DarrowCircleArray','DarrowSettings', 'DarrowExport', 'DarrowLibrary']

#-----------------------------------------------------#  
#     imports    
#-----------------------------------------------------#  
import bpy
from . import addon_updater_ops
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
    addon_updater_ops.register(bl_info)
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
    addon_updater_ops.unregister()
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()

if __name__ == "__main__":
    register()