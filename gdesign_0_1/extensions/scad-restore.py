#!/usr/bin/env python 

"""
scad-restore
"""

import os.path
import json
import inkex

class ScadRestore(inkex.Effect):
    """
    class ScadRestore
    """

    paramList = ['scad-header','scad-footer']

    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--restore",
                        action="store", type="string", 
                        dest="restore", default="",
                        help="Scad parameters filename")

    def setParam(self,node):
        for subNode in node:
            if subNode.tag == inkex.addNS('g','svg'):
                self.setParam(subNode)
            elif subNode.tag == inkex.addNS('path','svg'):
                idpath =  subNode.get('id')
                if self.scadparam.has_key(idpath):
                    for item in ScadRestore.paramList:
                        try:
                            del subNode.attrib[item]
                        except:
                            pass
                        try:
                            subNode.set(item,self.scadparam[idpath][item])
                        except:
                            pass

    def effect(self):
        filename = os.path.dirname(self.svg_file) + os.path.sep + self.options.restore

        f = open(filename,mode='r')
        self.scadparam = json.load(f)
        self.setParam(self.document.getroot())
        f.close()

z = ScadRestore()
z.affect()
