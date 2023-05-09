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

class Hand( QObject ) :

    signal_procesado = Signal()
    signal_abrirTecladoVirtual = Signal()
    signal_cerrarAplicacion = Signal()
    signal_maximizarAplicacion = Signal()
    signal_activarDesactivarProcesamiento = Signal()
    signal_cambiarDeManoDerechaIzquierda = Signal()
    signal_intercambiarControlDibujar = Signal()

    signal_thumb = Signal()

    def __init__( self ) :
        super( Hand, self ).__init__()

        self.camara = 0

        # Creo una imagen negra de 10 x 10 y la interpretaré como una imagen vacía. Es para chequear cuando inicia el programa
        self.frameProcesado = np.zeros( ( 10, 10, 3 ),'uint8' )
        
        # Para tener información de si el clic izquierdo está pulsado. Se usa en el modo dibujar.
        self.mouseDownLeft = False
        # Para tener información de si el clic derecho está pulsado
        self.mouseDownRight = False         

        self.configurar()  # Deja disponible self.config con todos los datos del json
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
      

        # factor de las ecuaciones paramétricas
        # Esto indica que en cada frame que la cámara entrega al slot_procesar, el mouse se acercará
        # a la punta del dedo en un porcentaje de _lambda entre la distancia de los mismos
        # self._lambda = self.config[ '_lambda' ]
        
        # Esto son los factores para agregar márgenes en la imagen de la cámara (leer más en slot_procesar)
        # a_x indica desde qué porcentaje de la imagen de la camara comienza a detectar el dedo
        self.a_x = self.config[ 'a_x' ] 
        self.b_x = self.config[ 'b_x' ] # b_x indica hasta dónde se detectará en x
        self.a_y = self.config[ 'a_y' ]
        self.b_y = self.config[ 'b_y' ]

        # Mantiene el valor de y en donde se realizó el gesto para scroll (generalmente el puño) y a partir
        # de ahí se realiza el scroll. Cuando el puño se libera, se vuelve al valor -1
        self.scroll_y = -1
        self.scroll_agarrado = False

        # Mantiene el valor de x en donde se realizó el gesto para las flechas (generalmente el puño) y éso se
        # toma como referencia. Cuando el puño se libera, se vuelve al valor -1
        self.flechas_x = -1
        self.flechas_agarrado = False

        # Ventana de frames. Aquí definiremos un vector con una cantidad self.ventana_frames de casilleros para
        # un vector que tiene los distintos z_8. Si la varianza dentro de este vector superar un umbral
        # self.umbral_ventana_z8 entendemos que el usuario quiere hacer clic.
        # Definimos el umbral self.umbral_para_mouse_fijo para que, en caso de ser superado, el mouse no se mueva,
        # ya que con esto suponemos que quiere hacer clic sin que se mueva el mouse.
        # El tiempo self.ventana_clic es para que no se den hagan muchos clics cuando estamos detectando los clic
        # al superar el umbral self.umbral_ventana_z8
        self.ventana_frames = self.config[ 'ventana_frames' ]
        self.vector_frames = np.zeros( self.ventana_frames, dtype = np.float32 ) 
        self.ventana_z_promedio = self.config[ 'ventana_z_promedio' ]
        self.vector_z_promedio = np.zeros( self.ventana_z_promedio, dtype = np.float32 ) 
        self.umbral_para_mouse_fijo = self.config[ 'umbral_para_mouse_fijo' ]
        self.isListo_para_clic = True
        self.timer_clic = QTimer()        
        self.isListo_para_accionar = True
        self.timer_nuevo_gesto = QTimer()

        # Este timer está para que no se envíen instrucciones de scroll en cada frame, sino que deje pasar
        # un pequeño tiempo. 
        self.timer_nuevo_scroll = QTimer()
        self.timer_nuevo_scroll.setInterval( self.config[ 'tiempo_para_timer_scroll' ] )
        self.isListo_para_scroll = True


        # Este timer está para que no se envíen instrucciones de flechas en cada frame, sino que deje pasar
        # un pequeño tiempo. 
        self.timer_nuevo_flechas = QTimer()
        self.timer_nuevo_flechas.setInterval( self.config[ 'tiempo_para_timer_flechas' ] )
        self.isListo_para_flechas = True


        # Aquí es donde se intenta hacer clic. Luego de desplazar el mouse con la mano abierta y se hace el gesto
        # de índice para hacer clic, puede suceder que haya habido un desplazamiento involuntario. Bueno, en ese
        # momento se almacena para que con otro gesto (la L en este caso) se pueda corregir este
        # desplazamiento en el método controlarDesplazamientoMouseCercano.
        # Aquí almacenamos ( x, y ) del mouse donde intenta hacer clic, seguido del ( x, y ) de donde intenta 
        # hacer clic pero dentro del ámbito de la imagen de la cámara.
        self.dondeIntentaClic = np.zeros( 4, dtype = np.int16 ) 
        self.dondeIntentaClic.fill( -1 )


        # Aquí almacenamos ( x, y ) en donde cerró el puño. A partir de aquí definiremos un umbral de distancia
        # para detectar hacia dónde se desplaza, si hacia los laterales o verticalmente, esto es para activar
        # el control del scroll o de las flechas izquierda o derecha para pasar diapositivas por ejemplo.
        # Se almacena el ( x, y ) donde cierra el puño, seguido del ( x, y ) donde cierra el puño
        # pero dentro del ámbito de la imagen de la cámara.
        self.dondeCierraPuno = np.zeros( 4, dtype = np.int16 ) 
        self.dondeCierraPuno.fill( -1 )



        # Este es un vector de los últimos 5 gestos distintos que sucedieron. Esto es para detectar algunas
        # combinaciones que se puedan llegar a configurar para realizar alguna acción
        self.vector_secuencia_gestos = np.zeros( 5, dtype = np.int8 ) 
        self.vector_secuencia_gestos.fill( -1 )

        # Es la ventana para los gestos detectados, para que indentifique según la moda
        self.vector_ventana_gestos = np.zeros( self.config[ 'ventana_de_gestos' ], dtype = np.float32 ) 

        QObject.connect( self.timer_clic, SIGNAL( "timeout()" ), self.slot_soltar_clic )
        QObject.connect( self.timer_nuevo_gesto, SIGNAL( "timeout()" ), self.slot_habilitar_acciones )
        QObject.connect( self.timer_nuevo_scroll, SIGNAL( "timeout()" ), self.slot_habilitar_scroll )
        QObject.connect( self.timer_nuevo_flechas, SIGNAL( "timeout()" ), self.slot_habilitar_flechas )

        


        # Esto se usa para todos los modoController
        ###################################################
        self.mp_drawing = mp.solutions.drawing_utils 
            
        self.mp_hands = mp.solutions.hands

        # Initialize MediaPipe Hands.
        self.hands = self.mp_hands.Hands( min_detection_confidence = self.config[ 'min_detection_confidence' ], 
                                          min_tracking_confidence = self.config[ 'min_tracking_confidence' ],
                                          static_image_mode = self.config[ 'static_image_mode' ],  
                                          max_num_hands = self.config[ 'max_num_hands' ] )


        # Carga del modelo creado para las manos
        json_file = open( self.config[ 'model_json' ], 'r' )
        loaded_model_json = json_file.read()
        json_file.close()
        self.loaded_model = model_from_json( loaded_model_json ) 
        self.loaded_model.load_weights( self.config[ 'model_h5' ] )

        # Estas líneas siguientes está únicamente para que se use por primera vez el método predict ya que
        # hace que se congele por unos segundos la aplicación. Mejor que este congelamiento se haga antes
        # de mostrar la cámara
        mano = np.zeros( ( 0, 3 ), dtype = float )
        for i in range( 0, 21 ) :                      
            mano = np.append( mano, [ [ 0, 0, 0 ] ], axis = 0 )
        tensor = T.crearTensor( mano ) 
        predicciones = self.loaded_model.predict( tensor )


        # estado = 0  ->  Configuración a partir del json
        # estado = 1  ->  Sólo pulgar
        self.estado = 0



        # Lo siguiente es para crear el dataset en CSV
        # Primero abrimos el archivo y escribimos la cabecera en el constructor de Visor
        # Luego registramos rows en slot_procesar
        # Y por último cerramos el archivo en detener() 

        if self.config[ 'capturar_csv_hand' ] == True :

            archivo_csv_existe = False
            if os.path.exists( self.config[ 'archivo_csv' ] ) :
                archivo_csv_existe = True

            self.csv_file = open( self.config[ 'archivo_csv' ], mode = 'at', newline = '' )
            fieldnames = [ 'gesto', 
                           'x0', 'y0', 'z0', 'x1', 'y1', 'z1', 'x2', 'y2', 'z2', 'x3', 'y3', 'z3', 
                           'x4', 'y4', 'z4', 'x5', 'y5', 'z5', 'x6', 'y6', 'z6', 'x7', 'y7', 'z7', 
                           'x8', 'y8', 'z8', 'x9', 'y9', 'z9', 'x10', 'y10', 'z10', 'x11', 'y11', 'z11', 
                           'x12', 'y12', 'z12', 'x13', 'y13', 'z13', 'x14', 'y14', 'z14', 'x15', 'y15', 'z15', 
                           'x16', 'y16', 'z16', 'x17', 'y17', 'z17', 'x18', 'y18', 'z18', 'x19', 'y19', 'z19', 
                           'x20', 'y20', 'z20' ]

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

    # Cuando se invoca este método se setea un intervalo de 100 ms para el timer que toma las imágenes
    # y comienza a registrar una cantidad de 'cuantos' manos (por defecto 50) en el archivo CSV
    # que está hardcodeado en el contructor de Visor.
    # Para comenzar a capturar se pone en True el isCapturando
    def capturarParaCSV( self, cuantos ) :
        self.cuantasCapturas = cuantos
        self.contadorCapturas = 0
        self.cuantasRepeticionesDeCapturasVan = self.cuantasRepeticionesDeCapturasVan + 1
        self.isCapturando = True
        self.timer.start( self.config[ 'tiempo_para_timer_csv' ] )


    @Slot()
    def slot_soltar_clic( self ) :        
        self.timer_clic.stop()
        self.isListo_para_clic = True     

    @Slot()
    def slot_habilitar_acciones( self ) :        
        self.timer_nuevo_gesto.stop()
        self.isListo_para_accionar = True     

    @Slot()
    def slot_habilitar_scroll( self ) :        
        self.timer_nuevo_scroll.stop()
        self.isListo_para_scroll = True     

    @Slot()
    def slot_habilitar_flechas( self ) :        
        self.timer_nuevo_flechas.stop()
        self.isListo_para_flechas = True             

    # Este método activa el procesamiento si está desactivado y lo desactiva si está activo
    def activarDesactivarProcesamiento( self ) :
        if self.config[ 'deshabilitar_todas_las_interacciones' ] == True :
            self.config[ 'deshabilitar_todas_las_interacciones' ] = False
        else :
            self.config[ 'deshabilitar_todas_las_interacciones' ] = True


    # Cambia la posición del recuadro verde para adaptarse a la mano izquierda o a la derecha
    # Tiene una secuencia de gestos para cambiarlo desde la NUI
    def cambiarDeManoDerechaIzquierda( self ) :
        self.a_x = 1 - self.b_x
        self.b_x = 1 - self.a_x

    def intercambiarControlDibujar( self ) :
        if self.config[ 'control_o_dibujar' ] == True :
            self.config[ 'control_o_dibujar' ] = False
        else :
            self.config[ 'control_o_dibujar' ] = True

    def recibirCamara( self, camara ) :
        self.camara = camara
        
    @Slot()
    def slot_procesar( self ) :

        if self.camara.hayFrame() == False :
            return

        frame = self.camara.frame

        h, w, ch = frame.shape
        bytesPerLine = ch * w


        # Para calcular el tiempo de procesamiento. 
        fps = 0
        if self.tiempo_procesamiento_start_time > 0 :
            elapsed_time = time() - self.tiempo_procesamiento_start_time
            T.inserta_y_desplaza( self.tiempos_procesamiento, [ elapsed_time ] )
            fps = round( 1 / np.mean( self.tiempos_procesamiento ) )
            # print( 'elapsed_time ', elapsed_time , ' fps=', fps )
        self.tiempo_procesamiento_start_time = time()
        
                

        # To improve performance, optionally mark the image as not writeable to pass by reference.
        frame.flags.writeable = False

        # e1 = cv2.getTickCount()     
        results = self.hands.process( frame )
        # e2 = cv2.getTickCount() ; segundos = (e2 - e1)/ cv2.getTickFrequency() ; print( segundos )

        # Draw the hand annotations on the image.
        frame.flags.writeable = True

        # Dibuja el rectángulo en donde está el rango de control con la punta del dedo índice
        if self.config[ 'mostrar_margenes' ] == True :
            cv2.rectangle( frame, ( int( self.config[ 'a_x' ] * w ), int( self.config[ 'a_y' ] * h ) ), 
                                  ( int( self.config[ 'b_x' ] * w ), int( self.config[ 'b_y' ] * h ) ), ( 0, 255, 0 ), 1 )

        if self.config[ 'control_o_dibujar' ] == False :
            if self.config[ 'mostrar_texto_drag_and_drop_etc' ] == True :
                cv2.putText( frame, 'Drag and Drop', ( 450, 30 ), 
                             cv2.FONT_HERSHEY_SIMPLEX, 0.75, ( 0, 0, 255 ), 2, cv2.LINE_AA ) 

        if self.config[ 'mostrar_fps' ] == True :
            cv2.putText( frame, 'fps=' + str( fps ), ( 20, 90 ), 
                                 cv2.FONT_HERSHEY_SIMPLEX, 1, ( 0, 0, 255 ), 2, cv2.LINE_AA ) 

        if self.config[ 'contador_de_frames' ] == True :
            cv2.putText( frame, 'frame nro. = ' + str( self.contador_de_frames ), ( 0, 350 ), 
                                 cv2.FONT_HERSHEY_SIMPLEX, 1, ( 0, 0, 255 ), 2, cv2.LINE_AA ) 
            self.contador_de_frames += 1

        if results.multi_hand_landmarks :

            for hand_landmarks in results.multi_hand_landmarks :

                mano = np.zeros( ( 0, 3 ), dtype = float )

                for i in range( 0, 21 ) :

                    # Notar aquí que hacemos una escalado según el ancho y alto de la imagen, y como la 
                    # documentación de mediapipe dice que z tiene una escala similar a x, entonces
                    # por eso multiplicamos z por w
                    mano = np.append( mano, [ [ float( hand_landmarks.landmark[ i ].x ) * float( w ),
                                                float( hand_landmarks.landmark[ i ].y ) * float( h ),
                                                float( hand_landmarks.landmark[ i ].z ) * float( w ) ] ], 
                                                axis = 0 )

                if self.config[ 'normalizar' ] == True :
                    # Realiza todas las transformaciones
                    escalada = self.transformar( mano )
                else :
                    escalada = mano

                # Esto es para medir la longitud de la mano
                # x_0 = float( hand_landmarks.landmark[ 0 ].x ) * float( w )
                # y_0 = float( hand_landmarks.landmark[ 0 ].y ) * float( h )
                # x_12 = float( hand_landmarks.landmark[ 12 ].x ) * float( w )                    
                # y_12 = float( hand_landmarks.landmark[ 12 ].y ) * float( h )
                # distancia = math.sqrt( pow( x_0 - x_12, 2 ) + pow( y_0 - y_12, 2 ) )
                # print( 'distancia kp 0-12 =', distancia )

                # Esto es para medir el desplazamiento en z del indice
                # x_12 = float( hand_landmarks.landmark[ 12 ].x ) * float( w )                    
                # y_12 = float( hand_landmarks.landmark[ 12 ].y ) * float( h )
                # z_12 = float( hand_landmarks.landmark[ 12 ].z ) * float( w )
                # print( int( z_12 ) )

                if self.config[ 'capturar_csv_hand' ] == True :

                    self.escribirCSV( self.config[ 'nombre_gesto' ], escalada )
                    print( escalada, ' - ', self.config[ 'nombre_gesto' ] )


                tensor = T.crearTensor( escalada )

                # Este línea lee el config.json y extrae algo así:
                # CLASS_MAP = { 0: 'abierta', 1: 'puno', 2: 'pulgar', 3: 'ok', 
                #               4: 'indice', 5: 'v', 6: 'cuerno' }
                CLASS_MAP = dict( zip( ( int( i ) for i in self.config[ 'gestos' ][ 0 ].keys() ), 
                                       self.config[ 'gestos' ][ 0 ].values() ) )

                # Con esto podemos medir el tiempo que lleva ejecutar la siguiente función
                # e1 = cv2.getTickCount()            

                predicciones = self.loaded_model.predict( tensor )

                # Medimos e imprimimos
                # e2 = cv2.getTickCount() ; segundos = (e2 - e1)/ cv2.getTickFrequency() ; print( segundos )

                predicciones = tf.math.argmax( predicciones, -1 )

                gesto_detectado = CLASS_MAP[ predicciones[ 0 ].numpy() ]
                label_gesto_detectado = list( CLASS_MAP.values() ).index( gesto_detectado )


                if self.config[ 'ventana_de_gestos_habilitada' ] == True :
                    T.inserta_y_desplaza( self.vector_ventana_gestos, [ label_gesto_detectado ] ) 
                    label_gesto_detectado = int( stat.mode( self.vector_ventana_gestos ) )
                    gesto_detectado = CLASS_MAP.get( label_gesto_detectado )
                else :
                    self.signal_gestoDetectado.emit( label_gesto_detectado )  # Emite sin usar ventana



                if self.config[ 'deshabilitar_secuencias_de_gestos' ] == False :

                    ###### Detector de secuencias de gestos
                    if self.config[ 'control_cierre_app' ] == True \
                       and self.detectar_secuencia_de_gestos( self.config[ 'control_cierre_secuencia' ] ) == True :
                        print( 'control_cierre_app')
                        self.signal_cerrarAplicacion.emit()

                    if self.config[ 'control_max_app' ] == True \
                       and self.detectar_secuencia_de_gestos( self.config[ 'control_max_secuencia' ] ) == True :
                        self.signal_maximizarAplicacion.emit()
                        print( 'signal_maximizarAplicacion.emit()' )

                    if self.config[ 'control_teclado_virtual' ] == True \
                       and self.detectar_secuencia_de_gestos( self.config[ 'control_teclado_secuencia' ] ) == True :
                        print( 'control_teclado_virtual')
                        self.signal_abrirTecladoVirtual.emit()

                    if self.config[ 'control_activar_procesamiento' ] == True \
                       and self.detectar_secuencia_de_gestos( self.config[ 'control_activar_secuencia' ] ) == True :
                        self.signal_activarDesactivarProcesamiento.emit()            

                    if self.config[ 'control_mano_der_izq' ] == True \
                       and self.detectar_secuencia_de_gestos( self.config[ 'control_mano_der_izq_secuencia' ] ) == True :
                        self.signal_cambiarDeManoDerechaIzquierda.emit()    

                    if self.detectar_secuencia_de_gestos( self.config[ 'control_o_dibujar_secuencia' ] ) == True :
                        self.signal_intercambiarControlDibujar.emit()    
                            
                    # Aquí se almacena el último gesto detectado y que sea distinto al anterior.
                    # Esto es para realizar algún análisis según la secuencia de gestos
                    # Tener en cuenta que si está habilitado 'ventana_de_gestos_habilitada' entonces
                    # se almacenará segun la moda en la ventana de gestos definida
                    # Cuando entra a este if es porque hay un gesto nuevo, y para que el cambio de gesto no
                    # provoque alguna acción que no deseamos (por ejemplo, un clic o un scroll), es el motivo
                    # por el cual desactivamos temporalmente las acciones (usando isListo_para_accionar)
                    if self.getUltimoGesto() != label_gesto_detectado :
                        T.inserta_y_desplaza( self.vector_secuencia_gestos, [ label_gesto_detectado ] ) 

                        self.timer_nuevo_gesto.start( self.config[ 'tiempo_para_accionar' ] )
                        self.isListo_para_accionar = False

                    ###### FIN - Detector de secuencias de gestos



                if self.config[ 'dibujar_esqueleto' ] == True :
                    self.mp_drawing.draw_landmarks( frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS )   


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

                
                # Si estado es 0, se controla con todo lo que veníamos trabajando con HandController
                if self.estado == 0 :

                    # Estas es cuando está habilitado el modo 'control' que controla el mouse, scroll, teclado
                    if self.config[ 'control_o_dibujar' ] == True :
                        if self.isListo_para_accionar == True and self.config[ 'deshabilitar_todas_las_interacciones' ] == False :
                            
                            self.controlarDesplazamientoMouse( label_gesto_detectado, hand_landmarks, frame )

                            if self.config[ 'clic_con_L1_en_lugar_de_z' ] == True :
                                self.controlarDesplazamientoMouseCercano_para_clic_con_L1( label_gesto_detectado, hand_landmarks, frame )

                                # Este método devuelve 'scroll' o 'izq_der' o 'ninguno' y además el punto incial donde se cerró en puño
                                ( is_scroll_o_izq_der, punto_inicial ) = self.detectarCierrePuno( label_gesto_detectado, hand_landmarks, frame )
                                
                                if is_scroll_o_izq_der == 'scroll' :
                                    self.controlarScroll( label_gesto_detectado, hand_landmarks, frame, punto_inicial )
                                elif is_scroll_o_izq_der == 'izq_der' :
                                    self.controlarFlecha_izq_der( label_gesto_detectado, hand_landmarks, frame, punto_inicial )

                                self.detectarClicIzquierdo_con_L1( label_gesto_detectado, hand_landmarks, frame )

                            if self.config[ 'clic_con_L1_en_lugar_de_z' ] == False :  # Aqui para cuando el cli izquierdo se hace acercando el indice

                                self.controlarDesplazamientoMouseCercano( label_gesto_detectado, hand_landmarks, frame )

                                # Este método devuelve 'scroll' o 'izq_der' o 'ninguno' y además el punto incial donde se cerró en puño
                                ( is_scroll_o_izq_der, punto_inicial ) = self.detectarCierrePuno( label_gesto_detectado, hand_landmarks, frame )
                                
                                if is_scroll_o_izq_der == 'scroll' :
                                    self.controlarScroll( label_gesto_detectado, hand_landmarks, frame, punto_inicial )
                                elif is_scroll_o_izq_der == 'izq_der' :
                                    self.controlarFlecha_izq_der( label_gesto_detectado, hand_landmarks, frame, punto_inicial )

                                self.detectarClicIzquierdo( label_gesto_detectado, hand_landmarks, frame )


                            self.detectarClicDerecho( label_gesto_detectado, hand_landmarks, frame )

                        else :

                            # Este else es sólo para resetear el dondeIntentaClic 
                            self.dondeIntentaClic.fill( -1 )

                            # Este else es sólo para resetear el dondeCierraPuno 
                            self.dondeCierraPuno.fill( -1 )
                       

                    else :  # Aquí es para cuando necesitemos dibujar con aplicación similar al Paint
                        if self.isListo_para_accionar == True and self.config[ 'deshabilitar_todas_las_interacciones' ] == False :

                            self.controlarDesplazamientoMouse( label_gesto_detectado, hand_landmarks, frame )

                            if self.config[ 'clic_con_L1_en_lugar_de_z' ] == True :
                                self.controlarDesplazamientoMouseCercano_para_clic_con_L1( label_gesto_detectado, hand_landmarks, frame )
                                self.detectarClicIzquierdo_con_L1( label_gesto_detectado, hand_landmarks, frame )
                            else :
                                self.controlarDesplazamientoMouseCercano( label_gesto_detectado, hand_landmarks, frame )
                                self.detectarClicIzquierdo( label_gesto_detectado, hand_landmarks, frame )
                            
                            self.detectarClicDerecho( label_gesto_detectado, hand_landmarks, frame )

                            self.dragAndDrop( label_gesto_detectado, hand_landmarks, frame )  

                            if self.mouseDownLeft == True :            
                                self.controlarDesplazamientoMouseConPuno( label_gesto_detectado, hand_landmarks, frame )
                            else : 
                                self.controlarDesplazamientoMouse( label_gesto_detectado, hand_landmarks, frame )

                        else :
                            
                            # Este else es sólo para resetear el dondeIntentaClic 
                            self.dondeIntentaClic.fill( -1 )

                            # Este else es sólo para resetear el dondeCierraPuno 
                            self.dondeCierraPuno.fill( -1 )


                elif self.estado == 1 :  # Sólo detecta pulgar
                    self.controlarDesplazamientoMouse( label_gesto_detectado, hand_landmarks, frame )
                    if gesto_detectado == 'Thumb' :
                        self.signal_thumb.emit()
                        self.resetear_metricas()

                elif self.estado == 2 :  # Sólo deplazamiento de mouse
                    self.controlarDesplazamientoMouse( label_gesto_detectado, hand_landmarks, frame )


        self.frameProcesado = frame
        self.signal_procesado.emit()


    # Este método lo usamos para setear las funcionalidades que quedan activas. Por ejemplo, sólo detección del pulgar,
    # sólo detección de secuencia de gestos
    def setEstado( self, estado ) :
        self.estado = estado
        

    def detener( self ) : 

        self.camara.apagar()

        if self.config[ 'capturar_csv_hand' ] == True :
            self.csv_file.close()
            
        if self.camara.isEncendida() == False :
            print( 'Cámara apagada' )


    def escribirCSV( self, gesto, mano ) :

        self.writer.writerow( { 'gesto': gesto, 
                                'x0': mano[ 0 ][ 0 ], 'y0': mano[ 0 ][ 1 ], 'z0': mano[ 0 ][ 2 ], 
                                'x1': mano[ 1 ][ 0 ], 'y1': mano[ 1 ][ 1 ], 'z1': mano[ 1 ][ 2 ], 
                                'x2': mano[ 2 ][ 0 ], 'y2': mano[ 2 ][ 1 ], 'z2': mano[ 2 ][ 2 ], 
                                'x3': mano[ 3 ][ 0 ], 'y3': mano[ 3 ][ 1 ], 'z3': mano[ 3 ][ 2 ], 
                                'x4': mano[ 4 ][ 0 ], 'y4': mano[ 4 ][ 1 ], 'z4': mano[ 4 ][ 2 ], 
                                'x5': mano[ 5 ][ 0 ], 'y5': mano[ 5 ][ 1 ], 'z5': mano[ 5 ][ 2 ], 
                                'x6': mano[ 6 ][ 0 ], 'y6': mano[ 6 ][ 1 ], 'z6': mano[ 6 ][ 2 ], 
                                'x7': mano[ 7 ][ 0 ], 'y7': mano[ 7 ][ 1 ], 'z7': mano[ 7 ][ 2 ], 
                                'x8': mano[ 8 ][ 0 ], 'y8': mano[ 8 ][ 1 ], 'z8': mano[ 8 ][ 2 ], 
                                'x9': mano[ 9 ][ 0 ], 'y9': mano[ 9 ][ 1 ], 'z9': mano[ 9 ][ 2 ], 
                                'x10': mano[ 10 ][ 0 ], 'y10': mano[ 10 ][ 1 ], 'z10': mano[ 10 ][ 2 ], 
                                'x11': mano[ 11 ][ 0 ], 'y11': mano[ 11 ][ 1 ], 'z11': mano[ 11 ][ 2 ], 
                                'x12': mano[ 12 ][ 0 ], 'y12': mano[ 12 ][ 1 ], 'z12': mano[ 12 ][ 2 ], 
                                'x13': mano[ 13 ][ 0 ], 'y13': mano[ 13 ][ 1 ], 'z13': mano[ 13 ][ 2 ], 
                                'x14': mano[ 14 ][ 0 ], 'y14': mano[ 14 ][ 1 ], 'z14': mano[ 14 ][ 2 ], 
                                'x15': mano[ 15 ][ 0 ], 'y15': mano[ 15 ][ 1 ], 'z15': mano[ 15 ][ 2 ], 
                                'x16': mano[ 16 ][ 0 ], 'y16': mano[ 16 ][ 1 ], 'z16': mano[ 16 ][ 2 ], 
                                'x17': mano[ 17 ][ 0 ], 'y17': mano[ 17 ][ 1 ], 'z17': mano[ 17 ][ 2 ], 
                                'x18': mano[ 18 ][ 0 ], 'y18': mano[ 18 ][ 1 ], 'z18': mano[ 18 ][ 2 ], 
                                'x19': mano[ 19 ][ 0 ], 'y19': mano[ 19 ][ 1 ], 'z19': mano[ 19 ][ 2 ], 
                                'x20': mano[ 20 ][ 0 ], 'y20': mano[ 20 ][ 1 ], 'z20': mano[ 20 ][ 2 ] } )


    # Este metodo detecta donde se cierra en puño y almacena estos valores en self.dondeCierraPuno
    # Además calcula se si está desplazando más en vertical o en horizontal, y finalmente devuelve 
    # una cadena para indicarlo "izq_der" o "scroll".
    # También devuelve el punto x,y inicial en donde se cerró el puño
    def detectarCierrePuno( self, label_gesto_detectado, hand_landmarks, frame ) :

        if label_gesto_detectado == self.config[ 'id_puno' ] :

            x_kp = hand_landmarks.landmark[ self.config[ 'keypoint_representativo_puno' ] ].x 
            y_kp = hand_landmarks.landmark[ self.config[ 'keypoint_representativo_puno' ] ].y

            # Esta es la ubicación del keypoint dentro e la imagen de la cámara (640x480)
            pos_kp_640x480 = QPoint( x_kp, y_kp ) 

            # Esta es la posición real (en la imagen de la cámara sin ajustar al recuadro verde) 
            pos_kp_screen = QPoint( x_kp * self.screen_w, y_kp * self.screen_h ) 

            if self.dondeCierraPuno[ 0 ] == -1 and \
               self.dondeCierraPuno[ 1 ] == -1 and \
               self.dondeCierraPuno[ 2 ] == -1 and \
               self.dondeCierraPuno[ 3 ] == -1 :

                self.dondeCierraPuno[ 0 ] = pos_kp_640x480.x()
                self.dondeCierraPuno[ 1 ] = pos_kp_640x480.y()

                self.dondeCierraPuno[ 2 ] = pos_kp_screen.x()
                self.dondeCierraPuno[ 3 ] = pos_kp_screen.y()

            # Dibujamos para saber dónde está
            h, w, ch = frame.shape

            punto_inicial = QPoint( int( self.dondeCierraPuno[ 2 ] * w / self.screen_w ),
                                    int( self.dondeCierraPuno[ 3 ] * h / self.screen_h ) )

            cv2.circle( frame, ( punto_inicial.x(), punto_inicial.y() ), 
                                 10, ( 0, 0, 0 ), thickness = cv2.FILLED )

            punto_actual = QPoint( int( pos_kp_screen.x() * w / self.screen_w ),
                                   int( pos_kp_screen.y() * h / self.screen_h ) )

            cv2.circle( frame, ( punto_actual.x(), punto_actual.y() ), 
                                 7, ( 255, 255, 255 ), thickness = cv2.FILLED )

            diferencia_x = abs( punto_actual.x() - punto_inicial.x() )
            diferencia_y = abs( punto_actual.y() - punto_inicial.y() )


            if ( diferencia_x - diferencia_y ) > self.config[ 'margen_inactividad_scroll_izq_der' ] :
                # print( 'izq_der', diferencia_x, diferencia_y )
                return ( str( "izq_der" ), punto_inicial )
            elif ( diferencia_x - diferencia_y ) < - self.config[ 'margen_inactividad_scroll_izq_der' ] :
                # print( 'scroll', diferencia_x, diferencia_y )
                return ( str( "scroll" ), punto_inicial )
        return ( str( "ninguno" ), QPoint( -1, -1 ) )


    
    def dragAndDrop( self, label_gesto_detectado, hand_landmarks, frame ) :

        if label_gesto_detectado == self.config[ 'id_puno' ] :
            if self.mouseDownLeft == False :
                print( 'left pulsado' )
                mouse.press( button = 'left', coords = ( int( QCursor.pos().x() * self.escala_dpi ), int( QCursor.pos().y() * self.escala_dpi ) ) )
                self.mouseDownLeft = True
        else : 
            if self.mouseDownLeft == True :
                mouse.release( button = 'left', coords = ( int( QCursor.pos().x() * self.escala_dpi ), int( QCursor.pos().y() * self.escala_dpi ) ) )
                self.mouseDownLeft = False
            

    def detectarClicIzquierdo( self, label_gesto_detectado, hand_landmarks, frame ) :

        if label_gesto_detectado == self.config[ 'clic_gesto' ] \
           and self.config[ 'clic' ] == True :

            # Haremos lo siguiente: Dentro de vector_frames se almacenan un cantidad 
            # ventana_frames de valores del keypoint clic_keypoint_z. Definimos 
            # un umbral_desviacion para que cuando la desviación de los datos 
            # almacenados en vector_frames supere este umbral, entonces se haga clic. 
            # Pero esto no considerar que cuando uno hace el gesto de presionar con el
            # índice, uno presiona y suelta. Pero lo anterior sólo detecta cuando se presiona.
            # Entonces lo que haremos será, cuando se supere el umbral, se calculará cuál 
            # fue el z más alejado de la pantalla (sería el menos negativo), esto para 
            # detectar desde dónde comenzó a hacer el gesto del clic. Con esto 
            # almacenado, el clic se hará efectivo cuando el z vuelva a la posición 
            # desde donde comenzó el gesto. Definiremos un nuevo umbral
            # umbral_retorno_z para hacer de cuenta que ya llegó al z inicial cuando esté dentro 
            # de este umbral.
            # Lo próximo que debemos hacer es defininir estos umbrales de forma variable, porque
            # dependiendo la distancia a la que esté la mano, es la magnitud de los valores de z.

            # Este es el valor z del kp que se usa para hacer clic. Generalmente la punta del índice
            clic_keypoint_z = hand_landmarks.landmark[ self.config[ 'clic_keypoint_z' ] ].z

            clic_keypoint_x = hand_landmarks.landmark[ self.config[ 'clic_keypoint_z' ] ].x
            clic_keypoint_y = hand_landmarks.landmark[ self.config[ 'clic_keypoint_z' ] ].y

            h, w, ch = frame.shape

            # Aquí dibujamos la punta del dedo para saber que con eso se debe hacer clic
            cv2.circle( frame, ( int( clic_keypoint_x * w ), int( clic_keypoint_y * h ) ), 
                        9, ( 20, 20, 255 ), thickness = cv2.FILLED )
            
            T.inserta_y_desplaza( self.vector_frames, [ int( clic_keypoint_z * w ) ] )

            # Aquí analizamos esta ventana de valores para detectar lo que dijimos en el 
            # comentario anterior.
            is_clic = self.analizar_si_hay_clic()

            if is_clic == True and self.isListo_para_clic == True :

                pyautogui.click()
                # mouse.click( button = 'left', 
                #              coords = ( int( QCursor.pos().x() * self.escala_dpi ), int( QCursor.pos().y() * self.escala_dpi ) ) )

                # mouse.press( button = 'left', 
                #              coords = ( int( QCursor.pos().x() * self.escala_dpi ), int( QCursor.pos().y() * self.escala_dpi ) ) )

                print( 'click()' )
                

                self.timer_clic.start( self.config[ 'ventana_clic' ] )
                self.isListo_para_clic = False

    # Esta funicon es para detectar el clic con el cambio desde la L hacia el 1. Es decir, se controla el mouse con la mano abierta
    # y cuando se quiera hacer clic se pone la mano en L y se acerca al lugar deseado con desplazamiento fino y cuando quiera hacer clic
    # cambia el gesto desde la L hasta el 1. Por eso le llamé detectarClicIzquierdo_con_L1
    # ESta función trabajará analizando el historial de gestos y analizará dentro de 
    def detectarClicIzquierdo_con_L1( self, label_gesto_detectado, hand_landmarks, frame ) :

        if label_gesto_detectado == self.config[ 'clic_gesto' ] \
           and self.config[ 'clic' ] == True and self.getPenultimoGesto() == self.config[ 'clic_cercano_gesto' ] :  # clic_cercano_gesto es el gesto L

            if self.isListo_para_clic == True :

                pyautogui.click()
                # mouse.click( button = 'left', 
                #              coords = ( int( QCursor.pos().x() * self.escala_dpi ), int( QCursor.pos().y() * self.escala_dpi ) ) )

                # mouse.press( button = 'left', 
                #              coords = ( int( QCursor.pos().x() * self.escala_dpi ), int( QCursor.pos().y() * self.escala_dpi ) ) )

                print( 'click()' )
                

                self.timer_clic.start( self.config[ 'ventana_clic_L1' ] )
                self.isListo_para_clic = False

        
    def detectarClicDerecho( self, label_gesto_detectado, hand_landmarks, frame ) :

        # Esto hace lo mismo que el clic izquierdo, pero ahora con el clic derecho
        if label_gesto_detectado == self.config[ 'clic_derecho_gesto' ] \
           and self.config[ 'clic_derecho' ] == True :

            # Este es el valor z del kp que se usa para hacer clic. 
            # Generalmente la punta del índice pero con el gesto V (porque es el clic derecho)
            clic_keypoint_z = hand_landmarks.landmark[ self.config[ 'clic_keypoint_z' ] ].z

            clic_keypoint_x = hand_landmarks.landmark[ self.config[ 'clic_keypoint_z' ] ].x
            clic_keypoint_y = hand_landmarks.landmark[ self.config[ 'clic_keypoint_z' ] ].y

            h, w, ch = frame.shape

            # Aquí dibujamos la punta del dedo para saber que con eso se debe hacer clic
            cv2.circle( frame, ( int( clic_keypoint_x * w ), int( clic_keypoint_y * h ) ), 
                        9, ( 20, 20, 255 ), thickness = cv2.FILLED )
            
            T.inserta_y_desplaza( self.vector_frames, [ int( clic_keypoint_z * w ) ] )

            # Aquí analizamos esta ventana de valores para detectar lo que dijimos en el 
            # comentario anterior.
            is_clic = self.analizar_si_hay_clic()

            if is_clic == True and self.isListo_para_clic == True :

                pyautogui.click( button = 'right' )

                self.timer_clic.start( self.config[ 'ventana_clic' ] )
                self.isListo_para_clic = False


    def controlarDesplazamientoMouse( self, label_gesto_detectado, hand_landmarks, frame ) :
        # Este if es para controlar el desplazamiento del mouse. Requiere configurar config_json
        #   "control_mouse": true,  -> Control habilitado
        #   "control_mouse_gesto": 4,   -> se controla con el gesto que tiene label 4
        #   "control_mouse_keypoint": 8,    -> del gesto con label 4, el mouse sigue el keypoint 8
        if label_gesto_detectado == self.config[ 'control_mouse_gesto' ] and self.config[ 'control_mouse' ] == True :

            x_kp = hand_landmarks.landmark[ self.config[ 'control_mouse_keypoint' ] ].x
            y_kp = hand_landmarks.landmark[ self.config[ 'control_mouse_keypoint' ] ].y
            z_kp = hand_landmarks.landmark[ self.config[ 'control_mouse_keypoint' ] ].z

            # https://math.stackexchange.com/questions/914823/shift-numbers-into-a-different-range/914843
            # Hacemos un cambio de rango: queremos mapear [a,b] en [c,d]
            # En nuestro caso [0.2, 0.8] en [0, 1]
            # Esto para dejar un margen ya que es difícil hacer llegar el dedo al borde de la imagen
            # La fórmula sería:     f(t) = c + [ ( d - c ) / ( b - a ) ] * ( t - a )
            # Mantengamos a y b como variables para poder ajustarlas si hace falta.
            # f(t) = 0 + [ ( 1 - 0 ) / ( b - a ) ] * ( t - a )
            # f(t) = ( t - a ) / ( b - a )
            # Esto lo tenemos que aplicar tanto para x como para y

            x_kp_con_margen = ( x_kp - self.config[ 'a_x' ] ) / ( self.config[ 'b_x' ] - self.config[ 'a_x' ] )
            y_kp_con_margen = ( y_kp - self.config[ 'a_y' ] ) / ( self.config[ 'b_y' ] - self.config[ 'a_y' ] )

            # Por último aplicamos controlamos que no se vaya de pantalla

            if x_kp_con_margen > self.screen_w :
                x_kp_con_margen = self.screen_w
            if x_kp_con_margen < 0 :
                x_kp_con_margen = 0
            if y_kp_con_margen > self.screen_h :
                y_kp_con_margen = self.screen_h
            if y_kp_con_margen < 0 :
                y_kp_con_margen = 0

            # Esta es la posición real detectada de la punta del dedo índice
            pos_kp = QPoint( x_kp_con_margen * self.screen_w, y_kp_con_margen * self.screen_h ) 

            mouseActual = QCursor.pos()

            # Para obtener la Ecuación paramétrica de la recta hacemos
            # x = mouseActual.x() + _lambda ( pos_kp8.x() - mouseActual.x() )
            # y = mouseActual.y() + _lambda ( pos_kp8.y() - mouseActual.y() )

            QCursor.setPos( mouseActual.x() + self.config[ '_lambda' ] * ( pos_kp.x() - mouseActual.x() ),
                            mouseActual.y() + self.config[ '_lambda' ] * ( pos_kp.y() - mouseActual.y() ) )


            # Aquí se activa la ventana_clic para que cuando se termine de desplazar el mouse, no se vaya 
            # a ejectuar el clic inmedietamente, que por lo menos que no se emita en un tiempo ventana_clic
            self.timer_clic.start( self.config[ 'ventana_clic' ] )
            self.isListo_para_clic = False

            # Por último dibujamos el keypoint con el cual se está controlando el desplazamiento del cursor
            h, w, ch = frame.shape
            cv2.circle( frame, ( int( x_kp * w ), int( y_kp * h ) ), 12, ( 255, 20, 20 ), thickness = cv2.FILLED )

    def controlarDesplazamientoMouseConPuno( self, label_gesto_detectado, hand_landmarks, frame ) :
        if ( label_gesto_detectado == self.config[ 'control_mouse_gesto_dibujar_1' ] or \
             label_gesto_detectado == self.config[ 'control_mouse_gesto_dibujar_2' ] ) and \
           self.config[ 'control_mouse' ] == True :

            x_kp = hand_landmarks.landmark[ self.config[ 'control_mouse_keypoint_dibujar' ] ].x
            y_kp = hand_landmarks.landmark[ self.config[ 'control_mouse_keypoint_dibujar' ] ].y
            z_kp = hand_landmarks.landmark[ self.config[ 'control_mouse_keypoint_dibujar' ] ].z

            # https://math.stackexchange.com/questions/914823/shift-numbers-into-a-different-range/914843
            # Hacemos un cambio de rango: queremos mapear [a,b] en [c,d]
            # En nuestro caso [0.2, 0.8] en [0, 1]
            # Esto para dejar un margen ya que es difícil hacer llegar el dedo al borde de la imagen
            # La fórmula sería:     f(t) = c + [ ( d - c ) / ( b - a ) ] * ( t - a )
            # Mantengamos a y b como variables para poder ajustarlas si hace falta.
            # f(t) = 0 + [ ( 1 - 0 ) / ( b - a ) ] * ( t - a )
            # f(t) = ( t - a ) / ( b - a )
            # Esto lo tenemos que aplicar tanto para x como para y

            x_kp_con_margen = ( x_kp - self.config[ 'a_x' ] ) / ( self.config[ 'b_x' ] - self.config[ 'a_x' ] )
            y_kp_con_margen = ( y_kp - self.config[ 'a_y' ] ) / ( self.config[ 'b_y' ] - self.config[ 'a_y' ] )

            # Por último aplicamos controlamos que no se vaya de pantalla

            if x_kp_con_margen > self.screen_w :
                x_kp_con_margen = self.screen_w
            if x_kp_con_margen < 0 :
                x_kp_con_margen = 0
            if y_kp_con_margen > self.screen_h :
                y_kp_con_margen = self.screen_h
            if y_kp_con_margen < 0 :
                y_kp_con_margen = 0

            # Esta es la posición real detectada de la punta del dedo índice
            pos_kp = QPoint( x_kp_con_margen * self.screen_w, y_kp_con_margen * self.screen_h ) 

            mouseActual = QCursor.pos()

            # Para obtener la Ecuación paramétrica de la recta hacemos
            # x = mouseActual.x() + _lambda ( pos_kp8.x() - mouseActual.x() )
            # y = mouseActual.y() + _lambda ( pos_kp8.y() - mouseActual.y() )

            QCursor.setPos( mouseActual.x() + self.config[ '_lambda' ] * ( pos_kp.x() - mouseActual.x() ),
                            mouseActual.y() + self.config[ '_lambda' ] * ( pos_kp.y() - mouseActual.y() ) )


            # Aquí se activa la ventana_clic para que cuando se termine de desplazar el mouse, no se vaya 
            # a ejectuar el clic inmedietamente, que por lo menos que no se emita en un tiempo ventana_clic
            self.timer_clic.start( self.config[ 'ventana_clic' ] )
            self.isListo_para_clic = False

            # Por último dibujamos el keypoint con el cual se está controlando el desplazamiento del cursor
            h, w, ch = frame.shape
            cv2.circle( frame, ( int( x_kp * w ), int( y_kp * h ) ), 12, ( 255, 20, 20 ), thickness = cv2.FILLED )



    # Este método es para controlar un pequeño desplazamiento del mouse con el 'clic_keypoint_z'
    # que es generalmente con la punta del índice, pero en una región pequeña, sólo con el fin de corregir 
    # algún pequeño desplazamiento involuntario
    def controlarDesplazamientoMouseCercano( self, label_gesto_detectado, hand_landmarks, frame ) :
        if ( label_gesto_detectado == self.config[ 'clic_cercano_gesto' ] or \
             label_gesto_detectado == self.config[ 'clic_derecho_cercano_gesto' ] ) and \
           self.config[ 'clic' ] == True :

            x_kp = hand_landmarks.landmark[ self.config[ 'clic_keypoint_z' ] ].x 
            y_kp = hand_landmarks.landmark[ self.config[ 'clic_keypoint_z' ] ].y

            # Esta es la posición real (en la imagen de la cámara sin ajustar al recuadro verde) 
            # detectada de la punta del dedo índice
            pos_kp = QPoint( x_kp * self.screen_w, y_kp * self.screen_h ) 

            if self.dondeIntentaClic[ 0 ] == -1 and \
               self.dondeIntentaClic[ 1 ] == -1 and \
               self.dondeIntentaClic[ 2 ] == -1 and \
               self.dondeIntentaClic[ 3 ] == -1 :

                self.dondeIntentaClic[ 0 ] = QCursor.pos().x()
                self.dondeIntentaClic[ 1 ] = QCursor.pos().y()

                self.dondeIntentaClic[ 2 ] = pos_kp.x()
                self.dondeIntentaClic[ 3 ] = pos_kp.y()


            diferencia_x = self.dondeIntentaClic[ 2 ] - pos_kp.x()
            diferencia_y = self.dondeIntentaClic[ 3 ] - pos_kp.y()

            mouseActual = QCursor.pos()

            desplazamiento_x = diferencia_x / self.config[ 'mouse_factor_cercano' ]
            desplazamiento_y = diferencia_y / self.config[ 'mouse_factor_cercano' ]

            QCursor.setPos( mouseActual.x() - desplazamiento_x, mouseActual.y() - desplazamiento_y )


            # Por último dibujamos el punto donde intenta hacer clic y el vector que define el 
            # pequeño desplazamiento sobre la vecindad
            h, w, ch = frame.shape
            cv2.circle( frame, ( int( self.dondeIntentaClic[ 2 ] * w / self.screen_w ), 
                                 int( self.dondeIntentaClic[ 3 ] * h / self.screen_h ) ), 
                                 10, ( 255, 20, 20 ), thickness = cv2.FILLED )

            cv2.line( frame, 
                      ( int( self.dondeIntentaClic[ 2 ] * w / self.screen_w ), 
                        int( self.dondeIntentaClic[ 3 ] * h / self.screen_h ) ), 
                      ( int( pos_kp.x() * w / self.screen_w ), 
                        int( pos_kp.y() * h / self.screen_h ) ),
                      ( 20, 20, 255 ), thickness = 5 )

            cv2.circle( frame, ( int( pos_kp.x() * w / self.screen_w ), 
                                 int( pos_kp.y() * h / self.screen_h ) ), 
                                 7, ( 20, 20, 255 ), thickness = cv2.FILLED )



    def controlarDesplazamientoMouseCercano_para_clic_con_L1( self, label_gesto_detectado, hand_landmarks, frame ) :
        if ( label_gesto_detectado == self.config[ 'clic_cercano_gesto' ] or \
             label_gesto_detectado == self.config[ 'clic_derecho_cercano_gesto' ] ) and self.config[ 'clic' ] == True :

            x_kp = hand_landmarks.landmark[ self.config[ 'clic_keypoint_L_antes_de_clic' ] ].x 
            y_kp = hand_landmarks.landmark[ self.config[ 'clic_keypoint_L_antes_de_clic' ] ].y

            # Esta es la posición real (en la imagen de la cámara sin ajustar al recuadro verde) 
            # detectada de la punta del dedo índice
            pos_kp = QPoint( x_kp * self.screen_w, y_kp * self.screen_h ) 

            if self.dondeIntentaClic[ 0 ] == -1 and \
               self.dondeIntentaClic[ 1 ] == -1 and \
               self.dondeIntentaClic[ 2 ] == -1 and \
               self.dondeIntentaClic[ 3 ] == -1 :

                self.dondeIntentaClic[ 0 ] = QCursor.pos().x()
                self.dondeIntentaClic[ 1 ] = QCursor.pos().y()

                self.dondeIntentaClic[ 2 ] = pos_kp.x()
                self.dondeIntentaClic[ 3 ] = pos_kp.y()


            diferencia_x = self.dondeIntentaClic[ 2 ] - pos_kp.x()
            diferencia_y = self.dondeIntentaClic[ 3 ] - pos_kp.y()

            mouseActual = QCursor.pos()

            desplazamiento_x = diferencia_x / self.config[ 'mouse_factor_cercano' ]
            desplazamiento_y = diferencia_y / self.config[ 'mouse_factor_cercano' ]

            QCursor.setPos( mouseActual.x() - desplazamiento_x, mouseActual.y() - desplazamiento_y )


            # Por último dibujamos el punto donde intenta hacer clic y el vector que define el 
            # pequeño desplazamiento sobre la vecindad
            h, w, ch = frame.shape
            cv2.circle( frame, ( int( self.dondeIntentaClic[ 2 ] * w / self.screen_w ), 
                                 int( self.dondeIntentaClic[ 3 ] * h / self.screen_h ) ), 
                                 10, ( 255, 20, 20 ), thickness = cv2.FILLED )

            cv2.line( frame, 
                      ( int( self.dondeIntentaClic[ 2 ] * w / self.screen_w ), 
                        int( self.dondeIntentaClic[ 3 ] * h / self.screen_h ) ), 
                      ( int( pos_kp.x() * w / self.screen_w ), 
                        int( pos_kp.y() * h / self.screen_h ) ),
                      ( 20, 20, 255 ), thickness = 5 )

            cv2.circle( frame, ( int( pos_kp.x() * w / self.screen_w ), 
                                 int( pos_kp.y() * h / self.screen_h ) ), 
                                 7, ( 20, 20, 255 ), thickness = cv2.FILLED )


    def controlarFlecha_izq_der( self, label_gesto_detectado, hand_landmarks, frame, punto_inicial ) :

        if label_gesto_detectado == self.config[ 'id_puno' ] \
           and self.config[ 'flechas' ] == True :

            h, w, ch = frame.shape

            if self.flechas_agarrado == False :
                
                # Este es el valor en x desde dónde se comienza a desplazar
                # self.flechas_x = hand_landmarks.landmark[ self.config[ 'flechas_keypoint' ] ].x * w
                self.flechas_agarrado = True

            else :
                flechas_y = hand_landmarks.landmark[ self.config[ 'keypoint_representativo_puno' ] ].y * h
                x_actual = hand_landmarks.landmark[ self.config[ 'keypoint_representativo_puno' ] ].x * w
                y_actual = hand_landmarks.landmark[ self.config[ 'keypoint_representativo_puno' ] ].y * h

                diferencia = int( punto_inicial.x() - x_actual )
                # print( 'diferencia', diferencia )

                # Cuando 'diferencia' es negativo es porque se desplaz+o a la derecha
                if abs( diferencia ) > self.config[ 'flechas_diferencia_x' ] and \
                   self.isListo_para_flechas == True :

                    if diferencia < 0 :  # Izquierda
                        pyautogui.press( 'right' )
                        # keyboard.send_keys( '{RIGHT}' )
                        print( 'right' )
                        self.flechas_agarrado == False 
                    else :  # Derecha
                        pyautogui.press( 'left' )
                        # keyboard.send_keys( '{LEFT}' )
                        print( 'left' )
                        self.flechas_agarrado == False 

                    self.timer_nuevo_flechas.start()
                    self.isListo_para_flechas = False

                # Por último dibujamos la línea desde donde se está tomando como referencia para el scroll                    
                cv2.line( frame, 
                          ( int( punto_inicial.x() ), 0 ), ( int( punto_inicial.x() ), w ),
                          ( 255, 20, 20 ), thickness = 5 )

                cv2.line( frame, 
                          ( int( x_actual ), 0 ), ( int( x_actual ), h ),
                          ( 20, 20, 255 ), thickness = 3 )

                cv2.line( frame, 
                          ( int( x_actual ), int( y_actual ) ), ( int( punto_inicial.x() ), int( flechas_y ) ),
                          ( 20, 20, 255 ), thickness = 4 )

                cv2.circle( frame, ( int( x_actual ), int( y_actual ) ), 
                            10, ( 255, 20, 20 ), thickness = cv2.FILLED )


        if label_gesto_detectado != self.config[ 'id_puno' ] \
           and self.config[ 'flechas' ] == True \
           and self.flechas_agarrado == True :

            self.flechas_x = -1
            self.flechas_agarrado = False



    def controlarScroll( self, label_gesto_detectado, hand_landmarks, frame, punto_inicial ) :

        if label_gesto_detectado == self.config[ 'id_puno' ] \
           and self.config[ 'scroll' ] == True :

            h, w, ch = frame.shape

            if self.scroll_agarrado == False :
                
                # self.scroll_y = hand_landmarks.landmark[ self.config[ 'scroll_keypoint' ] ].y * h
                self.scroll_agarrado = True

            else :
                scroll_x = hand_landmarks.landmark[ self.config[ 'keypoint_representativo_puno' ] ].x * w
                x_actual = hand_landmarks.landmark[ self.config[ 'keypoint_representativo_puno' ] ].x * w
                y_actual = hand_landmarks.landmark[ self.config[ 'keypoint_representativo_puno' ] ].y * h

                diferencia = int( punto_inicial.y() - y_actual )
                # print( 'diferencia ', diferencia )
                # self.scroll_y = y_actual
                # print( 'Scroll ', int( diferencia / 5 ), ' en ', x_actual, ', ', y_actual )
                # pyautogui.scroll( int( diferencia / 5 ), x_actual, y_actual )

                # Este valor es para tener un margen en donde no se hace scroll. Sólo hará scroll
                # cuando la diferencia sea mayor que este valor. La diferencia es entre el lugar en y donde
                # cerró el puño hasta la posición actual de y detectada del scroll_keypoint
                if abs( diferencia ) > self.config[ 'scroll_diferencia_y' ] and \
                   self.isListo_para_scroll == True :

                    # scroll_factor_division_diferencia = 30  para Toshibe - resolución 1366x768
                    # scroll_factor_division_diferencia = 0.75  para Ispiron - resolución 1920x1080

                    # print( diferencia, int( diferencia / self.config[ 'scroll_factor_division_diferencia' ] ) )

                    pyautogui.scroll( int( diferencia / self.config[ 'scroll_factor_division_diferencia' ] ) )
                    
                    # pyautogui.scroll( int( diferencia / 10 ), x_actual, y_actual )
                    self.timer_nuevo_scroll.start()
                    self.isListo_para_scroll = False

                # Por último dibujamos la línea desde donde se está tomando como referencia para el scroll                    
                cv2.line( frame, 
                          ( 0, int( punto_inicial.y() ) ), ( w, int( punto_inicial.y() ) ),
                          ( 255, 20, 20 ), thickness = 5 )

                cv2.line( frame, 
                          ( 0, int( y_actual ) ), ( w, int( y_actual ) ),
                          ( 20, 20, 255 ), thickness = 3 )

                cv2.line( frame, 
                          ( int( x_actual ), int( y_actual ) ), ( int( scroll_x ), int( punto_inicial.y() ) ),
                          ( 20, 20, 255 ), thickness = 4 )

                cv2.circle( frame, ( int( x_actual ), int( y_actual ) ), 
                            10, ( 255, 20, 20 ), thickness = cv2.FILLED )


        if label_gesto_detectado != self.config[ 'id_puno' ] \
           and self.config[ 'scroll' ] == True \
           and self.scroll_agarrado == True :

            # self.scroll_y = -1
            self.scroll_agarrado = False




    def getUltimoGesto( self ) :
        size_vector_secuencia_gestos = self.vector_secuencia_gestos.shape[ 0 ]
        return self.vector_secuencia_gestos[ size_vector_secuencia_gestos - 1 ]

    def getPenultimoGesto( self ) :
        size_vector_secuencia_gestos = self.vector_secuencia_gestos.shape[ 0 ]
        return self.vector_secuencia_gestos[ size_vector_secuencia_gestos - 2 ]

    def getAntepenultimoGesto( self ) :
        size_vector_secuencia_gestos = self.vector_secuencia_gestos.shape[ 0 ]
        return self.vector_secuencia_gestos[ size_vector_secuencia_gestos - 3 ]        


    # Detecta el comportamiento dentro del vector_frames
    def analizar_si_hay_clic( self ) :

        desviacion_clic_keypoint_z = int( np.std( self.vector_frames ) )
        promedio_clic_keypoint_z = int( np.mean( self.vector_frames ) )
        varianza_clic_keypoint_z = int( np.var( self.vector_frames ) )
        max_clic_keypoint_z = int( max( self.vector_frames ) )
        min_clic_keypoint_z = int( min( self.vector_frames ) )        

        # print( self.vector_frames, ' desv=', desviacion_clic_keypoint_z, ' prom=', promedio_clic_keypoint_z,
        #        ' var=', varianza_clic_keypoint_z, ' centro=', min_clic_keypoint_z, 
        #        ' extremos=', max_clic_keypoint_z )

        mitad = self.config[ 'ventana_frames' ] / 2

        # Entra a este if cuando el valor de la cresta (que sería el mínimo) está en la ubicación central del
        # vector_frames. En este momento entonces debemos tomar el valor máximo de la primer mitad de las 
        # ubicaciones de este vector_frames para luego detectar si se encuentra un mayor + umbral_retorno_z 
        # en la segunda mitad.
        if min_clic_keypoint_z == self.vector_frames[ int( mitad ) ] :

            primer_mitad_vector_frames = self.vector_frames[ :  int( self.config[ 'ventana_frames' ] / 2 ) ] 
            segunda_mitad_vector_frames = self.vector_frames[ int( self.config[ 'ventana_frames' ] / 2 ) : ] 

            mayor_1er_mitad = int( max( primer_mitad_vector_frames ) )
            mayor_2da_mitad = int( max( segunda_mitad_vector_frames ) )

            centro = abs( min_clic_keypoint_z )
            extremo_promedio = ( abs( mayor_1er_mitad ) + abs( mayor_2da_mitad ) ) / 2

            diferencia_centro_extremo = centro - extremo_promedio


            # print( '^^^^^^^^^^^^^^^^^^', ' mayor primer=', mayor_1er_mitad,
            #        ' mayor segunda=', mayor_2da_mitad )

            umbral_desv = self.config[ 'umbral_desv_min_clic' ]
            umbral_factor = self.config[ 'umbral_desv_factor_de_division' ]            

            # if abs( mayor_2da_mitad ) > ( abs( mayor_1er_mitad ) - self.config[ 'umbral_retorno_z' ] / 2 ) :
            #     print( 'cumple mayor_1er_mitad', mayor_1er_mitad )

            # if abs( mayor_2da_mitad ) < ( abs( mayor_1er_mitad ) + self.config[ 'umbral_retorno_z' ] / 2 ) :
            #     print( 'cumple mayor_2da_mitad', mayor_2da_mitad )

            # if varianza_clic_keypoint_z > self.config[ 'umbral_varianza' ] :
            #     print( 'varianza_clic_keypoint_z', varianza_clic_keypoint_z )

            # if diferencia_centro_extremo > self.config[ 'clic_diferencia_centro_extremo' ] :
            #     print( 'diferencia_centro_extremo', diferencia_centro_extremo )

            if abs( mayor_2da_mitad ) > ( abs( mayor_1er_mitad ) - self.config[ 'umbral_retorno_z' ] / 2 ) \
                and abs( mayor_2da_mitad ) < ( abs( mayor_1er_mitad ) + self.config[ 'umbral_retorno_z' ] / 2 ) \
                and diferencia_centro_extremo > self.config[ 'clic_diferencia_centro_extremo' ] :
                # and varianza_clic_keypoint_z > self.config[ 'umbral_varianza' ] :
                # and desviacion_clic_keypoint_z > ( umbral_desv + abs( promedio_clic_keypoint_z ) / umbral_factor ) :

                # print( 'devuelve True' )
                # self.vector_frames = np.full_like( self.vector_frames, 0 )

                # resetea las métricas para evitar que detecte algún clic en intentos de clics anteriores
                self.resetear_metricas()

                return True

        return False



    # Este método analiza self.vector_secuencia_gestos para detectar alguna secuencia particular y
    # realizar alguna acción
    def detectar_secuencia_de_gestos( self, secuencia ) :

        # Creamos un vector de tamaño igual a secuencia y colocamos los últimos gestos de vector_secuencia_gestos
        ultimos_gestos = np.zeros( len( secuencia ), dtype = np.int8 ) 
        ultimos_gestos = self.vector_secuencia_gestos[ - len( secuencia ) : ]

        for i in range( 0, len( secuencia ) ) :

            # Si entra a este if es porque la secuencia tiene más elementos que vector_secuencia_gestos
            if i >= len( self.vector_secuencia_gestos ) :
                return False

            if secuencia[ i ] != ultimos_gestos[ i ] :
                return False

        # Cuando una secuencia es detectada, se devuelve True para que realice la acción para la cuál está
        # configurada. Para que no siga detectando esta secuencia, entonces la reseteamos poniendo todo
        # en -1. 
        self.vector_secuencia_gestos.fill( -1 )

        return True


    def transformar( self, mano ) :
        mano_trasladada = T.traslacion( mano )
        mano_trasladada_rotada = T.rotacion_alinear_al_eje_y( mano_trasladada )
        mano_palma_alineada = T.rotacion_palma( mano_trasladada_rotada )

        palmaAlFrente = mano_palma_alineada
        if T.isPalmaAlFrente( mano_palma_alineada ) == False :
            palmaAlFrente = T.rotacion_sobre_ejeY( mano_palma_alineada, 180 )

        manoDerecha = palmaAlFrente
        if T.isManoDerecha( palmaAlFrente ) == False :
            manoDerecha = T.reflejar_sobre_planoX( palmaAlFrente )

        escalada = T.escalado( manoDerecha, 100 )

        return escalada
