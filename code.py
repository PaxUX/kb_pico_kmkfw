print("Starting-PAXUXv4")
#
# A split keyboard using a 2 Pico over a jack connector
# using NeoPixel LED strip of 3 LED as Status RGB LED Strip WS2812B 
# the design is a 6x5 for each
#
#  Logical			Physical
# X X X X X X     X X X X X X
# X X X X X X	  X X X X X X
# X X X X X X	  X X X X X X
# X X X X X X	X X X X X X X
# X X X X X X			X X X
#						 X X
#
#   Reversed for the Right side
#
# Docs for Split KB setup
# https://github.com/KMKfw/kmk_firmware/blob/master/docs/en/split_keyboards.md
#
import board
import gc
#import time

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC, make_key
from kmk.scanners import DiodeOrientation

#used by the Self.Matrix Next 2 lines can be removed
from kmk.scanners.keypad import MatrixScanner
from kmk.handlers.sequences import simple_key_sequence

#enable Irish type keys
#from kmk.extensions.international import International
from kmk.handlers.sequences import send_string
from kmk.modules.tapdance import TapDance
from kmk.modules.layers import Layers
from kmk.extensions.lock_status import LockStatus
from kmk.modules.mouse_keys import MouseKeys
#from kmk.modules.dynamic_sequences import DynamicSequences
from kmk.extensions.RGB import RGB

locks = LockStatus()
#See which side of the keyboard
#from kb import data_pin
from kmk.modules.split import Split, SplitSide
from storage import getmount
side = SplitSide.RIGHT if str(getmount('/').label)[-1] == 'R' else SplitSide.LEFT

#lockneoled is an empty module that processes on every after_matrix_scan (main loop)
#it does a call back to a method passed in when init and is
#used to manage caps/num lock status LEDs/RGB on/off
#from lockneoled import lockneoled
class lockneoled:
    def __init__(self, sFun):
        self.SetLight = sFun
    def after_matrix_scan(self, keyboard):
        #Just do callback
        self.SetLight()
        pass
    def process_key(self, keyboard, key, is_pressed, int_coord):
        return key    
    def during_bootup(self, keyboard):
        return
    def after_hid_send(self, keyboard):
        return
    def before_hid_send(self, keyboard):
        return
    def before_matrix_scan(self, keyboard):
        return

#Nomral Single
keyboard = KMKKeyboard()
#keyboard.debug_enabled = True


#Split Keyboard
if side == SplitSide.RIGHT:
  keyboard.col_pins = (board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7)
  keyboard.row_pins = (board.GP17, board.GP18, board.GP19, board.GP20, board.GP21)
  keyboard.diode_orientation = DiodeOrientation.ROW2COL
else:
  keyboard.col_pins = (board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7)
  keyboard.row_pins = (board.GP17, board.GP18, board.GP19, board.GP20, board.GP21)
  keyboard.diode_orientation = DiodeOrientation.ROW2COL

# R
# Wired Split Keyboard then add to Modules
#split = Split(data_pin=board.GP0, data_pin2=board.GP1, use_pio=True, uart_flip = True) not this one...
#split = Split(use_pio=True, uart_flip = True, data_pin=board.GP1) #this line is the one that works
split = Split(uart_interval=20, split_flip=False, use_pio=False, uart_flip = True, data_pin=board.GP1) #this line is the one that works
keyboard.modules.append(split)

keyboard.modules.append(Layers())
#international
#keyboard.extensions.append(International())

tmpMouse = MouseKeys()
tmpMouse.def_move_step = 1
tmpMouse.max_speed = 3
tmpMouse.ac_interval = 2500
keyboard.modules.append(tmpMouse)

#Tap Dance
tapdance = TapDance()
tapdance.tap_time = 170
keyboard.modules.append(tapdance)
#Caps Lock Status
keyboard.extensions.append(locks)
###Below is scan checking
###Below is scan checking
###Below is scan checking
# N = len(keyboard.col_pins) * len(keyboard.row_pins) * 2
# #
# keyboard.coord_mapping = list(range(N))
# #
# layer = []
# #
# for i in range(N):
#    c, r = divmod(i, 100)
#    d, u = divmod(r, 10)
#    layer.append(
#        simple_key_sequence(
#            (
#                getattr(KC, 'N' + str(c)),
#                getattr(KC, 'N' + str(d)),
#                getattr(KC, 'N' + str(u)),
#                KC.COMMA,
#                KC.SPC,
#            )
#        )
#    )
# keyboard.keymap = [layer]
# #
# print(str(getmount('/').label)[-1], "In Scan Mode")
# #
# if __name__ == '__main__':
#    keyboard.go()
###Below is scan checking
###Below is scan checking
###Below is scan checking


