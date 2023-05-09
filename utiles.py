
teclas = { 
            0: '{ESC}', 
            1: '|', 
            2: '1', 
            3: '2', 
            4: '3', 
            5: '4', 
            6: '5', 
            7: '6', 
            8: '7', 
            9: '8', 
            10: '9', 
            11: '0', 
            12: "'", 
            13: '¿', 
            14: '{BACKSPACE}', 
            15: '{TAB}', 
            16: 'q', 
            17: 'w', 
            18: 'e', 
            19: 'r', 
            20: 't', 
            21: 'y', 
            22: 'u', 
            23: 'i', 
            24: 'o', 
            25: 'p', 
            26: '´', 
            27: '{VK_ADD}', 
            28: '{ENTER}', 
            29: '{CAPSLOCK}', 
            30: 'a', 
            31: 's', 
            32: 'd', 
            33: 'f', 
            34: 'g', 
            35: 'h', 
            36: 'j', 
            37: 'k', 
            38: 'l', 
            39: 'ñ', 
            40: '{', 
            41: '}', 
            42: '', 
            43: '{VK_LSHIFT}', 
            44: '<', 
            45: 'z', 
            46: 'x', 
            47: 'c', 
            48: 'v', 
            49: 'b', 
            50: 'n', 
            51: 'm', 
            52: ',', 
            53: '.', 
            54: '-', 
            55: '{UP}', 
            56: '{VK_RSHIFT}', 
            57: '{DEL}', 
            58: '{VK_LCONTROL}', 
            59: 'fn', 
            60: '{VK_LWIN}', 
            61: 'alt', 
            62: '{SPACE}', 
            63: 'alt', 
            64: '{VK_RCONTROL}', 
            65: '{LEFT}', 
            66: '{DOWN}', 
            67: '{RIGHT}', 
            68: 'option' 
         }
       

# Seteos que se ven muy bien, son los siguientes:

# Para la oficina de Investigación en Pascal (cámara laptop Toshiba)
####################################################################
# CAP_PROP_FRAME_WIDTH :  640.0
# CAP_PROP_FRAME_HEIGHT :  480.0
# CAP_PROP_BRIGHTNESS :  47.0
# CAP_PROP_CONTRAST :  37.0
# CAP_PROP_SATURATION :  36.0
# CAP_PROP_HUE :  0.0
# CAP_PROP_AUTO_WB :  0.0
# CAP_PROP_GAMMA :  10.0
# CAP_PROP_WB_TEMPERATURE :  3470.0
# CAP_PROP_SHARPNESS :  20.0
# CAP_PROP_BACKLIGHT :  1.0
# CAP_PROP_AUTO_EXPOSURE :  -1.0
# CAP_PROP_TEMPERATURE :  3470.0
# CAP_PROP_GAIN :  -1.0
# CAP_PROP_EXPOSURE :  -1.0
# CAP_PROP_GAMMA :  10.0
# CAP_PROP_TEMPERATURE :  3470.0
# CAP_PROP_BACKLIGHT :  1.0
# CAP_PROP_BUFFERSIZE :  4.0
# CAP_PROP_BACKEND :  200.0

propiedades_de_la_camara = \
    [ "CAP_PROP_FRAME_WIDTH",  # Width of the frames in the video stream.
      "CAP_PROP_FRAME_HEIGHT", # Height of the frames in the video stream.
      "CAP_PROP_BRIGHTNESS",   # Brightness of the image (only for cameras).
      "CAP_PROP_CONTRAST",     # Contrast of the image (only for cameras).
      "CAP_PROP_SATURATION",   # Saturation of the image (only for cameras).
      "CAP_PROP_HUE",
      "CAP_PROP_AUTO_WB",      # Auto White Balance. Si no está automático, se habilita CAP_PROP_WB_TEMPERATURE
      "CAP_PROP_GAMMA",
      "CAP_PROP_WB_TEMPERATURE",
      "CAP_PROP_SHARPNESS",    # nitidez
      "CAP_PROP_BACKLIGHT",    # retroiluminación
      "CAP_PROP_AUTO_EXPOSURE",
      "CAP_PROP_TEMPERATURE",
      
      # "CAP_PROP_GAIN",         # Gain of the image (only for cameras).
      # "CAP_PROP_EXPOSURE",
      # "CAP_PROP_TEMPERATURE",
      # "CAP_PROP_BUFFERSIZE",
      # "CAP_PROP_BACKEND",
      # "CAP_PROP_POS_MSEC",
      # "CAP_PROP_POS_FRAMES",
      # "CAP_PROP_POS_AVI_RATIO",
      # "CAP_PROP_FPS",
      # "CAP_PROP_FOURCC",
      # "CAP_PROP_FRAME_COUNT",
      # "CAP_PROP_FORMAT",
      # "CAP_PROP_MODE",
      # "CAP_PROP_CONVERT_RGB",
      # "CAP_PROP_WHITE_BALANCE_BLUE_U",
      # "CAP_PROP_RECTIFICATION",
      # "CAP_PROP_MONOCHROME",
      # "CAP_PROP_TRIGGER",
      # "CAP_PROP_TRIGGER_DELAY",
      # "CAP_PROP_WHITE_BALANCE_RED_V",
      # "CAP_PROP_ZOOM",
      # "CAP_PROP_FOCUS",
      # "CAP_PROP_GUID",
      # "CAP_PROP_ISO_SPEED",
      # "CAP_PROP_BACKLIGHT",
      # "CAP_PROP_PAN",
      # "CAP_PROP_TILT",
      # "CAP_PROP_ROLL",
      # "CAP_PROP_IRIS",
      # "CAP_PROP_SETTINGS",
      # "CAP_PROP_BUFFERSIZE",
      # "CAP_PROP_AUTOFOCUS",
      # "CAP_PROP_SAR_NUM",
      # "CAP_PROP_SAR_DEN",
      # "CAP_PROP_BACKEND",
      # "CAP_PROP_CHANNEL",
      # "CAP_PROP_AUTO_WB",
      # "CAP_PROP_WB_TEMPERATURE",
      # "CAP_PROP_CODEC_PIXEL_FORMAT",
      # "CAP_PROP_BITRATE",
      # "CAP_PROP_ORIENTATION_META",
      # "CAP_PROP_ORIENTATION_AUTO" 
    ]



