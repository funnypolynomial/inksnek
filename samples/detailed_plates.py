#! /usr/bin/env python
'''
Inksnek sample
Adapted from FlipClock (https://hackaday.io/project/167162-flipclock)
Reasonably complex plate design
'''

import inkex
from math import *
from inksnek import *


class MyDesign(inkex.Effect):
  def __init__(self):
    inkex.Effect.__init__(self)
    
  def m3_hole(self, group, x, y):
    # cut an m3 hole centred at (x,y) and show size of head/nut 
    inksnek.add_circle(group, x, y, self.m3_hole_diameter/2.0, inksnek.cut_style)
    inksnek.add_circle(group, x, y, 5.3/2.0, inksnek.ignore_style)
  
  def add_arduino(self, group, x, y, bottom): 
    # add mounting holes for Arduino, show approx extent of board and LCD
    # coords are bottom-left mounting hole
    arduino = inksnek.add_group(group, inksnek.translate_group(x, y))
    # dims from https://blog.adafruit.com/2011/02/28/arduino-hole-dimensions-drawing/
    # the shield+LCD stack isn't very square...
    if bottom:
        # mounting holes
        self.m3_hole(arduino, 0, 0)                                  # bottom-left
        self.m3_hole(arduino, 1.3 + 50.6, 5.1)                       # bottom-right
        self.m3_hole(arduino, 1.3 + 50.6, 5.1 + 27.5)                # top-right
        self.m3_hole(arduino, 1.3 + 50.6 - 50.5, 5.1 + 27.5 + 15.2)  # top-left
        # board outline
        inksnek.add_rect(arduino, -14.0, -2.5, 68.6, 53.3, inksnek.ignore_style)
    # lcd shield outline
    if bottom:
        inksnek.add_rect(arduino, -14.0 + 8.0, -2.5 - (self.lcd_height - 53.3)/2.0, self.lcd_width, self.lcd_height, inksnek.ignore_style)
        
  def cutout(self, inset_x, inset_y, sign_x, sign_y, round_radius):
    # add a cutout insetX from the side, insetY from the top
    # inset is upward if signY is +ve, inset is to the right if signX is +ve
    path = ""
    path += inksnek.path_vert_by(sign_y*(inset_y - 2.0*round_radius))
    path += inksnek.path_round_by(sign_x*round_radius, sign_y*round_radius, -round_radius)
    path += inksnek.path_horz_by(sign_x*(inset_x - 2.0*round_radius))
    path += inksnek.path_round_by(sign_x*round_radius, sign_y*round_radius, +round_radius)
    path += inksnek.path_vert_by(sign_y*(self.plate_height - 2.0*inset_y - 2.0*round_radius))
    path += inksnek.path_round_by(-sign_x*round_radius, sign_y*round_radius, +round_radius)
    path += inksnek.path_horz_by(-sign_x*(inset_x - 2.0*round_radius))
    path += inksnek.path_round_by(-sign_x*round_radius, sign_y*round_radius, -round_radius)
    path += inksnek.path_vert_by(sign_y*(inset_y - 2.0*round_radius))    
    return path
    
  def add_plate(self, group, bottom):
    # add top or bottom plate at (0,0) in group
    round_radius = 5.3/2.0 # curvature of corners
    # trace the cut path, anti-clockwise
    path = inksnek.path_start();
    # bottom edge, starting at bottom right of rounded corner at bottom left
    path += inksnek.path_move_by(round_radius, 0)
    path += inksnek.path_horz_by(self.plate_width - 2.0*round_radius)
    path += inksnek.path_round_by(+round_radius, +round_radius, -round_radius) # bottom right corner, curving up
    
    if bottom: # right side, including deep cutout inset on RHS, tracing up
        path += self.cutout(38.0, 12.0, -1, +1, round_radius)
    else: # right side is just a straight vertical
        path += inksnek.path_vert_by(self.plate_height - 2.0*round_radius)
        
    path += inksnek.path_round_by(-round_radius, +round_radius, -round_radius) # top right corner
    
    # top edge, going right to left
    if bottom:
        # just move, no cut-line, sharing the bottom cut-line of the top plate
        path += inksnek.path_move_by(-(self.plate_width - 2.0*round_radius), 0)
    else:
        path += inksnek.path_horz_by(-(self.plate_width - 2.0*round_radius))
    path += inksnek.path_round_by(-round_radius, -round_radius, -round_radius) # top left corner
    
    if bottom: # the shallow inset on the left side of bottom plate, tracing down
        path += self.cutout(7.5, 12.0, +1, -1, round_radius)
    else:
        path += inksnek.path_vert_by(-(self.plate_height - 2.0*round_radius))
        
    path += inksnek.path_round_by(+round_radius, -round_radius, -round_radius) # final corner, bottom left
    inksnek.add_path(group, path, inksnek.cut_style)
    # holes to join plates
    self.m3_hole(group, self.hole_inset, self.hole_inset)
    self.m3_hole(group, self.plate_width - self.hole_inset, self.hole_inset)
    self.m3_hole(group, self.hole_inset, self.plate_height - self.hole_inset)
    self.m3_hole(group, self.plate_width - self.hole_inset, self.plate_height - self.hole_inset)
    # position Arduino + LCD shield
    y = (self.plate_height - (5.1 + 27.5 + 15.2))/2.0
    self.add_arduino(group, 22.0, y, bottom)
    
    
  ################
  def effect(self):
    self.m3_hole_diameter = 3.0
    self.lcd_width = 85.5
    self.lcd_height = 55.5
    self.plate_width = 117.5
    self.plate_height = 70
    self.hole_inset = 5
    org_x = 2
    org_y = 2
    inksnek.setup(self, inksnek.A4, inksnek.ACRYLIC, 3.0, 'mm', inksnek.DEVEL)

    bottom_plate = inksnek.add_group(inksnek.top_group, inksnek.translate_group(org_x, org_y))
    self.add_plate(bottom_plate, True)
    top_plate = inksnek.add_group(inksnek.top_group, inksnek.translate_group(org_x, org_y + self.plate_height))
    self.add_plate(top_plate, False)
	

    
if __name__ == '__main__':
    e = my_design()
    e.affect()