#       ####### ######           #####
#       #       #     #         #     #  ######   #####  #    #  #####
#       #       #     #         #        #          #    #    #  #    #
#       #####   #     #          #####   #####      #    #    #  #    #
#       #       #     #               #  #          #    #    #  #####
#       #       #     #         #     #  #          #    #    #  #
####### ####### ######           #####   ######     #     ####   #
#Setup the total number of LEDs 
vNumLEDs = 3
#create the NeoLED object that will control our lights
rgb = RGB(pixel_pin=board.GP22, num_pixels=vNumLEDs, val_limit=100, hue_default=0, sat_default=0, val_default=0)
#   testing the lights  -- we have everything required to test...
# rgb.set_rgb((100, 100, 100), 0)
# rgb.set_rgb((100, 100, 100), 1)
# print("Lightes on")
# time.sleep(10)
# print("Lightes off")

#Setup variable to manage RGB for 3 lights
# simple bit fliping kind of thing here but using R G B as our bits
# each color is its own light, limit is 3 keys per LED as RGB
# this setup has a total of 6 independent lights with our 3 Neo Pixel LEDs
#       R G B   R G B   R G B
vRGB = [0,0,0],[0,0,0],[0,0,0]
vR, vG, vB = 0, 1, 2
vBrightness = 50  # Code below will double this value / do not set over 100 without changing code below
vLockBrightness = 5  # Used by Lock Status LEDs might be always on, so I dont want it bright
#Setup which (of the 3) LEDs to use by each Lock
NumLockLED = 2
CapLockLED = 1
#On Keyboard boot set Locks to the following States, doing this to make sure Numlock is enable as we need numkeys activated for layer later
vCAPinitStat = False
vNUMinitStat = True
#Track Lock changes used during the DoLOCKChk() which is a call back function used by lockneoled module
vCAPLockStat = False
vNUMLockStat = False
#Assigning 2 colors to Caps/Num locks
# L0 vB -- This is Caps Lock used by lockneoled.py
# L1 vG -- This is Num Lock used by lockneoled.py
# Seems to take about 4-8 loops before the keyboard's backend reads the Num Lock correctly???
StupidLoop = 1
WaitCount = 20
StopStupid = False
def DoLOCKChk():
    #Get the variables we need
    global keyboard
    global vCAPLockStat, vNUMLockStat, NumLockLED, CapLockLED, vCAPinitStat, vNUMinitStat
    global StupidLoop, StopStupid, WaitCount

    # When True will do a Set_RGB to update NeoPixels
    lStatChg = False
    
    #Flip Num Lock twice to get it back to where it was on boot.
    #get_num_lock() doesn't work till the key is used at least once, based off my testing
    #This is a dumb workaround as I can't see a better way
    if StupidLoop == 1:
        #Cycle key to activate Get Status function
        keyboard.tap_key(KC.NUMLOCK)
        keyboard.tap_key(KC.NUMLOCK)
        
    #Keyboard should be ready, just check that get_num_lock() is returning correct setup
    #if it doesn't keep looping till it does, this could create an infinit loop, there is catch later
    if StupidLoop != 0:   # use this IF to turn off the rest of the IFs later
        #Loop till KMK confirms the Num Lock is enabled as it should be
        if StupidLoop > WaitCount + 10:
            StupidLoop += 1
            print(StupidLoop, locks.get_num_lock(), locks.get_caps_lock() )
            if locks.get_num_lock() == vNUMinitStat:
                StupidLoop = 0

        #Stop the Stupid loop from go to infinity and beyond, this is soooo stupid, get_num_lock should just work right
        elif StupidLoop > (WaitCount * 2):
             StupidLoop = 0
    
        #A stupid wait loop, giving the keyboard time to initialis
        #Try to wait till the keyboard is reading locks correctly
        if StopStupid == False:
            StupidLoop += 1
            #Takes a couple of loops for keyboard to warmup and work right on get lock checks
            if StupidLoop > WaitCount:
                print("Stupid loop done")
                print("1. NumLock:", locks.get_num_lock() )
                print("1. CapsLock:", locks.get_caps_lock() )
                lStatChg = True  #refresh lights
                #set the defaults configured above
                if locks.get_num_lock() != vNUMinitStat:
                    keyboard.tap_key(KC.NUMLOCK)
                if locks.get_caps_lock() != vCAPinitStat:   
                    keyboard.tap_key(KC.CAPSLOCK)
                #Now enable Status tracking, Lights should be right
                vNUMLockStat = locks.get_num_lock()
                vCAPLockStat = locks.get_caps_lock()
                #Trigger another damn loop to wait for the above keyboard.tap_key to process, it takes a couple of loops
                StupidLoop = WaitCount + 3
                #This Stupid loop is done, don't need to rerun the init
                StopStupid = True
        #end StopStupid == False
     #end if StupidLoop > 0       

