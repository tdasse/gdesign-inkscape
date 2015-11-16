#! /usr/bin/python
"""
"""

import inkex
from gdesign import *
##import cubicsuperpath, simplestyle, copy, math, re, bezmisc

##def numsegs(csp):
##    return sum([len(p)-1 for p in csp])
##def tpoint((x1,y1), (x2,y2), t = 0.5):
##    return [x1+t*(x2-x1),y1+t*(y2-y1)]
##def cspbezsplit(sp1, sp2, t = 0.5):
##    m1=tpoint(sp1[1],sp1[2],t)
##    m2=tpoint(sp1[2],sp2[0],t)
##    m3=tpoint(sp2[0],sp2[1],t)
##    m4=tpoint(m1,m2,t)
##    m5=tpoint(m2,m3,t)
##    m=tpoint(m4,m5,t)
##    return [[sp1[0][:],sp1[1][:],m1], [m4,m,m5], [m3,sp2[1][:],sp2[2][:]]]
##def cspbezsplitatlength(sp1, sp2, l = 0.5, tolerance = 0.001):
##    bez = (sp1[1][:],sp1[2][:],sp2[0][:],sp2[1][:])
##    t = bezmisc.beziertatlength(bez, l, tolerance)
##    return cspbezsplit(sp1, sp2, t)
##def cspseglength(sp1,sp2, tolerance = 0.001):
##    bez = (sp1[1][:],sp1[2][:],sp2[0][:],sp2[1][:])
##    return bezmisc.bezierlength(bez, tolerance)    
##def csplength(csp):
##    total = 0
##    lengths = []
##    for sp in csp:
##        lengths.append([])
##        for i in xrange(1,len(sp)):
##            l = cspseglength(sp[i-1],sp[i])
##            lengths[-1].append(l)
##            total += l            
##    return lengths, total
##def numlengths(csplen):
##    retval = 0
##    for sp in csplen:
##        for l in sp:
##            if l > 0:
##                retval += 1
##    return retval

class ToPolygon(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--errormax",
                        action="store", type="float", 
                        dest="errormax", default = 0.1,
                        help="error max in mm")

    def effect(self):

        err = self.options.errormax*90/2.54
        
        for id, node in self.selected.iteritems():
            if node.tag == inkex.addNS('path','svg'):
                path = gdesign.Path().from_svg_path(node.get('d'))
                poly = path.to_polyline(err)
                node.set('d',poly.to_svg_path())
                
##                p = cubicsuperpath.parsePath(node.get('d'))
##                
##                #lens, total = csplength(p)
##                #avg = total/numlengths(lens)
##                #inkex.debug("average segment length: %s" % avg)
##
##                new = []
##                for sub in p:
##                    new.append([sub[0][:]])
##                    i = 1
##                    while i <= len(sub)-1:
##                        length = cspseglength(new[-1][-1], sub[i])
##                        
##                        if self.options.method == 'bynum':
##                            splits = self.options.segments
##                        else:
##                            splits = math.ceil(length/self.options.max)
##
##                        for s in xrange(int(splits),1,-1):
##                            new[-1][-1], next, sub[i] = cspbezsplitatlength(new[-1][-1], sub[i], 1.0/s)
##                            new[-1].append(next[:])
##                        new[-1].append(sub[i])
##                        i+=1
##                    
##                node.set('d',cubicsuperpath.formatPath(new))

if __name__ == '__main__':
    e = ToPolygon()
    e.affect()
##
##
### vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
##
##"""
##gdesign-topolygon
##"""
##
##import inkex
##from gdesign import *
##
##def get_path(node,pathList = [],transform=''):
##    for subNode in node:
##        if subNode.tag == inkex.addNS('g','svg'):
##            trans = subNode.get('transform')
##            if trans:
##                get_path(subNode,pathList,transform+' '+trans)
##            else:
##                get_path(subNode,pathList,transform[:])
##        elif subNode.tag == inkex.addNS('path','svg'):
##            idpath =  subNode.get('id')
##            trans = subNode.get('transform')
##            shead = subNode.get('scad-header')
##            if not shead:
##                shead = ''
##            else:
##                shead += '\n'
##            sfoot = subNode.get('scad-footer')
##            if not sfoot:
##                sfoot = ''
##            else:
##                sfoot = '\n' + sfoot
##            if trans:
##                pathList.append([idpath,subNode.get('d'),transform+' '+trans,shead,sfoot])
##            else:
##                pathList.append([idpath,subNode.get('d'),transform,shead,sfoot])
##    return pathList
##
##
##class GdTest(inkex.Effect):
##    """
##    class GdTest
##    """
##
##    def __init__(self):
##        inkex.Effect.__init__(self)
##
##    def effect(self):
##
##        h = self.unittouu(self.document.getroot().get('height'))
##        m = self.unittouu('1mm')
##        scale = 'matrix('+str(1.0/m)+',0,0,'+str(-1.0/m)+',0,'+str(1.0*h/m)+') '
##
##        s = Svg(mode='inkscape')
##
##        pathList = get_path(self.document.getroot())
##        for path in pathList:
##            svgpath = Path().from_svg_path(path[1],TransformMatrix().fromText(scale+path[2]))
##
##            s.add(svgpath,path[0])
##
##        s.write('bidule.svg')
##
##out = GdTest()
##out.affect(output = False)
##
