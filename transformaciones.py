
import math
import numpy as np
import tensorflow as tf


def rotacion_z( mano ) :

    kp5x = mano[ 5 ][ 0 ]
    kp5y = mano[ 5 ][ 1 ]
    kp5z = mano[ 5 ][ 2 ]

    kp5_mod = math.sqrt( kp5x ** 2 + kp5y ** 2 + kp5z ** 2 )
    theta = math.acos( kp5z / kp5_mod )

    mano_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 21 ) :

        kpix = mano[ i ][ 0 ]
        kpiy = mano[ i ][ 1 ]
        kpiz = mano[ i ][ 2 ]

        kpix_nuevo = math.cos( theta ) * kpix - math.sin( theta ) * kpiy
        kpiy_nuevo = math.sin( theta ) * kpix + math.cos( theta ) * kpiy 
        kpiz_nuevo = kpiz

        mano_nueva = np.append( mano_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ) ] ], axis = 0 )

    return mano_nueva      


def rotacion_x( mano ) :

    kp5x = mano[ 5 ][ 0 ]
    kp5y = mano[ 5 ][ 1 ]
    kp5z = mano[ 5 ][ 2 ]

    kp5_mod = math.sqrt( kp5x ** 2 + kp5y ** 2 + kp5z ** 2 )
    theta = math.acos( kp5x / kp5_mod )

    mano_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 21 ) :

        kpix = mano[ i ][ 0 ]
        kpiy = mano[ i ][ 1 ]
        kpiz = mano[ i ][ 2 ]

        kpix_nuevo = kpix
        kpiy_nuevo = math.cos( theta ) * kpiy - math.sin( theta ) * kpiz
        kpiz_nuevo = math.sin( theta ) * kpiy + math.cos( theta ) * kpiz 

        mano_nueva = np.append( mano_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ) ] ], axis = 0 )

    return mano_nueva     


def rotacion_eje_arbitrario( mano ) :

    kp5x = mano[ 5 ][ 0 ]
    kp5y = mano[ 5 ][ 1 ]
    kp5z = mano[ 5 ][ 2 ]

    kp5_mod = math.sqrt( kp5x ** 2 + kp5y ** 2 + kp5z ** 2 )
    gamma = math.acos( kp5y / kp5_mod )

    mano_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 21 ) :

        kpix = mano[ i ][ 0 ]
        kpiy = mano[ i ][ 1 ]
        kpiz = mano[ i ][ 2 ]

        kpix_nuevo = math.cos( gamma ) * kpix + math.sin( gamma ) * kpiz
        kpiy_nuevo = kpiy
        kpiz_nuevo = - math.sin( gamma ) * kpix + math.cos( gamma ) * kpiz 

        mano_nueva = np.append( mano_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ) ] ], axis = 0 )

    return mano_nueva  


def rotacion_alinear_al_eje_y( mano ) :

    kp9x = mano[ 9 ][ 0 ]
    kp9y = mano[ 9 ][ 1 ]
    kp9z = mano[ 9 ][ 2 ]

    kp9_mod = math.sqrt( kp9x ** 2 + kp9y ** 2 + kp9z ** 2 )
    gamma = math.acos( kp9y / kp9_mod )
    norma_w = math.sqrt( kp9z ** 2 + kp9x ** 2 )
    w_unitario_x = - kp9z / norma_w
    w_unitario_z = kp9x / norma_w

    mano_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 21 ) :

        kpix = mano[ i ][ 0 ]
        kpiy = mano[ i ][ 1 ]
        kpiz = mano[ i ][ 2 ]

        kpix_nuevo = ( math.cos(gamma) + w_unitario_x**2 * (1-math.cos(gamma)) ) * kpix \
                     - w_unitario_z * math.sin(gamma) * kpiy \
                     + w_unitario_x * w_unitario_z * (1-math.cos(gamma)) * kpiz

        kpiy_nuevo = w_unitario_z * math.sin(gamma) * kpix \
                     + math.cos(gamma) * kpiy \
                     - w_unitario_x * math.sin(gamma) * kpiz

        kpiz_nuevo = w_unitario_z * w_unitario_x * (1-math.cos(gamma)) * kpix \
                     + w_unitario_x * math.sin( gamma ) * kpiy \
                     + ( math.cos(gamma) + w_unitario_z**2 * (1-math.cos(gamma)) ) * kpiz

        mano_nueva = np.append( mano_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ) ] ], axis = 0 )

    return mano_nueva  

