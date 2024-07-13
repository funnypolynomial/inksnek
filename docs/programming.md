# GROUPS
Every element in a design is part of a **group**.  
Groups help structure a design by organising elements into a hierarchy. 
They can also simplify the code by allowing elements to be added relative to `(0, 0)` in a group, with the group created in the desired location. 
In addition, groups can aid design validation. 
After some some initial un-grouping (_Shift-Ctrl-G_) to break up the heirarchy, larger grouped structures, like an enclosure plate, can be moved around, rotated etc, to check the fit with other structures.  

After calling `setup()`, the inksnek method `top_group()` provides a parent group.  Things can be added directly into this, but it is probably better to create subgroups.  For example
```
box_group = inksnek.add_group(inksnek.top_group(), inksnek.translate_group(10.0, 10.0))
```
This creates `box_group` as a child of the top group, located at `(10.0, 10.0)`.

# PATHS
Most elements in a design are **paths**. Paths have two important attributes, the _group_ they are in and their _style_.  
The path’s coordinates are relative to the group. Usually the style defines a stroked line, but can also be a fill (or even both).
The pattern for a simple path is something like this:
```
box_path = inksnek.path_start() # Note: box_path is a string
box_path += inksnek.path_move_to(10.0, 10.0)
box_path += inksnek.path_horz_by(5.0)
box_path += inksnek.path_vert_by(5.0)
box_path += inksnek.path_horz_by(-5.0)
inksnek.path_add(box_group, box_path, inknek.cut_style)
```
This creates a 5x5 square at `(10, 10)` within `box_group`, to be laser-cut. 
Based on the creation of `box_group` above, the box will be at `(20, 20)` from the design origin (the origin of `top_group`).

# STYLES
The class creates three predefined styles, for line cutting and etching and for area etches:  
`cut_style`  
`etch_style`  
`fill_style`  
In addition  
`ignore_style`  
creates linework which is visible in `DEVEL` mode but is omitted from the SVG in `FINAL` mode.
