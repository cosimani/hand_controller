import os, sys

import cv2 

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# Con lo siguiente se ven las versiones y los paquetes de python instalados: pip3 freeze
import mediapipe as mp  # mediapipe==0.8.1 # Para detectar los KeyPoints

import numpy as np
import statistics as stat
import math

import tkinter as tk

import json
import glob
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from matplotlib import pyplot as plt
from datetime import datetime
from time import time

import pyautogui
from pywinauto import mouse

import transformaciones as T
import utiles as U
import ventana

import csv
import json

from time import time

from keras.models import model_from_json

from skimage.filters import threshold_yen
from skimage.exposure import rescale_intensity

np.set_printoptions( suppress = True )  # Para que la notacion no sea la cientifica

class Camara( QObject ) :

    # Definimos una signal
    # Para más info ver: https://wiki.qt.io/Qt_for_Python_Signals_and_Slots
    # No pude programar que la signal envíe la imagen, así que cn esta signal aviso que hay nuevo frame
    signal_newFrame = Signal()

    def __init__( self ) :
        super( Camara, self ).__init__()

        self.ventana = 0

        self.configurar()  # Deja disponible self.config con todos los datos del json
        
        self.videoCapture = cv2.VideoCapture( self.config[ 'camara_o_mp4' ] )

        # Creo una imagen negra de 10 x 10 y la interpretaré como una imagen vacía. Es para chequear cuando inicia el programa
        self.frame = np.zeros( ( 10, 10, 3 ),'uint8' )

        if self.config[ 'control_prop_camara' ] == True :

	        print( '\nPropiedades de la Cámara al iniciar' )

	        for prop in U.propiedades_de_la_camara :
	            val = self.videoCapture.get( eval( "cv2." + prop ) )
	            print ( prop, ": " , str( val ) )

	        self.videoCapture.set( cv2.CAP_PROP_BRIGHTNESS,         self.config[ 'propiedades_camara' ][ 0 ] )
	        self.videoCapture.set( cv2.CAP_PROP_CONTRAST,           self.config[ 'propiedades_camara' ][ 1 ] )
	        self.videoCapture.set( cv2.CAP_PROP_SATURATION,         self.config[ 'propiedades_camara' ][ 2 ] ) 
	        self.videoCapture.set( cv2.CAP_PROP_HUE,                self.config[ 'propiedades_camara' ][ 3 ] ) 
	        self.videoCapture.set( cv2.CAP_PROP_AUTO_WB,            self.config[ 'propiedades_camara' ][ 4 ] ) 
	        self.videoCapture.set( cv2.CAP_PROP_GAMMA,              self.config[ 'propiedades_camara' ][ 5 ] ) 
	        self.videoCapture.set( cv2.CAP_PROP_WB_TEMPERATURE,     self.config[ 'propiedades_camara' ][ 6 ] ) 
	        self.videoCapture.set( cv2.CAP_PROP_SHARPNESS,          self.config[ 'propiedades_camara' ][ 7 ] ) 
	        self.videoCapture.set( cv2.CAP_PROP_BACKLIGHT,          self.config[ 'propiedades_camara' ][ 8 ] ) 
	        self.videoCapture.set( cv2.CAP_PROP_AUTO_EXPOSURE,      self.config[ 'propiedades_camara' ][ 9 ] )
	        self.videoCapture.set( cv2.CAP_PROP_TEMPERATURE,        self.config[ 'propiedades_camara' ][ 10 ] ) 

	        print( '\nPropiedades de la Cámara luego de configurarla' )

	        for prop in U.propiedades_de_la_camara :
	            val = self.videoCapture.get( eval( "cv2." + prop ) )
	            print ( prop, ": " , str( val ) )

	        print( '\n' )            

        if self.config[ 'contador_de_frames' ] : 
            self.contador_de_frames = 1

        self.timer = QTimer()

        # Connecting the signal
        QObject.connect( self.timer, SIGNAL( "timeout()" ), self.slot_capturar )
        self.timer.start( self.config[ 'tiempo_para_timer_procesar' ] )        


    # Método que lee el json para configurar o actualizar todos los parámetros
    def configurar( self ) :      
        with open( 'config.json' ) as json_file : 
            self.config = json.load( json_file )      


    def pausar( self ) :
        if self.timer.isActive() :
            self.timer.stop()
        else :
            self.timer.start( self.config[ 'tiempo_para_timer_procesar' ] ) 
        
    def detener( self ) :
        self.timer.stop()

    def iniciar( self ) :
        self.timer.start( self.config[ 'tiempo_para_timer_procesar' ] ) 


    def recibirVentana( self, ventana ) :
        self.ventana = ventana


    def apagar( self ) :
        self.videoCapture.release()

    def isEncendida( self ) :
        return self.videoCapture.isOpened()

    def hayFrame( self ) :
        if self.frame.shape[ 0 ] == 10 and self.frame.shape[ 1 ] == 10 : 
            return False
        return True


    @Slot()
    def slot_capturar( self ) :

        if self.videoCapture.isOpened() == False :
            return

        success, self.frame = self.videoCapture.read()

        if success == False :
            return

        # Para que no rote la imagen si es un video mp4
        if str( self.config[ 'camara_o_mp4' ] ).find( 'mp4' ) == -1 :
            self.frame = cv2.flip( self.frame, 1 )

        self.frame = cv2.cvtColor( self.frame, cv2.COLOR_BGR2RGB )

        self.signal_newFrame.emit()  # Emite una signal avisando que en camara hay nuevo frame


    def detener( self ) : 

        self.timer.stop()
        self.videoCapture.release()
            
        if self.videoCapture.isOpened() == False :
            print( 'Cámara apagada' )

