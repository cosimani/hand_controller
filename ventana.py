import os, sys

from PySide6.QtCore import *
from PySide6.QtGui import QIcon, QGuiApplication, QPixmap, QImage
from PySide6.QtWidgets import QWidget, QApplication, QGridLayout, QSystemTrayIcon, QMenu, QLabel, QMessageBox

import numpy as np
import cv2

import tkinter as tk

import json
import glob
from matplotlib import pyplot as plt
from datetime import datetime
from time import time

import visor
import configuracion
import teclado
import utiles as U

import pyautogui
import pywinauto

np.set_printoptions( suppress = True )  # Para que la notacion no sea la cientifica


class Ventana( QWidget ) :
    def __init__( self, parent = None ) :
        super( Ventana, self ).__init__( parent )

        self.configurar()  # Deja disponible self.config con todos los datos del json

        self.visor = visor.Visor()
        self.visor.recibirVentana( self )

        grid = QGridLayout()
        grid.setContentsMargins( 0, 0, 0, 0 )
        grid.addWidget( self.visor, 0, 0 )
        self.setLayout( grid ) 
        self.setWindowTitle( 'HandController' )

        self.teclado = teclado.Teclado()
        self.teclado.setWindowOpacity( self.config[ 'alpha_teclado' ] )

        self.configuracion = configuracion.Configuracion()

        # SysTray Icon
        tray = QSystemTrayIcon( self )

        # Check if System supports STray icons
        if tray.isSystemTrayAvailable() :
            tray.setIcon( QIcon( "HandController_icon.png" ) )

            # Context Menu
            ctmenu = QMenu()
            actionshow = ctmenu.addAction( "Show/Hide" )
            actionshow.triggered.connect( lambda: self.hide() if self.isVisible() else self.show() )
            actionConfig = ctmenu.addAction( "Config" )
            actionConfig.triggered.connect( self.slot_configuracion )
            actionNUI = ctmenu.addAction( "NUI on/off" )
            actionNUI.triggered.connect( self.slot_nui_onoff )
            actionquit = ctmenu.addAction( "Quit" )
            actionquit.triggered.connect( self.slot_cerrarAplicacion )

            tray.setContextMenu( ctmenu )
            tray.show()
        else :
            # Destroy unused var
            tray = None
                       

        self.setAttribute( Qt.WA_TranslucentBackground )  # Hace transparente el color gris de los widgets

        # Para que se mantenga en top - para ventana sin bordes - y para que el clic atraviese esta ventana 
        # Tool para ocultar el windowIcon
        self.setWindowFlags( Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowTransparentForInput | Qt.Tool )  


        ############################# Conexiones Signals - Slots
        # self.visor.hand.signal_abrirTecladoVirtual.connect( self.slot_abrirTecladoVirtual )        

        QObject.connect( self.visor.hand, SIGNAL( "signal_abrirTecladoVirtual()" ), self.slot_abrirTecladoVirtual )
        QObject.connect( self.visor.hand, SIGNAL( "signal_cerrarAplicacion()" ), self.slot_cerrarAplicacion )        
        QObject.connect( self.visor.hand, SIGNAL( "signal_activarDesactivarProcesamiento()" ), self.slot_activarDesactivarProcesamiento )
        QObject.connect( self.visor.hand, SIGNAL( "signal_cambiarDeManoDerechaIzquierda()" ), self.slot_cambiarDeManoDerechaIzquierda )
        QObject.connect( self.visor.hand, SIGNAL( "signal_intercambiarControlDibujar()" ), self.slot_intercambiarControlDibujar )
        QObject.connect( self.teclado, SIGNAL( "signal_clic( int )" ), self, SLOT( 'slot_teclaPulsada( int )' ) )
        QObject.connect( self.configuracion, SIGNAL( "signal_jsonActualizado()" ), self.slot_jsonActualizado )

        # self.visor.hand.signal_thumb.connect( self.abrirGaleria )

        # self.galeria.signal_gameOver.connect( self.iniciar )




    # Método que lee el json para configurar o actualizar todos los parámetros
    def configurar( self ) :      

        # Aquí leemos el archivo config.json para traer las variables de configuración
        # Podemos acceder así: config[ 'max_num_hands' ]
        # Al usar dentro del with el archivo se cierra autmáticamente al salir del with
        with open( 'config.json' ) as json_file : 
            self.config = json.load( json_file )      

    @Slot( int )
    def slot_teclaPulsada( self, id ) :      
        print( 'id =', id, 'tecla =', U.teclas[ id ] ) 
        pywinauto.keyboard.send_keys( U.teclas[ id ] )

    def slot_jsonActualizado( self ) :      
        with open( 'config.json' ) as json_file : 
            self.config = json.load( json_file ) 

        self.visor.config = self.config

        screen = QGuiApplication.primaryScreen()
        screen_w = screen.availableSize().width()
        screen_h = screen.availableSize().height()

        ancho_imagen_camara = self.config[ 'ancho_imagen_camara' ]
        alto_imagen_camara = self.config[ 'alto_imagen_camara' ]
        self.resize( ancho_imagen_camara, alto_imagen_camara )

        if self.config[ 'posicion_ventana' ] == 'centro' :
            self.move( screen_w / 2 - ancho_imagen_camara / 2, screen_h / 2 - alto_imagen_camara / 2 )
        elif self.config[ 'posicion_ventana' ] == 'abajo_der' :        
            self.move( screen_w - ancho_imagen_camara, screen_h - alto_imagen_camara )
        elif self.config[ 'posicion_ventana' ] == 'arriba_izq' :        
            self.move( 0, 0 )
        elif self.config[ 'posicion_ventana' ] == 'arriba_der' :        
            self.move( screen_w - ancho_imagen_camara, 0 )
        elif self.config[ 'posicion_ventana' ] == 'abajo_izq' :        
            self.move( 0, screen_h - alto_imagen_camara )

        

    def slot_cambiarDeManoDerechaIzquierda( self ) :
        print( 'slot_cambiarDeManoDerechaIzquierda' )     
        self.visor.hand.cambiarDeManoDerechaIzquierda()

    def slot_intercambiarControlDibujar( self ) :
        print( 'slot_intercambiarControlDibujar' )     
        self.visor.hand.intercambiarControlDibujar()

    def slot_activarDesactivarProcesamiento( self ) :
        print( 'slot_activarDesactivarProcesamiento' )     
        self.visor.hand.activarDesactivarProcesamiento()

    def slot_cerrarAplicacion( self ) :
        self.close()        

    def slot_configuracion( self ) :
        self.configuracion.resize( 900, 750 )
        self.configuracion.move( 0, 0 )
        self.configuracion.leerJsonCargandoGUI()   
        self.configuracion.show()   

    def slot_nui_onoff( self ) :
        self.visor.activarDesactivarProcesamiento()    


    @Slot( int )
    def slot_gestoDetectado( self, label_gesto_detectado ) :
        print( 'slot_gestoDetectado()', label_gesto_detectado )

    def resizeEvent( self, e ) :
        print( 'old=', e.oldSize(), 'visor=', self.visor.size() )
        print( 'size=', e.size(), 'visor=', self.visor.size() )

    def slot_capturar( self ) :
        self.visor.capturarParaCSV( cuantos = 500 )

    def slot_abrirTecladoVirtual( self ) :    
        print( 'teclado')  
        if self.teclado.isVisible() :
            self.teclado.hide()
        else : 
            self.teclado.show()


    def keyPressEvent( self, e ) :

        if e.key() == Qt.Key_Escape :
            self.close()

        elif e.key() == Qt.Key_N :
            event = QMouseEvent( QEvent.MouseButtonPress, QCursor.pos(), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier )
            QCoreApplication.sendEvent( self, event )

        elif e.key() == Qt.Key_C :
            self.slot_capturar()

        elif e.key() == Qt.Key_P :  # P de prueba
            self.visor.prueba()

        elif e.key() == Qt.Key_Space :  # P de prueba
            self.visor.pausar()

    def closeEvent( self, e ) :
        self.visor.hand.detener()        
        qApp.quit()     
        sys.exit()

    def showEvent( self, e ) :
        screen = QGuiApplication.primaryScreen()
        screen_w = screen.availableSize().width()
        screen_h = screen.availableSize().height()

        ancho_imagen_camara = self.config[ 'ancho_imagen_camara' ]
        alto_imagen_camara = self.config[ 'alto_imagen_camara' ]
        self.resize( ancho_imagen_camara, alto_imagen_camara )

        if self.config[ 'posicion_ventana' ] == 'centro' :
            self.move( screen_w / 2 - ancho_imagen_camara / 2, screen_h / 2 - alto_imagen_camara / 2 )
        elif self.config[ 'posicion_ventana' ] == 'abajo_der' :        
            self.move( screen_w - ancho_imagen_camara, screen_h - alto_imagen_camara )
        elif self.config[ 'posicion_ventana' ] == 'arriba_izq' :        
            self.move( 0, 0 )
        elif self.config[ 'posicion_ventana' ] == 'arriba_der' :        
            self.move( screen_w - ancho_imagen_camara, 0 )
        elif self.config[ 'posicion_ventana' ] == 'abajo_izq' :        
            self.move( 0, screen_h - alto_imagen_camara )

if __name__ == '__main__':
    app = QApplication( sys.argv )

    # Aquí detectamos el archivo .py que estamos ejecutando, leemos su directorio y la seteamos como
    # carpeta de trabajo. Esto es para que independientemente desde dónde se ejecute este .py, que la
    # carpeta de trabajo sea la misma donde se encuentra el .py ejecutado.
    os.chdir( os.path.dirname( os.path.abspath( __file__ ) ) )

    with open( 'config.json' ) as json_file : 
        config = json.load( json_file )      

    if config[ 'modoController' ] == 'HandController' :
        app.setApplicationName( "Hand Controller" )
    elif config[ 'modoController' ] == 'PoseController' :        
        app.setApplicationName( "Pose Controller" )
    elif config[ 'modoController' ] == 'FaceController' :        
        app.setApplicationName( "Face Controller" )
    else :
        app.setApplicationName( "Hand Controller" )
    app.setOrganizationName( "CIADE-IT UBP - ACG UAL" )    

    ventana = Ventana()
    ventana.resize( 0, 0 )  # Esto para que no se vea un destello al iniciar la aplicación
    ventana.show()


    sys.exit( app.exec_() )