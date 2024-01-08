#Console Debugging
print("Starting")
#https://github.com/KMKfw/kmk_firmware/tree/master/boards/lily58
#https://github.com/KMKfw/kmk_firmware/blob/master/boards/kyria/main.py
#https://github.com/KMKfw/kmk_firmware/blob/master/docs/en/split_keyboards.md
import board
import time

#boiler plate code to get KMKfw running
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
#used by the Self.Matrix used on initial build to get key placement codes
from kmk.scanners.keypad import MatrixScanner
from kmk.handlers.sequences import simple_key_sequence
#enable Irish type keys
from kmk.extensions.international import International
from kmk.handlers.sequences import send_string
from kmk.modules.tapdance import TapDance
from kmk.modules.layers import Layers
from kmk.extensions.lock_status import LockStatus
from kmk.modules.mouse_keys import MouseKeys
from kmk.extensions.RGB import RGB

#lockneoled is an empty module that processes on every after_matrix_scan (main loop)
#it does a call back to a method passed in when init and is
#used to manage caps/num lock status LEDs/RGB on/off
from lockneoled import lockneoled

#Create Keyboard base
keyboard = KMKKeyboard()
#keyboard.debug_enabled = True

#Keyboard v4 physical layout
keyboard.col_pins = (board.GP3 , board.GP2 , board.GP1 , board.GP0 , board.GP4 , board.GP5, #LEFT 
                     board.GP20, board.GP17, board.GP22, board.GP19, board.GP18, board.GP21) #RIGHT
keyboard.row_pins = (board.GP6 , board.GP7 , board.GP8 , board.GP9 , board.GP10, #LEFT
                     board.GP11, board.GP12, board.GP13, board.GP14, board.GP15) #RIGHT
keyboard.diode_orientation = DiodeOrientation.ROW2COL

# Above is the smallest amount of setup required to have a functioning keyboard, we can scan a key matrix if requried now

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
# print("Return Map Codes")
# #
# if __name__ == '__main__':
#    keyboard.go()
# ###Above is scan checking
# ###Above is scan checking
# ###Above is scan checking
# keyboard.coord_mapping = [  # V4 map
# #L								 R
# 000, 001, 002, 003, 004, 005,    078, 083, 079, 082, 080, 081, 
# 036, 037, 038, 039, 040, 041,    114, 119, 115, 118, 116, 117, 
# 012, 013, 014, 015, 016, 017,    066, 071, 067, 070, 068, 069, 
# 024, 025, 026, 027, 028, 029,    090, 095, 091, 094, 092, 093, 
# 048, 051, 052, 053, 049, 050,    102, 107, 103, 106, 104, 105,  
# ]

#back to adding modules required for the keyboard functionality

#Multi Layer Keyboard
keyboard.modules.append(Layers())

#international keys -- This never really worked right in my testing
keyboard.extensions.append(International())

#Mouse Keys
keyboard.modules.append(MouseKeys())

#Tap Dance - Double Tab to get a different key, this also slows down the initial press as it waits to see if a second press occurs
tapdance = TapDance()
tapdance.tap_time = 170
keyboard.modules.append(tapdance)

#Lock Status / caps, numlock, scroll lock, this module is cursed!
locks = LockStatus()
keyboard.extensions.append(locks)


#       ####### ######           #####
#       #       #     #         #     #  ######   #####  #    #  #####
#       #       #     #         #        #          #    #    #  #    #
#       #####   #     #          #####   #####      #    #    #  #    #
#       #       #     #               #  #          #    #    #  #####
#       #       #     #         #     #  #          #    #    #  #
####### ####### ######           #####   ######     #     ####   #

#Setup the total number of LEDs 
vNumLEDs = 2
#create the NeoLED object that will control our lights
rgb = RGB(pixel_pin=board.GP28, num_pixels=vNumLEDs, val_limit=100, hue_default=0, sat_default=0, val_default=0)
#   testing the lights  -- we have everything required to test...
# rgb.set_rgb((100, 100, 100), 0)
# rgb.set_rgb((100, 100, 100), 1)
# print("Lightes on")
# time.sleep(10)
# print("Lightes off")

#Setup variable to manage RGB for 2 lights
# simple bit fliping kind of thing here but using R G B as our bits
# each color is its own light, limit is 3 keys per LED as RGB
# this setup has a total of 6 independent lights with our 2 Neo Pixel LEDs
#       R G B   R G B
vRGB = [0,0,0],[0,0,0]
vR, vG, vB = 0, 1, 2
vBrightness = 50  # Code below will double this value / do not set over 100 without changing code below
vLockBrightness = 5  # Used by Lock Status LEDs might be always on, so I dont want it bright
#Setup which (of the 2) LEDs to use by each Lock
NumLockLED = 1
CapLockLED = 0
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
    #seems some require global to work correctly
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
        if StupidLoop > WaitCount + 2:
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

#Some of this was legacy when trynig to get International characters working
#Right >
RtGT = KC.LSHIFT( KC.DOT )
#Remap US to IE Keymappings
EIDQ = KC.AT

#UNIX like alias, a single key prints a full string of text to active screen location, useful for cmds
#I've removed my commands
CMDStr1 = send_string("--")
CMDStr2 = send_string("--")
CMDStr3 = send_string("--")
CMDStr4 = send_string("--")
CMDStr5 = send_string("--")

