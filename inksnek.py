#! /usr/bin/env python
'''
Mark Wilson
Python helper class for creating structured designs in Inkscape

2016: Created to assist creating laser-cut project enclosures etc in Inkscape 0.92, to be sent to Ponoko.com
2024: Mods for Inkscape 1.3.2, cleaned up, rationalised a bit

Distances are in the units specified in setup(), eg "mm"/"in"/"px"
Angles are in degrees turned clockwise from 12 O'Clock

'''

import sys
from math import *
import inkex
from inkex import PathElement,Circle,Group,TextElement

class Inksnek:
    def __init__(self):
        self.template_number = 0
        self.top_group = None

    # CONSTANTS 
    # mode
    DEVEL = 0     # Cut/etch colours; IgnoreStyle shown, 10x thicker lines
    FINAL = 1     # LASER-READY; IgnoreStyle hidden, fine lines
    REAL  = 2     # Realistic look; etches are shades of gray, fills are degrees of transparency, cuts are black, ignore is omitted, 20x thicker lines
    PRINT = 3     # Printable, all cut, etch & ignore lines are black, fills are omitted, 10x thicker lines
    PROTO = 4     # Prototype; cuttable (by hand), all cut, & etch lines are black, ignore & fills are omitted, 10x thicker lines
    
    # templates
    CUSTOM, A3, A4 = 0, 1, 2

    # materials
    ACRYLIC, STYRENE, CARD, WOOD = 0,1,2,3
    
    # annotation alignments, can be added. 3 in the x-direction, 3 in the y.
    LEFT_ALIGN, CENTRE_ALIGN, RIGHT_ALIGN,  BASE_ALIGN, TOP_ALIGN, MID_ALIGN = 0x00,0x02,0x04,0x00,0x08,0x10
    
    
    def setup(self, effect, template_number, material, thickness, units, mode):
        self._Effect = effect
        self.template_number = template_number
        if self.template_number == self.A3:
            self.template_height = 420.0
            self.template_width  = 297.0
            self.template_margin = 0.0
        if self.template_number == self.A4:
            self.template_height = 297.0
            self.template_width  = 210.0
            self.template_margin = 0.0
        else:
            self.template_margin = 5.0
        self.units = "mm"
        self.material = material
        self.material_thickness = thickness
        self.line_width = self._length(0.01, "mm")
        self._last_xy = (0, 0)
        self.mode = mode
        
        # * Cut  = Blue
        # * Etch = Red
        # * Fill = Black
        
        if self.mode != Inksnek.FINAL:
          # thicker (more visible) lines when developing
          self.line_width = self._length(0.1, "mm")
          # and use transparency for fills
          Inksnek._light_fill_colour  = "#000000"
          Inksnek._medium_fill_colour = "#000000"
          Inksnek._heavy_fill_colour  = "#000000"
          Inksnek._light_fill_opacity = "0.25"
          Inksnek._medium_fill_opacity= "0.50"
          Inksnek._heavy_fill_opacity = "0.75"
          
        if self.mode == Inksnek.REAL:
          # cuts are black
          Inksnek._cut_colour        = "#000000"
          # grays for intensity of etch
          Inksnek._light_etch_colour  = "#AAAAAA"
          Inksnek._medium_etch_colour = "#555555"
          Inksnek._heavy_etch_colour  = "#000000"
          # make the colour show
          self.line_width = self._length(0.2, "mm")
        elif self.mode == Inksnek.PRINT:
          # everything is black
          Inksnek._cut_colour        = "#000000"
          # gray for etch
          Inksnek._light_etch_colour  = "#000000"
          Inksnek._medium_etch_colour = "#000000"
          Inksnek._heavy_etch_colour  = "#000000"
          Inksnek._ignore_colour     = "#000000"
          # no fills
          Inksnek._light_fill_opacity = Inksnek._medium_fill_opacity = Inksnek._heavy_fill_opacity  = "0"
        elif self.mode == Inksnek.PROTO:
          # everything is black
          Inksnek._cut_colour        = "#000000"
          # gray for etch
          Inksnek._light_etch_colour  = "#000000"
          Inksnek._medium_etch_colour = "#000000"
          Inksnek._heavy_etch_colour  = "#000000"
          # no fills
          Inksnek._light_fill_opacity = Inksnek._medium_fill_opacity = Inksnek._heavy_fill_opacity  = "0"

        
        # cut-through linestyle 
        self.cut_style        = str(inkex.Style({"stroke":Inksnek._cut_colour,        "stroke-width":self.line_width, "fill":"none"}))
        
        # etch-into linestyle(s)
        self.light_etch_style  = str(inkex.Style({"stroke":Inksnek._light_etch_colour,  "stroke-width":self.line_width, "fill":"none"}))
        self.medium_etch_style = str(inkex.Style({"stroke":Inksnek._medium_etch_colour, "stroke-width":self.line_width, "fill":"none"}))
        self.heavy_etch_style  = str(inkex.Style({"stroke":Inksnek._heavy_etch_colour,  "stroke-width":self.line_width, "fill":"none"}))
        self.etch_style = self.heavy_etch_style
        
        # area-etch fillstyle(s)
        self.light_fill_style  = str(inkex.Style({"stroke":"none", "stroke-width":"none", "fill":Inksnek._light_fill_colour, "opacity":Inksnek._light_fill_opacity}))
        self.medium_fill_style = str(inkex.Style({"stroke":"none", "stroke-width":"none", "fill":Inksnek._medium_fill_colour, "opacity":Inksnek._medium_fill_opacity}))
        self.heavy_fill_style  = str(inkex.Style({"stroke":"none", "stroke-width":"none", "fill":Inksnek._heavy_fill_colour, "opacity":Inksnek._heavy_fill_opacity}))
        self.fill_style = self.heavy_fill_style
        
        # visible in design, but N/A for laser (but see _Ignore)
        self.ignore_style     = str(inkex.Style({"stroke":Inksnek._ignore_colour,     "stroke-width":self.line_width, "fill":"none"}))
        
        origin_x = 0
        origin_y = 0
        if self.template_number != 0:
            # adjust absolute coords for template area.  other coords are relative
            origin_x += self.template_margin
            origin_y -= self.template_height+self.template_margin
        self.top_group = Group("design")
        self.top_group.set("transform", self.translate_group(origin_x, origin_y))
        self._Effect.svg.get_current_layer().add(self.top_group)
        self.units = units
    
    def set_custom_template(self, width, height, margin):
        self.template_number = self.CUSTOM
        self.template_width  = width
        self.template_height = height
        self.template_margin = margin
        origin_x = self.template_margin
        origin_y = -(self.template_height - self.template_margin)
        self.template_width  -= 2*margin
        self.template_height -= 2*margin
        self.top_group = Group("design")
        self.top_group.set("transform", self.translate_group(origin_x, origin_y))
        self._Effect.svg.get_current_layer().add(self.top_group)
        
    def debug(self, thing): # will show in an "Inkscape has received additional data from the script executed." window
      inkex.utils.debug(thing)

    # transformations to pass to addGroup, can be added together
    def translate_group(self, delta_x, delta_y):
        return " translate(" + str(self._x_coord(delta_x)) + "," + str(self._y_coord(delta_y)) + ") "
        
    def rotate_group(self, angle_degrees):  # angle is clockwise DEGREES
        return " rotate(" + str(angle_degrees) + ") "

    def scale_group(self, scale_x, scale_y = None):
        if scale_y is None:
            return " scale(" + str(scale_x) + "," + str(scale_x) + ") "
        else:
            return " scale(" + str(scale_x) + "," + str(scale_y) + ") "
    
    def add_group(self, parent, transform):
        g = Group()
        g.set("transform", transform)
        return parent.add(g)
        
    def create_stroke_style(self, colour, width, opacity = 1.0):
        return str(inkex.Style({"stroke":colour, "stroke-width":inksnek._length(width, "px"), "fill":"none", "opacity":opacity}))
        
    def create_fill_style(self, colour, opacity = 1.0):
        return str(inkex.Style({"stroke":"none", "stroke-width":"none", "fill":colour, "opacity":opacity}))
        
    def create_style(self, line_colour, line_width, fill_colour, opacity = 1.0):
        return str(inkex.Style({"stroke":line_colour, "stroke-width":line_width, "fill":colour, "opacity":opacity}))
        
    def path_start(self): return ""  # for completeness
    # x and y or a tuple with (x, y)
    def path_move_to(self, x, y = None):  return "M"+Inksnek._coord_format_str % self._xy_coord(x, y)
    def path_line_to(self, x, y = None):  return "L"+Inksnek._coord_format_str % self._xy_coord(x, y)
    def path_move_by(self, x, y = None):  return "m"+Inksnek._coord_format_str % self._xy_coord(x, y)
    def path_line_by(self, x, y = None):  return "l"+Inksnek._coord_format_str % self._xy_coord(x, y)
    
    def path_horz_to(self, h):            return "H"+Inksnek._ord_format_str % self._x_coord(h)
    def path_vert_to(self, v):            return "V"+Inksnek._ord_format_str % self._y_coord(v)
    def path_horz_by(self, h):            return "h"+Inksnek._ord_format_str % self._x_coord(h)
    def path_vert_by(self, v):            return "v"+Inksnek._ord_format_str % self._y_coord(v)
    
    def path_round_by(self, x, y, R):     # 90 deg "round" arc, drawn in x, y direction, -ve R means anti-clockwise, no validation
      # for example, pathRoundBy(+R, +R, -R) will add a 90deg anti-clockwise arc, sweeping RIGHT and UP
      if R == 0.0:
        return ""
      else:
        return "a %.3f %.3f 0 0 %i" % (self._length(abs(R)), self._length(abs(R)), R > 0) + " %.3f %.3f" % self._xy_coord(x, y)
    
    # needs to be preceded by pathMoveTo or pathLineTo (*not* By, Horz or Vert variants)
    def path_arrow_to(self, x, y, length): 
        prev = self._last_xy
        path = self.path_line_to(x, y)
        this = self._last_xy
        delta_x = this[0] - prev[0]
        delta_y = this[1] - prev[1]
        angle = pi - atan2(delta_y, delta_x)
        head_angle = atan2(1.0, 3.0)   # 3:1 ratio
        path += self.path_line_by(self.polar_to_rectangular(self._length(length), self.radians_to_degrees(angle + head_angle)))
        path += self.path_move_to(x, y)
        path += self.path_line_by(self.polar_to_rectangular(self._length(length), self.radians_to_degrees(angle - head_angle)))
        path += self.path_move_to(x, y)
        return path
    
    def path_close(self): return "z"
    
    def add_path(self, group, path, style):
        # add the path with the style to the group
        if path != "" and not self._ignore(style):  # Avoid SVG with an empty path
            p = PathElement()
            p.style = style
            p.path = path
            return group.add(p)
        else:
            return None;

    def add_line_by(self, group, x, y, delta_x, delta_y, style):
      return self.add_path(group, "M"+Inksnek._coord_format_str % self._xy_coord(x, y) + "l"+Inksnek._coord_format_str % self._xy_coord(delta_x, delta_y), style)
    
    def add_line_to(self, group, x1, y1, x2, y2, style):
      return self.add_path(group, "M"+Inksnek._coord_format_str % self._xy_coord(x1, y1) + "L"+Inksnek._coord_format_str % self._xy_coord(x2, y2), style)
      
    def add_rect(self, group, x, y, width, height, style, sides="TLRB"):
        # add the rectangle with the style to the group
        # sides can be a string consisting of the characters "TLRB" to draw the Top, Left, Right and/or Bottom sides
        path  = self.path_move_to(x, y)
        path += self.path_horz_by(+width)      if "B" in sides else self.path_move_by(+width, 0)
        path += self.path_vert_by(+height)     if "R" in sides else self.path_move_by(0,      +height)
        path += self.path_horz_by(-width)      if "T" in sides else self.path_move_by(-width, 0)
        if sides != "TLRB":
            path += self.path_vert_by(-height) if "L" in sides else self.path_move_by(0,      -height)
        else:
            path += self.path_close()
        return self.add_path(group, path, style)
        
    def add_round_rect(self, group, x, y, width, height, radius, style):
        # add the rectangle with rounded corners, and with the style, to the group
        path  = self.path_move_to(x + width - radius, y)  + self.path_round_by(+radius, +radius, -radius)
        path += self.path_vert_by(height - 2.0*radius)    + self.path_round_by(-radius, +radius, -radius)
        path += self.path_horz_by(-(width - 2.0*radius))  + self.path_round_by(-radius, -radius, -radius)
        path += self.path_vert_by(-(height - 2.0*radius)) + self.path_round_by(+radius, -radius, -radius)
        path += self.path_close()
        return self.add_path(group, path, style)
        
    def add_circle(self, group, x, y, radius, style):
        # add a circle
        if self._ignore(style):  return None
        c = Circle()
        c.style = style
        c.radius = self._length(radius)
        c.center = (self._x_coord(x), self._y_coord(y))
        return group.add(c)
        
    def add_arc(self, group, cx, cy, radius, start_angle_deg, end_angle_deg, style, large = None):
        # arc is clockwise from startAngle to endAngle, anticlockwise if radius < 0, large is deduced unless specified
        # https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/d
        # "(rx ry x-axis-rotation large-arc-flag sweep-flag x y)
        #  Draws an elliptical arc from the current point to (x, y). 
        #  The size and orientation of the ellipse are defined by two radii (rx, ry) and an x-axis-rotation, 
        #  which indicates how the ellipse as a whole is rotated relative to the current coordinate system. 
        #  The center (cx, cy) of the ellipse is calculated automatically to satisfy the constraints imposed by the other parameters. 
        #  large-arc-flag (1=large) and sweep-flag (1=clockwise) contribute to the automatic calculations and help determine how the arc is drawn."
        if large == None:
            start_angle_deg = self.normalise_angle(start_angle_deg)
            end_angle_deg = self.normalise_angle(end_angle_deg)
            if radius > 0:  # clockwise
                span = end_angle_deg - start_angle_deg
            else:    
                span = start_angle_deg - end_angle_deg
            large = abs(self.normalise_angle(span)) > 180
        abs_r = self._length(abs(radius))
        s = self.polar_to_rectangular(abs_r, start_angle_deg)
        e = self.polar_to_rectangular(abs_r, end_angle_deg)
        path = self.path_move_to(cx + s[0], cy + s[1]) + "A %.3f %.3f 0 %i %i" % (abs_r, abs_r, large, radius > 0) + " %.3f %.3f" % self._xy_coord((cx + e[0], cy + e[1]))
        return self.add_path(group, path, style)

    def add_X_marker(self, group, x, y, size = 2.0, style = None):
        # add an 'X'
        if style is None:  style = self.ignore_style
        g = self.add_group(group, self.translate_group(x, y))
        path =  self.path_move_to(-size, -size)
        path += self.path_line_to(+size, +size)
        path += self.path_move_to(-size, +size)
        path += self.path_line_to(+size, -size)
        return self.add_path(g, path, style)
        
    def add_hole(self, group, x, y, radius, style = None):
        # add a circle, cut by default
        if style is None:  style = self.cut_style
        self.add_circle(group, x, y, radius, style)
    
    def add_text(self, group, x, y, size, family, text, spacing = 0, align = "center", anchor = "middle", style = None):
        # add text. This is rudimentary!
        # https://inkscape.gitlab.io/extensions/documentation/source/inkex.elements._text.html#inkex.elements._text.TextElement
        if style is None:  style = self.fill_style
        if self._ignore(style):  return None
        tstyle = {'text-align' : align, 'text-anchor': anchor, 'font-size':self._length(size), 'font-family':family, 'letter-spacing':self._length(spacing)}
        tstyle.update(inkex.Style.parse_str( style ))
        txt = inkex.TextElement()
        txt.set("x", str(self._x_coord(x)))
        txt.set("y", str(self._y_coord(y)))
        txt.set("style", str(inkex.Style(tstyle)))
        txt.text = text
        group.add(txt)
        
    def add_shape(self, group, x, y, scale_x, scale_y, shape, style):
        # shape is [[x1,y1], [x2,y2], ...]. draw-to's are [x,y], moves are [[x,y]], a close is [].
        # nodes are at (x + xN*scaleX, y + yN*scaleY)
        path = self.path_start()
        for idx in range(len(shape)):
          node = shape[idx]
          if len(node) == 2:
            path += self.path_line_to(x + node[0]*scale_x, y + node[1]*scale_y)
          elif len(node) == 1:
            path += self.path_move_to(x + node[0][0]*scale_x, y + node[0][1]*scale_y)
          elif len(node) == 0:
            path += self.path_close()
        self.add_path(group, path, style)
    
    def add_annotation(self, group, x, y, text, size = 2.0, style = None, align = 0):
        # add text using a simple stroked "font", see annotationPath
        if style is None:  style = self.ignore_style
        self.add_path(group, self.annotation_path(x, y, text, size, align), style)
        
    def annotation_path(self, x, y, text, size, align = 0):
        # return a path of the text stroked using a simple "font"
        # size is height, width is height/2, spacing between letters is width/2 (height/4), between lines 1.5*height
        # additional control characters:  \n (\x0D) line feed; \x08 backspace; \x11,\x10 lower, higher; 
        #       \x0F,\x0E narrower, wider; \x1F,\x1E shorter, taller; \x1B underline toggle; 0xFn italic n=0 none, n=F max
        if text == "":  return None;
        linestext = maxlinelen = linelen = 0
        for ch in text: 
            if ch == '\n':
                maxlinelen, linelen, linestext = max(maxlinelen, linelen), 0, linestext+1
            else:
                linelen += (0, 1)[' ' <= ch and ch <= self._strokes_last_char]    # count non-control chars
        maxlinelen = max(maxlinelen, linelen)
        linestext += 1
        x_scale, y_scale = size/4.0, size/2.0
        x_origin, y_origin = x, y
        if align & self.CENTRE_ALIGN:
          x_origin -= (maxlinelen*3.0*x_scale - x_scale)/2.0
        elif align & self.RIGHT_ALIGN:
          x_origin -= maxlinelen*3.0*x_scale - x_scale
        if align & self.TOP_ALIGN:
          y_origin -= 2.0*y_scale
        elif align & self.MID_ALIGN:
          y_origin -= y_scale - y_scale*3.0*(linestext - 1)/2.0
        x = x_origin
        underline = False
        italic = 0.0
        path = ""
        for ch in text:
            if ch == '\n': x_origin = x; y_origin -= 3.0*y_scale; continue # basic newline
            elif ch == chr(0x11): y_origin -= 0.25*y_scale;  continue    # lower
            elif ch == chr(0x10): y_origin += 0.25*y_scale;  continue    # higher
            elif ch == chr(0x0F): x_scale  *= 0.75;          continue    # narrower
            elif ch == chr(0x0E): x_scale  /= 0.75;          continue    # wider
            elif ch == chr(0x1F): y_scale  *= 0.75;          continue    # shorter
            elif ch == chr(0x1E): y_scale  /= 0.75;          continue    # taller           
            elif ch == chr(0x08): x_origin -= 3.0*x_scale;   continue    # backspace
            elif ch == chr(0x1B): underline = not underline; continue # underline
            elif ch >= chr(0xF0) and ch <= chr(0xFF): italic = (ord(ch) - 0xF0)/15.0; continue # italic
            strokes = self._strokes[ (31, ord(ch) - 32)[' ' <= ch and ch <= self._strokes_last_char] ]   # use '?' if not defined 
            box, prev, scale_y, shift_y = False, None, 1.0, 0.0
            if (strokes & 0x0F) <= 0x07:  # ends with a move, special values
                if (strokes & 0x03) == 0x01:
                    scale_y = 0.5 # half vertical scale
                elif (strokes & 0x03) == 0x02:
                    shift_y = -y_scale # drop half height
                elif (strokes & 0x03) == 0x03:
                    shift_y = -y_scale/2.0 # drop quarter height
                if (strokes & 0x04) == 0x04: # middle dot
                    path += self.path_move_to(x_origin + x_scale + (y_scale + x_scale/2.0)*italic, y_origin + y_scale + x_scale/2.0)
                    box = True
                strokes &= 0xFFFFFFF0 # clear it
            for cmd in range(8):
                if box:
                    path += self.path_horz_by(x_scale/2.0) + self.path_vert_by(x_scale/2.0) + self.path_horz_by(-x_scale/2.0) + self.path_vert_by(-x_scale/2.0)
                    box = False
                nibble = (strokes & 0xF0000000) >> 28
                strokes <<= 4
                node_idx = nibble & 0x07
                y_ord = ((0x22211000 >> node_idx*4) & 0x0F)*y_scale*scale_y + shift_y
                y = y_origin + y_ord
                x = x_origin + ((0x21020210 >> node_idx*4) & 0x0F)*x_scale + y_ord*italic
                if nibble & 0x08:  # high bit=draw
                    if cmd == 0:  path += self.path_move_to(x_origin + shift_y*italic, y_origin + shift_y)  # start with a draw: insert a move 0
                    path += self.path_line_to(x, y)
                    box = not prev is None and node_idx == (prev & 0x07)
                else:
                    if prev == nibble and nibble == 0:  x, y = x_origin + x_scale + (y_scale*scale_y + shift_y)*italic, y_origin + y_scale*scale_y + shift_y # 0,0=centre
                    if strokes == 0:  break # ignore *trailing* 0's
                    path += self.path_move_to(x, y)
                prev = nibble
            if underline: path += self.path_move_to(x_origin, y_origin - y_scale/2.0) + self.path_line_by(3.0*x_scale, 0)
            x_origin += 3.0*x_scale
        return path
        
    perf_board_pitch = 2.54
    
    # return distance spanned by the number of perfboard holes
    def on_perf_board(self, holes): return int(holes)*self.perf_board_pitch
    
    def add_perf_board(self, group, x, y, cols, rows, style = None): # grid of cols x rows holes, 2.54mm apart, 1mm diameter
      if style is None:  style = self.ignore_style
      board = self.add_group(group, self.translate_group(x, y))
      for col in range(cols):
        for row in range(rows):
          self.add_circle(board, self.on_perf_board(col), self.on_perf_board(row), 0.5, style)
            
    def degrees_to_radians(self, angle_degrees):
        # angleDegrees is degrees clockwise from 12 O'clock, returns radians anti-clockwise from 3 O'Clock
        return pi*(90.0 - angle_degrees)/180.0
        
    def radians_to_degrees(self, angle_radians):
        # angleRadians is radians anti-clockwise from 3 O'Clock, returns degrees clockwise from 12 O'clock
        return 90.0 - (180.0*angle_radians/pi)
        
    def polar_to_rectangular(self, radius, angle_degrees): # polar to rectangular
        x = radius * cos(self.degrees_to_radians(angle_degrees))
        y = radius * sin(self.degrees_to_radians(angle_degrees))
        return (x, y)
        
    def normalise_angle(self, degrees):
        while degrees > 360.0:
            degrees = degrees - 360
        while degrees < 0.0:
            degrees = degrees + 360
        return degrees
        
    def ignore_colour(self):
        # return the no-laser colour
        return self._ignore_colour
     
    ################ PRIVATE
    def _length(self, d, units = None): # transform distance from "user units" to inkscape internal
        if units is None:
            units = self.units
        uud = self._Effect.svg.unittouu(str(d) + units)
        return uud
        
    def _x_coord(self, x): # transform x-coord from "user units" to inkscape internal
        uux = self._length(x)
        return uux
        
    def _y_coord(self, y): # transform y-coord from "user units" to inkscape internal
        uuy = -self._length(y)  # y increases DOWN
        return uuy
        
    def _xy_coord(self, x, y = None): # transform coords from "user units" to inkscape internal
        if y is None: # expect a tuple:
            self._last_xy = (self._x_coord(x[0]), self._y_coord(x[1]))
        else:
            self._last_xy = (self._x_coord(x), self._y_coord(y))
        return self._last_xy
        
    def _ignore(self, style):
        # Cutting service may not ignore N/A colours, so don't add things with that style if FINAL (or REAL)
        return (self.mode == Inksnek.FINAL or self.mode == Inksnek.REAL or self.mode == Inksnek.PROTO) and style.find(Inksnek._ignore_colour) != -1
        
    _cut_colour        = "#0000FF"
    _light_etch_colour  = "#FF00FF"
    _medium_etch_colour = "#00FF00"
    _heavy_etch_colour  = "#FF0000"
    _light_fill_colour  = "#E6E6E6"
    _medium_fill_colour = "#808080"
    _heavy_fill_colour  = "#000000"
    _ignore_colour     = "#F6921E"
    
    _light_fill_opacity  = "1"
    _medium_fill_opacity = "1"
    _heavy_fill_opacity  = "1"
    
    _ord_format_str     = "%.3f"    # 3dps
    _coord_format_str   = _ord_format_str+","+_ord_format_str

    # Simple line font
    # Each nibble, starting from most significant, is a command and vertex on these grids
    # move:    draw:
    # 5 6 7    D E F
    # 3 X 4    B   C
    # 0 1 2    8 9 A     (eg 0x5A draws a diagonal line)
    #  * If the FIRST command is a DRAW, a MOVE 0 is inserted before it
    #  * Two consecutive 0's are interpreted as a MOVE to the CENTRE node (X)
    #  * A zero-length DRAW draws a small box/dot at the vertex (eg for '?')
    #  * Trailing 0's are ignored
    #  * If the least significant nibble (last) is a MOVE, it instead transforms the shape thus:
    #     1   : shrink by half (eg 's')
    #     2,3 : lower by half, quarter (eg 'p')
    #     bit3: box/dot at centre (X) (eg 'j')
    _strokes = [0x00000000,0x00E19000,0x3D00E000,0xE1F5C3A0,0x7DBCA81E,0xFDBE4A9C,0x49BEDA00,0x00E00000,  # <sp>!"#$%&'
                0x6B900000,0x6C900000,0x5A69783C,0x693C0000,0x1CC00003,0x3C000000,0x19000000,0x0F000000,  # ()*+,-./
                0x5FA8D780,0x5E90A000,0x5FCB8A00,0x5FCB4A80,0x5BC7A000,0x7DBCA800,0x7D8ACB00,0x5FA00000,0x5FA8D3C0,0x5FA5BC00, # '0'...'9' 0x69000000 is a sans-serif '1'
                0x19000004,0x1CC7F003,0x2BF00000,0x5F3C0003,0x5C800000,0x1900CFDB,0x28DFCBEC, # :;<=>?@
                0x2FD83C00,0x00FD89CB,0x7D8A0000,0x589CED00,0x7D8A00B0,0x7D800B00,0x7D8AC00C,0x587A3C00,0x5F286900,0x5F698000,0x583F3A00,0x58A00000,0x2FD86900, # 'A'...'M'
                0x7AD80000,0x5FA8D000,0x3CFD8000,0xAFD8A00A,0xDFCB00A0,0x7DBCA800,0x5F690000,0x58AF0000,0x59F00000,0x58AF1E00,0x0F5A0000,0x5BC7A800,0x5F8A0000, # 'N'...'Z'
                0x29EF0000,0x5A000000,0x5E980000,0xA0000000,0x3EC00000,0x00D00000, # [\]_^`
                0x5FA8BC01,0x58ACB000,0x28BC0000,0x7A8BC000,0x28DFCB01,0x1EF3C000,0xAFDBC002,0xD3CA0000,0x00900004,0x9E000006,0xD3A3C000,0x1E000000,0xBCA00900, # 'a'...'m'
                0xD3EFA001,0xBCA80000,0xDFCB8002,0x2FDBC002,0xD3EF0001,0xACBDF001,0x29E3C000,0x589CFA01,0x39C00000,0x38AC0090,0xC3A00000,0x5BCF4A82,0x3C8A0000, # 'n'...'z'
                0x29EF00B0,0x1E000000,0x9ED00C00,0x3DCF0001,  # {|}~
                
                0x1BEC9000,0x4BE1B000,0x3CE1C000,0x1EB4E000,0x69B49000,0x3CFDB000,0x7DBC9800] # 0x7F-0x85=diamond, left-, right-, up-, down-arrows, degree, alt-5
    _strokes_last_char = '\x85'
                                  
                 
        
# global instance  
inksnek = Inksnek()

