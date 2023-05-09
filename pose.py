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


class Pose( QObject ) :

    signal_procesado = Signal()
    signal_gestoDetectado = Signal( int )


    def __init__( self ) :
        super( Pose, self ).__init__()

        self.camara = 0
        self.configurar()  # Deja disponible self.config con todos los datos del json
        
        # Este es un vector de los últimos 5 gestos distintos que sucedieron. Esto es para detectar algunas
        # combinaciones que se puedan llegar a configurar para realizar alguna acción
        self.vector_secuencia_gestos = np.zeros( 5, dtype = np.int8 ) 
        self.vector_secuencia_gestos.fill( -1 )

        # Es la ventana para los gestos detectados, para que indentifique según la moda
        self.vector_ventana_gestos = np.zeros( self.config[ 'ventana_de_gestos' ], dtype = np.float32 ) 

        # Esto se usa para todos los modoController
        ###################################################
        self.mp_drawing = mp.solutions.drawing_utils 

        self.mp_pose = mp.solutions.pose

        self.poses = self.mp_pose.Pose( min_detection_confidence = self.config[ 'min_detection_confidence' ], 
                                       model_complexity = 2,                                          
                                       static_image_mode = self.config[ 'static_image_mode' ] )


        json_file = open( self.config[ 'model_json_pose' ], 'r' )
        loaded_model_json = json_file.read()
        json_file.close()
        self.loaded_model = model_from_json( loaded_model_json ) 
        self.loaded_model.load_weights( self.config[ 'model_h5_pose' ] )

        # # Estas líneas siguientes está únicamente para que se use por primera vez el método predict ya que
        # # hace que se congele por unos segundos la aplicación. Mejor que este congelamiento se haga antes
        # # de mostrar la cámara
        pose = np.zeros( ( 0, 4 ), dtype = float )
        for i in range( 0, 33 ) :                      
            pose = np.append( pose, [ [ 0, 0, 0, 0 ] ], axis = 0 )
        tensor = T.crearTensor_pose( pose ) 
        predicciones = self.loaded_model.predict( tensor )


        if self.config[ 'capturar_csv_pose' ] == True :

            archivo_csv_existe = False
            if os.path.exists( self.config[ 'archivo_csv' ] ) :
                archivo_csv_existe = True

            self.csv_file = open( self.config[ 'archivo_csv' ], mode = 'at', newline = '' )
            fieldnames = [ 'gesto', 
                           'x0', 'y0', 'z0', 'v0', 'x1', 'y1', 'z1', 'v1', 'x2', 'y2', 'z2', 'v2', 'x3', 'y3', 'z3', 'v3', 
                           'x4', 'y4', 'z4', 'v4', 'x5', 'y5', 'z5', 'v5', 'x6', 'y6', 'z6', 'v6', 'x7', 'y7', 'z7', 'v7', 
                           'x8', 'y8', 'z8', 'v8', 'x9', 'y9', 'z9', 'v9', 'x10', 'y10', 'z10', 'v10', 'x11', 'y11', 'z11', 'v11', 
                           'x12', 'y12', 'z12', 'v12', 'x13', 'y13', 'z13', 'v13', 'x14', 'y14', 'z14', 'v14', 'x15', 'y15', 'z15', 'v15', 
                           'x16', 'y16', 'z16', 'v16', 'x17', 'y17', 'z17', 'v17', 'x18', 'y18', 'z18', 'v18', 'x19', 'y19', 'z19', 'v19', 
                           'x20', 'y20', 'z20', 'v20', 'x21', 'y21', 'z21', 'v21', 'x22', 'y22', 'z22', 'v22', 'x23', 'y23', 'z23', 'v23',
                           'x24', 'y24', 'z24', 'v24', 'x25', 'y25', 'z25', 'v25', 'x26', 'y26', 'z26', 'v26', 'x27', 'y27', 'z27', 'v27',
                           'x28', 'y28', 'z28', 'v28', 'x29', 'y29', 'z29', 'v29', 'x30', 'y30', 'z30', 'v30', 'x31', 'y31', 'z31', 'v31',
                           'x32', 'y32', 'z32', 'v32' ]

            self.writer = csv.DictWriter( self.csv_file, fieldnames = fieldnames )

            if archivo_csv_existe == False :
                self.writer.writeheader()

            


    # Método que lee el json para configurar o actualizar todos los parámetros
    def configurar( self ) :      
        with open( 'config.json' ) as json_file : 
            self.config = json.load( json_file )      


    # Este método se encarga de poner todas las variables y arrays en valores por defecto. Esto es para que no
    # vaya a detectar un clic que haya quedado de un gesto anterior.
    def resetear_metricas( self ) :
        self.vector_frames = np.zeros( self.ventana_frames, dtype = np.float32 ) 
        self.vector_z_promedio = np.zeros( self.ventana_z_promedio, dtype = np.float32 ) 

        
    @Slot()
    def slot_procesar( self ) :

        if self.camara.hayFrame() == False :
            return

        frame = self.camara.frame

        h, w, ch = frame.shape
        bytesPerLine = ch * w

        
        # To improve performance, optionally mark the image as not writeable to pass by reference.
        frame.flags.writeable = False

        results = self.poses.process( frame )

        # Draw the hand annotations on the image.
        frame.flags.writeable = True

        if results.pose_landmarks :
            # results.pose_landmarks = class mediapipe.framework.formats.landmark_pb2.NormalizedLandmarkList

            pose = np.zeros( ( 0, 4 ), dtype = float )

            for pose_landmarks in results.pose_landmarks.landmark :
                # pose_landmarks = class mediapipe.framework.formats.landmark_pb2.NormalizedLandmark
                # results.pose_landmarks.landmark = class google.protobuf.internal.containers.RepeatedCompositeFieldContainer

                pose = np.append( pose, [ [ float( pose_landmarks.x ) * float( w ),
                                            float( pose_landmarks.y ) * float( h ),
                                            float( pose_landmarks.z ) * float( w ),
                                            float( pose_landmarks.visibility ) ] ], 
                                            axis = 0 )

            if self.config[ 'normalizar' ] == True :
                # Realiza todas las transformaciones
                escalada = self.transformar_pose( pose )
            else :
                escalada = pose

            if self.config[ 'capturar_csv_pose' ] == True :

                self.escribirCSV_pose( self.config[ 'nombre_gesto' ], escalada )
                print( escalada, ' - ', self.config[ 'nombre_gesto' ] )

            if self.config[ 'dibujar_esqueleto' ] == True :
                self.mp_drawing.draw_landmarks( frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS )   


            tensor = T.crearTensor_pose( escalada )

            # Este línea lee el config.json y extrae algo así:
            # CLASS_MAP = { 0: 'abierta', 1: 'puno', 2: 'pulgar', 3: 'ok', 
            #               4: 'indice', 5: 'v', 6: 'cuerno' }
            CLASS_MAP = dict( zip( ( int( i ) for i in self.config[ 'gestos_pose' ][ 0 ].keys() ), 
                                   self.config[ 'gestos_pose' ][ 0 ].values() ) )

            # Con esto podemos medir el tiempo que lleva ejecutar la siguiente función
            # e1 = cv2.getTickCount()            

            predicciones = self.loaded_model.predict( tensor )

            # Medimos e imprimimos
            # e2 = cv2.getTickCount() ; segundos = (e2 - e1)/ cv2.getTickFrequency() ; print( segundos )

            predicciones = tf.math.argmax( predicciones, -1 )

            gesto_detectado = CLASS_MAP[ predicciones[ 0 ].numpy() ]
            label_gesto_detectado = list( CLASS_MAP.values() ).index( gesto_detectado )


            if self.config[ 'dibujar_label_gesto' ] == True :

                x_label = self.config[ 'x_label_gesto' ]
                y_label = self.config[ 'y_label_gesto' ]

                ( text_width, text_height ), _ = cv2.getTextSize( gesto_detectado,
                                                                  cv2.FONT_HERSHEY_SIMPLEX,
                                                                  fontScale = 1.2, 
                                                                  thickness = 2 )

                cv2.rectangle( frame, ( x_label - 5, y_label + 9 ),
                               ( x_label + text_width + 3, 
                                 y_label - text_height - 6 ),
                               ( 191, 226, 171 ), thickness = cv2.FILLED )
                                
                cv2.putText( frame, gesto_detectado, ( x_label, y_label ), 
                             cv2.FONT_HERSHEY_SIMPLEX, fontScale = 1.2, color = ( 108, 28, 28 ), 
                             thickness = 2, lineType = cv2.LINE_AA ) 


        self.frameProcesado = frame
        self.signal_procesado.emit()



    def recibirCamara( self, camara ) :
        self.camara = camara

    def detener( self ) : 

        self.camara.apagar()

        if self.config[ 'capturar_csv_face' ] == True :
            self.csv_file.close()
            
        if self.camara.isEncendida() == False :
            print( 'Cámara apagada' )


    def escribirCSV_pose( self, gesto, cuerpo ) :

        self.writer.writerow( { 'gesto': gesto, 
                                'x0': cuerpo[ 0 ][ 0 ], 'y0': cuerpo[ 0 ][ 1 ], 'z0': cuerpo[ 0 ][ 2 ], 'v0': cuerpo[ 0 ][ 3 ],
                                'x1': cuerpo[ 1 ][ 0 ], 'y1': cuerpo[ 1 ][ 1 ], 'z1': cuerpo[ 1 ][ 2 ], 'v1': cuerpo[ 1 ][ 3 ], 
                                'x2': cuerpo[ 2 ][ 0 ], 'y2': cuerpo[ 2 ][ 1 ], 'z2': cuerpo[ 2 ][ 2 ], 'v2': cuerpo[ 2 ][ 3 ], 
                                'x3': cuerpo[ 3 ][ 0 ], 'y3': cuerpo[ 3 ][ 1 ], 'z3': cuerpo[ 3 ][ 2 ], 'v3': cuerpo[ 3 ][ 3 ], 
                                'x4': cuerpo[ 4 ][ 0 ], 'y4': cuerpo[ 4 ][ 1 ], 'z4': cuerpo[ 4 ][ 2 ], 'v4': cuerpo[ 4 ][ 3 ], 
                                'x5': cuerpo[ 5 ][ 0 ], 'y5': cuerpo[ 5 ][ 1 ], 'z5': cuerpo[ 5 ][ 2 ], 'v5': cuerpo[ 5 ][ 3 ], 
                                'x6': cuerpo[ 6 ][ 0 ], 'y6': cuerpo[ 6 ][ 1 ], 'z6': cuerpo[ 6 ][ 2 ], 'v6': cuerpo[ 6 ][ 3 ], 
                                'x7': cuerpo[ 7 ][ 0 ], 'y7': cuerpo[ 7 ][ 1 ], 'z7': cuerpo[ 7 ][ 2 ], 'v7': cuerpo[ 7 ][ 3 ], 
                                'x8': cuerpo[ 8 ][ 0 ], 'y8': cuerpo[ 8 ][ 1 ], 'z8': cuerpo[ 8 ][ 2 ], 'v8': cuerpo[ 8 ][ 3 ], 
                                'x9': cuerpo[ 9 ][ 0 ], 'y9': cuerpo[ 9 ][ 1 ], 'z9': cuerpo[ 9 ][ 2 ], 'v9': cuerpo[ 9 ][ 3 ], 
                                'x10': cuerpo[ 10 ][ 0 ], 'y10': cuerpo[ 10 ][ 1 ], 'z10': cuerpo[ 10 ][ 2 ], 'v10': cuerpo[ 10 ][ 3 ], 
                                'x11': cuerpo[ 11 ][ 0 ], 'y11': cuerpo[ 11 ][ 1 ], 'z11': cuerpo[ 11 ][ 2 ], 'v11': cuerpo[ 11 ][ 3 ], 
                                'x12': cuerpo[ 12 ][ 0 ], 'y12': cuerpo[ 12 ][ 1 ], 'z12': cuerpo[ 12 ][ 2 ], 'v12': cuerpo[ 12 ][ 3 ], 
                                'x13': cuerpo[ 13 ][ 0 ], 'y13': cuerpo[ 13 ][ 1 ], 'z13': cuerpo[ 13 ][ 2 ], 'v13': cuerpo[ 13 ][ 3 ], 
                                'x14': cuerpo[ 14 ][ 0 ], 'y14': cuerpo[ 14 ][ 1 ], 'z14': cuerpo[ 14 ][ 2 ], 'v14': cuerpo[ 14 ][ 3 ], 
                                'x15': cuerpo[ 15 ][ 0 ], 'y15': cuerpo[ 15 ][ 1 ], 'z15': cuerpo[ 15 ][ 2 ], 'v15': cuerpo[ 15 ][ 3 ], 
                                'x16': cuerpo[ 16 ][ 0 ], 'y16': cuerpo[ 16 ][ 1 ], 'z16': cuerpo[ 16 ][ 2 ], 'v16': cuerpo[ 16 ][ 3 ], 
                                'x17': cuerpo[ 17 ][ 0 ], 'y17': cuerpo[ 17 ][ 1 ], 'z17': cuerpo[ 17 ][ 2 ], 'v17': cuerpo[ 17 ][ 3 ], 
                                'x18': cuerpo[ 18 ][ 0 ], 'y18': cuerpo[ 18 ][ 1 ], 'z18': cuerpo[ 18 ][ 2 ], 'v18': cuerpo[ 18 ][ 3 ], 
                                'x19': cuerpo[ 19 ][ 0 ], 'y19': cuerpo[ 19 ][ 1 ], 'z19': cuerpo[ 19 ][ 2 ], 'v19': cuerpo[ 19 ][ 3 ], 
                                'x20': cuerpo[ 20 ][ 0 ], 'y20': cuerpo[ 20 ][ 1 ], 'z20': cuerpo[ 20 ][ 2 ], 'v20': cuerpo[ 20 ][ 3 ], 
                                'x21': cuerpo[ 21 ][ 0 ], 'y21': cuerpo[ 21 ][ 1 ], 'z21': cuerpo[ 21 ][ 2 ], 'v21': cuerpo[ 21 ][ 3 ], 
                                'x22': cuerpo[ 22 ][ 0 ], 'y22': cuerpo[ 22 ][ 1 ], 'z22': cuerpo[ 22 ][ 2 ], 'v22': cuerpo[ 22 ][ 3 ], 
                                'x23': cuerpo[ 23 ][ 0 ], 'y23': cuerpo[ 23 ][ 1 ], 'z23': cuerpo[ 23 ][ 2 ], 'v23': cuerpo[ 23 ][ 3 ], 
                                'x24': cuerpo[ 24 ][ 0 ], 'y24': cuerpo[ 24 ][ 1 ], 'z24': cuerpo[ 24 ][ 2 ], 'v24': cuerpo[ 24 ][ 3 ], 
                                'x25': cuerpo[ 25 ][ 0 ], 'y25': cuerpo[ 25 ][ 1 ], 'z25': cuerpo[ 25 ][ 2 ], 'v25': cuerpo[ 25 ][ 3 ], 
                                'x26': cuerpo[ 26 ][ 0 ], 'y26': cuerpo[ 26 ][ 1 ], 'z26': cuerpo[ 26 ][ 2 ], 'v26': cuerpo[ 26 ][ 3 ], 
                                'x27': cuerpo[ 27 ][ 0 ], 'y27': cuerpo[ 27 ][ 1 ], 'z27': cuerpo[ 27 ][ 2 ], 'v27': cuerpo[ 27 ][ 3 ], 
                                'x28': cuerpo[ 28 ][ 0 ], 'y28': cuerpo[ 28 ][ 1 ], 'z28': cuerpo[ 28 ][ 2 ], 'v28': cuerpo[ 28 ][ 3 ], 
                                'x29': cuerpo[ 29 ][ 0 ], 'y29': cuerpo[ 29 ][ 1 ], 'z29': cuerpo[ 29 ][ 2 ], 'v29': cuerpo[ 29 ][ 3 ], 
                                'x30': cuerpo[ 30 ][ 0 ], 'y30': cuerpo[ 30 ][ 1 ], 'z30': cuerpo[ 30 ][ 2 ], 'v30': cuerpo[ 30 ][ 3 ], 
                                'x31': cuerpo[ 31 ][ 0 ], 'y31': cuerpo[ 31 ][ 1 ], 'z31': cuerpo[ 31 ][ 2 ], 'v31': cuerpo[ 31 ][ 3 ], 
                                'x32': cuerpo[ 32 ][ 0 ], 'y32': cuerpo[ 32 ][ 1 ], 'z32': cuerpo[ 32 ][ 2 ], 'v32': cuerpo[ 32 ][ 3 ] } )



    def transformar_pose( self, pose ) :
        pose_trasladada = T.traslacion_pose( pose )  # Hombro derecho al origen
        pose_trasladada_rotada = T.rotacion_alinear_al_eje_y_pose( pose_trasladada )  # Alinea ambos hombros en el eje Y
        pose_pecho_alineado = T.rotacion_pecho( pose_trasladada_rotada )

        pechoAlFrente = pose_pecho_alineado
        # Lo del pecho al frente no sirve porque cuando la persona esta de espalda, MediaPipe no identifica
        # si está de espaldas, o sea, si la persona se pone de espaldas, le identifica la cara en la nuca
        # if T.isPechoAlFrente( pose_pecho_alineado ) == False :
        #     pechoAlFrente = T.rotacion_sobre_ejeY_pose( pose_pecho_alineado, 180 )

        escalada = T.escalado_pose( pechoAlFrente, 100, True )

        return escalada
