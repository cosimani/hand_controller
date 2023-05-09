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

import csv
import json

from time import time

from keras.models import model_from_json

from skimage.filters import threshold_yen
from skimage.exposure import rescale_intensity

np.set_printoptions( suppress = True )  # Para que la notacion no sea la cientifica


class Face( QObject ) :

    signal_procesado = Signal()
    signal_gestoDetectado = Signal( int )



    def __init__( self ) :
        super( Face, self ).__init__()

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

        self.mp_face = mp.solutions.face_mesh

        self.face = self.mp_face.FaceMesh( min_detection_confidence = self.config[ 'min_detection_confidence_cara' ], 
                                           max_num_faces = 2,                                          
                                           static_image_mode = self.config[ 'static_image_mode_cara' ] )

        json_file_cara = open( self.config[ 'model_json_cara' ], 'r' )
        loaded_model_json_cara = json_file_cara.read()
        json_file_cara.close()
        self.loaded_model_cara = model_from_json( loaded_model_json_cara ) 
        self.loaded_model_cara.load_weights( self.config[ 'model_h5_cara' ] )

        cara = np.zeros( ( 0, 3 ), dtype = float )
        for i in range( 0, 468 ) :                      
            cara = np.append( cara, [ [ 0, 0, 0 ] ], axis = 0 )
        tensor_cara = T.crearTensor_cara( cara ) 
        predicciones_cara = self.loaded_model_cara.predict( tensor_cara )

        # elif self.config[ 'modoController' ] == 'FaceDetection' :

        self.mp_face_detection = mp.solutions.face_detection

        self.face_detection = self.mp_face_detection.FaceDetection( model_selection = 0, 
                                                                    min_detection_confidence = 0.5 )

         



        # Lo siguiente es para crear el dataset en CSV
        # Primero abrimos el archivo y escribimos la cabecera en el constructor de Visor
        # Luego registramos rows en slot_procesar
        # Y por último cerramos el archivo en detener() 

        if self.config[ 'capturar_csv_face' ] == True :

            archivo_csv_existe = False
            if os.path.exists( self.config[ 'archivo_csv' ] ) :
                archivo_csv_existe = True

            self.csv_file = open( self.config[ 'archivo_csv' ], mode = 'at', newline = '' )
            
            fieldnames = [ 'gesto' ]

            for i in range( 468 ) :
                fieldnames.append( 'x' + str( i ) )
                fieldnames.append( 'y' + str( i ) )
                fieldnames.append( 'z' + str( i ) )

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
        results_cara = self.face.process( frame )

        # Draw the hand annotations on the image.
        frame.flags.writeable = True

        drawing_spec_cara = self.mp_drawing.DrawingSpec( thickness = 1, circle_radius = 1 )

        if results_cara.multi_face_landmarks :

            for face_landmarks in results_cara.multi_face_landmarks :

                cara = np.zeros( ( 0, 3 ), dtype = float )

                for i in range( 0, 468 ) :
                    # Notar aquí que hacemos una escalado según el ancho y alto de la imagen, y como la 
                    # documentación de mediapipe dice que z tiene una escala similar a x, entonces
                    # por eso multiplicamos z por w
                    cara = np.append( cara, [ [ float( face_landmarks.landmark[ i ].x ) * float( w ),
                                                float( face_landmarks.landmark[ i ].y ) * float( h ),
                                                float( face_landmarks.landmark[ i ].z ) * float( w ) ] ], 
                                                axis = 0 )

                # Realiza todas las transformaciones
                escalada_cara = self.transformar_cara( cara )

                if self.config[ 'capturar_csv_face' ] == True :

                    self.escribirCSV_face( self.config[ 'nombre_gesto' ], escalada_cara )
                    print( escalada_cara, ' - ', self.config[ 'nombre_gesto' ] )


                tensor_cara = T.crearTensor_cara( escalada_cara )

                # Este línea lee el config.json y extrae algo así:
                # CLASS_MAP = { 0: 'blank', 1: 'smile' }
                CLASS_MAP_cara = dict( zip( ( int( i ) for i in self.config[ 'gestos_cara' ][ 0 ].keys() ), 
                                       self.config[ 'gestos_cara' ][ 0 ].values() ) )

                predicciones_cara = self.loaded_model_cara.predict( tensor_cara )
                predicciones_cara = tf.math.argmax( predicciones_cara, -1 )

                gesto_detectado_cara = CLASS_MAP_cara[ predicciones_cara[ 0 ].numpy() ]
                label_gesto_detectado_cara = list( CLASS_MAP_cara.values() ).index( gesto_detectado_cara )

                if self.config[ 'dibujar_esqueleto' ] == True :
                    # self.mp_drawing.draw_landmarks( frame, results.multi_face_landmarks, self.mp_pose.POSE_CONNECTIONS )   

                    # self.mp_drawing.draw_landmarks( image = frame,
                    #                                 landmark_list = face_landmarks,
                    #                                 connections = self.mp_face.FACEMESH_TESSELATION,
                    #                                 landmark_drawing_spec = drawing_spec_cara,
                    #                                 connection_drawing_spec = drawing_spec_cara )
                    self.mp_drawing.draw_landmarks( image = frame,
                                                    landmark_list = face_landmarks,
                                                    connections = self.mp_face.FACEMESH_CONTOURS,
                                                    landmark_drawing_spec = drawing_spec_cara,
                                                    connection_drawing_spec = drawing_spec_cara )
                    # self.mp_drawing.draw_landmarks( image = frame,
                    #                                 landmark_list = face_landmarks,
                    #                                 connections = self.mp_face.FACEMESH_IRISES,
                    #                                 landmark_drawing_spec = None,
                    #                                 connection_drawing_spec = self.mp_face.drawing_styles.mp_drawing_styles.get_default_face_mesh_iris_connections_style() )


                if self.config[ 'dibujar_label_gesto_cara' ] == True :

                    x_label = self.config[ 'x_label_gesto_cara' ]
                    y_label = self.config[ 'y_label_gesto_cara' ]

                    ( text_width, text_height ), _ = cv2.getTextSize( gesto_detectado_cara,
                                                                      cv2.FONT_HERSHEY_SIMPLEX,
                                                                      fontScale = 1.2, 
                                                                      thickness = 2 )

                    cv2.rectangle( frame, ( x_label - 5, y_label + 9 ),
                                   ( x_label + text_width + 3, 
                                     y_label - text_height - 6 ),
                                   ( 191, 226, 171 ), thickness = cv2.FILLED )
                                    
                    cv2.putText( frame, gesto_detectado_cara, ( x_label, y_label ), 
                                 cv2.FONT_HERSHEY_SIMPLEX, fontScale = 1.2, color = ( 108, 28, 28 ), 
                                 thickness = 2, lineType = cv2.LINE_AA ) 

        elif self.config[ 'modoController' ] == 'FaceDetection' :

            # To improve performance, optionally mark the image as not writeable to pass by reference.
            frame.flags.writeable = False
            results_face_detection = self.face_detection.process( frame )

            # Draw the hand annotations on the image.
            frame.flags.writeable = True

            if results_face_detection.detections :
                for detection in results_face_detection.detections :
                    self.mp_drawing.draw_detection( frame, detection )
                    # if detection[ 'score' ] < 0.9 :
                    print( detection )




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


    def escribirCSV_face( self, gesto, cara ) :

        cara_para_csv = {}

        cara_para_csv[ 'gesto' ] = gesto

        for i in range( 468 ) :
            cara_para_csv[ 'x' + str( i ) ] = cara[ i ][ 0 ]
            cara_para_csv[ 'y' + str( i ) ] = cara[ i ][ 1 ]
            cara_para_csv[ 'z' + str( i ) ] = cara[ i ][ 2 ]

        self.writer.writerow( cara_para_csv )



    def transformar_cara( self, cara ) :
        cara_trasladada = T.traslacion_cara( cara )
        cara_trasladada_rotada = T.rotacion_alinear_al_eje_y_cara( cara_trasladada )
        cara_alineada = T.rotacion_cara( cara_trasladada_rotada )

        narizAlFrente = cara_alineada
        if T.isNarizAlFrente( cara_alineada ) == False :
            narizAlFrente = T.rotacion_sobre_ejeY_cara( cara_alineada, 180 )

        escalada = T.escalado_cara( narizAlFrente, 100 )

        return escalada
