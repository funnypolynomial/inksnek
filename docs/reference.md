# class Inksnek Reference
There is a single instance of the class:
```
# global instance  
inksnek = Inksnek()
```

## STATICS/CONSTANTS

### Design modes:   `DEVEL, FINAL, REAL, PRINT, PROTO`
`DEVEL` is for _working_ on a design.  
`FINAL` is for _sending to be laser cut_ -- lines are finer, `ignore_style`/`ignore_colour` objects are omitted.  
`REAL` attempts a _realistic_ look -- etches are shades of gray, fills are degrees of transparency, cuts are black, ignore is omitted, lines are thicker.  
`PRINT` is intended for _printing_ -- all cut, etch and ignore lines are black, fills are omitted, lines are thicker.  
`PROTO` this is intended for printing the cutting by hand, all cut, and etch lines are black, ignore and fills are omitted, lines are thicker.  
    
### Templates:  `CUSTOM, A3, A4`
These are a bit of a hold-over from my original usage, where designs were cut from fixed-size sheets.
Setting the template sets `template_width`, `template_height` and `template_margin`
If `CUSTOM` is used, call `set_custom_template()`
    
### Materials:  `ACRYLIC, STYRENE, CARD, WOOD`
Somewhat moot, but in theory a design could adjust itself to the selected material.

### Alignment:  `LEFT_ALIGN, CENTRE_ALIGN, RIGHT_ALIGN, BASE_ALIGN, TOP_ALIGN, MID_ALIGN`
Passed to `add_annotation()` to align text

## METHODS/MEMBERS
### Setup
`setup(self, effect, template_number, material, thickness, units, mode)`  
A design starts with this, it should be the first call in `effect()`, it sets up the class for rendering a design.  
`effect` -- use `self`  
`template_number` -- use a **Template** from above.  
`material` -- use a **Material** from above.  
`thickness` -- provide the target material's thickness, available to the subsequent design code as `material_thickness`.  
`units` -- "mm", "in" or "px".  Sets the units of all numbers used in the design.  
`mode` -- use a **Design mode** from above.  

`set_custom_template(self, width, height, margin)`  
Use this to define a custom template.
        
### Debug
`debug(self, thing)`  
Will show the `thing` in an _"Inkscape has received additional data from the script executed"_ window.

### Groups
`add_group(self, parent, transform)`  
Returns a new group, a child of `parent`, and transformed as specified.

These three return transformations which are passed to `add_group`. They can be **added together**.  
`translate_group(self, delta_x, delta_y)`  
Moves the group by `delta_x` and `delta_y`

`rotate_group(self, angle_degrees)`  
Rotates the group _clockwise_ by `angle_degrees`.

`scale_group(self, scale_x, scale_y = None)`  
Scales the group. If `scale_y` is omitted, `scale_x` is used.
    

### Styles
#### Members
Predefined styles:  
`cut_style`  
Specifies a **laser cut line** through the material. A thin blue line.  

`etch_style`
Specifies a **laser etched line** into the material. A thin red line.  

`fill_style`  
Specifies a **laser etched area**. A black filled area.  

`ignore_style`  
Specifies a visible line **ignored by the laser**. A thin orange line.

#### Methods
`ignore_colour()`  
Returns the "ignore" colour which will not be used in the `FINAL` design.  

(Opacity of 1.0 means fully opaque, 0.0 is fully transparent.)
        
`create_stroke_style(self, colour, width, opacity = 1.0)`  
Returns a style for stroked lines.
        
`create_fill_style(self, colour, opacity = 1.0)`  
Returns a style for filled areas.

`create_style(self, line_colour, line_width, fill_colour, opacity = 1.0)`  
Returns a style for stroked and filled areas.

### Paths
Paths are _strings_, these methods _add_ to a path.  
`path_start(self)`  
Starts a path.  For completeness. Just returns an empty string.

The following are arbitrary absolute or relative moves or draws. if y is omitted, x is assumed to be (x, y).

`path_move_to(self, x, y = None)`  
`path_line_to(self, x, y = None)`  
`path_move_by(self, x, y = None)`  
`path_line_by(self, x, y = None)`  

The following are absolute or relative moves or draws either _horizontally or vertically_.  
`path_horz_to(self, h)`  
`path_vert_to(self, v)`  
`path_horz_by(self, h)`  
`path_vert_by(self, v)`  
    
`path_round_by(self, x, y, R)`  
Returns a 90 degree _clockwise_ arc, drawn in the x and y direction, a negative R means _anti-clockwise_.  For example, `path_round_by(+R, +R, -R)` will add a 90 degree anti-clockwise arc, sweeping **right** and **up**, like a 'J'.

