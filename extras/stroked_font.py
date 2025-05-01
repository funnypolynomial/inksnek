#! /usr/bin/env python

from inksnek import *
class StrokedFont:

    def __init__(self):
        # first byte in a definition is <character> then data bytes to <0xFF>
        # data bytes are 0bDxxxyyyy where D is 1 for a draw, 0 for a move, coords are {xxx,yyyy}
        # Normally, x is 0..6, y is 0..12, but across to 7 for '_' and down to 15 for descenders. (0,0) is top-left
        # two moves are an arc
        # character definitions must be in numerical order, but gaps/omissions (like lowercase) are OK
        # missing chars are shown as blank
        # adapted from C++ code with macros
        self.MAX_X = 6  # X's are 0..6 left-to-right
        self.MAX_Y = 12 # Y's are 00..12, top-to-bottom but can descend to 15
        self.FULL_Y = 18 # with arc descender, bottom is 15+3
        self.GAP_X = 2  # extra grid steps between chars
        self.GAP_Y = 2  # extra grid steps between lines
        self.DRAW_FLAG = 0b10000000
        self.MASK_X = 0b00000111 # 3 bits for X
        self.SHIFT_X = 4
        self.MASK_Y = 0b00001111 # 4 bits for Y
        #self.END = 0b11111111 # equivalent to DRAW(7, 15)
        self.font_defn = [
            # hand-crafted char definitions.
            [self.CHAR('\x18'),   self.MOVE(0,3), self.DRAW(3,0), self.DRAW(6,3), self.MOVE(3,0), self.DRAW(3,12)], # <up arrow>
            [self.CHAR('\x19'),   self.MOVE(0,9), self.DRAW(3,12), self.DRAW(6,9), self.MOVE(3,0), self.DRAW(3,12)], # <down arrow>
            [self.CHAR('\x1A'),   self.MOVE(3,3), self.DRAW(6,6), self.DRAW(3,9), self.MOVE(0,6), self.DRAW(6,6)], # <right arrow>
            [self.CHAR('\x1B'),   self.MOVE(3,3), self.DRAW(0,6), self.DRAW(3,9), self.MOVE(0,6), self.DRAW(6,6)], # <left arrow>

            [self.CHAR('!'),    self.MOVE(3,0), self.DRAW(3,9), self.DOT(3,11)],
            [self.CHAR('"'),    self.MOVE(2,0), self.DRAW(2,2), self.MOVE(4,0), self.DRAW(4,2)],
            [self.CHAR('#'),    self.MOVE(3,0), self.DRAW(1,12), self.MOVE(5,0), self.DRAW(3,12), self.MOVE(0,4), self.DRAW(6,4), self.MOVE(0,8), self.DRAW(6,8)],
            [self.CHAR('$'),    self.MOVE(3,0), self.DRAW(3,12), self.ARC(3,4,2,0b1101), self.ARC(3,8,2,0b0111)],
            [self.CHAR('%'),    self.MOVE(0,12), self.DRAW(6,0), self.ARC(1,1,1,0b1111), self.ARC(5,11,1,0b1111)],
            [self.CHAR('&'),    self.MOVE(2,5), self.DRAW(6,12), self.MOVE(0,7), self.DRAW(0,9), self.ARC(3,2,2,0b1111), self.ARC(3,9,3,0b0110), self.ARC(3,7,3,0b1000)],
            [self.CHAR('\''),   self.MOVE(3,0), self.DRAW(3,2)],
            [self.CHAR('('),    self.MOVE(1,3), self.DRAW(1,9), self.ARC(4,3,3,0b1000), self.ARC(4,9,3,0b0100)],
            [self.CHAR(')'),    self.MOVE(5,3), self.DRAW(5,9), self.ARC(2,3,3,0b0001), self.ARC(2,9,3,0b0010)],
            [self.CHAR('*'),    self.MOVE(0,6), self.DRAW(6,6), self.MOVE(3,3), self.DRAW(3,9), self.MOVE(1,4), self.DRAW(5,8), self.MOVE(1,8), self.DRAW(5,4)],
            [self.CHAR('+'),    self.MOVE(0,6), self.DRAW(6,6), self.MOVE(3,3), self.DRAW(3,9)],
            [self.CHAR(','),    self.DOT(3,11), self.MOVE(3,12), self.DRAW(2,13)],
            [self.CHAR('-'),    self.MOVE(0,6), self.DRAW(6,6)],
            [self.CHAR('.'),    self.DOT(3,11)],
            [self.CHAR('/'),    self.MOVE(6,0), self.DRAW(0,12)],

            [self.CHAR('0'),    self.MOVE(0,3), self.DRAW(0,9), self.DRAW(6,3), self.DRAW(6,9), self.ARC(3,3,3,0b1001), self.ARC(3,9,3,0b0110)],
            [self.CHAR('1'),    self.MOVE(3,0), self.DRAW(3,12), self.MOVE(0,3), self.DRAW(3,0), self.MOVE(0,12), self.DRAW(6,12)],
            [self.CHAR('2'),    self.MOVE(6,3), self.DRAW(6,5), self.DRAW(0,12), self.DRAW(6,12), self.ARC(3,3,3,0b1001)],
            [self.CHAR('3'),    self.MOVE(3,0), self.DRAW(0,0), self.MOVE(0,12), self.DRAW(3,12), self.MOVE(0,6), self.DRAW(3,6), self.ARC(3,3,3,0b0011), self.ARC(3,9,3,0b0011)],
            [self.CHAR('4'),    self.MOVE(4,0), self.DRAW(0,6), self.DRAW(6,6), self.MOVE(4,0), self.DRAW(4,12)],
            [self.CHAR('5'),    self.MOVE(6,0), self.DRAW(0,0), self.DRAW(0,5), self.DRAW(3,6), self.ARC(3,9,3,0b0111)],
            [self.CHAR('6'),    self.MOVE(0,3), self.DRAW(0,9), self.ARC(3,3,3,0b1001), self.ARC(3,9,3,0b1111)],
            [self.CHAR('7'),    self.MOVE(0,0), self.DRAW(6,0), self.DRAW(0,12)],
            [self.CHAR('8'),    self.ARC(3,3,3,0b1111), self.ARC(3,9,3,0b1111)],
            [self.CHAR('9'),    self.MOVE(6,0), self.DRAW(6,12), self.ARC(3,3,3,0b1111)],
            [self.CHAR(':'),    self.DOT(3,6), self.DOT(3,11)],
            [self.CHAR(';'),    self.DOT(3,6), self.DOT(3,11), self.MOVE(3,12), self.DRAW(2,13)],
            [self.CHAR('<'),    self.MOVE(6,2), self.DRAW(0,6), self.DRAW(6,10)],
            [self.CHAR('='),    self.MOVE(0,4), self.DRAW(6,4), self.MOVE(0,8), self.DRAW(6,8)],
            [self.CHAR('>'),    self.MOVE(0,2), self.DRAW(6,6), self.DRAW(0,10)],
            [self.CHAR('?'),    self.MOVE(3,6), self.DRAW(3,9), self.DOT(3,11), self.ARC(3,3,3,0b1011)],

            [self.CHAR('@'),    self.MOVE(0,3), self.DRAW(0,9), self.MOVE(6,3), self.DRAW(6,5), self.ARC(4,5,2,0b1111), self.ARC(3,3,3,0b1001), self.ARC(3,9,3,0b0110)],
            [self.CHAR('A'),    self.MOVE(0,3), self.DRAW(0,12), self.MOVE(6,3), self.DRAW(6,12), self.MOVE(0,6), self.DRAW(6,6), self.ARC(3,3,3,0b1001)],
            [self.CHAR('B'),    self.MOVE(3,0), self.DRAW(0,0), self.DRAW(0,12), self.DRAW(3,12), self.MOVE(0,6), self.DRAW(3,6), self.ARC(3,3,3,0b0011), self.ARC(3,9,3,0b0011)],
            [self.CHAR('C'),    self.MOVE(3, 0), self.DRAW(6, 0), self.MOVE(3, 12), self.DRAW(6, 12), self.MOVE(0, 3), self.DRAW(0, 9), self.ARC(3,3,3,0b1000), self.ARC(3,9,3,0b0100)],
            [self.CHAR('D'),    self.MOVE(3, 0), self.DRAW(0,0), self.DRAW(0, 12), self.DRAW(3, 12), self.MOVE(6, 3), self.DRAW(6, 9), self.ARC(3,3,3,0b0001), self.ARC(3,9,3,0b0010)],
            [self.CHAR('E'),    self.MOVE(6,0), self.DRAW(0,0), self.DRAW(0,12), self.DRAW(6,12), self.MOVE(0,6), self.DRAW(6,6)],
            [self.CHAR('F'),    self.MOVE(6,0), self.DRAW(0,0), self.DRAW(0,12), self.MOVE(0,6), self.DRAW(6,6)],
            [self.CHAR('G'),    self.MOVE(0,3), self.DRAW(0,9), self.MOVE(3,6), self.DRAW(6,6), self.DRAW(6,9), self.ARC(3,3,3,0b1001), self.ARC(3,9,3,0b0110)],
            [self.CHAR('H'),    self.MOVE(0,0), self.DRAW(0,12), self.MOVE(6,0), self.DRAW(6,12), self.MOVE(0,6), self.DRAW(6,6)],
            [self.CHAR('I'),    self.MOVE(3,0), self.DRAW(3,12), self.MOVE(0,0), self.DRAW(6,0), self.MOVE(0,12), self.DRAW(6,12)],
            [self.CHAR('J'),    self.MOVE(4,0), self.DRAW(4,10), self.MOVE(0,0), self.DRAW(6,0), self.ARC(2,10,2,0b0110)],
            [self.CHAR('K'),    self.MOVE(0,0), self.DRAW(0,12), self.MOVE(6,0), self.DRAW(0,6), self.DRAW(6,12)],
            [self.CHAR('L'),    self.MOVE(0,0), self.DRAW(0,12), self.DRAW(6,12)],
            [self.CHAR('M'),    self.MOVE(0,0), self.DRAW(0,12), self.MOVE(6,3), self.DRAW(6,12), self.MOVE(3,0), self.DRAW(3,12), self.ARC(3,3,3,0b1001)],
            [self.CHAR('N'),    self.MOVE(0,12), self.DRAW(0,0), self.DRAW(6,12), self.DRAW(6,0)],
            [self.CHAR('O'),    self.MOVE(0,3), self.DRAW(0,9), self.MOVE(6,3), self.DRAW(6,9), self.ARC(3,3,3,0b1001), self.ARC(3,9,3,0b0110)],
            [self.CHAR('P'),    self.MOVE(0,0), self.DRAW(0,12), self.ARC(3,3,3,0b1111)],
            [self.CHAR('Q'),    self.MOVE(0,3), self.DRAW(0,9), self.MOVE(6,3), self.DRAW(6,9), self.ARC(3,3,3,0b1001), self.ARC(3,9,3,0b0110), self.MOVE(3,8), self.DRAW(6,12)],
            [self.CHAR('R'),    self.MOVE(3,0), self.DRAW(0,0), self.DRAW(0,12), self.MOVE(3,6), self.DRAW(0,6), self.DRAW(6,12), self.ARC(3,3,3,0b0011)],
            [self.CHAR('S'),    self.ARC(3,3,3,0b1101), self.ARC(3,9,3,0b0111)],
            [self.CHAR('T'),    self.MOVE(3,0), self.DRAW(3,12), self.MOVE(0,0), self.DRAW(6,0)],
            [self.CHAR('U'),    self.MOVE(0,0), self.DRAW(0,9), self.MOVE(6,0), self.DRAW(6,9), self.ARC(3,9,3,0b0110)],
            [self.CHAR('V'),    self.MOVE(0,0), self.DRAW(3,12), self.DRAW(6,0)],
            [self.CHAR('W'),    self.MOVE(0,0), self.DRAW(0,9), self.MOVE(6,0), self.DRAW(6,9), self.MOVE(3,0), self.DRAW(3,12), self.ARC(3,9,3,0b0110)],
            [self.CHAR('X'),    self.MOVE(0,0), self.DRAW(6,12), self.MOVE(0,12), self.DRAW(6,0)],
            [self.CHAR('Y'),    self.MOVE(0,0), self.DRAW(0,3), self.MOVE(6,0), self.DRAW(6,9), self.ARC(3,3,3,0b0110), self.ARC(3,9,3,0b0110)],
            [self.CHAR('Z'),    self.MOVE(0,0), self.DRAW(6,0), self.DRAW(0,12), self.DRAW(6,12)],

            [self.CHAR('['),    self.MOVE(5,0), self.DRAW(1,0), self.DRAW(1,12), self.DRAW(5,12)],
            [self.CHAR('\\'),   self.MOVE(0,0), self.DRAW(6,12)],
            [self.CHAR(']'),    self.MOVE(1,0), self.DRAW(5,0), self.DRAW(5,12), self.DRAW(1,12)],
            [self.CHAR('^'),    self.MOVE(2,3), self.DRAW(3,0), self.DRAW(4,3)],
            [self.CHAR('_'),    self.MOVE(0,12), self.DRAW(7,12)],
            [self.CHAR('`'),    self.MOVE(3,0), self.DRAW(4,2)],

            [self.CHAR('a'),    self.MOVE(6,6), self.DRAW(6,12), self.ARC(3,9,3,0b1111)],
            [self.CHAR('b'),    self.MOVE(0,0), self.DRAW(0,12), self.ARC(3,9,3,0b1111)],
            [self.CHAR('c'),    self.MOVE(3,6), self.DRAW(6,6), self.MOVE(3,12), self.DRAW(6,12), self.ARC(3,9,3,0b1100)],
            [self.CHAR('d'),    self.MOVE(6,0), self.DRAW(6,12), self.ARC(3,9,3,0b1111)],
            [self.CHAR('e'),    self.MOVE(0,9), self.DRAW(6,9), self.MOVE(3,12), self.DRAW(6,12), self.ARC(3,9,3,0b1101)],
            [self.CHAR('f'),    self.MOVE(3,2), self.DRAW(3,12), self.MOVE(0,6), self.DRAW(6,6), self.MOVE(5,0), self.DRAW(6,0), self.ARC(5,2,2,0b1000)],
            [self.CHAR('g'),    self.MOVE(6,6), self.DRAW(6,14), self.ARC(3,9,3,0b1111), self.ARC(3,14,3,0b0110)],
            [self.CHAR('h'),    self.MOVE(0,0), self.DRAW(0,12), self.MOVE(6,8), self.DRAW(6,12), self.ARC(3,8,3,0b1001)],
            [self.CHAR('i'),    self.DOT(3,2), self.MOVE(3,6), self.DRAW(3,12)],
            [self.CHAR('j'),    self.DOT(6,2), self.MOVE(6,6), self.DRAW(6,14), self.ARC(3,14,3,0b0110)],
            [self.CHAR('k'),    self.MOVE(0,0), self.DRAW(0,12), self.MOVE(0,9), self.DRAW(6,6), self.MOVE(0,9), self.DRAW(6,12)],
            [self.CHAR('l'),    self.MOVE(3,0), self.DRAW(3,12)],
            [self.CHAR('m'),    self.MOVE(0,6), self.DRAW(0,12), self.MOVE(6,9), self.DRAW(6,12), self.MOVE(3,6), self.DRAW(3,12), self.ARC(3,9,3,0b1001)],
            [self.CHAR('n'),    self.MOVE(0,6), self.DRAW(0,12), self.MOVE(6,9), self.DRAW(6,12), self.ARC(3,9,3,0b1001)],
            [self.CHAR('o'),    self.ARC(3,9,3,0b1111)],
            [self.CHAR('p'),    self.MOVE(0,6), self.DRAW(0,14), self.ARC(3,9,3,0b1111)],
            [self.CHAR('q'),    self.MOVE(6,6), self.DRAW(6,14), self.ARC(3,9,3,0b1111)],
            [self.CHAR('r'),    self.MOVE(0,6), self.DRAW(0,12), self.ARC(3,9,3,0b1001)],
            [self.CHAR('s'),    self.MOVE(3,6), self.DRAW(6,6), self.MOVE(0,12), self.DRAW(3,12), self.MOVE(0,9), self.DRAW(6,9), self.ARC(3,9,3,0b1010)],
            [self.CHAR('t'),    self.MOVE(3,0), self.DRAW(3,12), self.MOVE(0,6), self.DRAW(6,6)],
            [self.CHAR('u'),    self.MOVE(6,6), self.DRAW(6,12), self.MOVE(0,9), self.DRAW(0,6), self.ARC(3,9,3,0b0110)],
            [self.CHAR('v'),    self.MOVE(0,6), self.DRAW(3,12), self.DRAW(6,6)],
            [self.CHAR('w'),    self.MOVE(0,6), self.DRAW(0,9), self.MOVE(6,6), self.DRAW(6,9), self.MOVE(3,6), self.DRAW(3,12), self.ARC(3,9,3,0b0110)],
            [self.CHAR('x'),    self.MOVE(0,6), self.DRAW(6,12), self.MOVE(6,6), self.DRAW(0,12)],
            [self.CHAR('y'),    self.MOVE(6,6), self.DRAW(6,14), self.MOVE(0,9), self.DRAW(0,6), self.ARC(3,9,3,0b0110), self.ARC(3,14,3,0b0110)],
            [self.CHAR('z'),    self.MOVE(0,6), self.DRAW(6,6), self.DRAW(0,12), self.DRAW(6,12)],

            [self.CHAR('{'),    self.MOVE(3,2), self.DRAW(3,4), self.MOVE(3,8), self.DRAW(3,10), self.ARC(5,2,2,0b1000), self.ARC(1,4,2,0b0010), self.ARC(1,8,2,0b0001), self.ARC(5,10,2,0b0100)],
            [self.CHAR('|'),    self.MOVE(3,0), self.DRAW(3,5), self.MOVE(3,6), self.DRAW(3,12)],
            [self.CHAR('}'),    self.MOVE(3,2), self.DRAW(3,4), self.MOVE(3,8), self.DRAW(3,10), self.ARC(1,2,2,0b0001), self.ARC(5,4,2,0b0100), self.ARC(5,8,2,0b1000), self.ARC(1,10,2,0b0010)],
            [self.CHAR('~'),    self.ARC(2,2,1,0b1001), self.ARC(4,2,1,0b0110)],

            [self.CHAR('\xB0'),   self.ARC(3,2,2,0b1111)], # <degrees>
          ]
        
    
    def textDims(self, scale, string, charGap = None):
        if charGap is None:
            charGap = self.GAP_X
        return (len(string)*scale*(self.MAX_X + charGap) - scale*charGap, scale*self.MAX_Y)
        
    def text(self, x0, y0, scale, string, charGap = None):
        # return a path of the string, baseline starting at (x0, y0)
        # chars are 6x12 (7*15 extra width, descenders) document units (eg 6x12mm)
        # scale multiplies, charGap is in unscaled doc units
        path = inksnek.path_start()
        prevX = x0
        prevY = y0
        if charGap is None:
            charGap = self.GAP_X
        for ch in string:
            defn = []
            for row in self.font_defn:
                if row[0] == ch: # found it
                    for elt in row: # flatten
                        if type(elt) is list:
                            defn.append(elt[0])
                            defn.append(elt[1])
                        else:
                            defn.append(elt)
                    break
            if len(defn):
                idx = 1
                while idx < len(defn):
                    elt = defn[idx]
                    idx += 1
                    x = x0 + scale*self.GET_X(elt)
                    y = y0 + scale*(self.MAX_Y - self.GET_Y(elt))
                    if elt & self.DRAW_FLAG:
                      # draw
                      path += inksnek.path_move_to(prevX, prevY)
                      path += inksnek.path_line_to(x, y)
                      prevX = x
                      prevY = y
                    elif defn[idx] & self.DRAW_FLAG:
                      # dot
                      prevX = x
                      prevY = y
                    else:
                      # arc
                      arc = defn[idx]
                      idx += 1
                      r = scale*self.GET_X(arc)
                      q = self.GET_Y(arc)
                      path += self.Arc(x, y, r, q)
            x0 += scale*(self.MAX_X + charGap)
        return path
    
    def GET_X(self, _b):
        return (_b >> self.SHIFT_X) & self.MASK_X

    def GET_Y(self, _b):
        return _b & self.MASK_Y

    def CHAR(self, _ch):
        return _ch 

    def MOVE(self, _x, _y):
        return 0b00000000 | ((_x & self.MASK_X) << self.SHIFT_X) | (_y & self.MASK_Y)

    def DRAW(self, _x, _y):
        return self.DRAW_FLAG  | ((_x & self.MASK_X) << self.SHIFT_X) | (_y & self.MASK_Y)

    # two consecutive moves are an arc: centre x, y; radius, quadrants  (0b0001 is 12-3, 0b0010 is 3-6, 0b0100 is 6-9, 0b1000 is 9-12 (clockwise))
    def ARC(self, _x, _y, _r, _q): # returns TWO things
        return  [self.MOVE(_x, _y), self.MOVE(_r, _q)]

    def DOT(self, _x, _y): # returns TWO things
        return  [self.MOVE(_x, _y), self.DRAW(_x, _y + 1)]
        
    def Arc(self, cx, cy, r, q):
      path = ""
      # combine quadrants
      if q & 0b0001:
        path += inksnek.path_move_to(cx, cy + r)
        path += inksnek.path_arc(cx, cy, r, 0, 90, False)
      if q & 0b0010:
        path += inksnek.path_move_to(cx + r, cy)
        path += inksnek.path_arc(cx, cy, r, 90, 180, False)
      if q & 0b0100:
        path += inksnek.path_move_to(cx, cy - r)
        path += inksnek.path_arc(cx, cy, r, 180, 270, False)
      if q & 0b1000:
        path += inksnek.path_move_to(cx - r, cy)
        path += inksnek.path_arc(cx, cy, r, 270, 360, False)
      return path


      
