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
import camara
import hand
import face
import pose

import csv
import json

from time import time

from keras.models import model_from_json

from skimage.filters import threshold_yen
from skimage.exposure import rescale_intensity

np.set_printoptions( suppress = True )  # Para que la notacion no sea la cientifica

class Visor( QLabel ) :



    def __init__( self ) :
        super( Visor, self ).__init__()

        self.ventana = 0

        self.configurar()  # Deja disponible self.config con todos los datos del json
        
        
        # Para tener información de si el clic izquierdo está pulsado. Se usa en el modo dibujar.
        self.mouseDownLeft = False
        # Para tener información de si el clic derecho está pulsado
        self.mouseDownRight = False   

        self.camara = camara.Camara()
        self.hand = hand.Hand() 
        self.hand.recibirCamara( self.camara )
        self.face = face.Face() 
        self.face.recibirCamara( self.camara )
        self.pose = pose.Pose() 
        self.pose.recibirCamara( self.camara )

        self.isCapturando = False
        self.contadorCapturas = 0
        self.cuantasRepeticionesDeCapturasVan = 0
        self.cuantasCapturas = 0

        if self.config[ 'contador_de_frames' ] : 
            self.contador_de_frames = 1

        root = tk.Tk()
        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()
        print( 'Resolución de la pantalla: %d x %d' % ( self.screen_w, self.screen_h ) )

        screen = QGuiApplication.primaryScreen()
        screen_w = screen.availableSize().width()
        screen_h = screen.availableSize().height()
        self.escala_dpi = self.screen_w / screen_w   


        # Lo siguiente es para calcular los fps y adaptar los parámetros para la detección de gestos
        # Hace un promedio entre los últimos 5
        self.tiempos_procesamiento = np.zeros( 5, dtype = np.float32 )
        self.tiempo_procesamiento_start_time = 0

        ############################# Conexiones Signals - Slots
        # self.hand.signal_procesado.connect( self.slot_pintar )
        # self.camara.signal_newFrame.connect( self.hand.slot_procesar )

        # self.face.signal_procesado.connect( self.slot_pintar )
        # self.camara.signal_newFrame.connect( self.face.slot_procesar )

        self.pose.signal_procesado.connect( self.slot_pintar )
        self.camara.signal_newFrame.connect( self.pose.slot_procesar )

        


    # Método que lee el json para configurar o actualizar todos los parámetros
    def configurar( self ) :      
        with open( 'config.json' ) as json_file : 
            self.config = json.load( json_file )      

          

    def recibirVentana( self, ventana ) :
        self.ventana = ventana


    @Slot()
    def slot_pintar( self ) :

        # if self.hand.camara.hayFrame() == False :
        #     return

        # frame = self.hand.frameProcesado

        # if self.face.camara.hayFrame() == False :
        #     return

        # frame = self.face.frameProcesado

        if self.pose.camara.hayFrame() == False :
            return

        frame = self.pose.frameProcesado


        h, w, ch = frame.shape
        bytesPerLine = ch * w

        convertToQtFormat = QImage( frame.data, w, h, bytesPerLine, QImage.Format_RGB888 )
        im = convertToQtFormat.scaled( self.ventana.width(), self.ventana.height() )

        im = im.convertToFormat( QImage.Format_ARGB32 )

        alpha = QImage( im.width(), im.height(), QImage.Format_Alpha8 )
        alpha.fill( self.config[ 'alpha_camara' ] )

        im.setAlphaChannel( alpha );

        pixmap = QPixmap.fromImage( im )
        self.setPixmap( pixmap );
