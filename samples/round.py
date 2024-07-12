#! /usr/bin/env python
'''
Inksnek sample
Adapted from Circular Turing machine, just the facade (https://hackaday.io/project/183146-turing-ring)
Targeted at thin white-on-black acrylic
Arcs and using a nicer font (PlotterFont) vs the built-in one (Annotation)
Also has samples using other fonts -- Outline8x8Font & NsegmentFont
'''

import inkex
import copy
from math import *
from simplepath import *
from inksnek import *
sys.path.append("C:/inksnek/extras")
from plotter_font import *
from outline_8x8_font import *
from n_segment_font import *

class MyDesign(inkex.Effect):
  def __init__(self):
    inkex.Effect.__init__(self)

  def add_text(self, group, x, y, str, height, style, slant = 0.0):
    # text using plotter font
    scale = height/self.font._std_height
    org_x = x
    for ch in str:
        ch_n = ord(ch)
        if ch_n < 7:
            x += scale*ch_n # bump gap
        elif ch == '\n':
            x = org_x
            y -=  scale*(self.font._size + 1)
        else:
            shape = self.font.get_char_shape(ch, slant)
            inksnek.add_shape(group, x, y, scale, scale, shape, style)
            x += scale*(self.font._std_width)
  
  
  _outer_labels = [
      "A",
      "B",
      "C",
      "D",
      "E",
      "F",
      "G",
      "H",
      "I",
      "J",  # =9th
      "Next\nState",
      "\x82\x04R", # gap 
      " N ",
      "L\x80",
      " Write\nSymbol",
      "Menu",
      "Clear",
      "Instr",
      "Symb",
      "State",
      "Mach",
      "Tape",
      "Run",
      #"Halt/\nBlank",
      "X"
      ]
      
    
  ################
  def radial_labels(self, dial, style):
    # words radiate out
    text_height = 3.0
    scale = text_height/8.0
    text_radius = self.ring_l_e_d_radius_outside + text_height*1.25
    # just the state char labels
    for label in range(24):
        label_str = self._outer_labels[label]
        if len(label_str) == 1:
            rect = inksnek.polar_to_rectangular(text_radius + text_height/4.0, 15.0*label)
            self.add_text(dial, rect[0] - text_height*len(label_str)/2.0 + text_height/8.0, rect[1] - text_height/2.0 - 2.0*text_height/8.0, label_str, text_height, style)
    # outer text labels
    text_height = 2.25
    text_radius = self.ring_l_e_d_radius_outside + text_height*0.75
    for label in range(24):
        label_str = self._outer_labels[label]
        if len(label_str) != 1: # not just a state label
            if label != 10:
                if 11 <= label and label <= 13: # move group
                    rect = inksnek.polar_to_rectangular(text_radius + 2.0*text_height, 15.0*label)
                    self.add_text(dial, rect[0] - text_height*len(label_str)/2.0 + text_height/8.0, rect[1] - text_height/2.0 - 2.0*text_height/8.0, label_str, text_height, style)
                else:
                    label_group = inksnek.add_group(dial, inksnek.rotate_group(label*360.0/24.0 + 90.0))
                    info = self.get_multi_line_str_info(label_str)
                    strlen = info[1]
                    ht = text_height
                    delta = 0.0
                    if info[0] != 1:  # special case for Write\nSymbol & Halt\nBlank(?)
                        ht = text_height*0.75
                        delta = ht/2.0
                    self.add_text(label_group, -text_radius - strlen*ht - ht/8.0, 0.0 - ht/2.0 - 2.0*ht/8.0 + delta, label_str, ht,style)
                        
            else:   # Next/State
                label_group = inksnek.add_group(dial, inksnek.rotate_group(label*360.0/24.0 - 90.0))
                ht = text_height*0.75
                delta = ht/2.0
                self.add_text(label_group, text_radius + ht/2.0, 0.0 - ht/2.0 - 2.0*ht/8.0 + delta, label_str, ht, style)
        elif label == 23:
            label_group = inksnek.add_group(dial, inksnek.rotate_group(-360.0/24.0))
            halt = "Halt"
            ht = text_height*0.75
            strlen = len(halt)
            self.add_text(label_group, -strlen*ht/2.0, self.outer_ring_r - 2.5*text_height, halt, ht, style)
    # "Move" label
    ht = text_height*0.75
    self.add_text(dial, -ht*1.8, -self.outer_ring_r + text_height, "Move", ht, style)
    
    # radial lines
    for idx in range(24):
        if idx in [9, 14, 15, 22,   10, 13, 23]:
            angle = 15.0*(idx + 0.5)
            if idx in [15, 10, 13, 23]:
                rect1 = inksnek.polar_to_rectangular(self.inner_ring_r + 1.0, angle)
                rect2 = inksnek.polar_to_rectangular((self.inner_ring_r+self.outer_ring_r)/2.0, angle)
            else:
                rect1 = inksnek.polar_to_rectangular(self.inner_ring_r + 1.0, angle)
                rect2 = inksnek.polar_to_rectangular(self.outer_ring_r - 1.0, angle)
            inksnek.add_path(dial, inksnek.path_move_to(rect1)+inksnek.path_line_to(rect2), style)
  
  def law_of_cosines(self, a, b, c):
    return inksnek.radians_to_degrees(acos(((a*a) + (b*b) - (c*c)) /
                                          (2.0*a*b)))
  
  def add_curves(self, group, style):
    # add the LED and rotary knob partial circles, connected with smaller partial infill circles
    r1 = self.outer_ring_r             # the big LED arc
    r2 = self.rotary_knob_radius + 1.75           # arc around the rotary knob
    r3 = r2/2.0      # infill arcs, looks in proportion
    a = self.rotary_radius
    b = r2 + r3
    c = r1 + r3
    # origin at centre of dial, -ve y to the rotary dial
    curves = inksnek.add_group(group, inksnek.rotate_group(self.rotary_angle + 180))
    B = self.law_of_cosines(a, c, b)  # (half) angle subtended by gap in large LED arc
    C = self.law_of_cosines(a, b, c)  # (half) angle subtended by gap in rotary arc
    inksnek.add_arc(curves, 0.0, 0.0, r1, -90.0 - B, 90.0 + B, style)  # LEDs arc
    inksnek.add_arc(curves, 0.0, -self.rotary_radius, r2, 90.0 - C, C - 90.0, style)   # rotary arc
    # infill arcs
    rect = inksnek.polar_to_rectangular(b, 90.0 - C)
    inksnek.add_arc(curves, +rect[0], rect[1] - self.rotary_radius, r3, -90.0 - C, +B - 90.0, style)
    inksnek.add_arc(curves, -rect[0], rect[1] - self.rotary_radius, r3, +90.0 - B, +90.0 + C, style)
    
  
  def get_multi_line_str_info(self, multi_line_str):
    # return [lines, length of longest line]
    lines = 0
    len = 0
    maxlen = 0
    for ch in multi_line_str:
      if ch == '\n':
        lines += 1
        if len > maxlen:
            maxlen = len
        len = 0
      else:
        len += 1
    lines += 1
    if len > maxlen:
        maxlen = len
    return [lines, maxlen]
   
  def add8x8_text(self, group, x, y, str, height, style, normal = True):
    # draw text centred at (x, y) using style
    scale = height/8
    x = x - len(str)*height/2
    y = y - height/2
    for idx in range(len(str)):
        if normal:
            inksnek.add_shape(group, x + idx*height, y, scale, scale, self.beeb.normal(str[idx]), style)
        else:
            inksnek.add_shape(group, x + idx*height, y, scale, scale, self.beeb.stencil(str[idx]), style)
        
  def add_seg_text(self, group, x, y, str, scale, style, seg_font):
    # text using seg font
    x -= len(str)*scale*(seg_font.width + seg_font.gap*3.0 + seg_font.thick*2.0)/2
    y -= scale*seg_font.height/2
    for ch in str:
        shape = seg_font.get_char_segments_list(ch, 0.0, 0.0)
        inksnek.add_shape(group, x, y, scale, scale, shape, style)
        x += scale*(seg_font.width + seg_font.gap*3.0 + seg_font.thick*2.0)

  def add_text_samples(self, group):
    # example text in Ignore colour
    fill_style = inksnek.create_fill_style(inksnek.ignore_colour())
    self.add8x8_text(group, 0.0, 10.0, "Outline8x8Font - Fill", 3.0, fill_style)
    self.add8x8_text(group, 0.0, 5.0, "Outline8x8Font - Stroke", 3.0, inksnek.ignore_style)
    self.add8x8_text(group, 0.0, 0.0, "04689ABDOPQR - Stencil", 3.0, inksnek.ignore_style, False)
    size = 3.0
    text = "Annotation"
    inksnek.add_annotation(group, -(len(text)*(size/2 + size/4) - size/2)/2, 15.0, text, size)
    size = 3.0
    text = "PlotterFont"
    self.add_text(group, -len(text)*size/2.0, -10, text, size, inksnek.ignore_style)
    self.add_seg_text(group, 0, -15, "7 SEG", 0.5, fill_style, self.font7_segs)
    self.add_seg_text(group, 0, -20, "14 SEGMENT", 0.5, fill_style, self.font14_segs)
    self.add_seg_text(group, 0, -25, "16 SEGMENT", 0.5, fill_style, self.font16_segs)


  def effect(self):
    self.font = PlotterFont()
    self.beeb = Outline8x8Font()
    self.font7_segs = NSegmentFont(7,             # 7-seg
                                   4, 8,          # width, height
                                   1, 0.25, 0.5)  # skew, gap, thickness
    self.font14_segs = NSegmentFont(14,            # 14-seg
                                    4, 8,          # width, height
                                    1, 0.25, 0.5)  # skew, gap, thickness
    self.font16_segs = NSegmentFont(16,            # 16-seg
                                    4, 8,          # width, height
                                    1, 0.25, 0.5)  # skew, gap, thickness


    self.plate_thickness = 3.0
    inksnek.setup(self, inksnek.A4, inksnek.ACRYLIC, self.plate_thickness, 'mm', inksnek.DEVEL)
    self.rotary_knob_radius = 28.0/2.0
    self.rotary_shaft_radius = 7.0/2.0
    self.ring_l_e_d_size = 5.0;
    self.ring_l_e_d_radius_outside = 65.0/2.0
    self.ring_l_e_d_radius_inside = self.ring_l_e_d_radius_outside - self.ring_l_e_d_size
    inner_cut_r = math.hypot(self.ring_l_e_d_radius_inside, self.ring_l_e_d_size/2.0) - 0.25
    outer_cut_r = math.hypot(self.ring_l_e_d_radius_outside, self.ring_l_e_d_size/2.0) + 0.25
    self.inner_ring_r = outer_cut_r
    self.outer_ring_r = outer_cut_r + 14.0
    self.rotary_angle = 150.0
    self.rotary_radius = self.outer_ring_r + self.rotary_knob_radius + 1.0
    front_margin = 9.0
    self.rotary_rect = inksnek.polar_to_rectangular(self.rotary_radius, self.rotary_angle)
    front_width = 2.0*self.outer_ring_r + front_margin
    front_base_height = abs(self.rotary_rect[1]) + self.rotary_knob_radius + front_margin  # straight sides
  
    
    m3_radius = 3.0/2.0
    m3_inset = inksnek.material_thickness + 2.0*m3_radius
    m3_hole_radius = 1.5
    m3_hole_at_radius = self.inner_ring_r + 10.0
    m3_hole_angles = [0.0, 120.0-360.0/48.0, 240.0+360.0/48.0]
    
    
    gap = 2.0
    dial = inksnek.add_group(inksnek.top_group, inksnek.translate_group(gap + front_width/2.0, gap + front_base_height)) # at centre of dial
    inksnek.add_X_marker(dial, 0, 0)
    cut_style = inksnek.cut_style
    for pair in range(12):
        pair_group = inksnek.add_group(dial, inksnek.rotate_group(pair*360.0/24.0))
        inksnek.add_rect(pair_group, -self.ring_l_e_d_size/2.0, +self.ring_l_e_d_radius_inside, self.ring_l_e_d_size, self.ring_l_e_d_size, cut_style)
        inksnek.add_rect(pair_group, -self.ring_l_e_d_size/2.0, -(self.ring_l_e_d_radius_inside + self.ring_l_e_d_size), self.ring_l_e_d_size, self.ring_l_e_d_size, cut_style)
        
    self.radial_labels(dial, inksnek.etch_style)
    inksnek.add_circle(dial, self.rotary_rect[0], self.rotary_rect[1], self.rotary_knob_radius, inksnek.ignore_style)
    inksnek.add_circle(dial, self.rotary_rect[0], self.rotary_rect[1], self.rotary_shaft_radius, inksnek.cut_style)
    
    self.add_curves(dial, cut_style)
    # m3 holes
    first_hole = True
    for m3_hole_angle in m3_hole_angles:
        m3_rect = inksnek.polar_to_rectangular(m3_hole_at_radius, m3_hole_angle)
        inksnek.add_circle(dial, m3_rect[0], m3_rect[1], m3_hole_radius, inksnek.cut_style)
    # centre hole
    inksnek.add_circle(dial, 0.0, 0.0, m3_radius, inksnek.cut_style)
    
    self.add_text_samples(inksnek.add_group(inksnek.top_group, inksnek.translate_group(gap + 1.5*front_width, gap + front_base_height)))# at centre of dial
    
if __name__ == '__main__':
    e = my_design()
    e.affect()
