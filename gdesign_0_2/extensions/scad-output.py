#!/usr/bin/env python 

"""
scad-output
"""

import inkex
from gdesign import *

def get_path(node,includes,pathList = [],transform=''):
    for subNode in node:
        if subNode.tag == inkex.addNS('g','svg'):
            groupid = subNode.get('id')
            groupname = subNode.get(inkex.addNS('label','inkscape'))
            if not groupname:
                groupname = groupid
            if includes.is_in(groupname):
                shead = subNode.get('scad-header')
                sfoot = subNode.get('scad-footer')
                if shead:
                    params = {'type':'group','#id':groupid}
                    params['scad-cmd'] = shead.replace('#id',params['#id'])
                    pathList.append(params)
                trans = subNode.get('transform')
                if trans:
                    get_path(subNode,includes,pathList,transform+' '+trans)
                else:
                    get_path(subNode,includes,pathList,transform[:])
                if sfoot:
                    params = {'type':'group','#id':groupid}
                    params['scad-cmd'] = sfoot.replace('#id',params['#id'])
                    pathList.append(params)
        elif subNode.tag == inkex.addNS('path','svg'):
            params = {'type':'path','#id':subNode.get('id')}
            trans = subNode.get('transform')
            if trans:
                params['transform'] = transform + ' ' + trans
            else:
                params['transform'] = transform
            params['pos'] = subNode.get('scad-pos')
            params['#fill'] = '[0,0,0]'
            style = subNode.get('style')
            if style:
                rvb = re.search('fill:#([0-9|A-F|a-f]{2})([0-9|A-F|a-f]{2})([0-9|A-F|a-f]{2})',style)
                if rvb:
                    params['#fill'] = '['+','.join([str(round(int(x,base=16)/255.0,3)) for x in rvb.groups()])+']'
            shead = subNode.get('scad-header')
            if not shead:
                params['header'] = ''
            else:
                shead = shead.replace('#id',params['#id'])
                shead = shead.replace('#fill',params['#fill'])
                params['header'] = shead
                
            sfoot = subNode.get('scad-footer')
            if not sfoot:
                params['footer'] = ''
            else:
                sfoot = sfoot.replace('#id',params['#id'])
                sfoot = sfoot.replace('#fill',params['#fill'])
                params['footer'] = sfoot
                
            params['d'] = subNode.get('d')            
            pathList.append(params)
            
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
        self.OptionParser.add_option("--includes",
                        action="store", type="string", 
                        dest="includes", default="",
                        help="includes")
        

    def effect(self):

        error = self.unittouu(str(self.options.error_max)+self.options.error_unit)

        h = self.unittouu(self.document.getroot().get('height'))
        m = self.unittouu('1'+self.options.openscad_unit)
        transUnit = TransformMatrix().set([float(m),0,0,-float(m),0,float(h)]).invert()

        if self.options.header:
            print self.options.header
        inctext = self.options.includes
        if not inctext:
            inctext = 'all'
        includes = Includes()
        if not includes.define(inctext):
            inkex.debug('wrong layer and groups includes')

        pathList = get_path(self.document.getroot(),includes)
        for path in pathList:
            if path['type'] == 'group':
                print path['scad-cmd']
            elif path['type'] == 'path':
                svgpath = Path().from_svg_path(path['d'],transUnit.mul(TransformMatrix().from_text(path['transform'])))
                if path['pos']:
                    bbox = svgpath.bounding_box()
                    center = bbox.get(path['pos']).reflect(Point(0,0))
                    svgpath.translate(center)

                if self.options.header_path:
                    head = self.options.header_path.replace('#id',path['#id'])+'\n'
                else:
                    head = ''
                if self.options.footer_path:
                    foot = '\n' + self.options.footer_path.replace('#id',path['#id'])
                else:
                    foot = ''
                print  head + path['header'] + svgpath.to_scad_poly(error,self.options.openscad_digit) + path['footer'] + foot
            
        if self.options.footer:
            print self.options.footer
        return 0

out = ScadOutput()
out.affect(output = False)
