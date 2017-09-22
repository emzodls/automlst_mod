#!/usr/bin/env python
# Copyright (C) 2015,2016 Mohammad Alanjary
# University of Tuebingen
# Interfaculty Institute of Microbiology and Infection Medicine
# Lab of Nadine Ziemert, Div. of Microbiology/Biotechnology
# Funding by the German Centre for Infection Research (DZIF)
#
# This file is part of ARTS
# ARTS is free software. you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version
#
# License: You should have received a copy of the GNU General Public License v3 with ARTS
# A copy of the GPLv3 can also be found at: <http://www.gnu.org/licenses/>.

from ete3 import Tree
from ete3 import NodeStyle
import argparse, os

def rendertree(infile, width=800, spname=False):
    if not infile:
        exit(1)
    T = Tree(infile)
    nstyle = NodeStyle()
    nstyle["bgcolor"] = "#00CC00"
    nstyle["size"] = 10
    if spname:
        for node in T:
            if "OUTGROUP" in node.name:
                T.set_outgroup(node)
                T.ladderize()
            if spname in node.name:
                node.set_style(nstyle)
    T.render(infile+".png", w=width, units="px")

# Commandline Execution
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Convert Newick files to PNG""")
    parser.add_argument("-in", "--infile", help="Newick file to use", default=None)
    parser.add_argument("-w", "--width", help="Width in pixels to output", type=int, default=800)
    parser.add_argument("-spname", "--speciesname", help="Highlight nodes matching species name", default=False)
    args = parser.parse_args()
    rendertree(args.infile,args.width,args.speciesname)