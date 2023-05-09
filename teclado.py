
from PySide6.QtCore import *
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QGuiApplication 
from PySide6.QtWidgets import QWidget, QGridLayout

import json
import numpy as np
import tkinter as tk
import pywintypes
import win32api
import win32con

np.set_printoptions( suppress = True )  # Para que la notacion no sea la cientifica

class Boton( QWidget ) :

    # Como no logré hacer que se envíe un string, entonces voy a definir un id a cada botón y la señal enviará ese id
    # Quedarán ordenados según el orden siguiente orden, comenzando con el id = 0
    # Esc, plica, 1, 2, 3, etc
    signal_clic = Signal( int )

    def __init__( self, tipo = 'normal', borde = 2, letra = '', letra_segunda = '', id = 0, parent = None ) :
        super( Boton, self ).__init__( parent )

        with open( 'config.json' ) as json_file: 
            self.config = json.load( json_file )       

        if tipo == 'normal' :
            self.setFixedSize( self.config[ 'boton_w' ], self.config[ 'boton_h' ] )
        elif tipo == 'doble' :
            self.setFixedSize( 2 * self.config[ 'boton_w' ], self.config[ 'boton_h' ] )
        elif tipo == 'espacio' :
            self.setFixedSize( 6 * self.config[ 'boton_w' ], self.config[ 'boton_h' ] )
        else :
            self.setFixedSize( self.config[ 'boton_w' ], self.config[ 'boton_h' ] )

        self.setMouseTracking( True )

        self.borde = borde
        self.letra = letra
        self.letra_segunda = letra_segunda
        self.id = id
        self.mouse_encima = False

    def mouseMoveEvent( self, e ) :
        # self.mouse_encima = True
        self.repaint()

    def leaveEvent( self, e ) :
        # self.mouse_encima = True
        self.repaint()    

    def mousePressEvent( self, e ) :
        self.signal_clic.emit( self.id )
           
    def paintEvent( self, e ) :
        painter = QPainter( self )

        pen = QPen( QColor( 255, 255, 255 ) )
        painter.setPen( pen )

        font = painter.font()
        font.setPixelSize( 16 )
        painter.setFont( font )

        if self.underMouse() :
            painter.fillRect( self.borde, self.borde, self.width() - 2 * self.borde, self.height() - 2 * self.borde, QColor( 30, 30, 220 ) )
        else :
            painter.fillRect( self.borde, self.borde, self.width() - 2 * self.borde, self.height() - 2 * self.borde, QColor( 51, 51, 51 ) )
            

        if self.letra_segunda == '' : 
            painter.drawText( 1 * self.borde, 1 * self.borde, self.width() - 2 * self.borde, self.height() - 2 * self.borde, 
                              Qt.AlignCenter, self.letra )
        else : 
            painter.drawText( 4 * self.borde, 4 * self.borde, self.width() - 2 * self.borde, self.height() - 2 * self.borde, 
                              Qt.AlignCenter, self.letra )

            pen = QPen( QColor( 150, 150, 150 ) )
            painter.setPen( pen )
            font = painter.font()
            font.setPixelSize( 14 )
            painter.setFont( font )
            painter.drawText( 1 * self.borde, 2 * self.borde, self.width() / 2, self.height() / 2, Qt.AlignCenter, self.letra_segunda )
            