# Alinea los hombros en el eje vertical kp12 con el kp11 (el cual ya debe estar en el origen)
def rotacion_alinear_al_eje_y_pose( pose ) :

    kp12x = pose[ 12 ][ 0 ]
    kp12y = pose[ 12 ][ 1 ]
    kp12z = pose[ 12 ][ 2 ]
    kp12v = pose[ 12 ][ 3 ]

    kp12_mod = math.sqrt( kp12x ** 2 + kp12y ** 2 + kp12z ** 2 )
    gamma = math.acos( kp12y / kp12_mod )
    norma_w = math.sqrt( kp12z ** 2 + kp12x ** 2 )
    w_unitario_x = - kp12z / norma_w
    w_unitario_z = kp12x / norma_w

    pose_nueva = np.zeros( ( 0, 4 ), dtype = float )

    for i in range( 0, 33 ) :

        kpix = pose[ i ][ 0 ]
        kpiy = pose[ i ][ 1 ]
        kpiz = pose[ i ][ 2 ]
        kpiv = pose[ i ][ 3 ]

        kpix_nuevo = ( math.cos(gamma) + w_unitario_x**2 * (1-math.cos(gamma)) ) * kpix \
                     - w_unitario_z * math.sin(gamma) * kpiy \
                     + w_unitario_x * w_unitario_z * (1-math.cos(gamma)) * kpiz

        kpiy_nuevo = w_unitario_z * math.sin(gamma) * kpix \
                     + math.cos(gamma) * kpiy \
                     - w_unitario_x * math.sin(gamma) * kpiz

        kpiz_nuevo = w_unitario_z * w_unitario_x * (1-math.cos(gamma)) * kpix \
                     + w_unitario_x * math.sin( gamma ) * kpiy \
                     + ( math.cos(gamma) + w_unitario_z**2 * (1-math.cos(gamma)) ) * kpiz

        kpiv_nuevo = kpiv

        pose_nueva = np.append( pose_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ), float( kpiv_nuevo ) ] ], axis = 0 )

    return pose_nueva      


# Alinea con el eje y la recta que pasa por el mentón (kp 152) y la frente (kp 10). 
def rotacion_alinear_al_eje_y_cara( cara ) :

    kp_frente_x = cara[ 10 ][ 0 ]
    kp_frente_y = cara[ 10 ][ 1 ]
    kp_frente_z = cara[ 10 ][ 2 ]

    kp_frente_mod = math.sqrt( kp_frente_x ** 2 + kp_frente_y ** 2 + kp_frente_z ** 2 )
    gamma = math.acos( kp_frente_y / kp_frente_mod )
    norma_w = math.sqrt( kp_frente_z ** 2 + kp_frente_x ** 2 )
    w_unitario_x = - kp_frente_z / norma_w
    w_unitario_z = kp_frente_x / norma_w

    cara_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 468 ) :

        kpix = cara[ i ][ 0 ]
        kpiy = cara[ i ][ 1 ]
        kpiz = cara[ i ][ 2 ]

        kpix_nuevo = ( math.cos(gamma) + w_unitario_x**2 * (1-math.cos(gamma)) ) * kpix \
                     - w_unitario_z * math.sin(gamma) * kpiy \
                     + w_unitario_x * w_unitario_z * (1-math.cos(gamma)) * kpiz

        kpiy_nuevo = w_unitario_z * math.sin(gamma) * kpix \
                     + math.cos(gamma) * kpiy \
                     - w_unitario_x * math.sin(gamma) * kpiz

        kpiz_nuevo = w_unitario_z * w_unitario_x * (1-math.cos(gamma)) * kpix \
                     + w_unitario_x * math.sin( gamma ) * kpiy \
                     + ( math.cos(gamma) + w_unitario_z**2 * (1-math.cos(gamma)) ) * kpiz

        cara_nueva = np.append( cara_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ) ] ], axis = 0 )

    return cara_nueva  


