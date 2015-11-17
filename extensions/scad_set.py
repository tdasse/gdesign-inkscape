#!/usr/bin/env python 

"""
scad-set
"""

import inkex

class ScadSet(inkex.Effect):
    """
    class ScadSet
    """

    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--header_path",
                        action="store", type="string", 
                        dest="header_path", default="",
                        help="Header of path")
        self.OptionParser.add_option("--pos_path",
                        action="store", type="string", 
                        dest="pos_path", default="",
                        help="pos of path")
        self.OptionParser.add_option("--footer_path",
                        action="store", type="string", 
                        dest="footer_path", default="",
                        help="Footer of path")

    def effect(self):

        for id, node in self.selected.iteritems():
            if node.tag == inkex.addNS('path','svg'):
                if self.options.header_path:
                    node.set('scad-header',self.options.header_path.replace('#id',id))
                else:
                    try:
                        del node.attrib['scad-header']
                    except:
                        pass
                if self.options.pos_path:
                    node.set('scad-pos',self.options.pos_path)
                else:
                    try:
                        del node.attrib['scad-pos']
                    except:
                        pass
                if self.options.footer_path:
                    node.set('scad-footer',self.options.footer_path.replace('#id',id))
                else:
                    try:
                        del node.attrib['scad-footer']
                    except:
                        pass

if __name__ == '__main__':
    z = ScadSet()
    z.affect()