class Teclado( QWidget ) :

    # Hacemos un pasa manos de las señales de cada botón 
    signal_clic = Signal( int )

    def __init__( self, parent = None ) :
        super( Teclado, self ).__init__( parent )

        with open( 'config.json' ) as json_file: 
            self.config = json.load( json_file ) 

        grid = QGridLayout( self )
        grid.setContentsMargins( 0, 0, 0, 0 )
        grid.setVerticalSpacing( 0 )
        grid.setHorizontalSpacing( 0 )

        b_esc = Boton( tipo = 'normal', parent = self, letra = 'Esc', id = 0 ) 
        b_plica = Boton( tipo = 'normal', parent = self, letra = '|', letra_segunda = '°', id = 1 )
        b_1 = Boton( tipo = 'normal', parent = self, letra = '1', letra_segunda = '!', id = 2 )
        b_2 = Boton( tipo = 'normal', parent = self, letra = '2', letra_segunda = '"', id = 3 )
        b_3 = Boton( tipo = 'normal', parent = self, letra = '3', letra_segunda = '#', id = 4 )
        b_4 = Boton( tipo = 'normal', parent = self, letra = '4', letra_segunda = '$', id = 5 )    
        b_5 = Boton( tipo = 'normal', parent = self, letra = '5', letra_segunda = '%', id = 6 )
        b_6 = Boton( tipo = 'normal', parent = self, letra = '6', letra_segunda = '&', id = 7 )   
        b_7 = Boton( tipo = 'normal', parent = self, letra = '7', letra_segunda = '/', id = 8 )
        b_8 = Boton( tipo = 'normal', parent = self, letra = '8', letra_segunda = '(', id = 9 )    
        b_9 = Boton( tipo = 'normal', parent = self, letra = '9', letra_segunda = ')', id = 10 )
        b_0 = Boton( tipo = 'normal', parent = self, letra = '0', letra_segunda = '=', id = 11 )   
        b_apostrofe = Boton( tipo = 'normal', parent = self, letra = '\'', letra_segunda = '?', id = 12 )
        b_abrirPregunta = Boton( tipo = 'normal', parent = self, letra = '¿', letra_segunda = '¡', id = 13 )
        b_backspace = Boton( tipo = 'doble', parent = self, letra = '<--', id = 14 )

        b_tab = Boton( tipo = 'doble', parent = self, letra = 'Tab', id = 15 );   
        b_q = Boton( tipo = 'normal', parent = self, letra = 'q', id = 16 )
        b_w = Boton( tipo = 'normal', parent = self, letra = 'w', id = 17 );    
        b_e = Boton( tipo = 'normal', parent = self, letra = 'e', id = 18 );
        b_r = Boton( tipo = 'normal', parent = self, letra = 'r', id = 19 );    
        b_t = Boton( tipo = 'normal', parent = self, letra = 't', id = 20 );
        b_y = Boton( tipo = 'normal', parent = self, letra = 'y', id = 21 );    
        b_u = Boton( tipo = 'normal', parent = self, letra = 'u', id = 22 );
        b_i = Boton( tipo = 'normal', parent = self, letra = 'i', id = 23 );    
        b_o = Boton( tipo = 'normal', parent = self, letra = 'o', id = 24 );
        b_p = Boton( tipo = 'normal', parent = self, letra = 'p', id = 25 )
        b_acentoAlReves = Boton( tipo = 'normal', parent = self, letra = '´', letra_segunda = '¨', id = 26 );
        b_mas = Boton( tipo = 'normal', parent = self, letra = '+', letra_segunda = '*', id = 27 )
        b_nada = Boton( tipo = 'doble', parent = self, letra = 'Enter', id = 28 )

        b_bloquearMay = Boton( tipo = 'doble', parent = self, letra = 'Bloq May', id = 29 );      
        b_a = Boton( tipo = 'normal', parent = self, letra = 'a', id = 30 )
        b_s = Boton( tipo = 'normal', parent = self, letra = 's', id = 31 );              
        b_d = Boton( tipo = 'normal', parent = self, letra = 'd', id = 32 );
        b_f = Boton( tipo = 'normal', parent = self, letra = 'f', id = 33 );              
        b_g = Boton( tipo = 'normal', parent = self, letra = 'g', id = 34 );
        b_h = Boton( tipo = 'normal', parent = self, letra = 'h', id = 35 );              
        b_j = Boton( tipo = 'normal', parent = self, letra = 'j', id = 36 );
        b_k = Boton( tipo = 'normal', parent = self, letra = 'k', id = 37 );              
        b_l = Boton( tipo = 'normal', parent = self, letra = 'l', id = 38 );
        b_enie = Boton( tipo = 'normal', parent = self, letra = 'ñ', id = 39 )
        b_abrirLlaves = Boton( tipo = 'normal', parent = self, letra = '{', letra_segunda = '[', id = 40 )
        b_cerrarLlaves = Boton( tipo = 'normal', parent = self, letra = '}', letra_segunda = ']', id = 41 )
        b_enter = Boton( tipo = 'doble', parent = self, letra = '', id = 42 )

        b_mayusculas = Boton( tipo = 'doble', parent = self, letra = 'Mayús', id = 43 );      
        b_mayor = Boton( tipo = 'normal', parent = self, letra = '<', id = 44 )
        b_z = Boton( tipo = 'normal', parent = self, letra = 'z', id = 45 );              
        b_x = Boton( tipo = 'normal', parent = self, letra = 'x', id = 46 );
        b_c = Boton( tipo = 'normal', parent = self, letra = 'c', id = 47 );              
        b_v = Boton( tipo = 'normal', parent = self, letra = 'v', id = 48 );
        b_b = Boton( tipo = 'normal', parent = self, letra = 'b', id = 49 );              
        b_n = Boton( tipo = 'normal', parent = self, letra = 'n', id = 50 );
        b_m = Boton( tipo = 'normal', parent = self, letra = 'm', id = 51 )      
        b_coma = Boton( tipo = 'normal', parent = self, letra = ',', letra_segunda = ';', id = 52 );
        b_punto = Boton( tipo = 'normal', parent = self, letra = '.', letra_segunda = ':', id = 53 )
        b_guion = Boton( tipo = 'normal', parent = self, letra = '-', letra_segunda = '_', id = 54 );
        b_arriba = Boton( tipo = 'normal', parent = self, letra = 'Arr', id = 55 );         
        b_mayDer = Boton( tipo = 'normal', parent = self, letra = 'Mayús', id = 56 )
        b_suprimir = Boton( tipo = 'normal', parent = self, letra = 'Supr', id = 57 )

        b_control = Boton( tipo = 'normal', parent = self, letra = 'Ctrl', id = 58 );      
        b_fn = Boton( tipo = 'normal', parent = self, letra = 'Fn', id = 59 )
        b_win = Boton( tipo = 'normal', parent = self, letra = 'Win', id = 60 );         
        b_alt = Boton( tipo = 'normal', parent = self, letra = 'Alt', id = 61 );
        b_espacio = Boton( tipo = 'espacio', parent = self, letra = 'Space', id = 62 );     
        b_altGr = Boton( tipo = 'normal', parent = self, letra = 'AltGr', id = 63 );
        b_controlDer = Boton( tipo = 'normal', parent = self, letra = 'Ctrl', id = 64 );  
        b_izq = Boton( tipo = 'normal', parent = self, letra = 'Izq', id = 65 );
        b_abajo = Boton( tipo = 'normal', parent = self, letra = 'Aba', id = 66 );       
        b_der = Boton( tipo = 'normal', parent = self, letra = 'Der', id = 67 );
        b_menu = Boton( tipo = 'normal', parent = self, letra = 'Option', id = 68 );          

        grid.addWidget( b_esc, 0, 0, 1, 1 );  grid.addWidget( b_plica, 0, 1, 1, 1 );
        grid.addWidget( b_1, 0, 2, 1, 1 );   grid.addWidget( b_2, 0, 3, 1, 1 )
        grid.addWidget( b_3, 0, 4, 1, 1 );    grid.addWidget( b_4, 0, 5, 1, 1 );   grid.addWidget( b_5, 0, 6, 1, 1 )
        grid.addWidget( b_6, 0, 7, 1, 1 );    grid.addWidget( b_7, 0, 8, 1, 1 );   grid.addWidget( b_8, 0, 9, 1, 1 )
        grid.addWidget( b_9, 0, 10, 1, 1 );    grid.addWidget( b_0, 0, 11, 1, 1 );  grid.addWidget( b_apostrofe, 0, 12, 1, 1 )
        grid.addWidget( b_abrirPregunta, 0, 13, 1, 1 );                            grid.addWidget( b_backspace, 0, 14, 1, 2 )

        grid.addWidget( b_tab, 1, 0, 1, 2 );  grid.addWidget( b_q, 1, 2, 1, 1 );   grid.addWidget( b_w, 1, 3, 1, 1 )
        grid.addWidget( b_e, 1, 4, 1, 1 );    grid.addWidget( b_r, 1, 5, 1, 1 );   grid.addWidget( b_t, 1, 6, 1, 1 )
        grid.addWidget( b_y, 1, 7, 1, 1 );    grid.addWidget( b_u, 1, 8, 1, 1 );   grid.addWidget( b_i, 1, 9, 1, 1 )
        grid.addWidget( b_o, 1, 10, 1, 1 );    grid.addWidget( b_p, 1, 11, 1, 1 );  grid.addWidget( b_acentoAlReves, 1, 12, 1, 1 )
        grid.addWidget( b_mas, 1, 13, 1, 1 );                                      grid.addWidget( b_nada, 1, 14, 1, 2 )

        grid.addWidget( b_bloquearMay, 2, 0, 1, 2 );  grid.addWidget( b_a, 2, 2, 1, 1 );      grid.addWidget( b_s, 2, 3, 1, 1 )
        grid.addWidget( b_d, 2, 4, 1, 1 );            grid.addWidget( b_f, 2, 5, 1, 1 );      grid.addWidget( b_g, 2, 6, 1, 1 )
        grid.addWidget( b_h, 2, 7, 1, 1 );            grid.addWidget( b_j, 2, 8, 1, 1 );      grid.addWidget( b_k, 2, 9, 1, 1 )
        grid.addWidget( b_l, 2, 10, 1, 1 );            grid.addWidget( b_enie, 2, 11, 1, 1 );  grid.addWidget( b_abrirLlaves, 2, 12, 1, 1 )
        grid.addWidget( b_cerrarLlaves, 2, 13, 1, 1 );                                        grid.addWidget( b_enter, 2, 14, 1, 2 )

        grid.addWidget( b_mayusculas, 3, 0, 1, 2 );  grid.addWidget( b_mayor, 3, 2, 1, 1 );    grid.addWidget( b_z, 3, 3, 1, 1 )
        grid.addWidget( b_x, 3, 4, 1, 1 );           grid.addWidget( b_c, 3, 5, 1, 1 );        grid.addWidget( b_v, 3, 6, 1, 1 )
        grid.addWidget( b_b, 3, 7, 1, 1 );           grid.addWidget( b_n, 3, 8, 1, 1 );        grid.addWidget( b_m, 3, 9, 1, 1 )
        grid.addWidget( b_coma, 3, 10, 1, 1 );        grid.addWidget( b_punto, 3, 11, 1, 1 );   grid.addWidget( b_guion, 3, 12, 1, 1 )
        grid.addWidget( b_arriba, 3, 13, 1, 1 );     grid.addWidget( b_mayDer, 3, 14, 1, 1 );  grid.addWidget( b_suprimir, 3, 15, 1, 1 )

        grid.addWidget( b_control, 4, 0, 1, 1 );      grid.addWidget( b_fn, 4, 1, 1, 1 );       grid.addWidget( b_win, 4, 2, 1, 1 )
        grid.addWidget( b_alt, 4, 3, 1, 1 );          grid.addWidget( b_espacio, 4, 4, 1, 6 );  grid.addWidget( b_altGr, 4, 10, 1, 1 )
        grid.addWidget( b_controlDer, 4, 11, 1, 1 );  grid.addWidget( b_izq, 4, 12, 1, 1 );     grid.addWidget( b_abajo, 4, 13, 1, 1 )
        grid.addWidget( b_der, 4, 14, 1, 1 );         grid.addWidget( b_menu, 4, 15, 1, 1 )
      
        QObject.connect( b_esc, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_plica, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_1, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_2, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_3, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_4, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_5, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_6, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_7, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_8, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_9, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_0, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_apostrofe, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_abrirPregunta, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_backspace, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_tab, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_q, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_w, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_e, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_r, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_t, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_y, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_u, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_i, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_o, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_p, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_acentoAlReves, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_mas, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_nada, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_bloquearMay, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_a, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_s, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_d, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_f, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_g, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_h, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_j, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_k, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_l, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_enie, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_abrirLlaves, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_cerrarLlaves, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_enter, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_mayusculas, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_mayor, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_z, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_x, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_c, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_v, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_b, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_n, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_m, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_coma, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_punto, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_guion, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_arriba, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_mayDer, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_suprimir, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_control, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_fn, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_win, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_alt, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_espacio, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_altGr, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_controlDer, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_izq, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_abajo, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_der, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        QObject.connect( b_menu, SIGNAL( "signal_clic( int )" ), self.slot_clic )
        

        self.setLayout( grid )
 
        self.setWindowTitle( 'Teclado virtual' )

        self.setWindowFlags( Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool | Qt.WindowDoesNotAcceptFocus )  

        # Esto es para solucionar el motivo porque no funciona el Qt.WindowDoesNotAcceptFocus
        hWindow = pywintypes.HANDLE( int( self.winId() ) )
        exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE
        win32api.SetWindowLong( hWindow, win32con.GWL_EXSTYLE, exStyle )


    @Slot( int )
    def slot_clic( self, id ) :
        self.signal_clic.emit( id )      

    def mousePressEvent( self, e ) :
        print( 'mouse teclado', e.pos().x(), e.pos().y() )

    def moveEvent( self, e ) :
        print( 'move teclado', e.pos().x(), e.pos().y() )

    def resizeEvent( self, e ) :
        print( 'nuevo tamano teclado', e.size().width(), e.size().height() )

    def showEvent( self, e ) :
        print( 'showEvent' ) 

        root = tk.Tk()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()  

        screen = QGuiApplication.primaryScreen()
        screen_w = screen.availableSize().width()
        screen_h = screen.availableSize().height()
        
        escala_dpi = root.winfo_screenwidth() / screen.availableSize().width()   


        print( 'availableSize', screen_w, screen_h, 'root', root.winfo_screenwidth(), root.winfo_screenheight(), escala_dpi )

        self.move( 0, screen_h - self.height() )

   
    def paintEvent( self, e ) :
        painter = QPainter( self )
        painter.fillRect( 0, 0, self.width(), self.height(), QColor( 24, 24, 24 ) )