def rotacion_palma( mano ) :

    kp17x = mano[ 17 ][ 0 ]
    kp17z = mano[ 17 ][ 2 ]
    
    beta = math.atan( kp17z / kp17x )

    mano_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 21 ) :

        kpix = mano[ i ][ 0 ]
        kpiy = mano[ i ][ 1 ]
        kpiz = mano[ i ][ 2 ]

        kpix_nuevo = math.cos( beta ) * kpix + math.sin( beta ) * kpiz
        kpiy_nuevo = kpiy
        kpiz_nuevo = - math.sin( beta ) * kpix + math.cos( beta ) * kpiz 

        mano_nueva = np.append( mano_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ) ] ], axis = 0 )

    return mano_nueva  


# Llevo el kp24 (cintura izq) al plano z=0
def rotacion_pecho( pose ) :

    kp24x = pose[ 24 ][ 0 ]
    kp24z = pose[ 24 ][ 2 ]
    
    beta = math.atan( kp24z / kp24x )

    pose_nueva = np.zeros( ( 0, 4 ), dtype = float )

    for i in range( 0, 33 ) :

        kpix = pose[ i ][ 0 ]
        kpiy = pose[ i ][ 1 ]
        kpiz = pose[ i ][ 2 ]
        kpiv = pose[ i ][ 3 ]

        kpix_nuevo = math.cos( beta ) * kpix + math.sin( beta ) * kpiz
        kpiy_nuevo = kpiy
        kpiz_nuevo = - math.sin( beta ) * kpix + math.cos( beta ) * kpiz 
        kpiv_nuevo = kpiv

        pose_nueva = np.append( pose_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ), float( kpiv_nuevo ) ] ], axis = 0 )

    return pose_nueva  


def rotacion_cara( cara ) :

    kp454x = cara[ 454 ][ 0 ]
    kp454z = cara[ 454 ][ 2 ]
    
    beta = math.atan( kp454z / kp454x )

    cara_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 468 ) :

        kpix = cara[ i ][ 0 ]
        kpiy = cara[ i ][ 1 ]
        kpiz = cara[ i ][ 2 ]

        kpix_nuevo = math.cos( beta ) * kpix + math.sin( beta ) * kpiz
        kpiy_nuevo = kpiy
        kpiz_nuevo = - math.sin( beta ) * kpix + math.cos( beta ) * kpiz 

        cara_nueva = np.append( cara_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ) ] ], axis = 0 )

    return cara_nueva  

def rotacion_sobre_ejeY( mano, anguloEnGrados = 180 ) :

    anguloRadianes = anguloEnGrados * 2 * math.pi / 360 
    
    mano_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 21 ) :

        kpix = mano[ i ][ 0 ]
        kpiy = mano[ i ][ 1 ]
        kpiz = mano[ i ][ 2 ]

        kpix_nuevo = math.cos(anguloRadianes) * kpix + math.sin(anguloRadianes) * kpiz 
        kpiy_nuevo = kpiy
        kpiz_nuevo = - math.sin(anguloRadianes) * kpix + math.cos(anguloRadianes) * kpiz 

        mano_nueva = np.append( mano_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ) ] ], axis = 0 )

    return mano_nueva  

def rotacion_sobre_ejeY_pose( pose, anguloEnGrados = 180 ) :

    anguloRadianes = anguloEnGrados * 2 * math.pi / 360 
    
    pose_nueva = np.zeros( ( 0, 4 ), dtype = float )

    for i in range( 0, 33 ) :

        kpix = pose[ i ][ 0 ]
        kpiy = pose[ i ][ 1 ]
        kpiz = pose[ i ][ 2 ]
        kpiv = pose[ i ][ 3 ]

        kpix_nuevo = math.cos( anguloRadianes ) * kpix + math.sin( anguloRadianes ) * kpiz 
        kpiy_nuevo = kpiy
        kpiz_nuevo = - math.sin( anguloRadianes ) * kpix + math.cos( anguloRadianes ) * kpiz 
        kpiv_nuevo = kpiv

        pose_nueva = np.append( pose_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ), float( kpiv_nuevo ) ] ], axis = 0 )

    return pose_nueva  


