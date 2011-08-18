#       generate_dot.py
#       
#       Copyright 2011 Hugo Teso <hugo.teso@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

def generate_dot(data, root_node):

    prefix = '<f0>'

    dotcode = '''
graph G {
    graph [ overlap="scale", bgcolor="#475672", concentrate="true",rankdir="LR" , root="%s"]
    node [color=azure3, fontcolor=white, fillcolor="#373D49", shape=circle, style=filled, height=0.7,width=0.7];

    "%s" [height=1, width=1, shape=circle]
''' % (root_node, root_node)

    for branch in data:
        node = branch.keys()[0]
        elements = branch[node]

        # Parse params to create clusters
        if '&amp;' in node or '&' in node or '?' in node or '&quest' in node:
            # Check if there is param name or just value
            if len( node.split('?') ) > 2:
                node = node.replace('?', '|')
            if len( node.split('&amp;') ) > 2:
                node = node.replace('&amp;', '|')
            if len( node.split('&') ) > 2:
                node = node.replace('&', '|')
            dotcode += '''"%s" [label="%s", shape="record", style="rounded, filled"]\n''' % (node, node)
            dotcode += '''"%s" -- "%s" [len=1.25, color=azure3]; ''' % (root_node, node)
        else:
            # Add branch node and connect with root
            dotcode += '''"%s" [shape="doublecircle", style=filled, fillcolor="#5E82C6", height=0.9, width=0.9, URL="%s"]\n''' % (node, node)
            dotcode += '''"%s" -- "%s" [len=1.25, color=azure3];\n''' % (root_node, node)

        # Add elements to node branch
        prev_element = node
        for element in elements:
            if element != '':
                if '&amp;' in element:
                    if not prefix in element:
                        element = prefix + element
                    element = element.replace('&amp;', '|')
                if '?' in element:
                    if not prefix in element:
                        element = prefix + element
                    element = element.replace('?', '|')
                if '&' in element:
                    if not prefix in element:
                        element = prefix + element
                    element = element.replace('&', '|')
                dotcode += '''"%s" [label="%s", shape="record", style="rounded, filled"]\n''' % (element, element)
                dotcode += '''"%s" -- "%s" [len=1.25, color=azure3]; ''' % (prev_element, element)
                prev_element = element

    dotcode += '\n}'

    #print dotcode
    return dotcode
