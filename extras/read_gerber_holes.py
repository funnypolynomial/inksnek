#!/usr/bin/python
''' 
Mark Wilson 2024:
Read holes from gerber .DRL files or in a zip
Very basic parsing, assumes metric, no error checking
Only used with files from EasyEDA

Created to use with inksnek to aid incorporating PCBs in laser cut enclosures
See parse_file_lines
'''
import sys
import argparse
import os
import zipfile # https://docs.python.org/3/library/zipfile.html#

class read_gerber_holes:
    # read zip file, return all holes
    def read_zip_file(self, zip_file_name):
        gerber_holes = [] # contains all the holes, [x, y, d]
        zip_file = zipfile.ZipFile(zip_file_name, 'r')
        for filename in zip_file.namelist():
            if os.path.splitext(filename)[1].lower() == '.drl': # drill file
                drill_file = zip_file.open(filename, 'r')
                blines = drill_file.readlines()
                lines = []
                for bline in blines: # convert from bytes string
                    lines.append(bline.decode('utf-8'))
                gerber_holes += self.parse_file_lines(lines)
        return gerber_holes

    def read_drill_file(self, drill_file_name):
        # read a single file, return holes
        drill_file = open(drill_file_name, 'r')
        return self.parse_file_lines(drill_file.readlines())

    def parse_file_lines(self, lines):
        # scans lines from .DRL file, returns list of holes [x, y, d]
        diameters = {}
        current_diameter = -1
        hole_num = -1
        file_holes = []
        for line in lines:
            # hole diameters TnnCd.ddd (mm)
            if line[0] == 'T':
                hole_num = int(line[1:3])
            if line.find('C') == 3: # diameter defined Tnn
                hole_diameter = float(line[4:])
                diameters[hole_num] = hole_diameter
            else: # hole specified
                current_hole_num = hole_num
            
            #  hole positions XxxxxxxYyyyyyy (mm*1000)
            if line[0] == 'X' and current_hole_num != -1:
                x = int(line[1:7 ])/1000.0
                y = int(line[8:14])/1000.0
                file_holes.append([x, y, diameters[current_hole_num]])
        return file_holes
