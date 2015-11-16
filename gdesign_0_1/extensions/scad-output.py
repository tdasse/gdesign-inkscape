#!/usr/bin/env python 

"""
scad-output
"""

import inkex
from gdesign import *

def getPath(node,pathList = [],transform=''):
    for subNode in node:
        if subNode.tag == inkex.addNS('g','svg'):
            trans = subNode.get('transform')
            if trans:
                getPath(subNode,pathList,transform+' '+trans)
            else:
                getPath(subNode,pathList,transform[:])
        elif subNode.tag == inkex.addNS('path','svg'):
            idpath =  subNode.get('id')
            trans = subNode.get('transform')
            shead = subNode.get('scad-header')
            if not shead:
                shead = ''
            else:
                shead += '\n'
            sfoot = subNode.get('scad-footer')
            if not sfoot:
                sfoot = ''
            else:
                sfoot = '\n' + sfoot
            if trans:
                pathList.append([idpath,subNode.get('d'),transform+' '+trans,shead,sfoot])
            else:
                pathList.append([idpath,subNode.get('d'),transform,shead,sfoot])
    return pathList


class ScadOutput(inkex.Effect):
    """
    class ScadOutput
    """

    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--tab",
                        action="store", type="string", 
                        dest="tab", default="sampling",
                        help="") 
        self.OptionParser.add_option("--openscad_unit",
                        action="store", type="string", 
                        dest="openscad_unit", default="mm",
                        help="openscad unit")
        self.OptionParser.add_option("--openscad_digit",
                        action="store", type="int", 
                        dest="openscad_digit", default=3,
                        help="number of digits")
        self.OptionParser.add_option("--header",
                        action="store", type="string", 
                        dest="header", default="",
                        help="Header of file")
        self.OptionParser.add_option("--header_path",
                        action="store", type="string", 
                        dest="header_path", default="",
                        help="Header of path")
        self.OptionParser.add_option("--footer_path",
                        action="store", type="string", 
                        dest="footer_path", default="",
                        help="Footer of path")
        self.OptionParser.add_option("--footer",
                        action="store", type="string", 
                        dest="footer", default="",
                        help="Footer of file")
        self.OptionParser.add_option("--error_max",
                        action="store", type="float", 
                        dest="error_max", default=0.1,
                        help="error max")
        self.OptionParser.add_option("--error_unit",
                        action="store", type="string", 
                        dest="error_unit", default="mm",
                        help="error unit")
        

    def effect(self):

        error = self.unittouu(str(self.options.error_max)+self.options.error_unit)
        h = self.unittouu(self.document.getroot().get('height'))
        m = self.unittouu('1'+self.options.openscad_unit)
        scale = 'matrix('+str(1.0/m)+',0,0,'+str(-1.0/m)+',0,'+str(1.0*h/m)+') '

        if self.options.header:
            print self.options.header

        pathList = getPath(self.document.getroot())
        for path in pathList:
            svgpath = Path().fromSvgPath(path[1],TransformMatrix().fromText(scale+path[2]))
            if self.options.header_path:
                head = self.options.header_path.replace('#id#',path[0])+'\n'
            else:
                head = ''
            if self.options.footer_path:
                foot = '\n' + self.options.footer_path.replace('#id#',path[0])
            else:
                foot = ''
            print  head + path[3] + svgpath.toScadPoly(error,self.options.openscad_digit) + path[4] + foot
        if self.options.footer:
            print self.options.footer
        return 0

out = ScadOutput()
out.affect(output = False)
