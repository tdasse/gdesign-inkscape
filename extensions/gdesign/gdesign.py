#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
gdesign's package

author : Thierry Dassé
version : 0.2.0
date : 10/11/2015
licence : GPL
"""

import os
import re
import math
import random
from lxml import etree

_nss = {
u'sodipodi' :u'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
u'cc'       :u'http://creativecommons.org/ns#',
u'ccOLD'    :u'http://web.resource.org/cc/',
u'svg'      :u'http://www.w3.org/2000/svg',
u'dc'       :u'http://purl.org/dc/elements/1.1/',
u'rdf'      :u'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
u'inkscape' :u'http://www.inkscape.org/namespaces/inkscape',
u'xlink'    :u'http://www.w3.org/1999/xlink',
u'xml'      :u'http://www.w3.org/XML/1998/namespace'
}

_units_pt = {'mm': 90.0/25.4, 'cm': 90.0/2.54, 'in': 90.0, 'ft': 1080.0,'pt': 1.0}
_units_mm =  {'mm': 1.0, 'cm': 10.0, 'in': 25.4, 'ft': 304.8}


def _str_num(x,digit = 5):
    """
    return a string wich represents a number
    x is an integer or a float
    digit is the maximum number of digits in the string

    Examples

    >>> print(_str_num(2.123,2))
    2.12
    >>> print(_str_num(3.0073,2))
    3.01
    >>> print(_str_num(3.0013,2))
    3

    """
    if round(x,digit) - round(x,0) == 0:
        return str(int(round(x,0)))
    else:
        return str(round(x,digit))

def _is_num(x):
    """
    return True if x represents a number (float or integer) else False

    Examples

    >>> print(_is_num(4.52))
    True
    >>> print(_is_num('-3.52e-3'))
    True
    >>> print(_is_num('7*3'))
    False
    >>> print(_is_num('hello'))
    False
    """
    try:
        float(x)
        return True
    except:
        return False

def _choose(i,n):
    """
    return the number of ways of picking i unordered outcomes from n possibilities.
    i and n must be positive integers

    Examples

    >>> print(_choose(1,3))
    3.0
    >>> print(_choose(2,5))
    10.0
     """
    return math.factorial(n)/(math.factorial(i)*math.factorial(n-i))

def _subst_ns(tag):
    """
    transform a dict or a tag in domain:tag format to {domain}tag
    used in xml files
    """
    if type(tag) == dict:
        r = {}
        for key,value in tag.items():
            r[_subst_ns(key)] = value
        return r
    else:        
        r = tag.split(':')
        if len(r) == 1:
            return tag
        elif len(r) == 2:
            return "{%s}%s" % (_nss[r[0]], r[1])

def _unit_to_pt(val):
    """
    convert a value in mm,cm,in or ft in points
    default ppi is 90
    """
    re_val = '^[ ]*(-?[0-9]+[.]?[0-9]*)[ ]*(mm|cm|in|ft)'
    try:
        s = re.search(re_val,val).groups()
        return float(s[0]) * _units_pt[s[1]]
    except:
        return None

def _unit_to_mm(val):
    """
    convert a value in mm,cm,in or ft in mm
    """
    re_val = '^[ ]*(-?[0-9]+[.]?[0-9]*)[ ]*(mm|cm|in|ft)'
    try:
        s = re.search(re_val,val).groups()
        return float(s[0]) * _units_mm[s[1]]
    except:
        return None


def _copy(obj):
    """
    return an object's copy
    if object type is a non primitive class instance object must have a copy() method
    """
    if type(obj) == int or type(obj) == float:
        return obj
    elif type(obj) == str:
        return obj[:]
    elif type(obj) == list:
        return [_copy(item) for item in obj]
    elif type(obj) == tuple:
        return tuple([_copy(item) for item in obj])
    elif type(obj) == dict:
        cpy = {}
        for key,value in obj.items():
            cpy[_copy(key)]=_copy(value)
        return cpy
    else:
        return obj.copy()

def _find(dic,root,key):
    """
    return a list of found keys in a dictionary of dictionary
    """
    result = []
    for k,v in dic.items():
        if root:
           p = root+'/'+k
        else:
           p = k
        if p.find(key) != -1:
            result.append(p)
        if type(v) == dict:
            result.extend(_find(v,p,key))
    return result

def _to_xml(location,name,dic):
    """
    insert a dictionary in an xml tree
    """
    param = {}
    for key,value in dic.items():
        if key == 'style' and type(value) == dict:
            r = [(k,str(v)) for k,v in value.items()]
            r.sort()
            param[key] = ';'.join([':'.join(item) for item in r])
        elif type(value) == int or type(value) == float or type(value) == str:
            param[_subst_ns(key)] = str(value)
    child = etree.SubElement(location,_subst_ns(name),param)       
    for key,value in dic.items():
        if key != 'style' and type(value) == dict:
            _to_xml(child,key,value)

def _get_dic(dic):
    """
    to be completed
    """
    param = {}
    for key,value in dic.items():
        if key == 'style' and type(value) == dict:
            r = [(k,str(v)) for k,v in value.items()]
            r.sort()
            param[key] = ';'.join([':'.join(item) for item in r])
        elif type(value) == int or type(value) == float or type(value) == str:
            param[_subst_ns(key)] = str(value)
        elif type(value) == dict:
            param[_subst_ns(key)] = _get_dic(value)
    return param

def _get_path(node,pathList = []):
    """
    return a path list from a svg type xml tree
    to be completed
    """
    for subNode in node:
        if subNode.tag == _subst_ns('svg:g'):
            _get_path(subNode,pathList)
        if subNode.tag == _subst_ns('svg:path'):
            params = {'id':subNode.get('id'),'color':[255,0,0]}
            style = subNode.get('style')
            if style:
                rvb = re.search('stroke:#([0-9|A-F|a-f]{2})([0-9|A-F|a-f]{2})([0-9|A-F|a-f]{2})',style)
                if rvb:
                    params['color'] = [int(x,base=16) for x in rvb.groups()]
            pathList.append(params)
    return pathList

class DTree(object):
    """
    class for dictionary of dictionary
    """

    def __init__(self,sep='/'):
        """
        init the dictionary and set the separator for tree keys
        """
        self.sep = sep
        self.clear()
        
    def clear(self):
        """
        remove all object in the dictionary
        """
        self.dic = {}
        
    def set(self,dic):
        """
        copy the dic dictionary to the dictionary
        """
        self.dic = _copy(dic)

    def find(self,key):
        """
        find key in the dictionary tree
        """
        return _find(self.dic,'',key)

    def get(self,key):
        """
        get value of the key in the dictionary tree
        """
        path = key.split(self.sep)
        dic = self.dic
        for i in range(len(path)-1):
            try:
                dic = dic[path[i]]
            except:
                return None
        try:
            return dic[path[-1]]
        except:
            return None

    def get_dic(self):
        """
        return the dictionay in the inkscape path format
        must be private
        """
        return _get_dic(self.dic)

    def add(self,key,value):
        """
        add a key:value in the dictionary tree

        example

        to be completed
        """
        path = key.split('/')
        dic = self.dic
        for i in range(len(path)-1):
            try:
                dic = dic[path[i]]
            except:
                dic[path[i]] = {}
                dic = dic[path[i]]
        dic[path[-1]] = value

    def delete(self,key):
        """
        delete the key in the dictionary tree
        """
        path = key.split('/')
        dic = self.dic
        for i in range(len(path)-1):
            try:
                dic = dic[path[i]]
            except:
                return False
        try:
            del dic[path[-1]]
        except:
            return False
        return True

    def to_xml(self,location,name):
        """
        insert the dictionary tree in a xml svg object
        must be private
        """
        _to_xml(location,name,self.dic)

class Includes(object):
    """
    class a string into includes and excludes keys

    examples of string

    'layer' : just 'layer'
    'layer1 + layer2 : 'layer1' and 'layer2'
    'all' : everything
    'all - layer1' : everything but layer1
    """
    def __init__(self,allbydefault = True):
        """
        init the Includes
        if allbydefault is True then all are includes at the begining (used to exclude some
        else nobody is included at the begining
        """
        self.clear()
        
    def clear(self,allbydefault = True):
        """
        clear the Includes
        """
        self.all = allbydefault
        self.includes = []
        self.excludes = []

    def define(self,rules):
        """
        define includes and excludes by a string

        example:

        to be completed
        """
        self.clear(allbydefault = False)
        op = ('+','-')
        rlist = rules.split(' ')
        mode = '+'
        for item in rlist:
            if not item:
                pass
            elif item in op:
                if not mode:
                    mode = item
                else:
                    self.clear()
                    return False
            elif mode == '+' and item == 'all':
                self.all = True
                mode = ''
            elif mode in op:
                if mode == '+':
                    self.includes.append(item)
                else:
                    self.excludes.append(item)
                mode = ''
            else:
                self.clear()
                return False
        if self.all:
            self.includes = []
        return True

    def is_in(self,obj):
        """
        return True if obj is included
        obj is a string
        """
        if obj in self.includes:
            return True
        elif self.all and obj not in self.excludes:
            return True
        else:
            return False

class TransformMatrix(object):
    """
    2D transformation matrix
    At initialisation the matrix is set to identity

    Example:

    >>> t = TransformMatrix().homothety(Point(2,-1),3)
    >>> print(t.get())
    [3, 0, 0, 3, -4, 2]
    >>> p = Point(5,1).transform(t)
    >>> print(p.x,p.y)
    11 5
    """

    re_translate = '^[ ]*translate\((-?[0-9]+[.]?[0-9]*[e]?-?[0-9]*,-?[0-9]+[.]?[0-9]*[e]?-?[0-9]*)\)'
    re_matrix = '^[ ]*matrix\((-?[0-9]+[.]?[0-9]*[e]?-?[0-9]*(,-?[0-9]+[.]?[0-9]*[e]?-?[0-9]*){5})\)'
    nullDeterminant = 1e-5

    def __init__(self,matrix = None):
        """
        set the matrix
        if matrix is None then set the matrix to identity
        else set the the matrix where matrix is a tuple or list of six numbers

        Example:

        >>> t = TransformMatrix()
        >>> print(t.get())
        [1, 0, 0, 1, 0, 0]
        >>> t = TransformMatrix([1,0,1,2,4,3])
        >>> print(t.get())
        [1, 0, 1, 2, 4, 3]
        """

        if matrix != None:
            self.set(matrix)
        else:
            self.identity()

    def identity(self):
        """
        set the matrix to identity
        return the transformMatrix
        corresponding to the mathematical transformation matrix
        (1 0 0)
        (0 1 0)
        (0 0 1)

        Example:

        >>> t = TransformMatrix().identity()
        >>> print(t.get())
        [1, 0, 0, 1, 0, 0]
        """

        self.matrix = [1,0,0,1,0,0]
        return self
        
    def get(self):
        """
        return the matrix as a list of 6 numbers
        [a,b,c,d,e,f] corresponding to the mathematical transformation matrix
        (a c e)
        (b d f)
        (0 0 1)

        Example:

        >>> t = TransformMatrix().homothety(Point(2,-1),3)
        >>> print(t.get())
        [3, 0, 0, 3, -4, 2]
        """
        return self.matrix

    def translation(self,v):
        """
        set the transformation matrix to a translation
        v is a Vector
        corresponding to the mathematical matrix
        (1 0 v.x)
        (0 1 v.y)
        (0 0  1 )
        return the TransfomMatrix

        Example:

        >>> t = TransformMatrix().translation(Vector(2,-3))
        >>> print(t.get())
        [1, 0, 0, 1, 2, -3]
        """

        self.matrix = [1,0,0,1,v.x,v.y]
        return self

    def scaling(self,sx,sy):
        """
        set the transformation matrix to an affine transform
        where sx and sy are scale factors of x-axis and y-axis
        corresponding to the mathematical matrix
        (sx  0 0)
        ( 0 sy 0)
        ( 0  0 1)
        return the TransfomMatrix

        Example:

        >>> t = TransformMatrix().scaling(1,2)
        >>> print(t.get())
        [1, 0, 0, 2, 0, 0]
        """
        
        self.matrix = [sx,0,0,sy,0,0]
        return self

    def homothety(self,center,ratio):
        """
        set the transformation matrix to a homothety
        center is the center Point of the homothety
        ratio is a float number
        corresponding to the mathematical matrix
        (ratio   0   *)
        (  0   ratio *)
        (  0     0   1)
        return the TransfomMatrix

        Example:

        >>> t = TransformMatrix().homothety(Point(2,-1),3)
        >>> print(t.get())
        [3, 0, 0, 3, -4, 2]
        """
        self.matrix = [ratio,0,0,ratio,(1-ratio)*center.x,(1-ratio)*center.y]
        return self

    def rotation(self,center,angle):
        """
        set the transformation matrix to a rotation
        center is the center point of the transrformation
        angle is the angle in radians
        corresponding to the mathematical matrix
        (cos(angle) -sin(angle) *)
        (sin(angle) cos(angle)  *)
        (   0          0        1)
        return the TransfomMatrix

        Example:

        >>> t = TransformMatrix().rotation(Point(0,0),math.pi/2)
        >>> print([round(val,3) for val in t.get()])
        [0.0, 1.0, -1.0, 0.0, 0.0, 0.0]
        """
        self.matrix = [math.cos(angle),math.sin(angle),-math.sin(angle),math.cos(angle),
                       center.x*(1-math.cos(angle))+center.y*math.sin(angle),
                       center.y*(1-math.cos(angle))-center.x*math.sin(angle)]
        return self

    def reflection(self,o):
        """
        set the transformation matrix to a reflection
        if o is a point then the reflection is a central symetry
        if o is a line then the reflection is an axial symetry
        return the TransfomMatrix

        Example

        >>> t = TransformMatrix().reflection(Point(0,0))
        >>> print(t.get())
        [-1, 0, 0, -1, 0, 0]
        >>> t = TransformMatrix().reflection(Line(Point(0,0),Point(0,1)))
        >>> print(t.get())
        [-1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        """

        if type(o) == Point:
            self.matrix = [-1,0,0,-1,2*o.x,2*o.y]
        elif type(o) == Line:
            a = o.start()
            u = o.vector()
            self.matrix = [2*u.x**2-1,2*u.x*u.y,2*u.x*u.y,2*u.y**2-1,2*a.x*(1-u.x**2)-2*a.y*u.x*u.y,2*a.y*(1-u.y**2)-2*a.x*u.x*u.y]
        return self

    def set(self,matrix):
        """
        set the transformation matrix to an affine transformation
        matrix is a tuple or list of six numbers a,b,c,d,e,f
        corresponding to the mathematical matrix
        (a c e)
        (b d f)
        (0 0 1)
        return the TransfomMatrix

        Example
        
        >>> t = TransformMatrix().set([1,1,0,1,2,3])
        >>> print(t.get())
        [1, 1, 0, 1, 2, 3]
        """

        if type(matrix) != list and type(matrix) != tuple:
            raise TypeError('Invalid argument type')
        if len(matrix) != 6:
            raise TypeError('Matrix must have 6 numbers')
        for i in range(6):
            if type(matrix[i]) != int and type(matrix[i]) != float:
                raise TypeError('Matrix must have 6 numbers')
        self.matrix = list(matrix)
        return self

    def mul(self,matrix):
        """
        return the product of two Transformation matrix
        this product is non commutative
        transformation order is matrix then self

        Example

        >>> t = TransformMatrix().translation(Vector(3,2))
        >>> u = TransformMatrix().reflection(Point(1,0))
        >>> m = t.mul(u)
        >>> print(m.get())
        [-1, 0, 0, -1, 5, 2]
        """

        m = TransformMatrix()
        m.matrix = [self.matrix[0]*matrix.matrix[0]+self.matrix[2]*matrix.matrix[1],
                    self.matrix[1]*matrix.matrix[0]+self.matrix[3]*matrix.matrix[1],
                    self.matrix[0]*matrix.matrix[2]+self.matrix[2]*matrix.matrix[3],
                    self.matrix[1]*matrix.matrix[2]+self.matrix[3]*matrix.matrix[3],
                    self.matrix[0]*matrix.matrix[4]+self.matrix[2]*matrix.matrix[5]+self.matrix[4],
                    self.matrix[1]*matrix.matrix[4]+self.matrix[3]*matrix.matrix[5]+self.matrix[5]]
        return m

    def determinant(self):
        """
        return the transformation matrix determinant

        Example:

        >>> t = TransformMatrix().homothety(Point(2,-1),3)
        >>> print(t.determinant())
        9
        """

        return self.matrix[0]*self.matrix[3]-self.matrix[1]*self.matrix[2]

    def invert(self):
        """
        return the invert transformation matrix
        if matrix determinant is null then return None

        Example:
        
        >>> t = TransformMatrix().set([1,1,0,1,2,3])
        >>> u = t.invert()
        >>> print(u.get())
        [1.0, -1.0, 0.0, 1.0, -2.0, -1.0]
        """

        det = float(self.determinant()) ## for 2.x compability
        if abs(det) < TransformMatrix.nullDeterminant:
            return None
        return TransformMatrix().set([self.matrix[3]/det,-self.matrix[1]/det,-self.matrix[2]/det,self.matrix[0]/det,
                                      (self.matrix[2]*self.matrix[5]-self.matrix[3]*self.matrix[4])/det,
                                      (self.matrix[1]*self.matrix[4]-self.matrix[0]*self.matrix[5])/det])

    def from_text(self,text):
        """
        translate a string to a transformation matrix
        text is a string wich is a list of transformation separated by spaces
        transformations order are from right to left
        available transformations are :
        translate(a,b)
        matrix(a,b,c,d,e,f)
        compatible with Inkscape transform field

        Example:

        >>> t = TransformMatrix().from_text('translate(12,5) matrix(2,0,0,2,0,0)')
        >>> print(t.get())
        [2.0, 0.0, 0.0, 2.0, 12.0, 5.0]
        """

        s = re.search(TransformMatrix.re_translate,text)
        if s:
            param = [float(item) for item in s.group(1).split(',')]
            m = TransformMatrix().translation(Vector(param[0],param[1]))
            e = TransformMatrix().from_text(text[s.span()[1]:])
            self.matrix = m.mul(e).matrix
        s = re.search(TransformMatrix.re_matrix,text)
        if s:
            m = TransformMatrix().set([float(item) for item in s.group(1).split(',')])
            e = TransformMatrix().from_text(text[s.span()[1]:])
            self.matrix = m.mul(e).matrix
        return self

class Coord(object):
    """
    2D coordinates object
    Parent class for points and vectors
    
    Example:

    >>> c = Coord(4,3)
    >>> print(c.radius())
    5.0
    """

    nullDistance = 1e-5
    
    def __init__(self,x = 0,y = 0):
        """
        create an object with cartesian coordinates (x,y)
        default coordinates are None

        Example:

        >>> c = Coord(1,0)
        >>> print(c.x)
        1
        """

        self.set(x,y)

    def set(self,x,y):
        """
        set x and y coordinates of the object
        return the object

        Example:

        >>> c = Coord()
        >>> print(c.set(3,-1).x)
        3
        """

        self.x = x
        self.y = y
        return self

    def set_polar(self,radius,angle):
        """
        set the coordinates of the object in polar system
        radius is the distance from origin
        angle is in radians

        Example:

        >>> c = Coord()
        >>> print(c.set_polar(5,-math.pi/2).y)
        -5.0
        """

        self.x = radius*math.cos(angle)
        self.y = radius*math.sin(angle)
        return self

    def radius(self):
        """
        return the radius of the object

        Example:

        >>> c = Coord(4,3)
        >>> print(c.radius())
        5.0
        """
        return math.sqrt(self.x**2+self.y**2)

    def angle(self):
        """
        return the angular coordinate in radians
        if the radius is null then return 0

        Example:

        >>> c = Coord(0,3)
        >>> print(round(c.angle(),3))
        1.571
        """
        
        r = self.radius()
        if r == 0:
            return 0
        else:
            return math.atan2(self.y,self.x)

class Vector(Coord):
    """
    2D Vector

    Example:

    >>> c = Vector(4,3).norm()
    >>> print(c.x,c.y)
    0.8 0.6
    """

    def copy(self):
        """
        return a copy of the vector
        
        Example :

        >>> v = Vector(5,-1)
        >>> w = v.copy()
        >>> w.x = 6
        >>> print(v.x,w.x)
        5 6
        """

        return Vector(self.x,self.y)
        
    def norm(self):
        """
        set the vector to a unit vector which has the same direction if vector is not null

        Example:

        >>> c = Vector(4,3).norm()
        >>> print(c.x,c.y)
        0.8 0.6
        """

        r = self.radius()
        if r != 0:
            self.x /= r
            self.y /= r
        return self

class Point(Coord):
    """
    2D Point
    At initialisation Point coordinates are set to None

    Example:
    
    >>> p = Point(7,1)
    >>> q = Point(2,-3)
    >>> print(round(p.distance(q),3))
    6.403
    """

    def copy(self):
        """
        return a copy of the point
        
        Example :

        >>> v = Point(5,-1)
        >>> w = v.copy()
        >>> w.x = 6
        >>> print(v.x,w.x)
        5 6
        """

        return Point(self.x,self.y)

    def distance(self,p):
        """
        return the distance from self to Point p

        Example:
        
        >>> p = Point(7,1)
        >>> q = Point(2,-3)
        >>> print(round(p.distance(q),3))
        6.403
        """

        return math.sqrt((p.x-self.x)**2+(p.y-self.y)**2)

    def closer(self,a,b):
        """
        return True if self is closer to a than b else return false

        Example:
        
        >>> p = Point(7,1)
        >>> q = Point(2,-3)
        >>> print(Point(2,1).closer(p,q))
        False
        """

        return self.distance(a) < self.distance(b)

    def translate(self,o):
        """
        translate the point
        if o is a Vector or Point then add o coordinates
        if o is a Line defined by A and B then add AB vector
        return the point
        
        Example:
        
        >>> p = Point(4,1).translate(Vector(2,3))
        >>> print(p.x, p.y)
        6 4
        """

        if type(o) == Point or type(o) == Vector:
            self.x,self.y = self.x+o.x,self.y+o.y
        elif type(o) == Line:
            self.x,self.y = self.x+o.b.x-o.a.x,self.y+o.b.y-o.a.y
        return self

    def rotate(self,center,angle):
        """
        rotate the point
        center is the center of rotation
        angle is in radians
        return the point
        
        Example:
        
        >>> p = Point(4,1).rotate(Point(3,0),math.pi/3)
        >>> print(round(p.x,3),round(p.y,3))
        2.634 1.366
        """
        
        self.x,self.y = (self.x-center.x)*math.cos(angle)-(self.y-center.y)*math.sin(angle)+center.x,(self.x-center.x)*math.sin(angle)+(self.y-center.y)*math.cos(angle)+center.y
        return self

    def scale(self,center,ratio):
        """
        transforms the point whith an homothety
        center is the center of homothety
        ratio is a number

        Example:

        >>> p = Point(3,0).scale(Point(0,1),2.5)
        >>> print(p.x,p.y)
        7.5 -1.5
        """
        
        self.x,self.y = ratio*self.x+(1-ratio)*center.x,ratio*self.y+(1-ratio)*center.y
        return self

    def reflect(self,o):
        """
        transform the point with a symetry
        if o is a Point then reflect is a central symetry
        if o is a Line then reflect is an axial symetry
        return the point
        
        Example:
        
        >>> p = Point(4,1).reflect(Point(2,0))
        >>> print(p.x,p.y)
        0 -1
        """
        self.transform(TransformMatrix().reflection(o))
        return self
    
    def transform(self,matrix):
        """
        transform the point
        matrix is a TransformMatrix
        
        Example
        
        >>> t = TransformMatrix([1,1,0,1,2,3])
        >>> p = Point(4,5).transform(t)
        >>> print(p.x,p.y)
        6 12
        """
        self.x,self.y = matrix.matrix[0]*self.x+matrix.matrix[2]*self.y+matrix.matrix[4],matrix.matrix[1]*self.x+matrix.matrix[3]*self.y+matrix.matrix[5]
        return self

class WPoints(object):
    """
    Set of weights points

    Example

    >>> s = WPoints([(Point(2,3),1),(Point(4,-1),2),(Point(5,-3),1)])
    >>> g = s.barycenter()
    >>> print(g.x,g.y)
    3.75 -0.5
    """

    def __init__(self,system = []):
        """
        Initialise the set

        Example

        >>> s = WPoints([(Point(2,3),1),(Point(4,-1),2)])
        """

        self.set(system)
        return None

    def clear(self):
        """
        clear the set
        return the object
        """

        self.points = []
        return self
    
    def set(self,system):
        """
        put the set
        system is a list of couple (p,w) where p is a Point and w a number
        return the object

        Example

        >>> s = WPoints()
        >>> g = s.set([(Point(2,3),1),(Point(4,-1),2),(Point(5,-3),1)]).barycenter()
        >>> print(g.x,g.y)
        3.75 -0.5
        """

        self.points = system
        return self
    
    def add(self,p,w):
        """
        add a couple (p,w)
        p is a Point
        w is a number
        return the object

        Example

        >>> s = WPoints()
        >>> s.add(Point(2,3),1)
        >>> s.add(Point(4,-1),2)
        >>> s.add(Point(5,-3),1)
        >>> g = s.barycenter()
        >>> print(g.x,g.y)
        3.75 -0.5
        """
        self.points.append((p,w))
        return self
        
    def barycenter(self):
        """
        return the set's barycenter

        Example

        >>> s = WPoints([(Point(2,3),1),(Point(4,-1),2),(Point(5,-3),1)])
        >>> g = s.barycenter()
        >>> print(g.x,g.y)
        3.75 -0.5
        """
        g = Point(0,0)
        w = 0
        for p in self.points:
            w += p[1]
            g.set(g.x+p[0].x*p[1],g.y+p[0].y*p[1])
        g.set(g.x/w,g.y/w)
        return g

class Line(object):
    """
    2D line
    """

    nullDet = 1e-5
    
    def __init__(self,a=None,b=None,inf=False):
        """
        Create a line between a and b. if inf is False, the line is a segment

        Example:

        >>> l = Line(Point(1,2),Point(3,4),inf=True)
        """

        self.set(a,b,inf)

    def set(self,a,b,inf=False):
        """
        Create a line between a and b. if inf is False, the line is a segment
        return the line
        
        Example:

        >>> l = Line()
        >>> l.set(Point(1,2),Point(3,4),inf=True)
        """

        if a:
            self.a = a.copy()
        if b:
            self.b = b.copy()
        self.inf = inf
        return self

    def copy(self):
        """
        return a copy of the line

        Example:

        >>> l = Line(Point(1,2),Point(3,4))
        >>> m = l.copy()
        """
        return Line(self.a,self.b,self.inf)
        
    def length(self):
        """
        return the length of the segment and None if line is infinite
        
        Example:

        >>> l = Line(Point(1,2),Point(3,4),inf=False)
        >>> print(round(l.length(),2))
        2.83
        >>> l = Line(Point(1,2),Point(3,4),inf=True)
        >>> print(l.length())
        None
        """
        
        if not self.inf:
            return self.a.distance(self.b)
        else:
            return None

    def angle(self):
        """
        return the line angle in radians
        angle is oriented from first to second point

        Example:

        >>> l = Line(Point(1,2),Point(3,4))
        >>> print(math.degrees(l.angle()))
        45.0
        """

        return Coord(self.b.x-self.a.x,self.b.y-self.a.y).angle()

    def to_line(self):
        """
        set a line or segment to a line
        return the line
        """

        self.inf = True
        return self

    def to_segment(self):
        """
        set a line or segment to a segment
        return the line
        """

        self.inf = False
        return self

    def is_infinite(self):
        """
        return True if self is a line and False if self is a segment

        Example:

        >>> l = Line(Point(1,2),Point(3,4))
        >>> print(l.is_infinite())
        False
        """

        return self.inf

    def reverse(self):
        """
        exchange first and second point
        return the line

        Example:

        >>> l = Line(Point(1,2),Point(3,4)).reverse()
        >>> print(l.start().x,l.start().y)
        3 4
        """

        self.a,self.b = self.b,self.a
        return self

    def start(self):
        """
        return first definition Point of the line

        Example:

        >>> l = Line(Point(1,2),Point(3,4))
        >>> s = l.start()
        >>> print(s.x,s.y)
        1 2
        """

        return self.a
    
    def end(self):
        """
        return second definition Point of the line

        Example:

        >>> l = Line(Point(1,2),Point(3,4))
        >>> s = l.end()
        >>> print(s.x,s.y)
        3 4
        """

        return self.b

    def vector(self):
        """
        return unit vector of the line

        Example:

        >>> l = Line(Point(1,2),Point(4,6))
        >>> v = l.vector()
        >>> print(v.x,v.y)
        0.6 0.8
        """
        d = self.a.distance(self.b)
        if d < Coord.nullDistance:
            return None
        return Vector(self.b.x-self.a.x,self.b.y-self.a.y).norm()

    def distance(self,p):
        """
        return the distance from p to self

        Example:

        >>> l = Line(Point(1,2),Point(4,6))
        >>> print(l.distance(Point(2,2)))
        0.8
        >>> print(round(l.distance(Point(0,1)),2))
        1.41
        >>> l = Line(Point(1,2),Point(4,6),inf=True)
        >>> print(round(l.distance(Point(0,1)),2))
        0.2
        """
        d = self.a.distance(self.b)
        if d < Coord.nullDistance:
            if self.inf:
                return None
            else:
                return p.distance(self.a)
        else:     
            if self.inf:
                return abs((p.x - self.a.x)*(self.b.y - self.a.y) - (p.y-self.a.y)*(self.b.x-self.a.x))/d
            else:
                s = (p.x-self.a.x)*(self.b.x-self.a.x) + (p.y-self.a.y)*(self.b.y-self.a.y)
                if s <= 0:
                    return p.distance(self.a)
                elif s >= d**2:
                    return p.distance(self.b)
                else:
                  return abs((p.x - self.a.x)*(self.b.y - self.a.y) - (p.y-self.a.y)*(self.b.x-self.a.x))/d

    def parallel(self,p):
        """
        return the parallel line through p

        Example:

        >>> l = Line(Point(1,2),Point(4,6))
        >>> m = l.parallel(Point(3,2))
        >>> a = m.start()
        >>> print(a.x,a.y)
        3 2
        >>> b = m.end()
        >>> print(b.x,b.y)
        3.6 2.8
        """
        v = self.vector()
        if v:
            return Line(p,Point(p.x+v.x,p.y+v.y),inf=True)
        else:
            return None

    def perpendicular(self,p):
        """
        return the perpendicular line through p

        Example:

        >>> l = Line(Point(1,2),Point(4,6))
        >>> m = l.perpendicular(Point(3,2))
        >>> a = m.start()
        >>> print(a.x,a.y)
        3 2
        >>> b = m.end()
        >>> print(b.x,b.y)
        2.2 2.6
        """
        v = self.vector()
        if v:
            return Line(p,Point(p.x-v.y,p.y+v.x),True)
        else:
            return None

    def midpoint(self):
        """
        return the midpoint of the segment
        if the object is an infinite line then return None

        Example:

        >>> l = Line(Point(1,2),Point(4,6))
        >>> m = l.midpoint()
        >>> print(m.x,m.y)
        2.5 4.0
        >>> l = Line(Point(1,2),Point(4,6),inf=True)
        >>> m = l.midpoint()
        >>> print(m)
        None
        """
        if not self.inf:
            return Point((self.a.x+self.b.x)/2,(self.a.y+self.b.y)/2)
        else:
            return None

    def midperpendicular(self):
        """
        return the midperpendicular line of the segment

        Example:

        >>> l = Line(Point(1,2),Point(4,6))
        >>> m = l.midperpendicular()
        >>> a = m.start()
        >>> print(a.x,a.y)
        2.5 4.0
        >>> b = m.end()
        >>> print(b.x,b.y)
        1.7 4.6
        """
        if self.inf:
            return None
        v = self.vector()
        if v:
            m =self.midpoint()
            return Line(m,Point(m.x-v.y,m.y+v.x),True)
        else:
            return None

    def bisector(self,l):
        """
        return the angle bisector line between self and l

        Example:

        >>> l = Line(Point(2,1),Point(5,2))
        >>> m = Line(Point(1,2),Point(4,6))
        >>> b = l.bisector(m)
        >>> print(b)
        None
        >>> l = Line(Point(2,1),Point(5,2),True)
        >>> m = Line(Point(1,2),Point(4,6),True)
        >>> b = l.bisector(m)
        >>> e = b.start()
        >>> print(round(e.x,2),round(e.y,2))
        -0.33 0.22
        >>> f = b.end()
        >>> print(round(f.x,2),round(f.y,2))
        0.48 0.81
        """
        i = self.inter(l)
        if type(i) == Point:
            a = (self.angle()+l.angle())/2
            return Line(i,Point(i.x+math.cos(a),i.y+math.sin(a)),True)
        else:
            return None

    def inter(self,l):
        """
        return the intersection between self and l if it exists else None

        Example:

        >>> l = Line(Point(2,1),Point(5,2))
        >>> m = Line(Point(1,2),Point(4,6))
        >>> i = l.inter(m)
        >>> print(i)
        None
        >>> l = Line(Point(2,1),Point(5,2),True)
        >>> m = Line(Point(1,2),Point(4,6),True)
        >>> i = l.inter(m)
        >>> print(round(i.x,2),round(i.y,2))
        -0.33 0.22
        """
        det = (self.b.x-self.a.x)*(l.b.y-l.a.y) - (self.b.y-self.a.y)*(l.b.x-l.a.x)
        if abs(det) < Line.nullDet:
            ## parallel lines
            if abs((self.b.x-self.a.x)*(l.a.y-self.a.y) - (self.b.y-self.a.y)*(l.a.x-self.a.x)) < Line.nullDet:
                if self.inf:
                    return l
                if l.inf:
                    return self
                ext = (self.b.x-self.a.x)**2 + (self.b.y-self.a.y)**2
                extLa = (self.b.x-self.a.x)*(l.a.x-self.a.x) + (self.b.y-self.a.y)*(l.a.y-self.a.y)
                extLb = (self.b.x-self.a.x)*(l.b.x-self.a.x) + (self.b.y-self.a.y)*(l.b.y-self.a.y)
                if extLa < extLb:
                    l2 = l
                else:
                    l2 = Line(l.b,l.a)
                    extLa,extLb = extLb,extLa
                if extLb <0 or extLa > ext:
                    return None
                if extLa < 0:
                    if extLb > ext:
                        return self
                    else:
                        return Line(self.a,l2.b,False)
                else:
                    if extLb > ext:
                        return Line(l2.a,self.b,False)
                    else:
                        return Line(l2.a,l2.b,False)
            else:
                ## strictly
                return None
        else:
            ## non parallel lines
            x = ((l.a.x*(l.b.y-l.a.y)-l.a.y*(l.b.x-l.a.x))*(self.b.x-self.a.x) - (self.a.x*(self.b.y-self.a.y)-self.a.y*(self.b.x-self.a.x))*(l.b.x-l.a.x))/det
            y = ((l.a.x*(l.b.y-l.a.y)-l.a.y*(l.b.x-l.a.x))*(self.b.y-self.a.y) - (self.a.x*(self.b.y-self.a.y)-self.a.y*(self.b.x-self.a.x))*(l.b.y-l.a.y))/det
            if not self.inf:
                ext = (self.b.x-self.a.x)*(x-self.a.x) + (self.b.y-self.a.y)*(y-self.a.y)
                if ext < 0 or ext > (self.b.x-self.a.x)**2 + (self.b.y-self.a.y)**2:
                    return None
            if not l.inf:
                ext = (l.b.x-l.a.x)*(x-l.a.x) + (l.b.y-l.a.y)*(y-l.a.y)
                if ext < 0 or ext > (l.b.x-l.a.x)**2 + (l.b.y-l.a.y)**2:
                    return None
            return Point(x,y)

    def translate(self,v):
        """
        translate the line
        v is a vector

        Example:

        >>> l = Line(Point(2,0),Point(4,3)).translate(Vector(1,-2))
        >>> a = l.start()
        >>> print(a.x,a.y)
        3 -2
        >>> b = l.end()
        >>> print(b.x,b.y)
        5 1
        """
        self.a.translate(v)
        self.b.translate(v)
        return self

    def rotate(self,center,angle):
        """
        rotate the line
        center is a point
        angle is in radians

        Example:

        >>> l = Line(Point(2,0),Point(4,3)).rotate(Point(0,1),math.pi/2)
        >>> a = l.start()
        >>> print(round(a.x,2),round(a.y,2))
        1.0 3.0
        >>> b = l.end()
        >>> print(round(b.x,2),round(b.y,2))
        -2.0 5.0
        """
        self.a.rotate(center,angle)
        self.b.rotate(center,angle)
        return self

    def scale(self,center,ratio):
        """
        transform the line usign a homothety

        Example:

        >>> l = Line(Point(2,0),Point(4,3)).scale(Point(0,1),2)
        >>> a = l.start()
        >>> print(round(a.x,2),round(a.y,2))
        4 -1
        >>> b = l.end()
        >>> print(round(b.x,2),round(b.y,2))
        8 5
        """
        self.a.scale(center,ratio)
        self.b.scale(center,ratio)
        return self

    def reflect(self,o):
        """
        flip the line
        o can be a point or a line

        Example:

        >>> l = Line(Point(2,0),Point(4,3))
        >>> m = l.reflect(Line(Point(1,0),Point(-1,3)))
        >>> a = m.start()
        >>> print(round(a.x,2),round(a.y,2))
        0.62 -0.92
        >>> b = m.end()
        >>> print(round(b.x,2),round(b.y,2))
        -2.92 -1.62
        """
        self.a.reflect(o)
        self.b.reflect(o)
        return self

    def transform(self,matrix):
        """
        transform the line
        matrix is a TransformMatrix

        Example:

        >>> m = TransformMatrix([1,1,0,2,3,4])
        >>> l = Line(Point(2,0),Point(4,3)).transform(m)
        >>> a = l.start()
        >>> print(a.x,a.y)
        5 6
        >>> b = l.end()
        >>> print(b.x,b.y)
        7 14
        """
        self.a.transform(matrix)
        self.b.transform(matrix)
        return self

class bounding_box(object):
    """
    class BoundingBox
    evaluate extrema points in a set of points

    example:

    to be completed
    """
    
    def __init__(self):
        """
        init the bounding box
        """
        self.origin = None
        self.min = None
        self.max = None
        self.minXinf = None
        self.minXsup = None
        self.minYinf = None
        self.minYsup = None
        self.maxXinf = None
        self.maxXsup = None
        self.maxYinf = None
        self.maxYsup = None

    def add_point(self,p):
        """
        add a p point to the bounding box
        """
        if not self.min:
            self.origin = p.copy()
            self.min = p.copy()
            self.max = p.copy()
            self.minXinf = p.copy()
            self.minXsup = p.copy()
            self.minYinf = p.copy()
            self.minYsup = p.copy()
            self.maxXinf = p.copy()
            self.maxXsup = p.copy()
            self.maxYinf = p.copy()
            self.maxYsup = p.copy()
        else:
            if abs(p.x - self.min.x) < 1e-6:
                if p.y < self.minXinf.y:
                    self.minXinf = p.copy()
                elif p.y > self.minXsup.y:
                    self.minXsup = p.copy()
            elif p.x < self.min.x:
                self.min.x = p.x
                self.minXinf = p.copy()
                self.minXsup = p.copy()
            if abs(p.y - self.min.y) < 1e-6:
                if p.x < self.minYinf.x:
                    self.minYinf = p.copy()
                elif p.x > self.minYsup.x:
                    self.minYsup = p.copy()
            elif p.y < self.min.y:
                self.min.y = p.y
                self.minYinf = p.copy()
                self.minYsup = p.copy()
            if abs(p.x - self.max.x) < 1e-6:
                if p.y < self.maxXinf.y:
                    self.maxXinf = p.copy()
                elif p.y > self.maxXsup.y:
                    self.maxXsup = p.copy()
            elif p.x > self.max.x:
                self.max.x = p.x
                self.maxXinf = p.copy()
                self.maxXsup = p.copy()
            if abs(p.y - self.max.y) < 1e-6:
                if p.x < self.maxYinf.x:
                    self.maxYinf = p.copy()
                elif p.x > self.maxYsup.x:
                    self.maxYsup = p.copy()
            elif p.y > self.max.y:
                self.max.y = p.y
                self.maxYinf = p.copy()
                self.maxYsup = p.copy()

    def add_bounding_box(self,b):
        """
        add another bounding box to the bounding box 
        """
        if b.origin:
            self.add_point(b.origin)
            self.add_point(b.minXinf)
            self.add_point(b.minXsup)         
            self.add_point(b.minYinf)
            self.add_point(b.minYsup)
            self.add_point(b.maxXinf)
            self.add_point(b.maxXsup)
            self.add_point(b.maxYinf)
            self.add_point(b.maxYsup)

    def frame(self):
        """
        return a polyline frame around the set of points
        """
        if self.min:
            path = Path()
            path.new_sub_path()
            poly = Polyline().add_node([self.min,Point(self.max.x,self.min.y),self.max,Point(self.min.x,self.max.y),self.min])
            path.add(poly)
            return path
        else:
            return None
        
    def get(self,pos = 'center'):
        """
        get a position in the bounding box
        available positions are:
        origin first point set in the bounding box
        top-left, top-right, bottom-left, bottom-right corners of bounding box's frame
        top, bottom, left, right middle points of bounding box's edges
        width, height frame's dimensions         
        """
        if not self.min:
            return None
        p = pos.lower().strip()
        if p == 'origin':
            return self.origin.copy()
        elif p == 'top-left':
            return Point(self.min.x,self.max.y)
        elif p == 'top':
            return Point((self.min.x+self.max.x)/2.0,self.max.y)
        elif p == 'top-right':
            return Point(self.max.x,self.max.y)
        elif p == 'left':
            return Point(self.min.x,(self.min.y+self.max.y)/2.0)
        elif p == 'center':
            return Point((self.min.x+self.max.x)/2.0,(self.min.y+self.max.y)/2.0)
        elif p == 'right':
            return Point(self.max.x,(self.min.y+self.max.y)/2.0)
        elif p == 'bottom-left':
            return Point(self.min.x,self.min.y)
        elif p == 'bottom':
            return Point((self.min.x+self.max.x)/2,self.min.y)
        elif p == 'bottom-right':
            return Point(self.max.x,self.min.y)
        elif p == 'minxinf':
            return self.minXinf
        elif p == 'minxsup':
            return self.minXsup
        elif p == 'minyinf':
            return self.minYinf
        elif p == 'minysup':
            return self.minYsup
        elif p == 'maxxinf':
            return self.maxXinf
        elif p == 'maxxsup':
            return self.maxXsup
        elif p == 'maxyinf':
            return self.maxYinf
        elif p == 'maxysup':
            return self.maxYsup
        elif p == 'width':
            return self.max.x - self.min.x
        elif p == 'height':
            return self.max.y - self.min.y
        else:
            raise ValueError('unexpected pos : %s' % p)

##    def cotation(self,x,y,stepx,stepy,side='xy'):
##        """
##        to be completed
##        """
#### MARK
##        paths = []
##        if not self.min:
##            return paths
##        if side == 'x' or side =='xy':
##            p = []
##            if abs(self.minXinf.y - y) < abs(self.minXsup.y - y):
##                p.append(Polyline().add_node([self.minXinf,Point(self.minXinf.x,y)]))
##            else:
##                p.append(Polyline().add_node([self.minXsup,Point(self.minXsup.x,y)]))
##            p.append(Polyline().add_node([Point(self.min.x,y),Point(self.max.x,y)]))
        
class GObj(object):
    """
    2D geometric object
    abstract class
    """
    
    def start(self):
        """
        abstract method
        return curve's first point
        """
        raise NotImplementedError("start is not implemented in "+str(type(self)))

    def end(self):
        """
        abstract method
        return curve's last point
        """
        raise NotImplementedError("end is not implemented in "+str(type(self)))

    def start_vector(self):
        """
        abstract method
        return a unit tangent vector to the curve at first point
        """
        raise NotImplementedError("startVector is not implemented in "+str(type(self)))

    def end_vector(self):
        """
        abstract method
        return a unit tangent vector to the curve at last point
        """
        raise NotImplementedError("startVector is not implemented in "+str(type(self)))


class NodeCurve(GObj):
    """
    generic class for polylines and bezier curves
    """

    SmoothCoeff = 0.6 ## for bezier curve

    def __init__(self):
        """
        Init the curve
        clear nodes list
        """
        self.clear()

    def clear(self):
        """
        clear nodes list
        return the object
        """
        self.nodes = []
        return self

    def add_node(self,p):
        """
        add a copy of the point to the nodes list
        p is a Point or a list of point
        return the object

        Example:

        >>> p = Polyline()
        >>> p.add_node(Point(3,-2))
        >>> p.add_node([Point(4,5),Point(7,-3),Point(8,2)])
        >>> print([(item.x,item.y) for item in p.get_nodes()])
        [(3, -2), (4, 5), (7, -3), (8, 2)]
        """
        if type(p) == list or type(p)==tuple:
                for item in p:
                    self.nodes.append(item.copy())
        else:
            self.nodes.append(p.copy())
        return self

    def append(self,curve):
        """
        Append the curve with a same type cuve
        curve must begin at the end of the object
        return True if possible and done
        else return False
   
        Example:

        >>> p = Polyline().add_node([Point(3,-2),Point(7,4)])
        >>> q = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> print(p.append(q))
        False
        >>> print(q.append(p))
        True
        >>> print([(item.x,item.y) for item in q.get_nodes()])
        [(4, 3), (6, 1), (3, -2), (7, 4)]
        """
        if type(self) == type(curve):
            if len(self.nodes) == 0:
                start = 0
            else:
                if self.end().distance(curve.start()) > Coord.nullDistance:
                    return False
                start = 1
            n = curve.get_nodes()
            for i in range(start,len(n)):
                self.add_node(n[i])
            return True
        else:
            return False

    def reverse(self):
        """
        reverse the nodes list
        return the object
   
        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> print([(item.x,item.y) for item in p.reverse().get_nodes()])
        [(3, -2), (6, 1), (4, 3)]
        """
        self.nodes.reverse()
        return self

    def get_nodes(self):
        """
        return the nodes list
   
        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> print([(item.x,item.y) for item in p.get_nodes()])
        [(4, 3), (6, 1), (3, -2)]
        """
        return self.nodes

    def get_node(self,index):
        """
        return, if it exists, the point at index in the nodes list
        first point index is 0
        return None if not found
   
        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> item = p.get_node(5)
        >>> print(item)
        None
        >>> item = p.get_node(1)
        >>> print(item.x,item.y)
        6 1
        """
        try:
            return self.nodes[index]
        except:
            return None

    def start(self):
        """
        return the curve's first point
   
        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> item = p.start()
        >>> print(item.x,item.y)
        4 3
        """
        try:
            return self.nodes[0]
        except:
            return None
        
    def end(self):
        """
        return the curve's last point
   
        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> item = p.end()
        >>> print(item.x,item.y)
        3 -2
        """
        try:
            return self.nodes[-1]
        except:
            return None

    def start_vector(self):
        """
        return a unit tangent vector to the curve at first point
   
        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> item = p.start_vector()
        >>> print(round(item.x,3),round(item.y,3))
        0.707 -0.707
        """
        try:
            l = self.nodes[0].distance(self.nodes[1])
            return Vector((self.nodes[1].x - self.nodes[0].x)/l,(self.nodes[1].y - self.nodes[0].y)/l)
        except:
            return None
    
    def end_vector(self):
        """
        return a unit tangent vector to the curve at last point
   
        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> item = p.end_vector()
        >>> print(round(item.x,3),round(item.y,3))
        -0.707 -0.707
        """
        try:
            l = self.nodes[-1].distance(self.nodes[-2])
            return Vector((self.nodes[-1].x - self.nodes[-2].x)/l,(self.nodes[-1].y - self.nodes[-2].y)/l)
        except:
            return None

    def translate(self,v):
        """
        translate the curve
        v is a Vector
        return the object

        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> p.translate(Vector(1,2))
        >>> print([(item.x,item.y) for item in p.get_nodes()])
        [(5, 5), (7, 3), (4, 0)]
        """
        for p in self.nodes:
            p.translate(v)
        return self

    def rotate(self,center,angle):
        """
        rotate the curve
        center is a point
        angle is the angle in radians
        return the object

        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> p.rotate(Point(0,1),math.pi/2)
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.get_nodes()])
        [(-2.0, 5.0), (0.0, 7.0), (3.0, 4.0)]
        """
        for p in self.nodes:
            p.rotate(center,angle)
        return self

    def scale(self,center,ratio):
        """
        transform the curve with a homothety
        center is a point
        ratio is a number
        return the object

        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> p.scale(Point(0,1),-2)
        >>> print([(item.x,item.y) for item in p.get_nodes()])
        [(-8, -3), (-12, 1), (-6, 7)]
        """
        for p in self.nodes:
            p.scale(center,ratio)
        return self

    def reflect(self,o):
        """
        flip the object with a reflection
        if o is a point then the reflection is a central symetry
        if o is a line then the reflection is an axial symetry
        return the object

        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> p.reflect(Point(0,1))
        >>> print([(item.x,item.y) for item in p.get_nodes()])
        [(-4, -1), (-6, 1), (-3, 4)]
        """
        matrix = TransformMatrix().reflection(o)
        for p in self.nodes:
            p.transform(matrix)
        return self

    def transform(self,matrix):
        """
        transform the object
        matrix TransformMatrix 
        return the object

        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> p.transform(TransformMatrix([1,0,0,-1,0,2]))
        >>> print([(item.x,item.y) for item in p.get_nodes()])
        [(4, -1), (6, 1), (3, 4)]
        """
        for p in self.nodes:
            p.transform(matrix)
        return self

class Polyline(NodeCurve):
    """
    Polyline is a continuous line composed of one or more line segments specified by endpoints(nodes).

    """

    def copy(self):
        """
        return a copy of the polyline

        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> q = p.copy()
        """
        poly = Polyline()
        for p in self.nodes:
            poly.add_node(p)
        return poly

    def length(self,n = 0):
        """
        return the length of the polyline
        n, useless here, is defined for compatibility with other GObj functions

        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(6,1),Point(3,-2)])
        >>> print(round(p.length(),3))
        7.071
        """
        l = 0
        for i in range(len(self.nodes)-1):
            l += self.nodes[i].distance(self.nodes[i+1])
        return l 

    def bounding_box(self):
        """
        return the polyline bounding box
        """
        bbox = bounding_box()
        for p in self.nodes:
            bbox.add_point(p)
        return bbox

    def to_polyline(self,approx = 0):
        """
        return an approx polyline of the object
        approx is the max distance to erase a node (default:0)

        if approx > 0 then simplify the polyline
        else has no effect
        return the polyline

        Example:

        >>> p = Polyline().add_node([Point(4,3),Point(4,1),Point(3,-2)])
        >>> q = p.to_polyline(0.2)
        >>> print([(item.x,item.y) for item in q.get_nodes()])
        [(4, 3), (4, 1), (3, -2)]
        >>> q = p.to_polyline(0.5)
        >>> print([(item.x,item.y) for item in q.get_nodes()])
        [(4, 3), (3, -2)]
        """
        if approx > 0:
            p = Polyline()
            l = self._simplify(approx)
            for node in l:
                p.add_node(node)
            return p
        else:
            return self.copy()

    def _simplify(self,approx=1e-3,a=0,b=-1):
        """
        simplify a polyline
        return a list of non erased nodes
        """
        if b == -1:
            b = len(self.nodes)-1
        dmax = 0
        idmax = 0
        l = Line(self.nodes[a],self.nodes[b],False)
        for i in range(a+1,b):
            d = l.distance(self.nodes[i])
            if d > dmax:
                idmax = i
                dmax = d
        if dmax > approx:
            left = self._simplify(approx,a,idmax)
            right = self._simplify(approx,idmax,b)
##            left[len(left):] = right[1:]
            left.extend(right[1:])
            return left
        else:
            return [self.nodes[a],self.nodes[b]]

class BCurve(NodeCurve):
    """
    Bezier curve
    defaults are cubic Bezier curves 

    Example:

    >>> p = BCurve().add_node([Point(4,3),Point(4,1),Point(3,0),Point(1,0)])
    >>> m = p.get(0.5)
    >>> print(m.x,m.y)
    3.25 0.75
    """
    
    def __init__(self,order = 3):
        """
        Init the bezier curve
        order is an integer (default:3)
         1 : linear
         2 : quadratic
         3 : cubic
        """
        NodeCurve.__init__(self)
        self.order = order

    def get_order(self):
        """
        Return the order of the bezier curve
        """
        return self.order

    def copy(self):
        """
        return a copy of the bezier curve
        """
        curve = BCurve(self.order)
        for p in self.nodes:
            curve.add_node(p)
        return curve

    def to_cubic(self):
        """
        Transform the bezier curve to a cubic (3rd order) bezier curve
        return the object

        to be completed: transform a 4th+ order to cubic

        Example:

        >>> c = BCurve(2).add_node([Point(2,1),Point(4,3),Point(3,5),Point(2,4),Point(1,4)])
        >>> c.to_cubic()
        >>> print([(round(item.x,2),round(item.y,2)) for item in c.get_nodes()])
        [(2, 1), (3.33, 2.33), (3.67, 3.67), (3, 5), (2.33, 4.33), (1.67, 4.0), (1, 4)]
        """
        if self.order == 1:
            nodes = []
            for i in range(self.path_len()-1):
                nodes.append(self.nodes[i])
                nodes.append(WPoints([(self.nodes[i],3),(self.nodes[i+1],1)]).barycenter())
                nodes.append(WPoints([(self.nodes[i],1),(self.nodes[i+1],3)]).barycenter())
            nodes.append(self.nodes[-1])
            self.order = 3
            self.nodes = nodes
        elif self.order == 2:
            nodes = []
            for i in range(self.path_len()):
                nodes.append(self.nodes[2*i])
                nodes.append(WPoints([(self.nodes[2*i],1),(self.nodes[2*i+1],2)]).barycenter())
                nodes.append(WPoints([(self.nodes[2*i+1],2),(self.nodes[2*i+2],1)]).barycenter())
            nodes.append(self.nodes[-1])
            self.order = 3
            self.nodes = nodes
        elif self.order == 3:
            pass
        elif self.order >= 4:
            raise NotImplementedError("not yet implemented")
        return self

    def path_len(self):
        """
        Return the number of bezier curve in the nodes list

        Example :
        
        >>> c = BCurve(2).add_node([Point(2,1),Point(4,3),Point(3,5),Point(2,4),Point(1,4)])
        >>> print(c.path_len())
        2
        """
        return int(len(self.nodes)/self.order)

    def is_valid_path(self):
        """
        Return True if the number of nodes is ok regarding to the order
        >>> c = BCurve(2).add_node([Point(2,1),Point(4,3),Point(3,5),Point(2,4)])
        >>> print(c.is_valid_path())
        False
        >>> c.add_node(Point(1,4))
        >>> print(c.is_valid_path())
        True
        """
        return (len(self.nodes) % self.order) == 1

    def length(self,n = 5):
        """
        return an approximate length of the Bezier curve using n points for each bezier curve
        n is an integer

        Example :
        
        >>> c = BCurve().add_node([Point(2,1),Point(4,3),Point(3,5),Point(2,4)])
        >>> print(round(c.length(),2))
        4.46
        >>> print(round(c.length(20),2))
        4.52
        """
        nb = n*self.path_len()
        step = 1.0/n ## pour python 2.x
        d = 0
        o = self.start()
        for i in range(nb):
            e = self.get((i+1)*step)
            d += o.distance(e)
            o = e
        return d

    def bounding_box(self):
        """
        return the BCurve bounding box
        """
        bbox = bounding_box()
        for i in range(self.path_len()):
            bbox.add_point(self.nodes[i*self.order])
        bbox.add_point(self.nodes[-1])

        if self.order == 2:
            for i in range(self.path_len()):
                d = self.nodes[self.order*i].x + self.nodes[self.order*i+2].x - 2*self.nodes[self.order*i+1].x
                if abs(d) > 1e-5:
                    t = (self.nodes[self.order*i].x - self.nodes[self.order*i+1].x)/d
                    if t > 0 and t < 1:
                        bbox.add_point(self.get(i+t))
                d = self.nodes[self.order*i].y + self.nodes[self.order*i+2].y - 2*self.nodes[self.order*i+1].y
                if abs(d) > 1e-5:
                    t = (self.nodes[self.order*i].y - self.nodes[self.order*i+1].y)/d
                    if t > 0 and t < 1:
                        bbox.add_point(self.get(i+t))
        elif self.order == 3:
            for i in range(self.path_len()):
                a = self.nodes[self.order*i+3].x - 3*self.nodes[self.order*i+2].x + 3*self.nodes[self.order*i+1].x - self.nodes[self.order*i].x
                b = 2*self.nodes[self.order*i+2].x - 4*self.nodes[self.order*i+1].x +2*self.nodes[self.order*i].x
                c = self.nodes[self.order*i+1].x - self.nodes[self.order*i].x
                if abs(a) > 1e-6:
                    delta = b**2 -4*a*c
                    if delta >= 0:
                        t = (-b-math.sqrt(delta))/(2.0*a)
                        if t > 0 and t < 1:
                            bbox.add_point(self.get(i+t))
                        t = (-b+math.sqrt(delta))/(2.0*a)
                        if t > 0 and t < 1:
                            bbox.add_point(self.get(i+t))
                elif abs(b) > 1e-6:
                    t = -1.0*c/b
                    if t > 0 and t < 1:
                        bbox.add_point(self.get(i+t))
                    
                a = self.nodes[self.order*i+3].y - 3*self.nodes[self.order*i+2].y + 3*self.nodes[self.order*i+1].y - self.nodes[self.order*i].y
                b = 2*self.nodes[self.order*i+2].y - 4*self.nodes[self.order*i+1].y + 2*self.nodes[self.order*i].y
                c = self.nodes[self.order*i+1].y - self.nodes[self.order*i].y
                if abs(a) > 1e-6:
                    delta = b**2 -4*a*c
                    if delta >= 0:
                        t = (-b-math.sqrt(delta))/(2.0*a)
                        if t > 0 and t < 1:
                            bbox.add_point(self.get(i+t))
                        t = (-b+math.sqrt(delta))/(2.0*a)
                        if t > 0 and t < 1:
                            bbox.add_point(self.get(i+t))
                elif abs(b) > 1e-6:
                    t = -1.0*c/b
                    if t > 0 and t < 1:
                        bbox.add_point(self.get(i+t))
        elif self.order >= 4:
            raise NotImplementedError("not yet implemented")
        return bbox

    def to_polyline(self,approx = 5e-2):
        """
        Return a Polyline wich approximate the bezier curve
        approx is maximum distance between the curve and the polyline
        
        Example:

        >>> p = BCurve().add_node([Point(4,3),Point(4,1),Point(3,0),Point(1,0)])
        >>> q = p.to_polyline(0.2)
        >>> print([(item.x,item.y) for item in q.get_nodes()])
        [(4.0, 3.0), (3.8125, 1.6875), (3.25, 0.75), (2.3125, 0.1875), (1.0, 0.0)]
        """
        n = max(int(self.length()/(2.0*approx)),5) ## at least 5 points
##        step = self.path_len()/n ## pour python 3
        step = self.path_len()/float(n) ## python 2.x

        l = Polyline()
        for i in range(n):
            try:
                l.add_node(self.get(i*step))
            except:
                break
        l.add_node(self.end())
        return l.to_polyline(approx)

    def get(self,t):
        """
        Return the t parameter point in the bezier curve
        0 <= t <= 1 first Bezier curve
        1 < t < 2 second Bezier curve
        ...
        n-1 < t <= n last Bezier curve

        Example:

        >>> p = BCurve().add_node([Point(4,3),Point(4,1),Point(3,0),Point(1,0)])
        >>> m = p.get(0.5)
        >>> print(m.x,m.y)
        3.25 0.75
        """
        if t > self.path_len():
            raise ValueError('{val} exceeds max : {vmax}'.format(val = t, vmax = self.path_len()))
        else:
            p = int(t)
            if p == self.path_len():
                p -= 1
            t -= p

            x = 0
            y = 0
            for i in range(self.order+1):
                c = _choose(i,self.order)*t**i*(1-t)**(self.order-i)
                x += c*self.nodes[self.order*p+i].x
                y += c*self.nodes[self.order*p+i].y
            return Point(x,y)

class Arc(GObj):
    """
    elliptical arc
    """

    def __init__(self,center,rx,ry,ax,a1,a2):
        """
        Init the elliptical arc
        center point, center of the ellipse
        rx and ry numbers, major and minor axes
        ax angle in radians, with x_axis
        a1 and a2 angles in radians, begin and end of the arc

        Example:

        >>> a = Arc(Point(1,0),5,4,0,0,math.pi/4)
        """
        self.set(center,rx,ry,ax,a1,a2)


    def set(self,center,rx,ry,ax,a1,a2):
        """
        set the elliptical arc parameters
        return the object

        Example:

        >>> a = Arc(Point(1,0),5,4,0,0,math.pi/4)
        >>> a.set(Point(3,0),5,4,0,0,math.pi/4)
        """
        self.center = center.copy()
        self.rx = rx
        self.ry = ry
        self.ax = ax
        self.a1 = a1
        self.a2 = a2
        return self

    def copy(self):
        """
        return a copy of the arc

        Example:

        >>> a = Arc(Point(1,0),5,4,0,0,math.pi/4)
        >>> b = a.copy()        
        """
        arc = Arc(self.center,self.rx,self.ry,self.ax,self.a1,self.a2)
        return arc

    def append(self,arc):
        """
        append arc if arc continues the object with same parameters 
        arc is an Arc
        return True if arc is added to the the object
        return False if impossible to do

        Example:

        >>> a = Arc(Point(1,0),5,4,0,0,math.pi/4)
        >>> b = Arc(Point(3,2),5,4,0,math.pi/4,math.pi/2)
        >>> print(a.append(b))
        False
        >>> b.set(Point(1,0),5,4,0,math.pi/4,math.pi/2)
        >>> print(a.append(b))
        True
        """
        if type(arc) == Arc:
            if arc.center.distance(self.center) < Point.nullDistance and arc.rx == self.rx and arc.ry == self.ry and arc.ax == self.ax and abs(arc.a1 - self.a2) < 1e-5 and abs(arc.a2 - self.a1) < 5:
                self.a2 = arc.a2
                return True
        return False
        
    def get(self,a):
        """
        Return a parameter point of the arc

        Example:

        >>> a = Arc(Point(1,0),5,4,0,0,math.pi)
        >>> p = a.get(0)
        >>> print(p.x,p.y)
        6.0 0.0
        >>> p = a.get(math.pi/4)
        >>> print(round(p.x,2),round(p.y,2))
        4.54 2.83
        
        """
        return Point(self.center.x+math.cos(self.ax)*self.rx*math.cos(a)-math.sin(self.ax)*self.ry*math.sin(a),
                     self.center.y+math.sin(self.ax)*self.rx*math.cos(a)+math.cos(self.ax)*self.ry*math.sin(a))

    def length(self,n = 5):
        """
        return an approximate length of the elliptical arc using n points
        n is an integer

        Example :
        
        >>> a = Arc(Point(2,3),4,2,0,0,math.pi/2)
        >>> print(round(a.length(),2))
        4.81
        >>> print(round(a.length(20),2))
        4.84
        """
        l = 0
        for i in range(n-1):
            l += self.get(self.a1+(self.a2-self.a1)*i/float(n-1)).distance(self.get(self.a1+(self.a2-self.a1)*(i+1)/float(n-1)))
        return l

    def start(self):
        """
        return the first point of the elliptical arc

        Example:

        >>> a = Arc(Point(2,3),4,2,0,0,math.pi/2)
        >>> p = a.start()
        >>> print(p.x,p.y)
        6.0 3.0
        """
        return self.get(self.a1)
    
    def end(self):
        """
        return the last point of the elliptical arc

        Example:

        >>> a = Arc(Point(2,3),4,2,0,0,math.pi/2)
        >>> p = a.end()
        >>> print(round(p.x,2),round(p.y,2))
        2.0 5.0
        """
        return self.get(self.a2)

    def start_vector(self):
        """
        return a unit tangent vector to the arc at first point

        Example:

        >>> a = Arc(Point(2,3),4,2,0,0,math.pi/2)
        >>> v = a.start_vector()
        >>> print(round(v.x,2),round(v.y,2))
        -0.0 1.0
        """
        x = -math.cos(self.ax)*self.rx*math.sin(self.a1)-math.sin(self.ax)*self.ry*math.cos(self.a1)
        y = -math.sin(self.ax)*self.rx*math.sin(self.a1)+math.cos(self.ax)*self.ry*math.cos(self.a1)
        r = 1.0*math.sqrt(x**2+y**2) ## for python 2.x
        if r == 0:
            return Vector(0,0)
        elif self.a2 > self.a1:
            return Vector(x/r,y/r)
        else:
            return Vector(-x/r,-y/r)
        
    def end_vector(self):
        """
        return a unit tangent vector to the arc at first point

        Example:

        >>> a = Arc(Point(2,3),4,2,0,0,math.pi/2)
        >>> v = a.end_vector()
        >>> print(round(v.x,2),round(v.y,2))
        -1.0 0.0
        """
        x = -math.cos(self.ax)*self.rx*math.sin(self.a2)-math.sin(self.ax)*self.ry*math.cos(self.a2)
        y = -math.sin(self.ax)*self.rx*math.sin(self.a2)+math.cos(self.ax)*self.ry*math.cos(self.a2)
        r = 1.0*math.sqrt(x**2+y**2) ## for python 2.x
        if r == 0:
            return Vector(0,0)
        elif self.a2 > self.a1:
            return Vector(x/r,y/r)
        else:
            return Vector(-x/r,-y/r)

    def bounding_box(self):
        """
        return the arc bounding box
        """

        bbox = bounding_box()
        bbox.add_point(self.start())
        bbox.add_point(self.end())

        if abs(math.cos(self.ax)) < 1e-5:
            ex = math.pi/2
            ey = 0
        else:
            ex = math.atan(-self.ry*math.tan(self.ax)/self.rx)
            if abs(math.sin(self.ax)) < 1e-5:
                ey = math.pi/2
            else:
                ey = math.atan(self.ry/math.tan(self.ax)/self.rx)

        n = math.ceil((min(self.a1,self.a2)-ex)/math.pi)
        while ex+n*math.pi < max(self.a1,self.a2):
            bbox.add_point(self.get(ex+n*math.pi))
            n += 1

        n = math.ceil((min(self.a1,self.a2)-ey)/math.pi)
        while ey+n*math.pi < max(self.a1,self.a2):
            bbox.add_point(self.get(ey+n*math.pi))
            n += 1

        return bbox

    def to_polyline(self,approx = 5e-2):
        """
        Return a Polyline wich approximate the
        approx is maximum distance between the curve and the polyline

        Example:

        >>> a = Arc(Point(2,3),4,2,0,0,math.pi/2)
        >>> p = a.to_polyline(0.1)
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.get_nodes()])
        [(6.0, 3.0), (5.78, 3.66), (4.83, 4.41), (3.74, 4.8), (2.0, 5.0)]
        """
        n = int(2*math.ceil(abs(self.a2-self.a1)*max(self.rx,self.ry)/(2*math.acos(1-approx/min(self.rx**2/float(self.ry),self.ry**2/float(self.rx))))))
        p = Polyline()
        for i in range(n):
            p.add_node(self.get(self.a1+i*(self.a2-self.a1)/n))
        p.add_node(self.end())
        return p.to_polyline(approx)

    def translate(self,v):
        """
        translate the arc
        v is a Vector
        return the object

        Example:

        >>> a = Arc(Point(2,3),4,2,0,0,math.pi/2)
        >>> a.translate(Vector(1,2))
        >>> print((a.center.x,a.center.y),a.rx,a.ry,round(a.ax,3),round(a.a1,3),round(a.a2,3))
        (3, 5) 4 2 0 0 1.571
        """
        self.center.translate(v)
        return self

    def rotate(self,center,angle):
        """
        rotate the arc
        center is a point
        angle is the angle in radians
        return the object

        Example:

        >>> a = Arc(Point(2,3),4,2,0,0,math.pi/2)
        >>> a.rotate(Point(3,-1),math.pi/3)
        >>> print((round(a.center.x,3),round(a.center.y,3)),a.rx,a.ry,round(a.ax,3),round(a.a1,3),round(a.a2,3))
        (-0.964, 0.134) 4 2 1.047 0 1.571
        """
        self.center.rotate(center,angle)
        self.ax += angle
        if self.ax > math.pi:
            self.ax -= 2*math.pi
        elif self.ax < -math.pi:
            self.ax += 2*math.pi
        return self

    def scale(self,center,ratio):
        """
        transform the arc with an homothety
        center is a point
        ratio is a number
        return the object

        Example:

        >>> a = Arc(Point(2,3),4,2,0,0,math.pi/2)
        >>> a.scale(Point(1,-1),2)
        >>> print((round(a.center.x,3),round(a.center.y,3)),a.rx,a.ry,round(a.ax,3),round(a.a1,3),round(a.a2,3))
        (3, 7) 8 4 0 0 1.571
        """
        self.center.scale(center,ratio)
        self.rx *= abs(ratio)
        self.ry *= abs(ratio)
        return self

    def reflect(self,o):
        """
        flip the object with a reflection
        if o is a point then the reflection is a central symetry
        if o is a line then the reflection is an axial symetry
        return the object

        Example:

        >>> a = Arc(Point(2,3),4,2,0,0,math.pi/2)
        >>> a.reflect(Point(1,0))
        >>> print((round(a.center.x,3),round(a.center.y,3)),a.rx,a.ry,round(a.ax,3),round(a.a1,3),round(a.a2,3))
        (0.0, -3.0) 4.0 2.0 3.142 0.0 1.571
        """
        self.transform(TransformMatrix().reflection(o))
        return self
    
    def transform(self,matrix):
        """
        transform the object
        matrix TransformMatrix
        return the object

        Example:

        >>> a = Arc(Point(2,3),4,2,0,0,math.pi/2)
        >>> a.transform(TransformMatrix([2,0,0,-1,0,2]))
        >>> print((round(a.center.x,3),round(a.center.y,3)),a.rx,a.ry,round(a.ax,3),round(a.a1,3),round(a.a2,3))
        (4.0, -1.0) 8.0 2.0 0.0 0.0 -1.571
        """
        m = matrix.mul(TransformMatrix([self.rx*math.cos(self.ax),self.rx*math.sin(self.ax),
                                              -self.ry*math.sin(self.ax),self.ry*math.cos(self.ax),
                                              self.center.x,self.center.y]))
        d = m.matrix[0]**2+m.matrix[1]**2-m.matrix[2]**2-m.matrix[3]**2
        if d == 0:
            t = math.pi/4   ### a verifier
        else:
            t = 0.5*math.atan(2*(m.matrix[0]*m.matrix[2]+m.matrix[1]*m.matrix[3])/d)
        center = Point(0,0).transform(m)
        px = Point(math.cos(t),math.sin(t)).transform(m)
        ax = Point(px.x-center.x,px.y-center.y).angle()
        rx = px.distance(center)
        ry = Point(-math.sin(t),math.cos(t)).transform(m).distance(center)
        u = TransformMatrix().set([rx*math.cos(ax),rx*math.sin(ax),-ry*math.sin(ax),ry*math.cos(ax),center.x,center.y])
        p1 = self.get(self.a1).transform(matrix).transform(u.invert())
        if p1.y <0:
            a1 = -math.acos(p1.x)
        else:
            a1 = math.acos(p1.x)
        p2 = self.get(self.a2).transform(matrix)
        if Point(math.cos(a1 + self.a1 - self.a2),math.sin(a1 + self.a1 - self.a2)).transform(u).distance(p2) < Coord.nullDistance:
            a2 = a1 + self.a1 - self.a2 ## indirect affine transformation
        else:
            a2 = a1 + self.a2 - self.a1 ## indirect affine transformation
        self.set(center,rx,ry,ax,a1,a2)
        return self

def _link(a,b,curveType ='bcurve',smooth = None):
    """
    return the curve wich links a and b curves
    curvetype can be bcurve(default) or polyline (or elliptical arc in further version)
    return None if a and b are already linked

    >>> p = Polyline().add_node([Point(2,3),Point(3,5)])
    >>> b = BCurve().add_node([Point(5,3),Point(6,3),Point(7,2),Point(8,1)])
    >>> l = _link(p,b)
    >>> print([(round(item.x,2),round(item.y,2)) for item in l.get_nodes()])
    [(3, 5), (3.76, 6.52), (3.3, 3.0), (5, 3)]
    """
    if smooth == None:
        smooth = NodeCurve.SmoothCoeff
        
    l= a.end().distance(b.start())
    if l < Coord.nullDistance:
        return None
    elif curveType == 'bcurve':
        s = BCurve()
        s.add_node(a.end().copy())
        l *= smooth
        s.add_node(Point(a.end().x+l*a.end_vector().x,a.end().y+l*a.end_vector().y))
        s.add_node(Point(b.start().x-l*b.start_vector().x,b.start().y-l*b.start_vector().y))
        s.add_node(b.start().copy())
        return s
    ###### add link with an arc
    else: ## line (polyline with 2 points) if curvetype != 'bcurve' and 'arc'
        s = Polyline()
        s.add_node(a.end().copy())
        s.add_node(b.start().copy())
        return s

class SvgObj(object):
    """
    class SvgObj
    objects are groups or paths
    """

    def __init__(self,param={}):
        """
        Init the object without parameters by default
        """
        self.param = DTree()
        self.set_param(param)
        
    def clear_param(self):
        """
        clear all object's parameters (such as id, style, ...)
        """
        self.param.clear()
        return self

    def set_param(self,dic):
        """
        set object's parameters
        """
        self.param.set(dic)
        return self

    def add_param(self,key,value):
        """
        add a parameter to the object

        Example:

        to be completed
        """
        self.param.add(key,value)
        return self

    def get_param(self,key):
        """
        return an object's parameter
        """
        return self.param.get(key)  

    def get_params(self):
        """
        return all object's parameters as a dictionary
        """
        return self.param.get_dic()

class Group(SvgObj):
    """
    class Group
    group of paths in a svg document
    """

    def __init__(self,param = {}):
        """
        initialise the group
        """
        SvgObj.__init__(self,param)

    
class Path(SvgObj):
    """
    Path made of subPaths composed by GObj
    """

    def __init__(self,param = {'style':{'fill':'none','stroke':'#000000','stroke-width':'0.3mm'}}):
        """
        Init the path
        clear all subpaths
        """
        SvgObj.__init__(self,param)
        self.paths = []

    def clear_path(self):
        """
        clear all subpaths
        return the object
        """
        self.paths = []
        return self

    def copy(self):
        """
        return a copy of the path

        to be completed : parameters copy
        """
        p = Path()
        for subpath in self.paths:
            p.new_sub_path()
            for curve in subpath:
                p.add(curve)
        ##param
        return p

    def new_sub_path(self):
        """
        add a new subpath
        return subpath index (0 for the first subpath)

        Example:

        >>> p = Path()
        >>> idx = p.new_sub_path()
        >>> print(idx)
        0
        """
        self.paths.append([])
        return len(self.paths)-1
        
    def subpath_len(self):
        """
        return the number of subpaths

        Example:

        >>> p = Path()
        >>> p.new_sub_path()
        >>> print(p.subpath_len())
        1
        """
        return len(self.paths)
        
    def add(self,curve,subPath = -1):
        """
        add a curve in a subpath
        curve is a line, bezier curve, arc ...
        subpath is the subpath index (last by default)
        return the path

        Example:

        >>> p = Path()
        >>> p.new_sub_path()
        >>> c = BCurve().add_node([Point(0,0),Point(1,0),Point(2,1),Point(3,1)])
        >>> p.add(c)
        """
        if len(self.paths[subPath]):
            if not self.paths[subPath][-1].append(curve.copy()):
                self.paths[subPath].append(curve.copy())
        else:
            self.paths[subPath].append(curve.copy())
        return self

    def bounding_box(self):
        """
        return the path's bounding box
        """
        bbox = bounding_box()
        if self.subpath_len():
            for subPath in self.paths:
                for path in subPath:
                    bbox.add_bounding_box(path.bounding_box())
        return bbox

    def is_linked(self,subPath = -1):
        """
        return True if all curves in subpath are linked together else return False
        subpath is the subpath index (-1 : last by default)

        Example:

        >>> p = Path()
        >>> p.new_sub_path()
        >>> c = BCurve().add_node([Point(0,0),Point(1,0),Point(2,1),Point(3,1)])
        >>> p.add(c)
        >>> d = Polyline().add_node([Point(3,1),Point(3,5)])
        >>> p.add(d)
        >>> print(p.is_linked())
        True
        >>> e = Polyline().add_node([Point(3,6),Point(1,3)])
        >>> p.add(e)
        >>> print(p.is_linked())
        False
        """
        l = len(self.paths[subPath]) 
        if l == 0:
            return False
        for i in range(l-1):
            if self.paths[subPath][i].end().distance(self.paths[subPath][i+1].start()) >= Coord.nullDistance:
                return False
        return True

    def link(self,subPath = -1,curveType = 'bcurve',smooth = NodeCurve.SmoothCoeff):
        """
        link all curves in the subpath
        subpath is the subpath index (-1 : last by default)
        curvetype string 'bcurve' or 'polyline'
        smooth float for 'bcurve' only
        return the path

        Example:

        >>> p = Path()
        >>> p.new_sub_path()
        >>> d = Polyline().add_node([Point(0,1),Point(2,1)])
        >>> p.add(d)
        >>> e = Polyline().add_node([Point(3,4),Point(5,3)])
        >>> p.add(e)
        >>> p.link()
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][1].get_nodes()])
        [(2, 1), (3.9, 1.0), (1.3, 4.85), (3, 4)]
        """
        l = len(self.paths[subPath])
        sp = []
        if l > 0:
            for i in range(l-1):
                sp.append(self.paths[subPath][i])
                if self.paths[subPath][i].end().distance(self.paths[subPath][i+1].start()) > Coord.nullDistance:
                    sp.append(_link(self.paths[subPath][i],self.paths[subPath][i+1],curveType,smooth))
            sp.append(self.paths[subPath][l-1])
        self.paths[subPath] = sp
        return self

    def is_closed(self,subPath = -1):
        """
        return True if all curves in subpath are linked together and subpath is closed else return False
        subpath is the subpath index (-1 : last by default)

        Example:

        >>> p = Path()
        >>> p.new_sub_path()
        >>> d = Polyline().add_node([Point(3,1),Point(3,5),Point(1,0)])
        >>> p.add(d)
        >>> print(p.is_closed())
        False
        >>> e = Polyline().add_node([Point(1,0),Point(3,1)])
        >>> p.add(e)
        >>> print(p.is_closed())
        True
        """
        if not self.is_linked(subPath):
            return False
        if self.paths[subPath][0].start().distance(self.paths[subPath][-1].end()) < Coord.nullDistance:
            return True
        else:
            return False

    def close(self,subPath = -1,curveType = 'bcurve',smooth = BCurve.SmoothCoeff):
        """
        link and close the subpath
        subpath is the subpath index (-1 : last by default)
        curvetype string 'bcurve' or 'polyline'
        smooth float for 'bcurve' only
        return the path

        Example:

        >>> p = Path()
        >>> p.new_sub_path()
        >>> d = Polyline().add_node([Point(3,1),Point(3,5),Point(1,0)])
        >>> p.add(d)
        >>> p.close(curveType='Polyline')
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][-1].get_nodes()])
        [(3, 1), (3, 5), (1, 0), (3, 1)]
        """
        self.link(subPath,curveType,smooth)
        if len(self.paths[subPath]):
            j = _link(self.paths[subPath][-1],self.paths[subPath][0],curveType,smooth)
            if j:
                self.add(j,subPath)
        return self

    def to_polyline(self,approx = 5e-2):
        """
        return a path in wich all subpaths are transformed to polyline
        approx is maximum distance between the curve and the polyline

        Example:

        >>> p = Path()
        >>> p.new_sub_path()
        >>> d = BCurve().add_node([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> r = p.to_polyline(0.1)
        >>> print([(round(item.x,2),round(item.y,2)) for item in r.paths[-1][-1].get_nodes()])
        [(3.0, 1.0), (4.37, 1.3), (5.75, 2.25), (6.7, 3.63), (7.0, 5.0)]
        """
        polyPath = Path()
        for path in self.paths:
            polyPath.new_sub_path()
            poly = Polyline()
            for subpath in path:
                r = poly.append(subpath.to_polyline(approx))
            polyPath.add(poly)
        return polyPath

    def translate(self,v):
        """
        translate the path
        v is a Vector
        return the object

        Example:

        >>> p = Path()
        >>> p.new_sub_path()
        >>> d = BCurve().add_node([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> p.translate(Vector(2,3))
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][-1].get_nodes()])
        [(5, 4), (7, 4), (9, 6), (9, 8)]
        """
        for path in self.paths:
            for subpath in path:
                subpath.translate(v)
        return self

    def rotate(self,center,angle):
        """
        rotate the path
        center is a point
        angle is the angle in radians
        return the object

        Example:

        >>> p = Path()
        >>> p.new_sub_path()
        >>> d = BCurve().add_node([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> p.rotate(Point(0,2),math.pi/2)
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][-1].get_nodes()])
        [(1.0, 5.0), (1.0, 7.0), (-1.0, 9.0), (-3.0, 9.0)]
        """
        for path in self.paths:
            for subpath in path:
                subpath.rotate(center,angle)
        return self

    def scale(self,center,ratio):
        """
        transform the path with an homothety
        center is a point
        ratio is a number
        return the object

        Example:

        >>> p = Path()
        >>> p.new_sub_path()
        >>> d = BCurve().add_node([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> p.scale(Point(1,1),2)
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][-1].get_nodes()])
        [(5, 1), (9, 1), (13, 5), (13, 9)]
        """
        for path in self.paths:
            for subpath in path:
                subpath.scale(center,ratio)
        return self

    def reflect(self,o):
        """
        flip the path with a reflection
        if o is a point then the reflection is a central symetry
        if o is a line then the reflection is an axial symetry
        return the object

        Example:

        >>> p = Path()
        >>> p.new_sub_path()
        >>> d = BCurve().add_node([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> p.reflect(Point(1,0))
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][-1].get_nodes()])
        [(-1, -1), (-3, -1), (-5, -3), (-5, -5)]
        """
        for path in self.paths:
            for subpath in path:
                subpath.reflect(o)
        return self


    def transform(self,matrix):
        """
        transform all curves
        matrix TransformMatrix
        return the object

        Example:

        >>> p = Path()
        >>> p.new_sub_path()
        >>> d = BCurve().add_node([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> p.transform(TransformMatrix([1,0,0,-1,2,0]))
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][-1].get_nodes()])
        [(5, -1), (7, -1), (9, -3), (9, -5)]
        """
        for path in self.paths:
            for subpath in path:
                subpath.transform(matrix)
        return self

    def from_svg_path(self,svgPath,matrix = None):
        """
        import the path from svgPath
        svgpath string corresponds to 'd' field on inkscape
        return the path

        Example:

        >>> p = Path().from_svg_path('M 10,0 L 20,30 L 40,15 z')
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][-1].get_nodes()])
        [(10.0, 0.0), (20.0, 30.0), (40.0, 15.0), (10.0, 0.0)]
        """
        svgList = svgPath.replace(',',' ').split()
        self.clear_path()
        cObj = None
        previousNode = Point(0,0)
        i = 0
        while i < len(svgList):
            if svgList[i] == 'M':
                self.new_sub_path()
                previousNode = Point(float(svgList[i+1]),float(svgList[i+2]))
                i += 3
                while i < len(svgList) and _is_num(svgList[i]):
                    if not cObj:
                        cObj = Polyline()
                        cObj.add_node(previousNode)
                    previousNode = Point(float(svgList[i]),float(svgList[i+1]))
                    cObj.add_node(previousNode)
                    i += 2
                if cObj:
                    self.add(cObj)
                    cObj = None
            elif svgList[i] == 'm':
                self.new_sub_path()
                previousNode = Point(previousNode.x+float(svgList[i+1]),previousNode.y+float(svgList[i+2]))
                i += 3
                while i < len(svgList) and _is_num(svgList[i]):
                    if not cObj:
                        cObj = Polyline()
                        cObj.add_node(previousNode)
                    previousNode = Point(previousNode.x+float(svgList[i]),previousNode.y+float(svgList[i+1]))
                    cObj.add_node(previousNode)
                    i += 2
                if cObj:
                    self.add(cObj)
                    cObj = None
            elif svgList[i] == 'L':
                cObj = Polyline()
                cObj.add_node(previousNode)
                i += 1
                while i < len(svgList) and _is_num(svgList[i]):
                    previousNode = Point(float(svgList[i]),float(svgList[i+1]))
                    cObj.add_node(previousNode)
                    i += 2
                self.add(cObj)
                cObj = None
            elif svgList[i] == 'l':
                cObj = Polyline()
                cObj.add_node(previousNode)
                i += 1
                while i < len(svgList) and _is_num(svgList[i]):
                    previousNode = Point(previousNode.x+float(svgList[i]),previousNode.y+float(svgList[i+1]))
                    cObj.add_node(previousNode)
                    i += 2
                self.add(cObj)
                cObj = None
            elif svgList[i] == 'z' or svgList[i] == 'Z':
                self.close(curveType = 'polyline')
                previousNode = self.paths[-1][-1].end()
                i += 1
            elif svgList[i] == 'C':
                cObj = BCurve()
                cObj.add_node(previousNode)
                i += 1
                while i < len(svgList) and _is_num(svgList[i]):
                    previousNode = Point(float(svgList[i]),float(svgList[i+1]))
                    cObj.add_node(previousNode)
                    i += 2
                self.add(cObj)
                cObj = None
            elif svgList[i] == 'c':
                cObj = BCurve()
                cObj.add_node(previousNode)
                i += 1
                while i < len(svgList) and _is_num(svgList[i]):
                    cObj.add_node(Point(previousNode.x+float(svgList[i]),previousNode.y+float(svgList[i+1])))
                    cObj.add_node(Point(previousNode.x+float(svgList[i+2]),previousNode.y+float(svgList[i+3])))
                    previousNode = Point(previousNode.x+float(svgList[i+4]),previousNode.y+float(svgList[i+5]))
                    cObj.add_node(previousNode)
                    i += 6
                self.add(cObj)
                cObj = None
            elif svgList[i] == 'Q':
                cObj = BCurve(order=2)
                cObj.add_node(previousNode)
                i += 1
                while i < len(svgList) and _is_num(svgList[i]):
                    previousNode = Point(float(svgList[i]),float(svgList[i+1]))
                    cObj.add_node(previousNode)
                    i += 2
                self.add(cObj)
                cObj = None
            elif svgList[i] == 'q':
                cObj = BCurve(order=2)
                cObj.add_node(previousNode)
                i += 1
                while i < len(svgList) and _is_num(svgList[i]):
                    cObj.add_node(Point(previousNode.x+float(svgList[i]),previousNode.y+float(svgList[i+1])))
                    previousNode = Point(previousNode.x+float(svgList[i+2]),previousNode.y+float(svgList[i+3]))
                    cObj.add_node(previousNode)
                    i += 4
                self.add(cObj)
                cObj = None
            elif svgList[i] == 'A':
                i += 1
                while i < len(svgList) and _is_num(svgList[i]):
                    rx = float(svgList[i])
                    ry = float(svgList[i+1])
                    phi = math.radians(float(svgList[i+2]))
                    fa = int(svgList[i+3])
                    fs = int(svgList[i+4])
                    b = Point(float(svgList[i+5]),float(svgList[i+6])).rotate(Point(0,0),-phi)
                    a = previousNode.copy().rotate(Point(0,0),-phi)

                    rad = min(math.sqrt(((b.x-a.x)/rx)**2+((b.y-a.y)/ry)**2)/2.0,1)
                    vx = (b.x-a.x)/rx/(2-4*fs)/rad
                    vy = (b.y-a.y)/ry/(4*fs-2)
                    if vy > 0:
                        v = math.asin(vx)
                    else:
                        v = math.pi - math.asin(vx)
                    if fa == 1:
                        u = math.pi - (2*fs-1)*math.asin(rad)
                    else:
                        u = (2*fs-1)*math.asin(rad)
                    center = Point(a.x-rx*math.cos(v-u),a.y-ry*math.sin(v-u)).rotate(Point(0,0),phi)
                    cObj = Arc(center,rx,ry,phi,v-u,v+u)
                    
                    self.add(cObj)
                    previousNode = Point(float(svgList[i+5]),float(svgList[i+6]))
                    i += 7
                cObj = None
            elif svgList[i] == 'a':
                i += 1
                while i < len(svgList) and _is_num(svgList[i]):
                    rx = float(svgList[i])
                    ry = float(svgList[i+1])
                    phi = math.radians(float(svgList[i+2]))
                    fa = int(svgList[i+3])
                    fs = int(svgList[i+4])
                    b = Point(float(svgList[i+5])+previousNode.x,float(svgList[i+6])+previousNode.y).rotate(Point(0,0),-phi)
                    a = previousNode.copy().rotate(Point(0,0),-phi)

                    rad = min(math.sqrt(((b.x-a.x)/rx)**2+((b.y-a.y)/ry)**2)/2.0,1)
                    vx = (b.x-a.x)/rx/(2-4*fs)/rad
                    vy = (b.y-a.y)/ry/(4*fs-2)
                    if vy > 0:
                        v = math.asin(vx)
                    else:
                        v = math.pi - math.asin(vx)
                    if fa == 1:
                        u = math.pi - (2*fs-1)*math.asin(rad)
                    else:
                        u = (2*fs-1)*math.asin(rad)
                    center = Point(a.x-rx*math.cos(v-u),a.y-ry*math.sin(v-u)).rotate(Point(0,0),phi)
                    cObj = Arc(center,rx,ry,phi,v-u,v+u)
                    
                    self.add(cObj)
                    previousNode = Point(float(svgList[i+5])+previousNode.x,float(svgList[i+6])+previousNode.y)
                    i += 7
                cObj = None
            else:
### COMMENT : A TESTER
                raise ValueError('unknown command %s in %s' % (svgList[i],svgPath))                

        if matrix:
            self.transform(matrix)

        return self

    def to_svg_path(self,digit = 3,matrix = None):
        """
        return a svgpath string corresponds to 'd' field on inkscape from the path
        digit integer, number of digits

        Example:

        >>> p = Path()
        >>> p.new_sub_path()
        >>> d = BCurve().add_node([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> svgpath = p.to_svg_path()
        >>> print(svgpath)
        M 3,1 C 5,1 7,3 7,5 
        """

        if matrix:
            tpath = self.copy().transform(matrix)
        else:
            tpath =self

        path = ''
        for p in range(len(tpath.paths)):
            startPath = True
            for obj in tpath.paths[p]:
                if startPath:
                    path += 'M '+_str_num(obj.start().x,digit)+','+_str_num(obj.start().y,digit)+' '
                    startPath =False
                if type(obj) == Polyline:
                    path += 'L '
                    for i in range(1,len(obj.nodes)):
                        path += _str_num(obj.nodes[i].x,digit)+','+_str_num(obj.nodes[i].y,digit)+' '
                elif type(obj) == BCurve:
                    if obj.order != 3:
                        cubicobj = obj.copy().to_cubic()
                    else:
                        cubicobj = obj
                    path += 'C '
                    for i in range(1,len(cubicobj.nodes)):
                        path += _str_num(cubicobj.nodes[i].x,digit)+','+_str_num(cubicobj.nodes[i].y,digit)+' '
                elif type(obj) == Arc:
                    path += 'A '+_str_num(obj.rx,digit)+','+_str_num(obj.ry,digit)+' '+_str_num(degrees(obj.ax),digit)+' '
                    if abs(obj.a2-obj.a1) > math.pi:
                        path += '1 '
                    else:
                        path += '0 '
                    if obj.a2-obj.a1 > 0:
                        path += '1 '
                    else:
                        path += '0 '
                    path += _str_num(obj.end().x,digit)+','+_str_num(obj.end().y,digit)+' '
            if tpath.is_closed(p):
                path += 'z '
        return path

    def to_scad_poly(self,approx = 5e-2 ,digit = 3):
        """
        return an approximate polygon string description from the path
        compatible with openscad

        Example:

        >>> p = Path()
        >>> p.new_sub_path()
        >>> d = BCurve().add_node([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> scadpoly = p.to_scad_poly(approx=0.1,digit=2)
        >>> print(scadpoly)
        polygon(points=[[3,1],[4.37,1.3],[5.75,2.25],[6.7,3.63],[7,5]],paths=[[0,1,2,3,4]]);
        """
        i = 0
        for i in range(self.subpath_len()):
            self.close(i,'polyline')
        curve = self.to_polyline(approx)
        points = ''
        paths = ''
        i = 0
        for subPath in curve.paths:
            paths += '['
            for p in subPath[0].nodes[:-1]:
                points += '['+_str_num(p.x,digit)+','+_str_num(p.y,digit)+'],'
                paths += str(i)+','
                i += 1
            paths = paths[:-1]+'],'

        return 'polygon(points=['+points[:-1]+'],paths=['+paths[:-1]+']);'

class Svg(object):
    """
    class SVG provides methods to open, read, modify and write SVG files

    Example:

    to be completed
    """

    markers = {'name':'marker','where':'//svg:defs',
               'Arrow1Mstart':{'inkscape:stockid':'Arrow1Mstart','orient':'auto','refY':'0.0','refX':'0.0','id':'Arrow1Mstart','style':'overflow:visible',
                               'inkscape:isstock':'true','path':{'id':'pathArrow','d':'M 0.0,0.0 L 5.0,-5.0 L -12.5,0.0 L 5.0,5.0 L 0.0,0.0 z ',
                                                                 'style':'fill-rule:evenodd;stroke:#000000;stroke-width:1pt;stroke-opacity:1;fill:#000000;fill-opacity:1',
                                                                 'transform':'scale(0.4) translate(10,0)'}
                               },
               'Arrow1Mend':{'inkscape:stockid':'Arrow1Mend','orient':'auto','refY':'0.0','refX':'0.0','id':'Arrow1Mend','style':'overflow:visible',
                               'inkscape:isstock':'true','path':{'id':'pathArrow','d':'M 0.0,0.0 L 5.0,-5.0 L -12.5,0.0 L 5.0,5.0 L 0.0,0.0 z ',
                                                                 'style':'fill-rule:evenodd;stroke:#000000;stroke-width:1pt;stroke-opacity:1;fill:#000000;fill-opacity:1',
                                                                 'transform':'scale(0.4) rotate(180) translate(10,0)'}
                               }
               }

    def __init__(self,svgFile = None,mode = 'egg',unit = 'mm'):
        """
        open a svg file for modification
        svgFile is svg filename if None then default.svg will be the filename
        if mode is egg then svgFile will be searched in the gdesign module
        if mode is inkscape then svgFile will be searched in the inkscape program templates (usable in inkscape's plugin)
        else use svgFile to search the file
        """

        p = etree.XMLParser(huge_tree=True)
        if not svgFile:
            svgFile = 'default.svg'
        if mode == 'egg':
            content = __loader__.get_data(os.path.dirname(__file__)+os.path.sep+svgFile)
        elif mode =='inkscape':
            content = open('../templates/'+svgFile,mode='rb').read()
        else:
            content = open(svgFile,mode='rb').read()

        self.root = etree.fromstring(content,p)
        
        height = _unit_to_pt(self.root.get('height'))
        pathUnit = _unit_to_pt('1'+unit)
        self.transUnit = TransformMatrix().set([pathUnit,0,0,-pathUnit,0,height])

    def exist(self,request):
        """
        return True if the xml request has results
        """
        result = self.root.iterfind(request)
        try:
            next(result)
            return True
        except:
            return False

    def delete(self,objId,objType='path'):
        """
        delete an object in the svg xml tree
        objType and objId are type and id of the xml element
        """
        result = self.root.xpath('//svg:%s[@id="%s"]'%(objType,objId),namespaces=_nss)
        if result:
            for node in result:
                node.getparent().remove(node)
            return True
        return False

    def search(self,objId,objType='path'):
        """
        search an object in the svg xml tree
        objType must be path or g
        return a tuple (node,transform)
        where node is the xml element in the tree and transform is the transform matrix to reach the element
        """
        result = self.root.xpath('//svg:%s[@id="%s"]'%(objType,objId),namespaces=_nss)
        if result:
            node = result[0]
            tr = node.get('transform')
            if tr:
                transText = tr
            else:
                transText = ''
            parent = node.getparent()
            while parent.tag == _subst_ns('svg:g'):
                tr = parent.get('transform')
                if tr:
                    transText = tr + ' ' + transText
                parent = parent.getparent()
            transform = TransformMatrix().from_text(transText)
            return (node,transform)
        else:
            return None

    def get_path(self,idPath):
        """
        return the path with idPath id
        """
        result = self.search(idPath)
        if result:
            return Path().from_svg_path(result[0].get('d'),self.transUnit.invert().mul(result[1]))
        else:
            return None ## raise ?

    def add(self,svgObj,where=''):
        """
        add a group or a path in the svg xml tree
        where is the group id where the object will be located
        if the object has no id, a random one will be used
        
        return the object's id
        """

        if where:
            location = self.search(where,objType='g')
            if not location:
                raise ValueError('group %s not found' % where)
        else:
            location = (self.root,TransformMatrix())

        idSvgObj = svgObj.get_param('id')
        if not idSvgObj:
            newObj = False
            while not newObj:
                ido = ''
                while len(ido) < 5:
                    ido = str(random.random())[2:7]
                if type(svgObj) == Path:
                    idSvgObj = 'path'+ ido
                    newObj = self.root.xpath('//svg:path[@id="%s"]'%idSvgObj,namespaces=_nss) == []
                elif type(svgObj) == Group:
                    idSvgObj = 'g'+ ido
                    newObj = self.root.xpath('//svg:g[@id="%s"]'%idSvgObj,namespaces=_nss) == []
                else:
                    raise TypeError('Inappropriate %s type' % type(svgObj))
        else:
            idRoot = idSvgObj
            if type(svgObj) == Path:
                newObj = self.root.xpath('//svg:path[@id="%s"]'%idSvgObj,namespaces=_nss) == []
            elif type(svgObj) == Group:
                newObj = self.root.xpath('//svg:g[@id="%s"]'%idSvgObj,namespaces=_nss) == []
            else:
                raise TypeError('Inappropriate %s type' % type(svgObj))
            while not newObj:
                idp = ''
                while len(idp) < 3:
                    idp = str(random.random())[2:5]
                idsvgObj = idRoot + idp
                if type(svgObj) == Path:
                    newObj = self.root.xpath('//svg:path[@id="%s"]'%idSvgObj,namespaces=_nss) == []
                elif type(svgObj) == Group:
                    newObj = self.root.xpath('//svg:g[@id="%s"]'%idSvgObj,namespaces=_nss) == []
                else:
                    raise TypeError('Inappropriate %s type' % type(svgObj))
        svgObj.add_param('id',idSvgObj)
        
        if type(svgObj) == Path:
            svgObj.add_param('d',svgObj.to_svg_path(matrix = location[1].invert().mul(self.transUnit)))
            etree.SubElement(location[0],_subst_ns('svg:path'),_subst_ns(svgObj.get_params()))
        elif type(svgObj) == Group:
            etree.SubElement(location[0],_subst_ns('svg:g'),_subst_ns(svgObj.get_params()))
        else:
            raise TypeError('Inappropriate %s type' % type(svgObj))
        
        return idSvgObj

    def add_extra(self,where,name,dic):
        """
        add an extra object to the svg xml tree such as markers
        to be completed
        """
        search = self.root.xpath(where,namespaces=_nss)
        if search:
            _to_xml(search[0],name,dic)
            return True
        else:
            return False

    def write(self,filename):
        """
        write the svg xml tree to filename file
        """
        f = open(filename,mode='wb')
        f.write(etree.tostring(self.root))
        f.close()

    def poly_write(self,filename,approx=0.2):
        """
        write the svg xml tree where each path is converted to a polyline 
        """
        s = Svg() 
        paths = _get_path(self.root)
        for path in paths:
            p = self.get_path(path['id'])
            s.add(p.to_polyline(approx=approx))
        s.write(filename)

    def tsf_write(self,jobName,jobNumber,path='',dpi=500):
        """
        write the svg xml tree in .tsf (Trotec laser cutter)
        subpath order is reversed to cut holes before bounding path
        """
        f = open(path+jobName+'.tsf','w')
        f.write('<!-- Version: 9.4.2.1034>\n<!-- PrintingApplication: inkscape.exe>\n<BegGroup: Header>\n<ProcessMode: Standard>\n')
        f.write('<Size: {0:.2f};{1:.2f}>\n'.format(_unit_to_mm(self.root.get('width')),_unit_to_mm(self.root.get('height'))))
        f.write('<MaterialGroup: Standard>\n<MaterialName: Standard>\n<JobName: {0}>\n<JobNumber: {1}>\n<Resolution: {2}>\n<Cutline: none>\n<EndGroup: Header>\n'.format(jobName,jobNumber,dpi))
        f.write('<BegGroup: DrawCommands>\n')

        height = int(_unit_to_mm(self.root.get('height'))*dpi/25.4)
        paths = _get_path(self.root,[])

        for path in paths:
            p = self.get_path(path['id'])
            if p:
                poly = p.to_polyline(25.4/dpi)
                for i in reversed(range(len(poly.paths))):
                    f.write('<DrawPolygon: {};{};{};{}'.format(len(poly.paths[i][0].nodes),path['color'][0],path['color'][1],path['color'][2]))
                    for pt in poly.paths[i][0].nodes:
                        f.write(';{};{}'.format(int(pt.x*dpi/25.4),height-int(pt.y*dpi/25.4)))
                    f.write('>\n')
        f.write('<EndGroup: DrawCommands>\n')
        f.close()
