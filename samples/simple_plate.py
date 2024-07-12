#! /usr/bin/env python
'''
Inksnek sample
A very basic design. A plate with m3 holes.
'''

import inkex
from inksnek import *

class MyDesign(inkex.Effect):
  def __init__(self):
    inkex.Effect.__init__(self)
   
  def add_plate(self, group, x, y):
    # cut plate outline
    inksnek.add_round_rect(group, x, y, self.plate_width, self.plate_height, self.plate_radius, inksnek.cut_style)
    # 4 corner holes (cut)
    inksnek.add_hole(group, x + self.hole_offset,                    y + self.hole_offset,                     self.hole_radius)
    inksnek.add_hole(group, x + self.plate_width - self.hole_offset, y + self.plate_height - self.hole_offset, self.hole_radius)
    inksnek.add_hole(group, x + self.hole_offset,                    y + self.plate_height - self.hole_offset, self.hole_radius)
    inksnek.add_hole(group, x + self.plate_width - self.hole_offset, y + self.hole_offset,                     self.hole_radius)
    # label/annotation in non-cutting style
    inksnek.add_annotation(group, self.plate_width/2, self.plate_height/2, "Simple Plate", 5.0, inksnek.ignore_style, inksnek.MID_ALIGN + inksnek.CENTRE_ALIGN)
    
  def effect(self):  # the main entry point for the design
    # initialise Inksnek
    inksnek.setup(self, inksnek.A4, inksnek.ACRYLIC, 3.0, 'mm', inksnek.DEVEL)
    # design parameters
    self.plate_width = 100.0
    self.plate_height = 60.0
    self.plate_radius = 3.0 # radius of rounded corners
    self.hole_radius = 2 # m3
    # x & y offset from sides to hole centre
    self.hole_offset = 3
    # make a group
    design = inksnek.add_group(inksnek.top_group, inksnek.translate_group(7.0, 7.0))
    # add the plate
    self.add_plate(design, 0, 0);

    
if __name__ == '__main__':
    e = my_design()
    e.affect()