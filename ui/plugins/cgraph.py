#       cgraph.py
#       
#       copyright 2011 hugo teso <hugo.teso@gmail.com>
#       
#       this program is free software; you can redistribute it and/or modify
#       it under the terms of the gnu general public license as published by
#       the free software foundation; either version 2 of the license, or
#       (at your option) any later version.
#       
#       this program is distributed in the hope that it will be useful,
#       but without any warranty; without even the implied warranty of
#       merchantability or fitness for a particular purpose.  see the
#       gnu general public license for more details.
#       
#       you should have received a copy of the gnu general public license
#       along with this program; if not, write to the free software
#       foundation, inc., 51 franklin street, fifth floor, boston,
#       ma 02110-1301, usa.

import plugins.graphs as graphs


def showCallGraph(pyew):
    """ Show the callgraph of the whole program """
    dot = graphs.CCallGraphGenerator(pyew)
    buf = dot.generateDot()

    return buf