#Assign Capslock to another key variable
KAPLOCK = KC.CAPSLOCK
#This allows double tab SHIFT to enable CapsLock
#Didn't like this key flow so just removed the mapping, but left the key names in place
#CAPS = KC.TD(KC.LSHIFT, KAPLOCK)
CAPS = KC.LSHIFT

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

#Copy Default keys to new variables for LED linking
SSSS    = KC.LSHIFT   
LCTRLED = KC.LCTRL  
# Following will link the On/Off Functions to the right Key/action
SSSS.before_press_handler(SSon) #call the key with the after_press_handler
SSSS.after_release_handler(SSoff)
LCTRLED.before_release_handler(CTRLoff)
LCTRLED.after_press_handler(CTRLon)
# Layers share LED
Layer1ALT.before_press_handler(Lay1on)
Layer1ALT.after_release_handler(Lay1off)
Layer2.before_press_handler(FNon) #call the key with the after_press_handler
Layer2.after_release_handler(FNoff) #call the key with the after_press_handler


#    #
#   #    ######   #   #  #####    ####     ##    #####   #####
#  #     #         # #   #    #  #    #   #  #   #    #  #    #
###      #####      #    #####   #    #  #    #  #    #  #    #
#  #     #          #    #    #  #    #  ######  #####   #    #
#   #    #          #    #    #  #    #  #    #  #   #   #    #
#    #   ######     #    #####    ####   #    #  #    #  #####

#This maps the correct Board Keyread code to the keymap of the same location below in Keymap
keyboard.coord_mapping = [  # V4 map
#L								 R
000, 001, 002, 003, 004, 005,    078, 083, 079, 082, 080, 081, 
036, 037, 038, 039, 040, 041,    114, 119, 115, 118, 116, 117, 
012, 013, 014, 015, 016, 017,    066, 071, 067, 070, 068, 069, 
024, 025, 026, 027, 028, 029,    090, 095, 091, 094, 092, 093, 
048, 051, 052, 053, 049, 050,    102, 107, 103, 106, 104, 105,  
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
        CAPS,			KC.TAB,		KC.BSPACE,	KC.SPACE,	Layer1ALT,	LCTRLED,			Layer2,			KC.SPACE,	KC.LALT,	LCTRLED,	KC.LGUI,	KC.ENTER,		
     ], 

    # M1 Layer -- Left Fn
    [   #LEFT																				RIGHT
        #1 COL GP--		2 COL GP--	3 COL GP--	4 COL GP--	5 COL GP--	6 COL GP--	<>		7 COL GP--		8 COL GP--	9 COL GP--	    10 COL GP--	11 COL GP--		12 COL GP--	
        KC.F1,			KC.F2,		KC.F3,		KC.F4,		KC.F5,		KC.F6,				KC.F7,			KC.F8,		KC.F9,			KC.F10,		KC.F11,			KC.F12, 
        KC.PGUP,		CTRLHOME,	CTRLUP,		CTRLEND,	XXXXXXX,	EIDQ,				CMDStr1,		KC.NUMLOCK,	KC.KP_7,		KC.KP_8,	KC.KP_9,		XXXXXXX, 
        KC.PGDN,		CTRLLEFT,	CTRLDOWN,	CTRLRIGHT,	KC.ESC,		KC.LPRN,			KC.RPRN,		KAPLOCK,	KC.KP_4,		KC.KP_5,	KC.KP_6, 		XXXXXXX,
        WinE,			LtShiftDEL, LtShiftINS,	KC.DELETE,	KC.LGUI,	KC.ENTER,			CMDStr3,		CMDStr2,	KC.KP_1,		KC.KP_2, 	KC.KP_3, 		KC.KP_0,
#Thumbs
        _______,		_______,	KC.DELETE,	_______,	XXXXXXX,	_______,			XXXXXXX,		_______,    _______,    	_______,    _______,    _______, 
     ],#
    
    # M2 Layer -- Right Fn
    [   #LEFT																				RIGHT
        #1 COL GP--		2 COL GP--	3 COL GP--	4 COL GP--	5 COL GP--	6 COL GP--	<>		7 COL GP--		8 COL GP--	9 COL GP--	    10 COL GP--	11 COL GP--		12 COL GP--	
        KC.F1,			KC.F2,		KC.F3,		KC.F4,		KC.F5,		KC.F6,				KC.F7,		    KC.F8,		KC.F9,			KC.F10,		KC.F11,			KC.F12, 
        KC.PGUP,		KC.HOME,	KC.UP,		KC.END,		XXXXXXX,	EIDQ,				CtStEsc,		XXXXXXX,	KC.MB_LMB,		KC.MS_UP,	KC.MB_RMB,		XXXXXXX, 
        KC.PGDN,		KC.LEFT,	KC.DOWN,	KC.RIGHT,	KC.ESC,		KC.LPRN,			CtAtDel,	    XXXXXXX,	KC.MS_LEFT,		KC.MS_DOWN,	KC.MS_RIGHT, 	XXXXXXX,
        XXXXXXX,		XXXXXXX,    XXXXXXX,	XXXXXXX,	XXXXXXX,	XXXXXXX,			CMDStr3,		CMDStr2,	KC.MW_UP,		KC.MB_MMB, 	KC.MW_DOWN, 	KC.NUBS,
#Thumbs
        _______,		_______,	KC.DELETE,	_______,	XXXXXXX,	_______,			XXXXXXX,		_______,    _______,    	_______,    _______,    _______, 
     ],#
]


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
    