def rotacion_sobre_ejeY_cara( cara, anguloEnGrados = 180 ) :

    anguloRadianes = anguloEnGrados * 2 * math.pi / 360 
    
    cara_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 468 ) :

        kpix = cara[ i ][ 0 ]
        kpiy = cara[ i ][ 1 ]
        kpiz = cara[ i ][ 2 ]

        kpix_nuevo = math.cos(anguloRadianes) * kpix + math.sin(anguloRadianes) * kpiz 
        kpiy_nuevo = kpiy
        kpiz_nuevo = - math.sin(anguloRadianes) * kpix + math.cos(anguloRadianes) * kpiz 

        cara_nueva = np.append( cara_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ) ] ], axis = 0 )

    return cara_nueva  



def reflejar_sobre_planoX( mano ) :

    mano_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 21 ) :

        kpix = mano[ i ][ 0 ]
        kpiy = mano[ i ][ 1 ]
        kpiz = mano[ i ][ 2 ]

        kpix_nuevo = -kpix
        kpiy_nuevo = kpiy
        kpiz_nuevo = kpiz

        mano_nueva = np.append( mano_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ) ] ], axis = 0 )

    return mano_nueva  


def isPalmaAlFrente( mano ) :
    
    contadorDedosAlFrente = 0
    kp1z = mano[ 1 ][ 2 ]
    kp4z = mano[ 4 ][ 2 ]
    kp5z = mano[ 5 ][ 2 ]
    kp8z = mano[ 8 ][ 2 ]
    kp9z = mano[ 9 ][ 2 ]
    kp12z = mano[ 12 ][ 2 ]
    kp13z = mano[ 13 ][ 2 ]
    kp16z = mano[ 16 ][ 2 ]
    kp17z = mano[ 17 ][ 2 ]
    kp20z = mano[ 20 ][ 2 ]

    if kp4z > kp1z :
        contadorDedosAlFrente += 1

    if kp8z > kp5z :
        contadorDedosAlFrente += 1

    if kp12z > kp9z :
        contadorDedosAlFrente += 1

    if kp16z > kp13z :
        contadorDedosAlFrente += 1

    if kp20z > kp17z :
        contadorDedosAlFrente += 1

    if contadorDedosAlFrente >= 3 :
        return True
    return False

# Detectar si el pecho esta para el frente viedo la posicion de las manos
def isPechoAlFrente( pose ) :
    
    contadorManosAlFrente = 0
    kp19z = pose[ 19 ][ 2 ]
    kp13z = pose[ 13 ][ 2 ]
    kp11z = pose[ 11 ][ 2 ]
    kp20z = pose[ 20 ][ 2 ]
    kp14z = pose[ 14 ][ 2 ]
    kp12z = pose[ 12 ][ 2 ]

    if kp19z > kp13z :
        contadorManosAlFrente += 1

    if kp19z > kp11z :
        contadorManosAlFrente += 1

    if kp20z > kp14z :
        contadorManosAlFrente += 1

    if kp20z > kp12z :
        contadorManosAlFrente += 1

    if contadorManosAlFrente >= 2 :
        return True
    return False

def isNarizAlFrente( cara ) :
    
    contadorDeKeypointsAlFrente = 0
    kp1z = cara[ 1 ][ 2 ]  # ESta es la punta de la nariz
    kp164z = cara[ 164 ][ 2 ]  # Justo abajo de la nariz

    kp280z = cara[ 280 ][ 2 ]  # Un cachete
    kp454z = cara[ 454 ][ 2 ]  # Borde de la cara

    kp50z = cara[ 50 ][ 2 ]  # El otro cachete
    kp234z = cara[ 234 ][ 2 ]  # El otro borde de la cara

    kp9z = cara[ 9 ][ 2 ]  # Centro de la frente
    kp10z = cara[ 10 ][ 2 ]  # arriba de la frente

    kp200z = cara[ 200 ][ 2 ]  # Centro del mentón
    kp152z = cara[ 152 ][ 2 ]  # Abajo del mentón

    if kp1z > kp164z :
        contadorDeKeypointsAlFrente += 1

    if kp280z > kp454z :
        contadorDeKeypointsAlFrente += 1

    if kp50z > kp234z :
        contadorDeKeypointsAlFrente += 1

    if kp9z > kp10z :
        contadorDeKeypointsAlFrente += 1

    if kp200z > kp152z :
        contadorDeKeypointsAlFrente += 1

    if contadorDeKeypointsAlFrente >= 3 :
        return True
    return False    