#Now to what should be the only code required in this function
#When the status of a lock changes update the NeoPixel
#Turn on/off the configured Neopixel of each of the two lock keys
    if locks.get_caps_lock() == False and vCAPLockStat == True:	# L0 vB
        lStatChg = True
        vCAPLockStat = False
        vRGB[CapLockLED][vB] = 0
    if locks.get_caps_lock() == True and vCAPLockStat == False:	# L0 vB
        lStatChg = True
        vCAPLockStat = True
        vRGB[CapLockLED][vB] = vLockBrightness
    if locks.get_num_lock() == False and vNUMLockStat == True:	# L1 vG
        lStatChg = True
        vNUMLockStat = False
        vRGB[NumLockLED][vG] = 0
    if locks.get_num_lock() == True and vNUMLockStat == False:	# L1 vG
        lStatChg = True
        vNUMLockStat = True
        vRGB[NumLockLED][vG] = vLockBrightness
    #Update all LEDs, but only if something has changed
    if lStatChg == True:
        #print("state change")
        vI = 0
        while vI < vNumLEDs:
            rgb.set_rgb((vRGB[vI][vR], vRGB[vI][vG], vRGB[vI][vB]), vI)
            vI = vI + 1
#End of DoLOCKChk

#Init the above NeoPixel Lock management method 
LockLEDs = lockneoled(DoLOCKChk)
#add RGB management into the KMK stack
keyboard.extensions.append(rgb)
#The goal of all this is to allow another keyboard or App to enable the Cap/Num Lock it will change the NeoPixel 
#Default KMKfw doesn't support this out of the box for NeoPixels
#add this custom module for NeoPixel LED Cap/Num Lock lights into the KMK Stack so it gets called after_matrix_scan loop is processed
keyboard.modules.append(LockLEDs)

#This took a lot more code than it should!


#    #                           #####
#   #    ######   #   #         #     #  ######   #####  #    #  #####
#  #     #         # #          #        #          #    #    #  #    #
###      #####      #            #####   #####      #    #    #  #    #
#  #     #          #                 #  #          #    #    #  #####
#   #    #          #           #     #  #          #    #    #  #
#    #   ######     #            #####   ######     #     ####   #


#Function Layer1 + Tab dance into ALT Key
Layer1ALT = KC.TD(KC.MO(1), KC.LALT)
Layer2    = KC.MO(2)
#Layer2TD  = KC.TD(KC.MO(2), KC.MO(0))

# standard filler keys  
_______ = KC.TRNS   # Use Key on the layer below, think default as bottom layer
XXXXXXX = KC.NO		# No Action NOOP

#Build out a bunch of Multi combo keys into a single key to use in keyboard
# CTRL ALT Delete
CtAtDel = KC.LCTL( KC.LALT( KC.DEL ))
# CTRL SHIFT ESC
CtStEsc = KC.LCTL( KC.LSHIFT( KC.ESC ))
# Windows E - File Explorer
WinE = KC.LGUI(KC.E)
# ALT + Tab
ALTAB = KC.LALT( KC.TAB )
    
#setup CTRL + Arrow keys for word jumping
CTRLUP		= KC.LCTL(KC.UP)
CTRLDOWN	= KC.LCTL(KC.DOWN)
CTRLLEFT	= KC.LCTL(KC.LEFT)
CTRLRIGHT	= KC.LCTL(KC.RIGHT)
CTRLHOME	= KC.LCTL(KC.HOME)
CTRLEND		= KC.LCTL(KC.END)
#cutnpasta
LtShiftDEL = KC.LSHIFT( KC.DELETE )
LtShiftINS = KC.LSHIFT( KC.INS )

