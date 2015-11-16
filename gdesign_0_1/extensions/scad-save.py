#!/usr/bin/env python 

"""
scad-save
"""

import os.path
import json
import inkex

class ScadSave(inkex.Effect):
    """
    class ScadSave
    """

    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--save_as",
                        action="store", type="string", 
                        dest="save_as", default="",
                        help="Scad parameters filename")

    def getParam(self,node):
        for subNode in node:
            if subNode.tag == inkex.addNS('g','svg'):
                self.getParam(subNode)
            elif subNode.tag == inkex.addNS('path','svg'):
                idpath =  subNode.get('id')
                shead = subNode.get('scad-header')
                sfoot = subNode.get('scad-footer')
                if shead or sfoot:
                    param = {}
                    if shead:
                        param['scad-header'] = shead
                    if sfoot:
                        param['scad-footer'] = sfoot
                    self.scadparam[idpath] = param                        

    def effect(self):
        filename = os.path.dirname(self.svg_file) + os.path.sep + self.options.save_as
        self.scadparam = {}

        f = open(filename,mode='w')
        self.getParam(self.document.getroot())
        json.dump(self.scadparam,f)
        f.close()

z = ScadSave()
z.affect()