def isManoDerecha( mano ) :

    kp17x = mano[ 17 ][ 0 ]
    kp5x = mano[ 5 ][ 0 ]

    if kp5x > kp17x :
        return True
    return False

def escalado( mano, magnitudMetacarpoGrande = 100, salida_int = True ) :

    kp9y = mano[ 9 ][ 1 ]

    if salida_int == True :
        mano_nueva = np.zeros( ( 0, 3 ), dtype = int )
    else :
        mano_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 21 ) :

        kpix = mano[ i ][ 0 ]
        kpiy = mano[ i ][ 1 ]
        kpiz = mano[ i ][ 2 ]

        kpix_nuevo = float( magnitudMetacarpoGrande ) / float( kp9y ) * float( kpix ) 
        kpiy_nuevo = float( magnitudMetacarpoGrande ) / float( kp9y ) * float( kpiy )
        kpiz_nuevo = float( magnitudMetacarpoGrande ) / float( kp9y ) * float( kpiz )

        if salida_int == True :
            mano_nueva = np.append( mano_nueva, [ [ int( kpix_nuevo ), int( kpiy_nuevo ),
                                                    int( kpiz_nuevo ) ] ], axis = 0 )
        else : 
            mano_nueva = np.append( mano_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                    float( kpiz_nuevo ) ] ], axis = 0 )

    return mano_nueva  


# Escala todo llevando a 100 la longitud entre los hombros
def escalado_pose( pose, magnitudEntreHombros = 100, salida_int = True ) :

    kp12y = pose[ 12 ][ 1 ]

    if salida_int == True :
        pose_nueva = np.zeros( ( 0, 4 ), dtype = int )
    else :
        pose_nueva = np.zeros( ( 0, 4 ), dtype = float )

    for i in range( 0, 33 ) :

        kpix = pose[ i ][ 0 ]
        kpiy = pose[ i ][ 1 ]
        kpiz = pose[ i ][ 2 ]
        kpiv = pose[ i ][ 3 ]

        kpix_nuevo = float( magnitudEntreHombros ) / float( kp12y ) * float( kpix ) 
        kpiy_nuevo = float( magnitudEntreHombros ) / float( kp12y ) * float( kpiy )
        kpiz_nuevo = float( magnitudEntreHombros ) / float( kp12y ) * float( kpiz )
        kpiv_nuevo = kpiv

        if salida_int == True :
            # Notar que a la visibilidad la pasamos a porcentaje y al convertir en int se truncan los decimales
            pose_nueva = np.append( pose_nueva, [ [ int( kpix_nuevo ), int( kpiy_nuevo ),
                                                    int( kpiz_nuevo ), int( kpiv_nuevo * 100 ) ] ], axis = 0 )
        else : 
            pose_nueva = np.append( pose_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                    float( kpiz_nuevo ), float( kpiv_nuevo ) ] ], axis = 0 )

    return pose_nueva  


def escalado_cara( cara, magnitudMentonFrente = 100, salida_int = True ) :

    kp_frente_y = cara[ 10 ][ 1 ]

    if salida_int == True :
        cara_nueva = np.zeros( ( 0, 3 ), dtype = int )
    else :
        cara_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 468 ) :

        kpix = cara[ i ][ 0 ]
        kpiy = cara[ i ][ 1 ]
        kpiz = cara[ i ][ 2 ]

        kpix_nuevo = float( magnitudMentonFrente ) / float( kp_frente_y ) * float( kpix ) 
        kpiy_nuevo = float( magnitudMentonFrente ) / float( kp_frente_y ) * float( kpiy )
        kpiz_nuevo = float( magnitudMentonFrente ) / float( kp_frente_y ) * float( kpiz )

        if salida_int == True :
            cara_nueva = np.append( cara_nueva, [ [ int( kpix_nuevo ), int( kpiy_nuevo ),
                                                    int( kpiz_nuevo ) ] ], axis = 0 )
        else : 
            cara_nueva = np.append( cara_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                    float( kpiz_nuevo ) ] ], axis = 0 )

    return cara_nueva  


