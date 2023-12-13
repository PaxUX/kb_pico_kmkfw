print("Starting")

#  Note: Drive Label is used to select between L/R side of keyboard
#   KB_L
#   KB_R
#
# See the following sites for more documentation 
# http://kmkfw.io/
# http://kmkfw.io/docs/keycodes/#international-keys
# https://github.com/KMKfw/kmk_firmware/blob/master/docs/en/keycodes.md

import board

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation

#used by the Self.Matrix Next 2 lines can be removed
from kmk.scanners.keypad import MatrixScanner
from kmk.handlers.sequences import simple_key_sequence

# Enable the required Moduals needed
from kmk.extensions.international import International
from kmk.handlers.sequences import send_string
from kmk.modules.tapdance import TapDance
from kmk.modules.layers import Layers
from kmk.extensions.lock_status import LockStatus
from kmk.modules.mouse_keys import MouseKeys

locks = LockStatus()
#See which side of the keyboard code is being run
#From kb import data_pin
from kmk.modules.split import Split, SplitSide
from storage import getmount
#   KB_L / KB_R
side = SplitSide.RIGHT if str(getmount('/').label)[-1] == 'R' else SplitSide.LEFT


#Nomral Single
keyboard = KMKKeyboard()
#keyboard.debug_enabled = True

#RGB
from kmk.extensions.RGB import RGB

#Split Keyboard, setup the wiring for each side
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
split = Split(use_pio=True, uart_flip = True, data_pin=board.GP1)
keyboard.modules.append(split)

#This is the as I have it guess this line could be removed
keyboard.modules.append(split)

keyboard.modules.append(Layers())
#international
keyboard.extensions.append(International())
#Mouse
keyboard.modules.append(MouseKeys())
#Tap Dance
tapdance = TapDance()
tapdance.tap_time = 170
keyboard.modules.append(tapdance)
#Caps Lock Status
keyboard.extensions.append(locks)

# The following is building up Layers and Customer Key types beyond the standard keys (strings, multi-purpose on double tab [tapdance] )
#Function Layer
#FnKey = KC.MO(1)
FnKey = KC.TD(KC.MO(1), KC.TG(1))
FnALT = KC.TD(KC.MO(1), KC.LALT)

# standard filler keys  (mean layer overlay has no key use here so use key from next level under, or make the key a No OP/No Key)
_______ = KC.TRNS
XXXXXXX = KC.NO

# Multi keypress to OS but Single keyboard key
# CTRL ALT Delete
CtAtDel = KC.LCTL( KC.LALT( KC.DEL ))
# CTRL SHIFT ESC
CtAtEsc = KC.LCTL( KC.LSHIFT( KC.ESC ))

#### The follow is trying to Fix US Keyboard Vs International, this a bit messy
#Right >
RtGT = KC.LSHIFT( KC.DOT )
#Remap US to IE Keymappings
EIDQ = KC.AT

#Works like a Copy/Paste.  Some keys type strings I type too much and just want a single button for
PASW = send_string("string1")
POOPS = send_string("string2")
PNOOPS = send_string("string3")

#Setup the LED for keypress
rgb = RGB(pixel_pin=board.GP22, num_pixels=3, val_limit=100, hue_default=0, sat_default=0, val_default=0)
keyboard.extensions.append(rgb)

#this allow double tab to enable the button, but its actually not used, as commented out... this setup has no caps lock
KAPLOCK = KC.CAPSLOCK
#CAPS = KC.TD(KC.LSHIFT, KAPLOCK)
CAPS = KC.LSHIFT

#Setup Overrides for LED colours
LOWER = KC.MO(1)    #Set layer to LOWER
SSSS  = KC.LSHIFT   
LCTRLED = KC.LCTRL  

#Functions to plug into the alerting system
def SSon(key, keyboard, *args):
    rgb.set_rgb((100, 0, 0), 0)  
    return True

#this might not work correctly with CAPS LOCK as I removed it from this version of the code
def SSoff(key, keyboard, *args):
    if locks.get_caps_lock() == False:
        rgb.set_rgb((0, 0, 0), 0)
    return True

#Enable LED when not using base keyboard Layer
def FNon(key, keyboard, *args):
    rgb.set_rgb((0, 100, 0), 1)
    return True

def FNoff(key, keyboard, *args):
    rgb.set_rgb((0, 0, 0), 1)
    return True

def CTRLon(key, keyboard, *args):
    rgb.set_rgb((0, 0, 100), 2)
    return True

