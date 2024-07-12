#! /usr/bin/env python
'''
Mark Wilson 2021
 A mono-spaced font family derived from character stroke coordinates from the Commodore 1520 plotter ROM
 The font definition bytes from one of the 325340-0x.s files here https://github.com/Project-64/reloaded/tree/master/1520/rom
 See also https://github.com/scruss/FifteenTwenty

 The original byte format is
    0bEXXXYYYP
    E - last command in list (1)
    X - x coordinate (0-7)
    Y - y coordinate (0-7)
    P - use pen (1), or just move (0)
    
 BUT here this has been transformed for convenience (easier to read & edit) to:
    Octal 0QXY  
    Q - 1=move; 2=last; 3=move & last
    X - x coordinate (0-7)
    Y - y coordinate (0-7)
    Note: an inital move is implied
          last is N/A
 AND missing characters have been implemented (<backslash>, ^`{|}), with extra graphical ones added at the end
 2024: Mods for Python3/Inkscape1.3.2
'''

class PlotterFont:

    def __init__(self):
        self._size = 7.0
        self._std_height = 5.0
        self._std_width = 5.0
        
    # char is ASCII range ' ' ... '~' plus some graphics chars
    # shape has [[x, y]] as a moveto, [x, y] as a lineto (for passing to inksnek.addShape)
    def get_char_shape(self, char, slant = 0.0):
        shape = []
        idx = ord(char) - ord(' ')
        if 0 <= idx and idx < len(self._p1520_strokes_octal):
            cmds = self._p1520_strokes_octal[idx]
            for cmd in cmds:
                # octal 0QXY  Q=1 (move) Q=2 (last)
                x = (cmd >> 3) & 0o07
                y = cmd & 0o07
                x = x + slant*y
                if cmd & 0x40 or shape == []: # move
                    shape += [[[x, y],],]
                else:
                    shape += [[x, y],]
        return shape
        
            
    # octal 0QXY  Q=1 (move) Q=2 (last)
    _p1520_strokes_octal = [
    # (originally just 639 raw bytes)
    #SPACE
            [0o300],
    #EXCLAMATION MARK                      *was* rectangles, now lines
            [0o127, 0o023, 0o122, 0o221],      # [0o121, 0o022, 0o032, 0o031, 0o021, 0o123, 0o027, 0o037, 0o033, 0o223],
    #QUOTATION MARK
            [0o117, 0o016, 0o137, 0o236],
    #NUMBER SIGN
            [0o112, 0o016, 0o136, 0o032, 0o143, 0o003, 0o105, 0o245],
    #DOLLAR SIGN
            [0o003, 0o012, 0o032, 0o043, 0o034, 0o014, 0o005, 0o016, 0o036, 0o045, 0o121, 0o027],
    #PERCENT SIGN
            [0o102, 0o046, 0o116, 0o006, 0o005, 0o015, 0o016, 0o133, 0o043, 0o042, 0o032, 0o233],
    #AMPERSAND
            [0o141, 0o005, 0o006, 0o017, 0o026, 0o025, 0o003, 0o002, 0o011, 0o021, 0o243],
    #APOSTROPHE
            [0o125, 0o227],
    #LEFT PARENTHESIS
            [0o131, 0o021, 0o012, 0o016, 0o027, 0o237],
    #RIGHT PARENTHESIS
            [0o121, 0o031, 0o042, 0o046, 0o037, 0o227],
    #ASTERISK
            [0o102, 0o046, 0o106, 0o042, 0o126, 0o222],
    #PLUS SIGN
            [0o122, 0o026, 0o104, 0o244],
    #COMMA
            [0o120, 0o031, 0o032, 0o022, 0o021, 0o231],
    #HYPHEN-MINUS
            [0o104, 0o244],
    #FULL STOP
            [0o121, 0o022, 0o032, 0o031, 0o221],
    #SOLIDUS
            [0o101, 0o256],
    #DIGIT ZERO
            [0o102, 0o046, 0o037, 0o017, 0o006, 0o002, 0o011, 0o031, 0o042, 0o246],
    #DIGIT ONE
            [0o116, 0o027, 0o021, 0o111, 0o231],
    #DIGIT TWO
            [0o106, 0o017, 0o037, 0o046, 0o045, 0o001, 0o241],
    #DIGIT THREE
            [0o106, 0o017, 0o037, 0o046, 0o045, 0o034, 0o024, 0o134, 0o043, 0o042, 0o031, 0o011, 0o202],
    #DIGIT FOUR
            [0o131, 0o037, 0o004, 0o003, 0o243],
    #DIGIT FIVE
            [0o102, 0o011, 0o031, 0o042, 0o044, 0o035, 0o005, 0o007, 0o247],
    #DIGIT SIX
            [0o104, 0o015, 0o035, 0o044, 0o042, 0o031, 0o011, 0o002, 0o006, 0o017, 0o037, 0o246],
    #DIGIT SEVEN
            [0o101, 0o045, 0o047, 0o207],
    #DIGIT EIGHT
            [0o114, 0o005, 0o006, 0o017, 0o037, 0o046, 0o045, 0o034, 0o043, 0o042, 0o031, 0o011, 0o002, 0o003, 0o014, 0o234],
    #DIGIT NINE
            [0o102, 0o011, 0o031, 0o042, 0o046, 0o037, 0o017, 0o006, 0o005, 0o014, 0o034, 0o245],
    #COLON
            [0o112, 0o013, 0o023, 0o022, 0o012, 0o115, 0o016, 0o026, 0o025, 0o215],
    #SEMICOLON
            [0o111, 0o022, 0o023, 0o013, 0o012, 0o022, 0o125, 0o026, 0o016, 0o015, 0o225],
    #LESS-THAN SIGN
            [0o141, 0o014, 0o247],
    #EQUALS SIGN
            [0o103, 0o043, 0o105, 0o245],
    #GREATER-THAN SIGN
            [0o111, 0o044, 0o217],
    #QUESTION MARK
            [0o106, 0o017, 0o037, 0o046, 0o045, 0o034, 0o024, 0o023, 0o122, 0o221],
    #COMMERCIAL AT
            [0o133, 0o035, 0o015, 0o012, 0o032, 0o043, 0o045, 0o036, 0o016, 0o005, 0o002, 0o011, 0o241],
    #LATIN CAPITAL LETTER A
            [0o101, 0o005, 0o027, 0o045, 0o041, 0o104, 0o244],
    #LATIN CAPITAL LETTER B
            [0o101, 0o007, 0o037, 0o046, 0o045, 0o034, 0o104, 0o034, 0o043, 0o042, 0o031, 0o201],
    #LATIN CAPITAL LETTER C
            [0o142, 0o031, 0o011, 0o002, 0o006, 0o017, 0o037, 0o246],
    #LATIN CAPITAL LETTER D
            [0o101, 0o007, 0o037, 0o046, 0o042, 0o031, 0o201],
    #LATIN CAPITAL LETTER E
            [0o141, 0o001, 0o007, 0o047, 0o134, 0o204],
    #LATIN CAPITAL LETTER F
            [0o101, 0o007, 0o047, 0o104, 0o234],
    #LATIN CAPITAL LETTER G
            [0o146, 0o037, 0o017, 0o006, 0o002, 0o011, 0o041, 0o044, 0o224],
    #LATIN CAPITAL LETTER H
            [0o101, 0o007, 0o147, 0o041, 0o104, 0o244],
    #LATIN CAPITAL LETTER I
            [0o101, 0o041, 0o121, 0o027, 0o107, 0o247], # wider crossbars
#           [0o111, 0o031, 0o121, 0o027, 0o117, 0o237],
    #LATIN CAPITAL LETTER J
            [0o102, 0o011, 0o021, 0o032, 0o237],
    #LATIN CAPITAL LETTER K
            [0o101, 0o007, 0o147, 0o003, 0o114, 0o241],
    #LATIN CAPITAL LETTER L
            [0o107, 0o001, 0o241],
    #LATIN CAPITAL LETTER M
            [0o101, 0o007, 0o025, 0o024, 0o025, 0o047, 0o241],
    #LATIN CAPITAL LETTER N
            [0o101, 0o007, 0o106, 0o042, 0o147, 0o241],
    #LATIN CAPITAL LETTER O
            [0o102, 0o006, 0o017, 0o037, 0o046, 0o042, 0o031, 0o011, 0o202],
    #LATIN CAPITAL LETTER P
            [0o101, 0o007, 0o037, 0o046, 0o045, 0o034, 0o204],
    #LATIN CAPITAL LETTER Q
            [0o123, 0o041, 0o131, 0o011, 0o002, 0o006, 0o017, 0o037, 0o046, 0o042, 0o231],
    #LATIN CAPITAL LETTER R
            [0o101, 0o007, 0o037, 0o046, 0o045, 0o034, 0o004, 0o114, 0o241],
    #LATIN CAPITAL LETTER S
            [0o102, 0o011, 0o031, 0o042, 0o043, 0o034, 0o014, 0o005, 0o006, 0o017, 0o037, 0o246],
    #LATIN CAPITAL LETTER T
            [0o121, 0o027, 0o107, 0o247],
    #LATIN CAPITAL LETTER U
            [0o107, 0o002, 0o011, 0o031, 0o042, 0o247],
    #LATIN CAPITAL LETTER V
            [0o107, 0o003, 0o021, 0o043, 0o247],
    #LATIN CAPITAL LETTER W
            [0o107, 0o001, 0o023, 0o124, 0o023, 0o041, 0o247],
    #LATIN CAPITAL LETTER X
            [0o101, 0o002, 0o046, 0o047, 0o107, 0o006, 0o042, 0o241],
    #LATIN CAPITAL LETTER Y
            [0o121, 0o024, 0o046, 0o047, 0o107, 0o006, 0o224],
    #LATIN CAPITAL LETTER Z
            [0o107, 0o047, 0o046, 0o002, 0o001, 0o241],
    #LEFT SQUARE BRACKET
            [0o121, 0o001, 0o007, 0o227],
    #BACKSLASH                                                                          *was* UPWARDS ARROW
            [0o006, 0o051],                                                               # [0o121, 0o026, 0o104, 0o026, 0o244],
    #RIGHT SQUARE BRACKET
            [0o111, 0o031, 0o037, 0o217],
    #CARET                                                                              *was* LEFTWARDS ARROW
            [0o015, 0o027, 0o035],                                                         # [0o122, 0o004, 0o026, 0o104, 0o254],
    #UNDERSCORE
            [0o000, 0o060],
    #BACKQUOTE                                                                          *was* BOX DRAWINGS LIGHT HORIZONTAL
            [0o035, 0o027],                                                               # [0o104, 0o274],
    #LATIN SMALL LETTER A
            [0o132, 0o021, 0o011, 0o002, 0o003, 0o014, 0o024, 0o033, 0o105, 0o025, 0o034, 0o032, 0o241],
    #LATIN SMALL LETTER B
            [0o107, 0o001, 0o021, 0o032, 0o034, 0o025, 0o205],
    #LATIN SMALL LETTER C
            [0o132, 0o021, 0o011, 0o002, 0o004, 0o015, 0o025, 0o234],
    #LATIN SMALL LETTER D
            [0o135, 0o015, 0o004, 0o002, 0o011, 0o031, 0o237],
    #LATIN SMALL LETTER E
            [0o103, 0o033, 0o034, 0o025, 0o015, 0o004, 0o002, 0o011, 0o231],
    #LATIN SMALL LETTER F
            [0o121, 0o027, 0o037, 0o114, 0o234],
    #LATIN SMALL LETTER G
            [0o101, 0o010, 0o020, 0o031, 0o034, 0o025, 0o015, 0o004, 0o003, 0o012, 0o022, 0o233],
    #LATIN SMALL LETTER H
            [0o101, 0o007, 0o105, 0o025, 0o034, 0o231],
    #LATIN SMALL LETTER I
            [0o111, 0o014, 0o115, 0o216], # shifted left
    #LATIN SMALL LETTER J
            [0o101, 0o010, 0o020, 0o031, 0o034, 0o135, 0o236],
    #LATIN SMALL LETTER K
            [0o131, 0o013, 0o107, 0o001, 0o102, 0o235],
    #LATIN SMALL LETTER L
            [0o117, 0o011, 0o221],
    #LATIN SMALL LETTER M
            [0o101, 0o005, 0o104, 0o015, 0o024, 0o021, 0o124, 0o035, 0o044, 0o241],
    #LATIN SMALL LETTER N
            [0o101, 0o005, 0o004, 0o015, 0o025, 0o034, 0o231],
    #LATIN SMALL LETTER O
            [0o102, 0o004, 0o015, 0o025, 0o034, 0o032, 0o021, 0o011, 0o202],
    #LATIN SMALL LETTER P
            [0o102, 0o022, 0o033, 0o034, 0o025, 0o005, 0o200],
    #LATIN SMALL LETTER Q
            [0o140, 0o030, 0o035, 0o015, 0o004, 0o003, 0o012, 0o232],
    #LATIN SMALL LETTER R
            [0o105, 0o014, 0o011, 0o114, 0o025, 0o235],
    #LATIN SMALL LETTER S
            [0o102, 0o011, 0o021, 0o032, 0o023, 0o013, 0o004, 0o015, 0o025, 0o234],
    #LATIN SMALL LETTER T
            [0o105, 0o025, 0o117, 0o011, 0o221],
    #LATIN SMALL LETTER U
            [0o005, 0o002, 0o011, 0o021, 0o032, 0o131, 0o035],   # more like the 'n',      *was* [0o105, 0o001, 0o031, 0o235],
    #LATIN SMALL LETTER V
            [0o105, 0o003, 0o021, 0o043, 0o245],
    #LATIN SMALL LETTER W
            [0o105, 0o002, 0o011, 0o022, 0o023, 0o022, 0o031, 0o042, 0o245],
    #LATIN SMALL LETTER X
            [0o101, 0o045, 0o105, 0o241],
    #LATIN SMALL LETTER Y
            [0o105, 0o004, 0o022, 0o145, 0o044, 0o200],
    #LATIN SMALL LETTER Z
            [0o105, 0o045, 0o001, 0o241],
    #LEFT BRACE *new*
            [0o031, 0o021, 0o012, 0o013, 0o004, 0o015, 0o016, 0o027, 0o037],
    #VERICAL BAR *new*
            [0o021, 0o027],
    #RIGHT BRACE *new*
            [0o121, 0o031, 0o042, 0o043, 0o054, 0o045, 0o046, 0o037, 0o227],
    #TILDE *new*
            [0o016, 0o027, 0o036, 0o047],
    #DEL *new*
            [0o000],
            
    #####################
    # ADDITIONS!
    #ANTI-CLOCKWISE ARROW \x80
            [0o050, 0o072, 0o074, 0o056, 0o036, 0o014, 0o017, 0o114, 0o044],
    #POSITIVE CENTRE SYMBOL \x81
            [0o052, 0o041, 0o021, 0o003, 0o005, 0o027, 0o047, 0o056, 0o136, 0o032, 0o114, 0o074],
    #CLOCKWISE ARROW    \x82
            [0o020, 0o002, 0o004, 0o026, 0o046, 0o064, 0o134, 0o064, 0o067],
    #POUND SIGN \x83
            [0o156, 0o046, 0o035, 0o032, 0o021, 0o011, 0o002, 0o013, 0o031, 0o051, 0o124, 0o244],
    #UPWARDS ARROW  \x84
            [0o121, 0o026, 0o104, 0o026, 0o244],
    #LEFTWARDS ARROW    \x85
            [0o122, 0o004, 0o026, 0o104, 0o254],
    #BOX DRAWINGS LIGHT HORIZONTAL  \x86
            [0o104, 0o274],
    #DOWNWARDS ARROW  \x87
            [0o121, 0o026, 0o103, 0o021, 0o243],
    #RIGHTWARDS ARROW    \x88
            [0o132, 0o054, 0o036, 0o154, 0o204],
    #LEFT-RIGHT ARROW    \x89
            [0o122, 0o004, 0o026, 0o142, 0o064, 0o046, 0o164, 0o204],
    ]
