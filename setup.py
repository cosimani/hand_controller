import sys
from cx_Freeze import setup, Executable

# packages = [ 'mediapipe', 'keras', 'tensorflow' ]
# includes = [ 'keras', 'tensorflow' ]
packages = [ 'mediapipe', 'keras', 'tensorflow' ]
includes = [ ]
include_files = [ 'model_9_hand.h5', 'model_9_hand.json', 
                  '3_gestos_face.h5', '3_gestos_face.json', 
                  'model_4_pose.h5', 'model_4_pose.json', 
                  'config.json', 'HandController_icon.png', 'HandController_icon.ico', 
                  'configuracion.ui' ]

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32" :
    base = "Win32GUI"

bdist_msi_options = {
    "add_to_path": False,  # Con True agrega HandController a la variable PATH. Al desinstalar lo borra.
    "all_users": False, 
    # "initial_target_dir": "C:\\Cosas\\HandController",Ê
    "upgrade_code": "{6A34B00E-8A82-4AB6-855C-B474A8232908}",
    "install_icon": "HandController_icon.ico",
}

setup(
    name = "HandController",
    version = "2.0",
    description = "Hand Controller",
    author = 'ACG UAL :: CIADE-IT UBP',
    options = { 
    	# 'build_exe' : { 'packages' : packages, 'include_files' : include_files },
        'build_exe' : { 'packages' : packages, 'includes' : includes, 'include_files' : include_files },        
    	'bdist_msi' : bdist_msi_options,
    },  
    executables = [ Executable( "ventana.py", 
    							base = base, 
    							icon = 'HandController_icon.ico',                                 
    							shortcut_name = 'Hand Controller',
            					shortcut_dir = 'DesktopFolder',
                                target_name = 'HandController_v2.exe' ) ]
)


# Ejemplos de setup.py
# https://python.hotexamples.com/es/examples/cx_Freeze/-/setup/python-setup-function-examples.html