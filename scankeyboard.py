print("Starting")

# The follow is based off 
#     http://kmkfw.io/docs/porting_to_kmk

# Note: it actually easier to get this code working in 
#     code.py 
# this way all the Spilt / Comms are in place
# But to make it easier to read its checked in as two standalone programs

# This creates the physical button grid map of keycodes to allow random order be resorted and place into the correct locations
# So maps the correct physical Keyread (keyboard.coord_mapping) to the keymap (keyboard.keymap) of the same location below keyboard.keymap
#   keyboard.coord_mapping
#   keyboard.keymap
#
# keyboard.coord_mapping = [
# #L								R
# 026, 029, 028, 027, 024, 025,  	054, 056, 058, 057, 055, 059,
# 020, 023, 022, 021, 018, 019, 	048, 050, 052, 051, 049, 053,
# 014, 017, 016, 015, 012, 013, 	042, 044, 046, 045, 043, 047,
# 002, 005, 004, 003, 000, 001, 	030, 032, 034, 033, 031, 035, 
# 008, 009, 006, 007, 011, 010, 	036, 038, 040, 039, 037, 041, 
# ]

# When one of the codes above is read it will print from the keymap, so if 022 is read, it prints KC.E
# keyboard.keymap = [
#     [                                                                                                                                            
#         KC.N1,		KC.N2,		KC.N3,		KC.N4,		KC.N5,		KC.N6,			KC.N7,			KC.N8,		KC.N9,		KC.N0,		KC.MINS,	KC.EQUAL,
#         KC.Q,		    KC.W,		KC.E,		KC.R,		KC.T,		KC.QUOTE,		PASW, 			KC.Y,		KC.U,		KC.I,		KC.O,		KC.P,		
#         KC.A,		    KC.S,		KC.D,		KC.F,		KC.G,		KC.LBRC,		KC.RBRC,		KC.H,		KC.J,		KC.K,		KC.L,		KC.SCLN,
#         KC.Z,		    KC.X,		KC.C,		KC.V,		KC.B,		KC.GRAVE,		KC.NUBS,		KC.N,		KC.M,		KC.COMM,	KC.DOT,     KC.SLASH,
#         CAPS,			KC.TAB,		KC.BSPACE,	KC.SPACE,	LOWER,		LCTRLED,		LOWER,		    KC.SPACE,	KC.LALT,	LCTRLED,	KC.LGUI,	KC.ENTER,		
#      ]
# ]

import board

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.scanners.keypad import MatrixScanner

#enable Irish type keys
from kmk.extensions.international import International
from kmk.handlers.sequences import send_string
from kmk.modules.tapdance import TapDance
from kmk.modules.layers import Layers


#only needed for the scaners
from kmk.handlers.sequences import simple_key_sequence
keyboard = KMKKeyboard()

#The following will need to be changed for each new pico project
#					 R																		L
keyboard.col_pins = (board.GP0, board.GP1, board.GP27, board.GP26, board.GP21, board.GP20,	board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7)
keyboard.row_pins = (board.GP16, board.GP17, board.GP18, board.GP19, board.GP22, 			board.GP8, board.GP9, board.GP10, board.GP11, board.GP12)
keyboard.diode_orientation = DiodeOrientation.ROW2COL

# Build out the grid keycodes
N = len(keyboard.col_pins) * len(keyboard.row_pins) * 2
keyboard.coord_mapping = list(range(N))
layer = []
for i in range(N):
    c, r = divmod(i, 100)
    d, u = divmod(r, 10)
    layer.append(
        simple_key_sequence(
            (
                getattr(KC, 'N' + str(c)),
                getattr(KC, 'N' + str(d)),
                getattr(KC, 'N' + str(u)),
                KC.SPC,
            )
        )
    )
keyboard.keymap = [layer]

# Keyboard should be fully active, now press all the keys in order from top left to bottom right to build out the keyboard.coord_mapping
# keyboard.coord_mapping will be used in the 'code.py'
if __name__ == '__main__':
    keyboard.go()