# # Que están en -1

# CAP_PROP_GAIN :  -1.0
# CAP_PROP_EXPOSURE :  -1.0
# CAP_PROP_AUTO_EXPOSURE :  -1.0
# CAP_PROP_POS_FRAMES :  -1.0
# CAP_PROP_POS_AVI_RATIO :  -1.0
# CAP_PROP_FRAME_COUNT :  -1.0
# CAP_PROP_GAIN :  -1.0
# CAP_PROP_EXPOSURE :  -1.0
# CAP_PROP_WHITE_BALANCE_BLUE_U :  -1.0
# CAP_PROP_RECTIFICATION :  -1.0
# CAP_PROP_MONOCHROME :  -1.0
# CAP_PROP_AUTO_EXPOSURE :  -1.0
# CAP_PROP_TRIGGER :  -1.0
# CAP_PROP_TRIGGER_DELAY :  -1.0
# CAP_PROP_WHITE_BALANCE_RED_V :  -1.0
# CAP_PROP_ZOOM :  -1.0
# CAP_PROP_FOCUS :  -1.0
# CAP_PROP_GUID :  -1.0
# CAP_PROP_ISO_SPEED :  -1.0
# CAP_PROP_PAN :  -1.0
# CAP_PROP_TILT :  -1.0
# CAP_PROP_ROLL :  -1.0
# CAP_PROP_IRIS :  -1.0
# CAP_PROP_SETTINGS :  -1.0
# CAP_PROP_AUTOFOCUS :  -1.0
# CAP_PROP_SAR_NUM :  -1.0
# CAP_PROP_SAR_DEN :  -1.0
# CAP_PROP_CHANNEL :  -1.0
# CAP_PROP_CODEC_PIXEL_FORMAT :  -1.0
# CAP_PROP_BITRATE :  -1.0
# CAP_PROP_ORIENTATION_META :  -1.0
# CAP_PROP_ORIENTATION_AUTO :  -1.0                        


# # Que cambiaron

# CAP_PROP_BRIGHTNESS :  64.0
# CAP_PROP_CONTRAST :  35.0
# CAP_PROP_SATURATION :  42.0

# CAP_PROP_BRIGHTNESS :  60.0
# CAP_PROP_CONTRAST :  20.0
# CAP_PROP_SATURATION :  20.0

# # Que tienen calores distintos a -1

# CAP_PROP_FRAME_WIDTH :  640.0
# CAP_PROP_FRAME_HEIGHT :  480.0
# CAP_PROP_POS_MSEC :  0.0
# CAP_PROP_CONVERT_RGB :  1.0
# CAP_PROP_HUE :  0.0
# CAP_PROP_FPS :  30.0
# CAP_PROP_FOURCC :  1448695129.0
# CAP_PROP_FORMAT :  16.0
# CAP_PROP_MODE :  0.0                        
# CAP_PROP_SHARPNESS :  20.0
# CAP_PROP_GAMMA :  8.0
# CAP_PROP_TEMPERATURE :  3130.0
# CAP_PROP_BACKLIGHT :  0.0
# CAP_PROP_BUFFERSIZE :  4.0
# CAP_PROP_BACKEND :  200.0
# CAP_PROP_AUTO_WB :  0.0
# CAP_PROP_WB_TEMPERATURE :  3130.0

# CAP_PROP_FRAME_WIDTH :  640.0
# CAP_PROP_FRAME_HEIGHT :  480.0
# CAP_PROP_POS_MSEC :  0.0
# CAP_PROP_CONVERT_RGB :  1.0
# CAP_PROP_HUE :  0.0
# CAP_PROP_FPS :  30.0
# CAP_PROP_FOURCC :  1448695129.0
# CAP_PROP_FORMAT :  16.0
# CAP_PROP_MODE :  0.0
# CAP_PROP_SHARPNESS :  20.0
# CAP_PROP_GAMMA :  8.0
# CAP_PROP_TEMPERATURE :  3130.0
# CAP_PROP_BACKLIGHT :  0.0
# CAP_PROP_BUFFERSIZE :  4.0
# CAP_PROP_BACKEND :  200.0
# CAP_PROP_AUTO_WB :  0.0
# CAP_PROP_WB_TEMPERATURE :  3130.0

