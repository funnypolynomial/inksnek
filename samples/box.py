#! /usr/bin/env python
'''
Inksnek sample
Adapted from BigBlue Clock #2 (https://flickr.com/photos/funnypolynomial/albums/72157641980811253/)
Box enclosure with sparse box joints
To validate the design, there are a lot of extra lines (using the Ignore style), see self.showGuides
'''

import inkex
import simplestyle, sys
from math import *
from inksnek import *
import operator


class MyDesign(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)

    def add_X_marker(self, group, at_x, at_y, label = None, size = None):
        if label is None:
            label = 'X'
        if size is None:
            size = 1.0
        inksnek.add_X_marker(group, at_x, at_y, size, self.etch, label)
    
    def add_drill_hole(self, group, x, y, radius):
        # NO kerf
        inksnek.add_circle(group, x, y, radius, inksnek.cut_style)
    
    
    def add_LCD(self, group, face_width, face_height):
        lcd = inksnek.add_group(group, inksnek.translate_group(face_width/2.0, face_height/2.0))
        inksnek.add_rect(lcd, -self.lcd_screen_width/2.0, -self.lcd_screen_height/2.0, self.lcd_screen_width, self.lcd_screen_height, inksnek.cut_style)
        inksnek.add_rect(lcd, -self.lcd_board_width/2.0,  -self.lcd_board_height/2.0,  self.lcd_board_width,  self.lcd_board_height,  inksnek.ignore_style)
        inksnek.add_annotation(lcd, -self.lcd_screen_width/2.0+self.label_size, -self.lcd_screen_height/2.0+self.label_size, "LCD", self.label_size, inksnek.ignore_style)
        d_x = self.lcd_holes_width/2.0
        d_y = self.lcd_holes_height/2.0
        self.add_drill_hole(lcd, -d_x, -d_y, self.lcd_hole_radius)
        self.add_drill_hole(lcd, +d_x, -d_y, self.lcd_hole_radius)
        self.add_drill_hole(lcd, -d_x, +d_y, self.lcd_hole_radius)
        self.add_drill_hole(lcd, +d_x, +d_y, self.lcd_hole_radius)
        
    def add_arduino(self, group, face_width, face_height):
        arduino = inksnek.add_group(group, inksnek.rotate_group(face_width/2.0, face_height/2.0, 180.0))
        inksnek.add_rect(arduino, -self.arduino_board_width/2.0, -self.arduino_board_height/2.0, self.arduino_board_width, self.arduino_board_height, inksnek.ignore_style)
        for hole in range(len(self.arduino_holes)):
          pos = self.arduino_holes[hole]
          self.add_drill_hole(arduino, -self.arduino_board_width/2.0 + pos[0], -self.arduino_board_height/2.0 + pos[1], self.arduino_hole_radius)
          if hole == 0:
            inksnek.add_circle(arduino, -self.arduino_board_width/2.0 + pos[0], -self.arduino_board_height/2.0 + pos[1], self.arduino_hole_radius, inksnek.light_fill_style)
          if self.show_labels:
            inksnek.add_annotation(arduino, -self.arduino_board_width/2.0 + pos[0] + self.arduino_hole_radius, -self.arduino_board_height/2.0 + pos[1], pos[2], self.label_size/2.0, inksnek.ignore_style)

    def add_perf_board(self, group, face_width, face_height):
        rows = 16
        cols = 32
        pitch = 2.54
        radius = 0.5
        perf = inksnek.add_group(group, inksnek.translate_group((face_width - cols*pitch)/2.0, (face_height - rows*pitch)/2.0))
        for row in range(rows):
          for col in range(cols):
            inksnek.add_circle(perf, col*pitch, row*pitch, radius, inksnek.ignore_style)

    def add_access_annotation(self, group, X, Y, radius):
        # draw an arrow
        path = inksnek.path_start()
        path += inksnek.path_move_to(X+4.5*radius, Y-4.5*radius)
        path += inksnek.path_arrow_to(X+1.5*radius, Y-1.5*radius, radius)
        inksnek.add_path(group, path, self.etch)
          
    
    def add_back_l_c_d_holes(self, group, face_width, face_height):
        holes = inksnek.add_group(group, inksnek.translate_group(face_width/2.0, face_height/2.0))
        d_x = self.lcd_holes_width/2.0
        d_y = self.lcd_holes_height/2.0
        self.add_drill_hole(holes, -d_x, -d_y, self.lcd_hole_radius)
        self.add_drill_hole(holes, +d_x, -d_y, self.lcd_hole_radius)
        self.add_drill_hole(holes, -d_x, +d_y, self.lcd_hole_radius)
        self.add_drill_hole(holes, +d_x, +d_y, self.lcd_hole_radius)

    def add_panel_holes(self, group, face_width, face_height):
        holes = inksnek.add_group(group, inksnek.translate_group(face_width/2.0, face_height/2.0) + inksnek.rotate_group(180.0))
        
        # buttons
        button_hole_radius = 6.8/2.0
        button_hole_x = 4*button_hole_radius
        button_hole_y = face_height/2.0 - self.box_material_thickness - 4*button_hole_radius
        self.add_drill_hole(holes, -button_hole_x, button_hole_y, button_hole_radius)
        self.add_drill_hole(holes, +button_hole_x, button_hole_y, button_hole_radius)
        inksnek.add_annotation(holes, -button_hole_x, button_hole_y+2*button_hole_radius, "SET", self.label_size, self.etch, inksnek.CENTRE_ALIGN)
        inksnek.add_annotation(holes, +button_hole_x, button_hole_y+2*button_hole_radius, "SEL", self.label_size, self.etch, inksnek.CENTRE_ALIGN)
        inksnek.add_circle(holes, -button_hole_x, button_hole_y, 5.0, inksnek.ignore_style)
        inksnek.add_circle(holes, +button_hole_x, button_hole_y, 5.0, inksnek.ignore_style)
        
        # power
        self.power_hole_radius = 5.7/2.0
        power_hole_x = 0
        power_hole_y = -(face_height/2.0 - self.box_material_thickness - 4*button_hole_radius)
        self.add_drill_hole(holes, power_hole_x, power_hole_y, self.power_hole_radius)
        inksnek.add_circle(holes, power_hole_x, power_hole_y, 5.0, inksnek.ignore_style)
        inksnek.add_annotation(holes, power_hole_x, power_hole_y-2*self.power_hole_radius, "TIP+5VDC", self.label_size/2.0, self.etch, inksnek.CENTRE_ALIGN+inksnek.TOP_ALIGN)

        # LDR 15x12 mm, holes 10mm apart, 3mm above sensor
        self.sensor_hole_radius = 3.0
        sensor_hole_x = 0
        sensor_hole_y = 0
        self.add_drill_hole(holes, sensor_hole_x, sensor_hole_y, self.sensor_hole_radius)
        self.add_drill_hole(holes, sensor_hole_x+5.0, sensor_hole_y+3.0, self.screw_head_radius)
        self.add_drill_hole(holes, sensor_hole_x-5.0, sensor_hole_y+3.0, self.screw_head_radius)
        inksnek.add_rect(holes, sensor_hole_x-15.0/2.0, sensor_hole_y-12.0/2.0, 15.0, 12.0, inksnek.ignore_style)
        inksnek.add_annotation(holes, sensor_hole_x, sensor_hole_y-2*self.power_hole_radius, "SENSOR", self.label_size/2.0, self.etch, inksnek.CENTRE_ALIGN+inksnek.TOP_ALIGN)
        
        # pass-thru LCD holes
        d_x = self.lcd_holes_width/2.0
        d_y = self.lcd_holes_height/2.0
        self.add_access_annotation(holes, -d_x, -d_y, self.screw_head_radius)
        self.add_access_annotation(holes, +d_x, -d_y, self.screw_head_radius)
        self.add_access_annotation(holes, -d_x, +d_y, self.screw_head_radius)
        self.add_access_annotation(holes, +d_x, +d_y, self.screw_head_radius)
        inksnek.add_annotation(holes, 0, -face_height/2 + self.label_size, "BIGBLUE II - MEW MMXIII", self.label_size/3.0, self.etch, inksnek.CENTRE_ALIGN+inksnek.TOP_ALIGN)

    def add_box(self, at_x, at_y, rotation):
        # origin is bottom-left of top face
        box = inksnek.add_group(inksnek.top_group, inksnek.translate_group(at_x, at_y) + inksnek.rotate_group(rotation))

        #####################   top
        top = inksnek.add_group(box, inksnek.translate_group(0, 0))
        if self.show_guides:
          inksnek.add_rect(top, self.box_material_thickness, self.box_material_thickness, self.box_internal_width, self.box_internal_depth, inksnek.ignore_style)
          inksnek.add_rect(top, 0, 0, self.box_external_width, self.box_external_depth, inksnek.ignore_style)
        if self.show_labels:
          inksnek.add_annotation(top, self.label_offset, self.label_offset, "T", self.label_size, inksnek.ignore_style)
        
        tab_size = self.box_material_thickness*2
        # bottom
        path  = inksnek.path_move_to(0, 0)
        path += inksnek.path_line_to(tab_size, 0)
        path += inksnek.path_line_to(tab_size, self.box_material_thickness)
        path += inksnek.path_line_to(self.box_external_width - tab_size, self.box_material_thickness)
        path += inksnek.path_line_to(self.box_external_width - tab_size, 0)
        path += inksnek.path_line_to(self.box_external_width, 0)
       
        # right
        path += inksnek.path_line_to(self.box_external_width, tab_size)
        path += inksnek.path_line_to(self.box_external_width - self.box_material_thickness, tab_size)
        path += inksnek.path_line_to(self.box_external_width - self.box_material_thickness, self.box_external_depth - tab_size)
        path += inksnek.path_line_to(self.box_external_width, self.box_external_depth - tab_size)
        path += inksnek.path_line_to(self.box_external_width, self.box_external_depth)
        
        #top
        path += inksnek.path_line_to(self.box_external_width - tab_size, self.box_external_depth)
        path += inksnek.path_line_to(self.box_external_width - tab_size, self.box_external_depth - self.box_material_thickness)
        path += inksnek.path_line_to(tab_size, self.box_external_depth - self.box_material_thickness)
        path += inksnek.path_line_to(tab_size, self.box_external_depth)
        path += inksnek.path_line_to(0, self.box_external_depth)
        
        # left
        path += inksnek.path_line_to(0, self.box_external_depth - tab_size)
        path += inksnek.path_line_to(self.box_material_thickness, self.box_external_depth - tab_size)
        path += inksnek.path_line_to(self.box_material_thickness, tab_size)
        path += inksnek.path_line_to(0, tab_size)

        path += inksnek.path_close()
        inksnek.add_path(top, path, inksnek.cut_style)

        #####################   front
        front = inksnek.add_group(box, inksnek.translate_group(0, -self.box_external_height + self.box_material_thickness))
        if self.show_guides:
          inksnek.add_rect(front, self.box_material_thickness, self.box_material_thickness, self.box_internal_width, self.box_internal_height, inksnek.ignore_style)
          inksnek.add_rect(front, 0, 0, self.box_external_width, self.box_external_height, inksnek.ignore_style)
        if self.show_labels:          
          inksnek.add_annotation(front, self.label_offset, self.label_offset, "F", self.label_size, inksnek.ignore_style)
        
        # bottom
        path  = inksnek.path_move_to(0, self.box_material_thickness)
        path += inksnek.path_line_to(tab_size, self.box_material_thickness)
        path += inksnek.path_line_to(tab_size, 0)
        path += inksnek.path_line_to(self.box_external_width - tab_size, 0)
        path += inksnek.path_line_to(self.box_external_width - tab_size, self.box_material_thickness)
        path += inksnek.path_line_to(self.box_external_width, self.box_material_thickness)

        # right
        path += inksnek.path_line_to(self.box_external_width, self.box_external_height - self.box_material_thickness)

        # top (inherited from cutting bottom of top face)
        path += inksnek.path_move_to(0, self.box_external_height - self.box_material_thickness)

        # left
        path += inksnek.path_line_to(0, self.box_material_thickness)
        
        path += inksnek.path_close()
        inksnek.add_path(front, path, inksnek.cut_style)

        #####################   back
        back = inksnek.add_group(box, inksnek.translate_group(0, self.box_external_depth - self.box_material_thickness))
        if self.show_guides:
          inksnek.add_rect(back, self.box_material_thickness, self.box_material_thickness, self.box_internal_width, self.box_internal_height, inksnek.ignore_style)
          inksnek.add_rect(back, 0, 0, self.box_external_width, self.box_external_height, inksnek.ignore_style)
        if self.show_labels:          
          inksnek.add_annotation(back, self.label_offset, self.label_offset, "B", self.label_size, inksnek.ignore_style)

        # left
        path  = inksnek.path_move_to(0, self.box_material_thickness)
        path += inksnek.path_vert_by((self.box_internal_height - tab_size)/2.0)
        path += inksnek.path_horz_by(self.box_material_thickness);
        path += inksnek.path_vert_by(tab_size);
        path += inksnek.path_horz_by(-self.box_material_thickness);
        path += inksnek.path_vert_by((self.box_internal_height - tab_size)/2.0)
        path += inksnek.path_line_to(self.box_material_thickness, self.box_external_height - self.box_material_thickness)        
        path += inksnek.path_line_to(tab_size, self.box_external_height - self.box_material_thickness)
        
        # top
        path += inksnek.path_line_to(tab_size, self.box_external_height)
        path += inksnek.path_line_to(self.box_external_width - tab_size, self.box_external_height)
        path += inksnek.path_line_to(self.box_external_width - tab_size, self.box_external_height - self.box_material_thickness)
        path += inksnek.path_line_to(self.box_external_width, self.box_external_height - self.box_material_thickness)
        
        # right
        path += inksnek.path_vert_by(-(self.box_internal_height - tab_size)/2.0)
        path += inksnek.path_horz_by(-self.box_material_thickness);
        path += inksnek.path_vert_by(-tab_size);
        path += inksnek.path_horz_by(+self.box_material_thickness);
        path += inksnek.path_vert_by(-(self.box_internal_height - tab_size)/2.0)

        # bottom (inherited)
        path += inksnek.path_move_to(0, self.box_material_thickness)

        inksnek.add_path(back, path, inksnek.cut_style)

        #####################  
        foot_size = 0
        #####################  left
        left = inksnek.add_group(box, inksnek.translate_group(self.box_material_thickness - self.box_external_depth, self.box_external_depth - self.box_material_thickness))
        if self.show_guides:
          inksnek.add_rect(left, self.box_material_thickness, self.box_material_thickness, self.box_internal_depth, self.box_internal_height, inksnek.ignore_style)
          inksnek.add_rect(left, 0, 0, self.box_external_depth, self.box_external_height, inksnek.ignore_style)
        if self.show_labels:
          inksnek.add_annotation(left, self.label_offset, self.label_offset, "L", self.label_size, inksnek.ignore_style)
        
        # bottom
        path  = inksnek.path_move_to(self.box_external_depth - self.box_material_thickness, self.box_material_thickness)
        path += inksnek.path_horz_by(-self.box_material_thickness)
        path += inksnek.path_vert_by(-self.box_material_thickness)
        path += inksnek.path_horz_by(-(self.box_external_depth - tab_size - self.box_material_thickness*2.0))
        path += inksnek.path_vert_by(+self.box_material_thickness)
        path += inksnek.path_horz_by(-self.box_material_thickness)
        
        # left
        path += inksnek.path_vert_by(self.box_external_height - self.box_material_thickness*2.0)

        # top
        path += inksnek.path_horz_by(+self.box_material_thickness)
        path += inksnek.path_vert_by(self.box_material_thickness + foot_size);
        path += inksnek.path_horz_by(self.box_external_depth - tab_size - self.box_material_thickness*2.0)
        path += inksnek.path_vert_by(-self.box_material_thickness - foot_size);
        path += inksnek.path_horz_by(+self.box_material_thickness)

        inksnek.add_path(left, path, inksnek.cut_style)

        #####################   right
        right = inksnek.add_group(box, inksnek.translate_group(self.box_external_width - self.box_material_thickness, self.box_external_depth - self.box_material_thickness))
        if self.show_guides:
          inksnek.add_rect(right, self.box_material_thickness, self.box_material_thickness, self.box_internal_depth, self.box_internal_height, inksnek.ignore_style)
          inksnek.add_rect(right, 0, 0, self.box_external_depth, self.box_external_height, inksnek.ignore_style)
        if self.show_labels:
          inksnek.add_annotation(right, self.label_offset, self.label_offset, "R", self.label_size, inksnek.ignore_style)
        
        # bottom
        path  = inksnek.path_move_to(self.box_material_thickness, self.box_material_thickness)
        path += inksnek.path_horz_by(self.box_material_thickness)
        path += inksnek.path_vert_by(-self.box_material_thickness)
        path += inksnek.path_horz_by(self.box_external_depth - tab_size - self.box_material_thickness*2.0)
        path += inksnek.path_vert_by(self.box_material_thickness)
        path += inksnek.path_horz_by(self.box_material_thickness)
        
        # right
        path += inksnek.path_vert_by(self.box_external_height - self.box_material_thickness*2.0)

        # top
        path += inksnek.path_horz_by(-self.box_material_thickness)
        path += inksnek.path_vert_by(self.box_material_thickness + foot_size);
        path += inksnek.path_horz_by(-(self.box_external_depth - tab_size - self.box_material_thickness*2.0))
        path += inksnek.path_vert_by(-self.box_material_thickness - foot_size);
        path += inksnek.path_horz_by(-self.box_material_thickness)

        inksnek.add_path(right, path, inksnek.cut_style)

        #####################        
        bottom = inksnek.add_group(box, inksnek.translate_group(0, - self.box_external_depth + self.box_material_thickness + -self.box_external_height + self.box_material_thickness))
        if self.show_guides:
          inksnek.add_rect(bottom, self.box_material_thickness, self.box_material_thickness, self.box_internal_width, self.box_internal_depth, inksnek.ignore_style)
          inksnek.add_rect(bottom, 0, 0, self.box_external_width, self.box_external_depth, inksnek.ignore_style)
        if self.show_labels:
          inksnek.add_annotation(bottom, self.label_offset, self.label_offset, "U", self.label_size, inksnek.ignore_style)

        # bottom
        path  = inksnek.path_move_to(0, 0)
        path += inksnek.path_line_to(tab_size, 0)
        path += inksnek.path_line_to(tab_size, self.box_material_thickness)
        path += inksnek.path_line_to(self.box_external_width - tab_size, self.box_material_thickness)
        path += inksnek.path_line_to(self.box_external_width - tab_size, 0)
        path += inksnek.path_line_to(self.box_external_width, 0)
        
        # right
        path += inksnek.path_line_to(self.box_external_width, tab_size)
        path += inksnek.path_line_to(self.box_external_width - self.box_material_thickness, tab_size)
        path += inksnek.path_line_to(self.box_external_width - self.box_material_thickness, self.box_external_depth - tab_size)
        path += inksnek.path_line_to(self.box_external_width, self.box_external_depth - tab_size)
        path += inksnek.path_line_to(self.box_external_width, self.box_external_depth)
        
        # top (inherited)
        path += inksnek.path_move_to(0, self.box_external_depth)
        
        # left
        path += inksnek.path_line_to(0, self.box_external_depth - tab_size)
        path += inksnek.path_line_to(self.box_material_thickness, self.box_external_depth - tab_size)
        path += inksnek.path_line_to(self.box_material_thickness, tab_size)
        path += inksnek.path_line_to(0, tab_size)
        path += inksnek.path_line_to(0, 0)

        inksnek.add_path(bottom, path, inksnek.cut_style)
        
        self.add_LCD(front, self.box_external_width, self.box_external_height)
        self.add_back_l_c_d_holes(back, self.box_external_width, self.box_external_height)
        self.add_panel_holes(back, self.box_external_width, self.box_external_height)
        #---------------------------------------------------------------------
    
    def effect(self):
        self.box_material_thickness = 3.0
        inksnek.setup(self, inksnek.A4, inksnek.ACRYLIC, self.box_material_thickness, 'mm', inksnek.DEVEL)
        
        
        self.etch = inksnek.heavy_etch_style

        # dims are mm
        self.margin = 0
        
        self.arduino_board_width = 68.6
        self.arduino_board_height = 53.3
        # PSU, USB, D0, A5:
        self.arduino_holes = [[14.0, 2.5, "PSU"],  [14.0+1.3, 2.5+5.1+27.9+15.2, "USB"], [14.0+1.3+50.8, 2.5+5.1+27.9, "D0"], [14.0+1.3+50.8, 2.5+5.1, "A5"]]
        self.arduino_hole_radius = 3.0/2.0
        
        self.lcd_board_width = 98.0
        self.lcd_board_height = 60.0
        self.lcd_holes_width = 93.0
        self.lcd_holes_height = 55.0
        self.lcd_screen_width = 98.0  # measured, vs "97.0"
        self.lcd_screen_height = 39.0 # measured, vs "39.5"
        self.lcd_hole_radius = 3.0/2.0
        self.screw_head_radius = 3.5/2.0
        
        self.box_internal_width  = 110.0
        self.box_internal_height = 80.0
        self.box_internal_depth  = 40.0  # for 50mm machine screws

        self.box_external_width  = self.box_internal_width  + self.box_material_thickness*2
        self.box_external_depth  = self.box_internal_depth  + self.box_material_thickness*2
        self.box_external_height = self.box_internal_height + self.box_material_thickness*2
        
        self.show_guides = True # show extra (Ignore) linework
        self.show_labels = True # label the parts
        self.label_size = 5
        self.label_offset = 5
        
        box_top_x = self.margin + self.box_external_depth
        box_top_y = inksnek.template_height - self.box_external_depth - self.box_external_height - self.margin
        self.add_box(box_top_x, box_top_y, 0)
