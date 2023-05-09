import os, sys

from PySide6.QtCore import *
from PySide6.QtGui import QIcon, QGuiApplication, QPixmap, QImage
from PySide6.QtWidgets import QWidget, QApplication, QGridLayout, QSystemTrayIcon, QMenu, QLabel
from PySide6.QtUiTools import QUiLoader

import json
import glob

from datetime import datetime
from time import time

import numpy as np

import utiles as U
import ventana

np.set_printoptions( suppress = True )  # Para que la notacion no sea la cientifica


class Configuracion( QWidget ) :

    signal_jsonActualizado = Signal()

    def __init__( self, parent = None ) :
        super( Configuracion, self ).__init__( parent )

        loader = QUiLoader()
        self.gui = loader.load( "configuracion.ui", None )  # configuracion.ui debe estar en la misma carpeta

        self.gui.show()

        print( type( self.gui ), self.gui.width(), self.gui.windowOpacity () )

        # Define un layout en self y coloca allí la interfaz creada con QtDesigner
        grid = QGridLayout()
        grid.setContentsMargins( 0, 0, 0, 0 )
        grid.addWidget( self.gui )
        self.setLayout( grid )
 
        self.setWindowTitle( 'Panel de configuración' )

        with open( 'config.json' ) as json_file : 
            self.config = json.load( json_file ) 

        QObject.connect( self.gui.pbActualizar, SIGNAL( "pressed()" ), self.slot_actualizar )

        self.leerJsonCargandoGUI()

        # Es necesario para que no se cierre la aplicación cuando cerramos la ventana de configuración
        self.setAttribute( Qt.WA_QuitOnClose, False )

        

    def leerJsonCargandoGUI( self ) :

        print( 'deshabilitar_todas_las_interacciones', self.config[ 'deshabilitar_todas_las_interacciones' ] )
        print( 'deshabilitar_secuencias_de_gestos', self.config[ 'deshabilitar_secuencias_de_gestos' ] )
        print( 'mostrar_margenes', self.config[ 'mostrar_margenes' ] )
        print( 'mostrar_fps', self.config[ 'mostrar_fps' ] )
        print( 'dibujar_esqueleto', self.config[ 'dibujar_esqueleto' ] )

        if self.config[ 'deshabilitar_todas_las_interacciones' ] :
            self.gui.checkInteraciones.setCheckState( Qt.Unchecked )
        else : 
            self.gui.checkInteraciones.setCheckState( Qt.Checked )

        if self.config[ 'deshabilitar_secuencias_de_gestos' ] :
            self.gui.checkSecuenciaGestos.setCheckState( Qt.Unchecked )
        else : 
            self.gui.checkSecuenciaGestos.setCheckState( Qt.Checked )

        if self.config[ 'dibujar_esqueleto' ] :
            self.gui.checkBoxEsqueleto.setCheckState( Qt.Checked )
        else : 
            self.gui.checkBoxEsqueleto.setCheckState( Qt.Unchecked )

        if self.config[ 'mostrar_fps' ] :
            self.gui.checkBoxFPS.setCheckState( Qt.Checked )
        else : 
            self.gui.checkBoxFPS.setCheckState( Qt.Unchecked )

        if self.config[ 'mostrar_margenes' ] :
            self.gui.checkBoxMargenes.setCheckState( Qt.Checked )
        else : 
            self.gui.checkBoxMargenes.setCheckState( Qt.Unchecked )

        if self.config[ 'dibujar_label_gesto' ] :
            self.gui.checkBoxLabelGesto.setCheckState( Qt.Checked )
        else : 
            self.gui.checkBoxLabelGesto.setCheckState( Qt.Unchecked )

        if self.config[ 'mostrar_texto_drag_and_drop_etc' ] :
            self.gui.checkBoxMostrarDragAndDrop.setCheckState( Qt.Checked )
        else : 
            self.gui.checkBoxMostrarDragAndDrop.setCheckState( Qt.Unchecked )

        if self.config[ 'corregir_imagen_de_alguna_manera' ] :
            self.gui.checkBoxCorreccion.setCheckState( Qt.Checked )
        else : 
            self.gui.checkBoxCorreccion.setCheckState( Qt.Unchecked )

        if self.config[ 'clic_con_L1_en_lugar_de_z' ] :
            self.gui.checkBoxClicConL.setCheckState( Qt.Checked )
        else : 
            self.gui.checkBoxClicConL.setCheckState( Qt.Unchecked )

        self.gui.leAnchoImagen.setText( str( self.config[ 'ancho_imagen_camara' ] ) )
        self.gui.leAltoImagen.setText( str( self.config[ 'alto_imagen_camara' ] ) )

        if self.config[ 'posicion_ventana' ] == "centro" :
            self.gui.rbPosCentro.setChecked( True )
        elif self.config[ 'posicion_ventana' ] == "abajo_der" :
            self.gui.rbPosAbaDer.setChecked( True )
        elif self.config[ 'posicion_ventana' ] == "arriba_der" :
            self.gui.rbPosArrDer.setChecked( True )
        elif self.config[ 'posicion_ventana' ] == "abajo_izq" :
            self.gui.rbPosAbaIzq.setChecked( True )
        elif self.config[ 'posicion_ventana' ] == "arriba_izq" :
            self.gui.rbPosArrIzq.setChecked( True )

        self.gui.leLambda.setText( str( self.config[ '_lambda' ] ) )
        self.gui.lea_x.setText( str( self.config[ 'a_x' ] ) )
        self.gui.leb_x.setText( str( self.config[ 'b_x' ] ) )
        self.gui.lea_y.setText( str( self.config[ 'a_y' ] ) )
        self.gui.leb_y.setText( str( self.config[ 'b_y' ] ) )

        self.gui.leAlphaCamara.setText( str( self.config[ 'alpha_camara' ] ) )
        self.gui.leAlphaTeclado.setText( str( self.config[ 'alpha_teclado' ] ) )


        if self.config[ 'control_o_dibujar' ] == True :
            self.gui.rbNavegacion.setChecked( True )
        else :
            self.gui.rbDibujo.setChecked( True )

        
            


        ################ Depuradores
        self.gui.leTiempoParaAccionar.setText( str( self.config[ 'tiempo_para_accionar' ] ) )
        self.gui.leMouseGesto.setText( str( self.config[ 'control_mouse_gesto' ] ) )
        self.gui.leMouseKeypoint.setText( str( self.config[ 'control_mouse_keypoint' ] ) )
        self.gui.leMouseFactorCercano.setText( str( self.config[ 'mouse_factor_cercano' ] ) )
        self.gui.leClicCercanoGesto.setText( str( self.config[ 'clic_cercano_gesto' ] ) )
        self.gui.leClicDerechoCercanoGesto.setText( str( self.config[ 'clic_derecho_cercano_gesto' ] ) )
        self.gui.leClicKeypointZ.setText( str( self.config[ 'clic_keypoint_z' ] ) )
        self.gui.leClicKeypointL.setText( str( self.config[ 'clic_keypoint_L_antes_de_clic' ] ) )
        self.gui.leVentanaClic.setText( str( self.config[ 'ventana_clic' ] ) )
        self.gui.leVentanaClicL1.setText( str( self.config[ 'ventana_clic_L1' ] ) )


  
    def slot_actualizar( self ) :
        
        print( 'Actualizar' )

        if self.gui.checkInteraciones.isChecked() :
            self.config[ 'deshabilitar_todas_las_interacciones' ] = False
        else : 
            self.config[ 'deshabilitar_todas_las_interacciones' ] = True

        if self.gui.checkSecuenciaGestos.isChecked() :
            self.config[ 'deshabilitar_secuencias_de_gestos' ] = False
        else : 
            self.config[ 'deshabilitar_secuencias_de_gestos' ] = True

        if self.gui.checkBoxEsqueleto.isChecked() :
            self.config[ 'dibujar_esqueleto' ] = True
        else : 
            self.config[ 'dibujar_esqueleto' ] = False

        if self.gui.checkBoxFPS.isChecked() :
            self.config[ 'mostrar_fps' ] = True
        else : 
            self.config[ 'mostrar_fps' ] = False

        if self.gui.checkBoxMargenes.isChecked() :
            self.config[ 'mostrar_margenes' ] = True
        else : 
            self.config[ 'mostrar_margenes' ] = False

        if self.gui.checkBoxLabelGesto.isChecked() :
            self.config[ 'dibujar_label_gesto' ] = True
        else : 
            self.config[ 'dibujar_label_gesto' ] = False

        if self.gui.checkBoxMostrarDragAndDrop.isChecked() :
            self.config[ 'mostrar_texto_drag_and_drop_etc' ] = True
        else : 
            self.config[ 'mostrar_texto_drag_and_drop_etc' ] = False

        if self.gui.checkBoxCorreccion.isChecked() :
            self.config[ 'corregir_imagen_de_alguna_manera' ] = True
        else : 
            self.config[ 'corregir_imagen_de_alguna_manera' ] = False

        if self.gui.checkBoxClicConL.isChecked() :
            self.config[ 'clic_con_L1_en_lugar_de_z' ] = True
        else : 
            self.config[ 'clic_con_L1_en_lugar_de_z' ] = False

        self.config[ 'ancho_imagen_camara' ] = int( self.gui.leAnchoImagen.text() )
        self.config[ 'alto_imagen_camara' ] = int( self.gui.leAltoImagen.text() )

        if self.gui.rbPosCentro.isChecked() :
            self.config[ 'posicion_ventana' ] = "centro"
        elif self.gui.rbPosAbaDer.isChecked() :
            self.config[ 'posicion_ventana' ] = "abajo_der"
        elif self.gui.rbPosArrDer.isChecked() :
            self.config[ 'posicion_ventana' ] = "arriba_der"
        elif self.gui.rbPosAbaIzq.isChecked() :
            self.config[ 'posicion_ventana' ] = "abajo_izq"
        elif self.gui.rbPosArrIzq.isChecked() :
            self.config[ 'posicion_ventana' ] = "arriba_izq"

        self.config[ '_lambda' ] = float( self.gui.leLambda.text() )
        self.config[ 'a_x' ] = float( self.gui.lea_x.text() )
        self.config[ 'b_x' ] = float( self.gui.leb_x.text() )
        self.config[ 'a_y' ] = float( self.gui.lea_y.text() )
        self.config[ 'b_y' ] = float( self.gui.leb_y.text() )
        
        self.config[ 'alpha_camara' ] = float( self.gui.leAlphaCamara.text() )
        self.config[ 'alpha_teclado' ] = float( self.gui.leAlphaTeclado.text() )

        if self.gui.rbNavegacion.isChecked() :
            self.config[ 'control_o_dibujar' ] = True
        elif self.gui.rbDibujo.isChecked() :
            self.config[ 'control_o_dibujar' ] = False

        ################ Depuradores
        self.config[ 'tiempo_para_accionar' ] = int( self.gui.leTiempoParaAccionar.text() )
        self.config[ 'control_mouse_gesto' ] = int( self.gui.leMouseGesto.text() )
        self.config[ 'control_mouse_keypoint' ] = int( self.gui.leMouseKeypoint.text() )
        self.config[ 'mouse_factor_cercano' ] = int( self.gui.leMouseFactorCercano.text() )
        self.config[ 'clic_cercano_gesto' ] = int( self.gui.leClicCercanoGesto.text() )
        self.config[ 'clic_derecho_cercano_gesto' ] = int( self.gui.leClicDerechoCercanoGesto.text() )
        self.config[ 'clic_keypoint_z' ] = int( self.gui.leClicKeypointZ.text() )
        self.config[ 'clic_keypoint_L_antes_de_clic' ] = int( self.gui.leClicKeypointL.text() )
        self.config[ 'ventana_clic' ] = int( self.gui.leVentanaClic.text() )
        self.config[ 'ventana_clic_L1' ] = int( self.gui.leVentanaClicL1.text() )

   


        with open( 'config.json', 'w' ) as outfile:
            json.dump( self.config, outfile, indent = 4 )

        self.signal_jsonActualizado.emit()