`path_arrow_to(self, x, y, length)`  
Adds an arrow from the previous `path_move_to` or `path_line_to` to (x, y). Arrowhead is of the given length.

`path_close(self)`  
Closes the path (to the most recent move).
    
`add_path(self, group, path, style)`  
Adds the path with the given `style` to the given `group`.

### Linework
`add_line_by(self, group, x, y, delta_x, delta_y, style)`  
Adds a line to the `group`, with the `style`, from `(x, y)` extending by `(delta_x, delta_y)`.

`add_line_to(self, group, x1, y1, x2, y2, style)`  
Adds a line to the `group`, with the `style`, from `(x, y)` to `(x2, y2)`.
  
`add_rect(self, group, x, y, width, height, style, sides="TLRB")`  
Adds a rectangle to the `group`, with the `style`, from `(x, y)` with the given `width` and `height`.  `sides` can be a string consisting of the characters "TLRB" to draw the Top, Left, Right and/or Bottom sides.
        
`add_round_rect(self, group, x, y, width, height, radius, style)`  
Adds a rectangle to the `group`, with the `style`, from `(x, y)` with the given `width` and `height`.  Corners are rounded with the given `radius`.
        
`add_circle(self, group, x, y, radius, style)`  
Adds a circle to the `group`, with the `style`, at `(x, y)` with the given `radius`.
        
`add_arc(self, group, cx, cy, radius, start_angle_deg, end_angle_deg, style, large = None)`  
Adds an arc to the `group`, with the `style`, _clockwise_, centred at `(x, y)` between the given angles, with the given `radius`.  The angles are clockwise degrees from 12 O'clock.  The arc is drawn _anticlockwise_ if `radius` is negative.  `large` is deduced unless specified.

`add_X_marker(self, group, x, y, size = 2.0, style = None)`  
Adds an 'X' to the `group` at `(x, y)`. The `style` defaults to `ignore_style`.
        
`add_hole(self, group, x, y, radius, style = None)`  
Adds a circle to the `group`, at `(x, y)` with the given `radius`. The `style` is `cut_style` by default.

### Text
`add_annotation(self, group, x, y, text, size = 2.0, style = None, align = 0)`  
Adds `text` to the `group`, with the `style`, at `(x, y)` of the given `size`. The `style` is `ignore_style` by default. `align` is an **Alignment** above, defaults to left-aligned on the baseline.  Uses a simple stroked "font", see `annotation_path()`.

`annotation_path(self, x, y, text, size, align = 0)`  
Returns a path of the text's strokes.

`add_text(self, group, x, y, size, family, text, spacing = 0, align = "center", anchor = "middle", style = None)`  
Adds `text` to the `group`, with the `style`, at `(x, y)`. Uses the given `size` and font `family` etc, the `style` is `fill_style` by default.  _This is rudimentary!_

### Shapes
A shape is a way of representing a complex path, it is of the form `[[x1,y1], [x2,y2], ...]`. **Draws** are `[x,y]`, **moves** are `[[x,y]]`, a **close** is `[]`.

`add_shape(self, group, x, y, scale_x, scale_y, shape, style)`  
Adds the `shape` as a _path_ in the `group`, _translated_ to `(x, y)` and _scaled_.

### Perf Board
#### Members
`perf_board_pitch = 2.54`
Pitch used below.  

#### Methods
`on_perf_board(self, holes)`  
Returns the distance spanned by the number of perfboard holes.
    
`add_perf_board(self, group, x, y, cols, rows, style = None)`  
Adds perfboard circles to the `group` in a grid of `cols` by `rows` holes, `perf_board_pitch` apart, 1mm diameter. The `style` is `ignore_style` by default.
            
### Utilities
`degrees_to_radians(self, angle_degrees)`  
Returns _radians anti-clockwise from 3 O'clock_, `angle_degrees` is _degrees clockwise from 12 O'clock_. 
        
`radians_to_degrees(self, angle_radians)`  
Returns _degrees clockwise from 12 O'clock_, `angle_radians` is _radians anti-clockwise from 3 O'clock_. 
        
`polar_to_rectangular(self, radius, angle_degrees)`  
Returns `(x, y)` corresponding to the `radius` at the angle. `angle_degrees` is _degrees clockwise from 12 O'clock_. 
        
`normalise_angle(self, degrees)`  
Returns `degrees` normalised to `[0,360)`.
        

### Other Members
```
units
material
material_thickness
line_width
mode
template_number
template_height
template_width
template_margin
```