def escalado_en_z( mano, multiplicador = 100 ) :

    mano_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 21 ) :

        kpix = mano[ i ][ 0 ]
        kpiy = mano[ i ][ 1 ]
        kpiz = mano[ i ][ 2 ]

        kpix_nuevo = kpix 
        kpiy_nuevo = kpiy 
        kpiz_nuevo = float( multiplicador ) * float( kpiz )

        mano_nueva = np.append( mano_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ) ] ], axis = 0 )

    return mano_nueva  

def traslacion( mano ) :

    kp0x = mano[ 0 ][ 0 ]
    kp0y = mano[ 0 ][ 1 ]
    kp0z = mano[ 0 ][ 2 ]

    mano_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 21 ) :

        kpix = mano[ i ][ 0 ]
        kpiy = mano[ i ][ 1 ]
        kpiz = mano[ i ][ 2 ]

        kpix_nuevo = kpix - kp0x
        kpiy_nuevo = kpiy - kp0y
        kpiz_nuevo = kpiz - kp0z

        mano_nueva = np.append( mano_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ) ] ], axis = 0 )

    return mano_nueva  

# Lleva el kp11 (hombro derecho) hacia el origen
def traslacion_pose( pose ) :

    kp11x = pose[ 11 ][ 0 ]
    kp11y = pose[ 11 ][ 1 ]
    kp11z = pose[ 11 ][ 2 ]
    kp11v = pose[ 11 ][ 3 ]

    pose_nueva = np.zeros( ( 0, 4 ), dtype = float )

    for i in range( 0, 33 ) :

        kpix = pose[ i ][ 0 ]
        kpiy = pose[ i ][ 1 ]
        kpiz = pose[ i ][ 2 ]
        kpiv = pose[ i ][ 3 ]

        kpix_nuevo = kpix - kp11x
        kpiy_nuevo = kpiy - kp11y
        kpiz_nuevo = kpiz - kp11z
        kpiv_nuevo = kpiv

        pose_nueva = np.append( pose_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ), float( kpiv_nuevo ) ] ], axis = 0 )

    return pose_nueva  


# Traslada al (0,0,0) e. kp del mentón (keypoint 152)
def traslacion_cara( cara ) :

    kp_chin_x = cara[ 152 ][ 0 ]
    kp_chin_y = cara[ 152 ][ 1 ]
    kp_chin_z = cara[ 152 ][ 2 ]

    cara_nueva = np.zeros( ( 0, 3 ), dtype = float )

    for i in range( 0, 468 ) :

        kpix = cara[ i ][ 0 ]
        kpiy = cara[ i ][ 1 ]
        kpiz = cara[ i ][ 2 ]

        kpix_nuevo = kpix - kp_chin_x
        kpiy_nuevo = kpiy - kp_chin_y
        kpiz_nuevo = kpiz - kp_chin_z

        cara_nueva = np.append( cara_nueva, [ [ float( kpix_nuevo ), float( kpiy_nuevo ),
                                                float( kpiz_nuevo ) ] ], axis = 0 )

    return cara_nueva  


