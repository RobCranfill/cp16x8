# Scrolling text displayed on an Adafruit 16x8 LED "backpack".
# 
# To make the upper left pixel (0,0), 
# the backpack orientation has the STEMMA connectors on the right edge.

# based on project
#   cp8x8
# which was based on
#   displayText.py
#   (c)2020 robcranfill@gmail.com


import board
import time
from adafruit_ht16k33 import matrix

import led8x8Font


class led_matrix_16x8:
    '''Display for Adafruit 16x8 display backpack based on adafruit_ht16k33 module.'''
    DISPLAY_HEIGHT = 8
    DISPLAY_WIDTH  = 16


    def __init__(self, i2c, display_string, delay, brightness=1.0):
        '''Initialize by giving us the I2C bus object, display string, and column delay.'''

        self.matrix_ = matrix.MatrixBackpack16x8(i2c)
        self.matrix_.brightness = brightness

        vr = self.make_V_rasters(display_string)
        self.display_forever(vr, delay)


    # For the string, create the big list of bit values (columns), left to right.
    #
    def make_V_rasters(self, string):

        if len(string) == 0: # is there a better way to handle this null-input case?
            string = "(no input given!)"

        # duplicate the first 2 chars onto the end of the data for easier scrolling.
        string += string[0]

        string += string[1] # duplicate the 2nd char onto the end of the data for easier scrolling.
        print(f" Input string now '{string}'")

        vrasters = []
        for char in string:
            # bl is the list of *horizontal* rasters for the char
            bl = byte_list_for_char(char)
            for bitIndex in range(self.DISPLAY_HEIGHT-1,-1,-1):
                thisVR = 0
                for hRasterIndex in range(self.DISPLAY_HEIGHT-1,-1,-1):
                    bitVal = ((1 << bitIndex) & bl[hRasterIndex])
                    if bitVal > 0:
                        thisVR += (1 << (self.DISPLAY_HEIGHT-hRasterIndex-1))
                vrasters.append(thisVR)

        # print(f"vraster (len {len(vrasters)}): {vrasters}")
        return vrasters


    # Rotate the list of vertical rasters thru the display, forever.
    # The input data already has the first 2 chars duplicated at the end, for ease of rotation.
    # Uses global displayDelay_ so we can change that after creating the thread.
    #
    def display_forever(self, vrs, delay):

        # Initially, render leftmost DISPLAY_WIDTH columns...
        #
        self.display_initial_rasters(vrs[0:self.DISPLAY_WIDTH])

        # ...Now just left-shift the exiting pixels, and paint the rightmost column, forever.
        c = self.DISPLAY_WIDTH
        while True:

            self.matrix_.shift(-1, 0)

            c += 1
            if c >= len(vrs):
                c = self.DISPLAY_WIDTH

            for y in range(self.DISPLAY_HEIGHT):
                self.matrix_[self.DISPLAY_WIDTH-1, y] = vrs[c] & (1<<(self.DISPLAY_HEIGHT-y-1))

            time.sleep(delay)


    # Display the given raster lines - full display width.
    # LSB of data is at top.
    #
    def display_initial_rasters(self, rasters):

        print(f"Displaying {rasters}...")
        
        for y in range(self.DISPLAY_HEIGHT):

            # TODO: I was hoping i could do like this, but no.
            # matrix[x] = rasters[x]

            for x in range(len(rasters)):
                self.matrix_[x, y] = rasters[x] & (1<<(self.DISPLAY_HEIGHT-y-1))


# Return a list of the bytes for the given character.
# TODO: catch missing chars?
#
def byte_list_for_char(char):
    bits = led8x8Font.FontData[char]
    return bits