#At an extra mapping for @
EIDQ = KC.AT

#UNIX like alias, a single key prints a full string of text to active screen location, useful for cmds
#I've removed my commands
# CMDStr1 = send_string("--")
# CMDStr2 = send_string("--")
# CMDStr3 = send_string("--")
# CMDStr4 = send_string("--")
# CMDStr5 = send_string("--")


# Each key needs its own On/Off Function; The following is how I wanted to implament that
#Light 0
def SSon(key, keyboard, *args):  	# L0 vR
    vLightNum = 0
    vRGB[vLightNum][vR] = vBrightness 
    rgb.set_rgb((vRGB[vLightNum][vR], vRGB[vLightNum][vG], vRGB[vLightNum][vB]), vLightNum)  
    return True
def SSoff(key, keyboard, *args):	# L0 vR
    vLightNum = 0
    vRGB[vLightNum][vR] = 0 
    rgb.set_rgb((vRGB[vLightNum][vR], vRGB[vLightNum][vG], vRGB[vLightNum][vB]), vLightNum) 
    return True
#Below in Keyboard layout there are 2 CTRL, this code will just make the light brighter if two are press
#Both keys need to be unpress for the Value to reset to 0 and LED turn off
def CTRLon(key, keyboard, *args):	# L0 vG
    vLightNum = 0
    vRGB[vLightNum][vG] += vBrightness # this could code bring if goes over 256
    rgb.set_rgb((vRGB[vLightNum][vR], vRGB[vLightNum][vG], vRGB[vLightNum][vB]), vLightNum)
    return True
def CTRLoff(key, keyboard, *args):	# L0 vG
    vLightNum = 0
    vRGB[vLightNum][vG] -= vBrightness 
    rgb.set_rgb((vRGB[vLightNum][vR], vRGB[vLightNum][vG], vRGB[vLightNum][vB]), vLightNum)
    return True

# L0 vB -- This is Caps Lock used by lockneoled.py
# L0 vB -- This is Caps Lock used by lockneoled.py
# L0 vB -- This is Caps Lock used by lockneoled.py

#Light 1
def FNon(key, keyboard, *args):		# L1 vR
    vLightNum = 1
    vRGB[vLightNum][vR] = vBrightness 
    rgb.set_rgb((vRGB[vLightNum][vR], vRGB[vLightNum][vG], vRGB[vLightNum][vB]), vLightNum)
    return True
def FNoff(key, keyboard, *args):	# L1 vR
    vLightNum = 1
    vRGB[vLightNum][vR] = 0 
    rgb.set_rgb((vRGB[vLightNum][vR], vRGB[vLightNum][vG], vRGB[vLightNum][vB]), vLightNum)
    return True
def Lay1on(key, keyboard, *args):	# L1 vB
    vLightNum = 1
    vRGB[vLightNum][vB] = vBrightness 
    rgb.set_rgb((vRGB[vLightNum][vR], vRGB[vLightNum][vG], vRGB[vLightNum][vB]), vLightNum)  
    return True
def Lay1off(key, keyboard, *args):	# L1 vB
    vLightNum = 1
    vRGB[vLightNum][vB] = 0 
    rgb.set_rgb((vRGB[vLightNum][vR], vRGB[vLightNum][vG], vRGB[vLightNum][vB]), vLightNum)
    return True

# L1 vG -- This is Num Lock used by lockneoled.py
# L1 vG -- This is Num Lock used by lockneoled.py
# L1 vG -- This is Num Lock used by lockneoled.py

# Following will link the On/Off Functions to the right Key/action
KC.LSHIFT.before_press_handler(SSon) #call the key with the after_press_handler
KC.LSHIFT.after_release_handler(SSoff)
KC.LCTRL.before_release_handler(CTRLoff)
KC.LCTRL.after_press_handler(CTRLon)
# Layers share LED
Layer1ALT.before_press_handler(Lay1on)
Layer1ALT.after_release_handler(Lay1off)
Layer2.before_press_handler(FNon) #call the key with the after_press_handler
Layer2.after_release_handler(FNoff) #call the key with the after_press_handler