def CTRLoff(key, keyboard, *args):
    rgb.set_rgb((0, 0, 0), 2)
    return True

# Map all the above colour changes to the keys that will trigger the LEDs
SSSS.before_press_handler(SSon) #call the key with the after_press_handler
SSSS.after_release_handler(SSoff)
KAPLOCK.before_press_handler(SSon)
KAPLOCK.after_release_handler(SSoff)
LOWER.after_press_handler(FNon) #call the key with the after_press_handler
LOWER.before_release_handler(FNoff) #call the key with the after_press_handler
LCTRLED.after_press_handler(CTRLon)
LCTRLED.before_release_handler(CTRLoff)


#This maps the correct Board Keyread code to the keymap of the same location below in Keymap
#  scankeyboard.py generated this see that program for details
keyboard.coord_mapping = [
#L								R
026, 029, 028, 027, 024, 025,  	054, 056, 058, 057, 055, 059,
020, 023, 022, 021, 018, 019, 	048, 050, 052, 051, 049, 053,
014, 017, 016, 015, 012, 013, 	042, 044, 046, 045, 043, 047,
002, 005, 004, 003, 000, 001, 	030, 032, 034, 033, 031, 035, 
008, 009, 006, 007, 011, 010, 	036, 038, 040, 039, 037, 041, 
]

keyboard.keymap = [
# Base Layer / defaults
    [                                                                                                                                            
#       #1 COL GP27		2 COL GP26	3 COL GP21	4 COL GP20	5 COL GP19	6 COL GP18	<>	7 COL GP17      8 COL GP17	9 COL GP16	10 COL GP0 	11 COL GP1 	12 COL GP3 	
        KC.N1,		    KC.N2,		KC.N3,		KC.N4,		KC.N5,		KC.N6,			KC.N7,			KC.N8,		KC.N9,		KC.N0,		KC.MINS,	KC.EQUAL,
        KC.Q,		    KC.W,		KC.E,		KC.R,		KC.T,		KC.QUOTE,		PASW, 			KC.Y,		KC.U,		KC.I,		KC.O,		KC.P,		
        KC.A,		    KC.S,		KC.D,		KC.F,		KC.G,		KC.LBRC,		KC.RBRC,		KC.H,		KC.J,		KC.K,		KC.L,		KC.SCLN,
        KC.Z,		    KC.X,		KC.C,		KC.V,		KC.B,		KC.GRAVE,		KC.NUBS,		KC.N,		KC.M,		KC.COMM,	KC.DOT,     KC.SLASH,
#Thumbs 
        CAPS,			KC.TAB,		KC.BSPACE,	KC.SPACE,	FnALT,		LCTRLED,		LOWER,		KC.SPACE,	KC.LALT,	LCTRLED,		KC.LGUI,	KC.ENTER,		
     ], 
    # M1 Layer -- Fnt
    [
        #1 COL GP--		2 COL GP--	3 COL GP--	4 COL GP--	5 COL GP--	6 COL GP--	<>	7 COL GP--		8 COL GP--	9 COL GP--	    10 COL GP--	11 COL GP--		12 COL GP--	
        KC.F1,		    KC.F2,		KC.F3,		KC.F4,		KC.F5,		KC.F6,			KC.F7,		    KC.F8,		KC.F9,		    KC.F10,		KC.F11,			KC.F12, 
        KC.PGUP,		KC.HOME,	KC.UP,	    KC.END,		XXXXXXX,	EIDQ,			KC.PAST,		CtAtEsc,	CtAtDel,	    KC.PSCR,	KC.SLCK,		KC.PAUS, 
        KC.PGDN,        KC.LEFT,	KC.DOWN,	KC.RIGHT,	KC.ESC,		KC.LPRN,		KC.RPRN,	    _______,	KC.MB_LMB,		KC.MS_UP,	KC.MB_RMB, 		XXXXXXX,
        XXXXXXX,		XXXXXXX,    XXXXXXX,	XXXXXXX,	XXXXXXX,	XXXXXXX,		PNOOPS,			POOPS,    	KC.MS_LEFT,		KC.MS_DOWN, KC.MS_RIGHT, 	KC.NUBS,
#Thumbs 
        CAPS,		_______,	KC.DELETE,	_______,	_______,	_______,		_______,		_______,    _______,    	_______,    _______,    _______, 
     ],
]


#the following is just debug to console to see what mode the code is running L/R
print(str(getmount('/').label)[-1])
# Run the Keyboard Software
if __name__ == '__main__':
    keyboard.go()