def crearTensor( mano ) :

    tensor = tf.constant( [ [ [ mano[ 0 ][ 0 ], 
                                mano[ 0 ][ 1 ],
                                mano[ 0 ][ 2 ] ],
                              [ mano[ 1 ][ 0 ], 
                                mano[ 1 ][ 1 ],
                                mano[ 1 ][ 2 ] ],
                              [ mano[ 2 ][ 0 ], 
                                mano[ 2 ][ 1 ],
                                mano[ 2 ][ 2 ] ],
                              [ mano[ 3 ][ 0 ], 
                                mano[ 3 ][ 1 ],
                                mano[ 3 ][ 2 ] ],
                              [ mano[ 4 ][ 0 ], 
                                mano[ 4 ][ 1 ],
                                mano[ 4 ][ 2 ] ],
                              [ mano[ 5 ][ 0 ], 
                                mano[ 5 ][ 1 ],
                                mano[ 5 ][ 2 ] ],
                              [ mano[ 6 ][ 0 ], 
                                mano[ 6 ][ 1 ],
                                mano[ 6 ][ 2 ] ],
                              [ mano[ 7 ][ 0 ], 
                                mano[ 7 ][ 1 ],
                                mano[ 7 ][ 2 ] ],
                              [ mano[ 8 ][ 0 ], 
                                mano[ 8 ][ 1 ],
                                mano[ 8 ][ 2 ] ],
                              [ mano[ 9 ][ 0 ], 
                                mano[ 9 ][ 1 ],
                                mano[ 9 ][ 2 ] ],
                              [ mano[ 10 ][ 0 ], 
                                mano[ 10 ][ 1 ],
                                mano[ 10 ][ 2 ] ],
                              [ mano[ 11 ][ 0 ], 
                                mano[ 11 ][ 1 ],
                                mano[ 11 ][ 2 ] ],
                              [ mano[ 12 ][ 0 ], 
                                mano[ 12 ][ 1 ],
                                mano[ 12 ][ 2 ] ],
                              [ mano[ 13 ][ 0 ], 
                                mano[ 13 ][ 1 ],
                                mano[ 13 ][ 2 ] ],
                              [ mano[ 14 ][ 0 ], 
                                mano[ 14 ][ 1 ],
                                mano[ 14 ][ 2 ] ],
                              [ mano[ 15 ][ 0 ], 
                                mano[ 15 ][ 1 ],
                                mano[ 15 ][ 2 ] ],
                              [ mano[ 16 ][ 0 ], 
                                mano[ 16 ][ 1 ],
                                mano[ 16 ][ 2 ] ],
                              [ mano[ 17 ][ 0 ], 
                                mano[ 17 ][ 1 ],
                                mano[ 17 ][ 2 ] ],
                              [ mano[ 18 ][ 0 ], 
                                mano[ 18 ][ 1 ],
                                mano[ 18 ][ 2 ] ],
                              [ mano[ 19 ][ 0 ], 
                                mano[ 19 ][ 1 ],
                                mano[ 19 ][ 2 ] ],
                              [ mano[ 20 ][ 0 ], 
                                mano[ 20 ][ 1 ],
                                mano[ 20 ][ 2 ] ]
                            ] ], dtype = tf.float64 )

    return tensor


def crearTensor_pose( pose ) :

    cuerpo_para_tensor = []

    for i in range( 33 ) :
        cuerpo_para_tensor.append( [ pose[ i ][ 0 ], pose[ i ][ 1 ], pose[ i ][ 2 ], pose[ i ][ 3 ] ] )

    cuerpo_para_tensor_listo = []
    cuerpo_para_tensor_listo.append( cuerpo_para_tensor )    

    tensor = tf.constant( cuerpo_para_tensor_listo, dtype = tf.float64 )

    return tensor


def crearTensor_cara( cara ) :

    cara_para_tensor = []

    for i in range( 468 ) :
        cara_para_tensor.append( [ cara[ i ][ 0 ], cara[ i ][ 1 ], cara[ i ][ 2 ] ] )

    cara_para_tensor_listo = []
    cara_para_tensor_listo.append( cara_para_tensor )    

    tensor = tf.constant( cara_para_tensor_listo, dtype = tf.float64 )

    return tensor



    
# Inserta al final de 'x' el dato 'y' y va desplazando hacia delante
# x=[ 0 0 0 3 5 ]   inserta_y_desplaza( x, [ 6 ] )       -> x=[ 0 0 3 5 6 ]
# x=[ 0 0 3 5 6 ]   inserta_y_desplaza( x, [ 6 5 ] )     -> x=[ 3 5 6 6 5 ]
# x=[ 3 5 6 6 5 ]   inserta_y_desplaza( x, [ 2 ] )       -> x=[ 5 6 6 5 2 ]
def inserta_y_desplaza( x, y ) :
    push_len = len( y )
    assert len( x ) >= push_len
    x[ : - push_len ] = x[ push_len : ]
    x[ - push_len : ] = y
    return x