# Record keys to allow short multi key combo macro
from kmk.modules.dynamic_sequences import DynamicSequences
dynamicSequences = DynamicSequences(
    slots=1, 		# The number of sequence slots to use, only uses one in this setup... 0
    timeout=60000,  # milliseconds, auto stop recording
    key_interval=0, # Milliseconds between key events while playing
    use_recorded_speed=False  # Whether to play the sequence at the speed it was typed
)
#Allows recording of Macros keypress to replay later
keyboard.modules.append(dynamicSequences)

# How create your own key
# make_key(
#     names=('MACPLAY',),
#     on_press=lambda *args: onRecordPlay,
# )

#Creating Tab Dance key, Stop, Record, Play... Easier to read this way in TD code
make_key(
    names=('MACRECOD',),
    on_press=lambda *args: dynamicSequences._record_sequence(KC.RECORD_SEQUENCE(0), keyboard ),
)
make_key(
    names=('MACSTOP',),
    on_press=lambda *args: keyboard.tap_key(KC.STOP_SEQUENCE(0)) ,
)
#Record Macro
tdMACSTRC = KC.TD(KC.MACSTOP, KC.PLAY_SEQUENCE(), KC.MACRECOD, tap_time=350) 


#Latch onto the Scan and check if recording and light the LED
lastRecordStatus = 0
def RecordChkLED():
    global lastRecordStatus
   
    #Turn off LED
    if dynamicSequences.status == 0 and lastRecordStatus == 1:
        lastRecordStatus = 0
        vLightNum = 1
        vRGB[vLightNum][vB] = 0 
        rgb.set_rgb((vRGB[vLightNum][vR], vRGB[vLightNum][vG], vRGB[vLightNum][vB]), vLightNum)
    #Trun on LED
    if dynamicSequences.status == 1 and lastRecordStatus == 0:
        lastRecordStatus = 1
        vLightNum = 1
        vRGB[vLightNum][vB] = 50 
        rgb.set_rgb((vRGB[vLightNum][vR], vRGB[vLightNum][vG], vRGB[vLightNum][vB]), vLightNum)
    #print("InChkLED")        

#Skelaton Modual
class macroRecCheck:
    def __init__(self, ipvRGB):
        self.iSetRGB = ipvRGB
    def after_matrix_scan(self, keyboard):
        self.iSetRGB()
        pass
    def process_key(self, keyboard, key, is_pressed, int_coord):
        return key    
    def during_bootup(self, keyboard):
        return
    def after_hid_send(self, keyboard):
        return
    def before_hid_send(self, keyboard):
        return
    def before_matrix_scan(self, keyboard):
        return

#Link new Class to Extenstions
mRecMarco = macroRecCheck(RecordChkLED)
keyboard.modules.append(mRecMarco)


#    #
#   #    ######   #   #  #####    ####     ##    #####   #####
#  #     #         # #   #    #  #    #   #  #   #    #  #    #
###      #####      #    #####   #    #  #    #  #    #  #    #
#  #     #          #    #    #  #    #  ######  #####   #    #
#   #    #          #    #    #  #    #  #    #  #   #   #    #
#    #   ######     #    #####    ####   #    #  #    #  #####

#This maps the correct Board Keyread code to the keymap of the same location below in Keymap
#taken from the output of the Scan key code that is commented out above
keyboard.coord_mapping = [
#L								R
026, 029, 028, 027, 024, 025,  	054, 056, 058, 057, 055, 059,
020, 023, 022, 021, 018, 019, 	048, 050, 052, 051, 049, 053,
014, 017, 016, 015, 012, 013, 	042, 044, 046, 045, 043, 047,
002, 005, 004, 003, 000, 001, 	030, 032, 034, 033, 031, 035, 
008, 009, 006, 007, 011, 010, 	036, 038, 040, 039, 037, 041, 
]
    

