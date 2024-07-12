#! /usr/bin/env python
'''
Mark Wilson 2016
16, 14 & 7-segment LED font
'''
from math import *

class NSegmentFont:
  # segments is 16, 14 or 7. 
  # width & heigh are dims of whole "character" 
  # skew is distance top is shifted to the right
  # gap is how far short of the corners the elements end
  # thick is how thick the elements are (0 makes simple lines)
  
  def __init__(self, segments, width, height, skew, gap, thick):
    (self.segments, self.width, self.height, self.skew, self.gap, self.thick) = (segments, width, height, skew, gap, thick)
    self._list = []
    self._draw_count = 0
    
  # 16 segments:
  #    -A-  -B-
  # |C \D |E /F |G
  #    -H-  -I-
  # |J /K |L \M |N
  #    -O-  -P-
  
  # 14 segments:
  #      --A--
  # |B \C |D /E |F
  #    -G-  -H-
  # |I /J |K \L |M
  #     --N--
  
  # 7 segments:
  #  --A--
  # |B   C|
  #   -D-
  # |E   F|
  #  --G--
      
  # segment lists have [[x, y]] as a moveto, [x,y] as a lineto and [] as a close ...
  
  # char is a CHARACTER, like 'B' or '2', 
  # custom is a list of strings of segment names, if char is \x0n, the n'th string will be used to define the segments, no validation
  def get_char_segments_list(self, char, origin_x, origin_y, custom = None):
    if self.segments == 16:
      font = self._16segment_font
    elif self.segments == 14:
      font = self._14segment_font
    elif self.segments == 7:
      font = self._7segment_font
    else:
      return []
    if char <= '\x0F':
      return self.get_named_segments_list(custom[ord(char)], origin_x, origin_y)
      
    for defn in font:
      if defn[0] == char:
        return self.get_named_segments_list(defn[1], origin_x, origin_y)
    return []

  def get_named_segments_list(self, segment_names, origin_x, origin_y): # segmentNames is a string of segment NAMES, 'A' etc, or "*" for all
    list = []
    for segment in range(self.segments):
      if segment_names.find(chr(segment + ord('A'))) != -1 or segment_names == '*':
        list += self.get_segment_list(segment, origin_x, origin_y)
    return list
    
  def get_segment_list(self, segment_num, origin_x, origin_y): # returns nodes for the segmentNum
    if self.segments == 16 and segment_num < 16:
      seg_defn = self._16segment_definition[segment_num]
    elif self.segments == 14 and segment_num < 14:
      seg_defn = self._14segment_definition[segment_num]
    elif self.segments == 7 and segment_num < 7:
      seg_defn = self._7segment_definition[segment_num]
    else:
      return []
      
    self.origin_y = origin_y
    (width, height, gap, thick) = (self.width, self.height, self.gap, self.thick)
    (seg_x0, seg_y0) = (seg_defn[0]/2.0, seg_defn[1]/2.0) # origin of segment
    (segd_x, segd_y) = (seg_defn[2],       seg_defn[3])   # deltas of segment
    (len_x, len_y) = (width/2.0*abs(segd_x) - 2*(gap + thick), height/2.0*abs(segd_y) - 2*(gap + thick)) # length of segment
    if segd_x != 0.0: segd_x /= abs(segd_x)
    if segd_y != 0.0: segd_y /= abs(segd_y)
    (org_x, org_y) = (origin_x + seg_x0*width  + segd_x*gap, origin_y + seg_y0*height + segd_y*gap)
    if segd_x == 0.0 and segd_y != 0.0:
      # vertical,  ^  or  _
      #           | |    | |
      #            v      v
      self._moveto(        org_x, org_y)
      self._lineby(-segd_y*thick, +segd_y*thick)
      self._lineby(           0, +segd_y*len_y)
      if len(seg_defn) == 5 and seg_defn[4]: # square cap at end
        self._lineby(+2.0*segd_y*thick, 0.0)
      else:
        self._lineby(+segd_y*thick,     +segd_y*thick)
        self._lineby(+segd_y*thick,     -segd_y*thick)
      self._lineby(           0, -segd_y*len_y)
    elif  segd_x != 0.0 and segd_y == 0.0:
      # horizontal, /----\
      #             \----/
      self._moveto(        org_x, org_y)
      self._lineby(+segd_x*thick, +segd_x*thick)
      self._lineby( +segd_x*len_x,      0)
      self._lineby(+segd_x*thick, -segd_x*thick)
      self._lineby(-segd_x*thick, -segd_x*thick)
      self._lineby( -segd_x*len_x, 0)
    else:
      # diagonal, outwards,  _
      #                     / |
      #                    |_/ 
      self._moveto(org_x + segd_x*thick, org_y + segd_y*thick)
      thick *= sqrt(2.0)/sin(pi/4.0 + atan2(len_y, len_x)) # keep the thickness the same
      len_x -= thick
      len_y -= thick
      self._lineby(0,            +thick*segd_y)
      self._lineby(+segd_x*len_x,  +segd_y*len_y)
      self._lineby(+segd_x*thick, 0)
      self._lineby(0,            -segd_y*thick)
      self._lineby(-segd_x*len_x,  -segd_y*len_y)
    self._close()
    return self._list
    
  def _moveto(self, x, y): 
    self._list = []
    self._add(x, y, True)
    
  def _lineby(self, dx, dy): 
    if dx != 0.0 or dy != 0.0: 
      self._add(self._prev_x + dx, self._prev_y + dy, False)
  
  def _close(self):
    if self._draw_count > 0:
      self._list += [[],]
    
  def _add(self, x, y, move): 
    (self._prev_x, self._prev_y) = (x, y)
    if move:
      self._draw_count = 0
      self._list += [[[x + self.skew*(y - self.origin_y)/self.height, y],],]
    else:
      self._draw_count += 1
      self._list += [[x + self.skew*(y - self.origin_y)/self.height, y],]
  
  # definitions are (x0, y0, dx, dy {,square end}) on a 2x2 grid. square end is optional, default False, only for vertical
  _16segment_definition = (
    (+0, +2,  +1, +0),
    (+1, +2,  +1, +0),

    (+0, +1,  +0, +1),
    (+0, +1,  +1, +1),
    (+1, +1,  +0, +1),
    (+2, +1,  -1, +1),
    (+2, +1,  +0, +1),

    (+0, +1,  +1, +0),
    (+1, +1,  +1, +0),

    (+0, +0,  +0, +1),
    (+0, +1,  +1, -1),
    (+1, +0,  +0, +1),
    (+2, +1,  -1, -1),
    (+2, +0,  +0, +1),

    (+0, +0,  +1, +0),
    (+1, +0,  +1, +0))

  _14segment_definition = (
    (+0, +2,  +2, +0),

    (+0, +1,  +0, +1),
    (+0, +1,  +1, +1),
    (+1, +1,  +0, +1, True),
    (+2, +1,  -1, +1),
    (+2, +1,  +0, +1),

    (+0, +1,  +1, +0),
    (+1, +1,  +1, +0),

    (+0, +0,  +0, +1),
    (+0, +1,  +1, -1),
    (+1, +1,  +0, -1, True),
    (+2, +1,  -1, -1),
    (+2, +0,  +0, +1),

    (+0, +0,  +2, +0))

  _7segment_definition = (
    (+0, +2,  +2, +0),

    (+0, +1,  +0, +1),
    (+2, +1,  +0, +1),

    (+0, +1,  +2, +0),

    (+0, +0,  +0, +1),
    (+2, +0,  +0, +1),

    (+0, +0,  +2, +0))
    
  # based on http://www.maximintegrated.com/app-notes/index.mvp/id/3212 but with mods   
  _16segment_font = (
      ('A', 'ABCGHIJN'),
      ('B', 'ABEGILNOP'),
      ('C', 'ABCJOP'),
      ('D', 'ABEGLNOP'),
      ('E', 'ABCHIJOP'),
      ('F', 'ABCHIJ'),
      ('G', 'ABCIJNOP'),
      ('H', 'CGHIJN'),
      ('I', 'ABELOP'),
      ('J', 'GJNOP'),
      ('K', 'CFHJM'),
      ('L', 'CJOP'),
      ('M', 'CDFGJN'),
      ('N', 'CDGJMN'),
      ('O', 'ABCGJNOP'),
      ('P', 'ABCGHIJ'),
      ('Q', 'ABCGJMNOP'),
      ('R', 'ABCGHIJM'),
      ('S', 'ABCHINOP'),
      ('T', 'ABEL'),
      ('U', 'CGJNOP'),
      ('V', 'CFJK'),
      ('W', 'CGJKMN'),
      ('X', 'DFKM'),
      ('Y', 'DFL'),
      ('Z', 'ABFKOP'),
      ('*', 'DEFHIKLM'),
      ('-', 'HI'),
      ('+', 'EHIL'),
      ('0', 'ABCGJNOP'),
      ('1', 'GN'),
      ('2', 'ABGHIJOP'),
      ('3', 'ABGHINOP'),
      ('4', 'CGHIN'),
      ('5', 'ABCHINOP'),
      ('6', 'ABCHIJNOP'),
      ('7', 'ABGN'),
      ('8', 'ABCGHIJNOP'),
      ('9', 'ABCGHINOP'),
    )
    
  _14segment_font = (
      ('A', 'ABFGHIM'),
      ('B', 'ADFHKMN'),
      ('C', 'ABIN'),
      ('D', 'ADFKMN'),
      ('E', 'ABGHIN'),
      ('F', 'ABGHI'),
      ('G', 'ABHIMN'),
      ('H', 'BFGHIM'),
      ('I', 'ADKN'),
      ('J', 'FIMN'),
      ('K', 'BEGIL'),
      ('L', 'BIN'),
      ('M', 'BCEFIM'),
      ('N', 'BCFILM'),
      ('O', 'ABFIMN'),
      ('P', 'ABFGHI'),
      ('Q', 'ABFILMN'),
      ('R', 'ABFGHIL'),
      ('S', 'ABGHMN'),
      ('T', 'ADK'),
      ('U', 'BFIMN'),
      ('V', 'BEIJ'),
      ('W', 'BFIJLM'),
      ('X', 'CEJL'),
      ('Y', 'CEK'),
      ('Z', 'AEJN'),
      ('*', 'CDEGHJKL'),
      ('-', 'GH'),
      ('+', 'DGHK'),
      ('0', 'ABFIMN'),
      ('1', 'FM'),
      ('2', 'AFGHIN'),
      ('3', 'AFGHMN'),
      ('4', 'BFGHM'),
      ('5', 'ABGHMN'),
      ('6', 'ABGHIMN'),
      ('7', 'AFM'),
      ('8', 'ABFGHIMN'),
      ('9', 'ABFGHMN'),
    )
  
  _7segment_font_original = (
      ('A', 'ABCDEF'),
      ('B', 'BDEFG'),
      ('C', 'ABEG'),
      ('D', 'CDEFG'),
      ('E', 'ABDEG'),
      ('F', 'ABDE'),
      ('-', 'D'),
      ('0', 'ABCEFG'),
      ('1', 'CF'),
      ('2', 'ACDEG'),
      ('3', 'ACDFG'),
      ('4', 'BCDF'),
      ('5', 'ABDFG'),
      ('6', 'ABDEFG'),
      ('7', 'ACF'),
      ('8', 'ABCDEFG'),
      ('9', 'ABCDFG'),
    )
    
  _7segment_font = (
(' ', ''),
('"', 'CB'),
#(''', 'C'),
('-', 'D'),
('0', 'ACFGEB'),
('1', 'CF'),
('2', 'ACGED'),
('3', 'ACFGD'),
('4', 'CFBD'),
('5', 'AFGBD'),
('6', 'AFGEBD'),
('7', 'ACF'),
('8', 'ACFGEBD'),
('9', 'ACFGBD'),
('=', 'GD'),
('A', 'ACFEBD'),
('B', 'ACFGEBD'),
('C', 'AGEB'),
('D', 'ACFGE'),
('E', 'AGEBD'),
('F', 'AEBD'),
('G', 'AFGEB'),
('H', 'CFEBD'),
('I', 'CF'),
('J', 'CFGE'),
('K', 'CGEBD'),
('L', 'GEB'),
('M', 'AFE'),
('N', 'ACFEB'),
('O', 'ACFGEB'),
('P', 'ACEBD'),
('Q', 'ACGBD'),
('R', 'ACEB'),
('S', 'AFGBD'),
('T', 'ACF'),
('U', 'CFGEB'),
('V', 'CEBD'),
('W', 'CGB'),
('X', 'FBD'),
('Y', 'CFGBD'),
('Z', 'ACGED'),
('[', 'AGEB'),
(']', 'ACFG'),
('^', 'ACB'),
('_', 'G'),
('a', 'ACFGED'),
('b', 'FGEBD'),
('c', 'GED'),
('d', 'CFGED'),
('e', 'ACGEBD'),
('f', 'AEBD'),
('g', 'ACFGBD'),
('h', 'FEBD'),
#('i', 'F'),
('i', 'E'),
('j', 'CFG'),
('k', 'AFEBD'),
('l', 'EB'),
('m', 'FE'),
('n', 'FED'),
('o', 'FGED'),
('p', 'ACEBD'),
('q', 'ACFBD'),
('r', 'ED'),
('s', 'AFGBD'),
('t', 'GEBD'),
('u', 'FGE'),
('v', 'CBD'),
('w', 'CB'),
('x', 'CED'),
('y', 'CFGBD'),
('z', 'ACGED'),
)