# On thing to note is that the Enable Layer Keys are only available on the default keyboard, any layer shift disables layer keys
#Board 4
keyboard.keymap = [
    [   #LEFT																				RIGHT                                                                                                                                        
#       #1 COL 			2 COL6		3 COL 		4 COL 		5 COL 		6 COL 		<>		7 COL 			8 COL		9 COL		10 COL		11 COL		12 COL GP3 	
        KC.N1,			KC.N2,		KC.N3,		KC.N4,		KC.N5,		KC.N6,				KC.N7,			KC.N8,		KC.N9,		KC.N0,		KC.MINS,	KC.EQUAL,
        KC.Q,			KC.W,		KC.E,		KC.R,		KC.T,		KC.QUOTE,			KC.INS, 		KC.Y,		KC.U,		KC.I,		KC.O,		KC.P,		
        KC.A,			KC.S,		KC.D,		KC.F,		KC.G,		KC.LBRC,			KC.RBRC,		KC.H,		KC.J,		KC.K,		KC.L,		KC.SCLN,
        KC.Z,			KC.X,		KC.C,		KC.V,		KC.B,		KC.GRAVE,			KC.NUBS,		KC.N,		KC.M,		KC.COMM,	KC.DOT,		KC.SLASH,
#Thumbs
        KC.LSHIFT,		KC.TAB,		KC.BSPACE,	Layer1ALT,	KC.SPACE,	KC.LCTRL,	        Layer2,			KC.SPACE,	KC.LALT,	KC.LCTRL,	KC.LGUI,	KC.ENTER,		
     ], 

    # M1 Layer -- Left Fn
    [   #LEFT																				RIGHT
        #1 COL GP--		2 COL GP--	3 COL GP--	4 COL GP--	5 COL GP--	6 COL GP--	<>		7 COL GP--		8 COL GP--	 9 COL GP--	    10 COL GP--	11 COL GP--		12 COL GP--	
        KC.F1,			KC.F2,		KC.F3,		KC.F4,		KC.F5,		KC.F6,				KC.F7,			KC.F8,		 KC.F9,			KC.F10,		KC.F11,			KC.F12, 
        KC.PGUP,		KC.HOME,	KC.UP,		KC.END, 	ALTAB,		EIDQ,				XXXXXXX,		KC.NUMLOCK,	 KC.KP_7,		KC.KP_8,	KC.KP_9,		KC.DQUO, 
        KC.PGDN,		KC.LEFT,	KC.DOWN,	KC.RIGHT,	KC.ESC,		KC.LPRN,			KC.RPRN,		KC.CAPSLOCK, KC.KP_4,		KC.KP_5,	KC.KP_6, 		KC.RESET,
        WinE,			LtShiftDEL, LtShiftINS,	KC.DELETE,	KC.LGUI,	KC.ENTER,			XXXXXXX,		XXXXXXX,	 KC.KP_1,		KC.KP_2, 	KC.KP_3, 		KC.KP_0,
#Thumbs\
        _______,		_______,	KC.DELETE,	XXXXXXX,	_______,	_______,			XXXXXXX,		_______,    _______,    	_______,    _______,    _______, 
     ],#
   
    
    # M2 Layer -- Right Fn
    [   #LEFT																				RIGHT
        #1 COL GP--		2 COL GP--	3 COL GP--	4 COL GP--	5 COL GP--	6 COL GP--	<>		7 COL GP--		8 COL GP--	9 COL GP--	    10 COL GP--	11 COL GP--		12 COL GP--	
        KC.F1,			KC.F2,		KC.F3,		KC.F4,		KC.F5,		KC.F6,				KC.F7,		    KC.F8,		KC.F9,			KC.F10,		KC.F11,			KC.F12, 
        KC.PGUP,		KC.HOME,	KC.UP,		KC.END,		ALTAB,		EIDQ,				CtStEsc,		XXXXXXX,	KC.MB_LMB,		KC.MS_UP,	KC.MB_RMB,		KC.DQUO, 
        KC.PGDN,		KC.LEFT,	KC.DOWN,	KC.RIGHT,	KC.ESC,		XXXXXXX,			CtAtDel,	    KC.LPRN,	KC.MS_LEFT,		KC.MS_DOWN,	KC.MS_RIGHT, 	KC.RPRN,
        XXXXXXX,		XXXXXXX,    XXXXXXX,	XXXXXXX,	XXXXXXX,	tdMACSTRC,			XXXXXXX,		XXXXXXX,	KC.MW_UP,		KC.MB_MMB, 	KC.MW_DOWN, 	KC.NUBS,
#Thumbs
        _______,		_______,	KC.DELETE,	XXXXXXX,	_______,	_______,			XXXXXXX,		_______,    _______,    	_______,    _______,    _______, 
     ],#
]


print("Free Memory: ", gc.mem_free())

#this just does a quick flash to visualise keyboard ready
iiLoop = 0
while iiLoop < vNumLEDs:
    rgb.set_rgb((100, 100, 100), iiLoop)
    iiLoop += 1

#Show Keybaord is ready - console output only
print("Loaded")
# Run the Keyboard Software
if __name__ == '__main__':
    keyboard.go()
    
    

