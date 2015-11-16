#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import math

def _strNum(x,digit = 5):
    """
    return a string wich represents a numbrr
    x is an integer or a float
    digit is the maximum number of digits in the string

    Examples

    >>> print(_strNum(2.123,2))
    2.12
    >>> print(_strNum(3.0073,2))
    3.01
    >>> print(_strNum(3.0013,2))
    3

    """
    if round(x,digit) - round(x,0) == 0:
        return str(int(round(x,0)))
    else:
        return str(round(x,digit))

def _isNum(x):
    """
    return True if x represents a number (float or integer) else False

    Examples

    >>> print(_isNum(4.52))
    True
    >>> print(_isNum('-3.52e-3'))
    True
    >>> print(_isNum('7*3'))
    False
    >>> print(_isNum('hello'))
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

    re_translate = '^[ ]*translate\((-?[0-9]+[.]?[0-9]*,-?[0-9]+[.]?[0-9]*)\)'
    re_matrix = '^[ ]*matrix\((-?[0-9]+[.]?[0-9]*(,-?[0-9]+[.]?[0-9]*){5})\)'
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
##            u = o.startVector()
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

    def fromText(self,text):
        """
        translate a string to a transformation matrix
        text is a string wich is a list of transformation separated by spaces
        transformations order are from right to left
        available transformations are :
        translate(a,b)
        matrix(a,b,c,d,e,f)
        compatible with Inkscape transform field

        Example:

        >>> t = TransformMatrix().fromText('translate(12,5) matrix(2,0,0,2,0,0)')
        >>> print(t.get())
        [2.0, 0.0, 0.0, 2.0, 12.0, 5.0]
        """

        s = re.search(TransformMatrix.re_translate,text)
        if s:
            param = [float(item) for item in s.group(1).split(',')]
            m = TransformMatrix().translation(Vector(param[0],param[1]))
            e = TransformMatrix().fromText(text[s.span()[1]:])
            self.matrix = m.mul(e).matrix
        s = re.search(TransformMatrix.re_matrix,text)
        if s:
            m = TransformMatrix().set([float(item) for item in s.group(1).split(',')])
            e = TransformMatrix().fromText(text[s.span()[1]:])
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

    def setPolar(self,radius,angle):
        """
        set the coordinates of the object in polar system
        radius is the distance from origin
        angle is in radians

        Example:

        >>> c = Coord()
        >>> print(c.setPolar(5,-math.pi/2).y)
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

    def toLine(self):
        """
        set a line or segment to a line
        return the line
        """

        self.inf = True
        return self

    def toSegment(self):
        """
        set a line or segment to a segment
        return the line
        """

        self.inf = False
        return self

    def isInfinite(self):
        """
        return True if self is a line and False if self is a segment

        Example:

        >>> l = Line(Point(1,2),Point(3,4))
        >>> print(l.isInfinite())
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
##            return Line(p,Point(p.x+v[0],p.y+v[1]),inf=True)
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
##            return Line(p,Point(p.x-v[1],p.y+v[0]),True)
        else:
            return None

    def midPoint(self):
        """
        return the midpoint of the segment
        if the object is an infinite line then return None

        Example:

        >>> l = Line(Point(1,2),Point(4,6))
        >>> m = l.midPoint()
        >>> print(m.x,m.y)
        2.5 4.0
        >>> l = Line(Point(1,2),Point(4,6),inf=True)
        >>> m = l.midPoint()
        >>> print(m)
        None
        """
        if not self.inf:
            return Point((self.a.x+self.b.x)/2,(self.a.y+self.b.y)/2)
        else:
            return None

    def midPerpendicular(self):
        """
        return the midperpendicular line of the segment

        Example:

        >>> l = Line(Point(1,2),Point(4,6))
        >>> m = l.midPerpendicular()
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
            m =self.midPoint()
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

    def startVector(self):
        """
        abstract method
        return a unit tangent vector to the curve at first point
        """
        raise NotImplementedError("startVector is not implemented in "+str(type(self)))

    def endVector(self):
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

    def addNode(self,p):
        """
        add a copy of the point to the nodes list
        p is a Point or a list of point
        return the object

        Example:

        >>> p = Polyline()
        >>> p.addNode(Point(3,-2))
        >>> p.addNode([Point(4,5),Point(7,-3),Point(8,2)])
        >>> print([(item.x,item.y) for item in p.getNodes()])
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

        >>> p = Polyline().addNode([Point(3,-2),Point(7,4)])
        >>> q = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
        >>> print(p.append(q))
        False
        >>> print(q.append(p))
        True
        >>> print([(item.x,item.y) for item in q.getNodes()])
        [(4, 3), (6, 1), (3, -2), (7, 4)]
        """
        if type(self) == type(curve):
            if len(self.nodes) == 0:
                start = 0
            else:
                if self.end().distance(curve.start()) > Coord.nullDistance:
                    return False
                start = 1
            n = curve.getNodes()
            for i in range(start,len(n)):
                self.addNode(n[i])
            return True
        else:
            return False

    def reverse(self):
        """
        reverse the nodes list
        return the object
   
        Example:

        >>> p = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
        >>> print([(item.x,item.y) for item in p.reverse().getNodes()])
        [(3, -2), (6, 1), (4, 3)]
        """
        self.nodes.reverse()
        return self

    def getNodes(self):
        """
        return the nodes list
   
        Example:

        >>> p = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
        >>> print([(item.x,item.y) for item in p.getNodes()])
        [(4, 3), (6, 1), (3, -2)]
        """
        return self.nodes

    def getNode(self,index):
        """
        return, if it exists, the point at index in the nodes list
        first point index is 0
        return None if not found
   
        Example:

        >>> p = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
        >>> item = p.getNode(5)
        >>> print(item)
        None
        >>> item = p.getNode(1)
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

        >>> p = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
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

        >>> p = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
        >>> item = p.end()
        >>> print(item.x,item.y)
        3 -2
        """
        try:
            return self.nodes[-1]
        except:
            return None

    def startVector(self):
        """
        return a unit tangent vector to the curve at first point
   
        Example:

        >>> p = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
        >>> item = p.startVector()
        >>> print(round(item.x,3),round(item.y,3))
        0.707 -0.707
        """
        try:
            l = self.nodes[0].distance(self.nodes[1])
            return Vector((self.nodes[1].x - self.nodes[0].x)/l,(self.nodes[1].y - self.nodes[0].y)/l)
        except:
            return None
    
    def endVector(self):
        """
        return a unit tangent vector to the curve at last point
   
        Example:

        >>> p = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
        >>> item = p.endVector()
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

        >>> p = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
        >>> p.translate(Vector(1,2))
        >>> print([(item.x,item.y) for item in p.getNodes()])
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

        >>> p = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
        >>> p.rotate(Point(0,1),math.pi/2)
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.getNodes()])
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

        >>> p = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
        >>> p.scale(Point(0,1),-2)
        >>> print([(item.x,item.y) for item in p.getNodes()])
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

        >>> p = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
        >>> p.reflect(Point(0,1))
        >>> print([(item.x,item.y) for item in p.getNodes()])
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

        >>> p = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
        >>> p.transform(TransformMatrix([1,0,0,-1,0,2]))
        >>> print([(item.x,item.y) for item in p.getNodes()])
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

        >>> p = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
        >>> q = p.copy()
        """
        poly = Polyline()
        for p in self.nodes:
##            poly.addNode(p.copy())
            poly.addNode(p)
        return poly

    def length(self,n = 0):
        """
        return the length of the polyline
        n, useless here, is defined for compatibility with other GObj functions

        Example:

        >>> p = Polyline().addNode([Point(4,3),Point(6,1),Point(3,-2)])
        >>> print(round(p.length(),3))
        7.071
        """
        l = 0
        for i in range(len(self.nodes)-1):
            l += self.nodes[i].distance(self.nodes[i+1])
        return l 

    def toPolyline(self,approx = 0):
        """
        return an approx polyline of the object
        approx is the max distance to erase a node (default:0)

        if approx > 0 then simplify the polyline
        else has no effect
        return the polyline

        Example:

        >>> p = Polyline().addNode([Point(4,3),Point(4,1),Point(3,-2)])
        >>> q = p.toPolyline(0.2)
        >>> print([(item.x,item.y) for item in q.getNodes()])
        [(4, 3), (4, 1), (3, -2)]
        >>> q = p.toPolyline(0.5)
        >>> print([(item.x,item.y) for item in q.getNodes()])
        [(4, 3), (3, -2)]
        """
        if approx > 0:
            p = Polyline()
            l = self._simplify(approx)
            for node in l:
                p.addNode(node)
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
            left[len(left):] = right[1:]
            return left
        else:
            return [self.nodes[a],self.nodes[b]]

class BCurve(NodeCurve):
    """
    Bezier curve
    defaults are quadratic Bezier curves 

    Example:

    >>> p = BCurve().addNode([Point(4,3),Point(4,1),Point(3,0),Point(1,0)])
    >>> m = p.get(0.5)
    >>> print(m.x,m.y)
    3.25 0.75
    """

##    SmoothCoeff = 0.6
    
    def __init__(self,order = 3):
        """
        Init the bezier curve
        order is an integer (default:3)
         1 : linear
         2 : cubic
         3 : quadratic
        """
        NodeCurve.__init__(self)
        self.order = order

    def getOrder(self):
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
            curve.addNode(p)
        return curve

    def toQuadratic(self):
        """
        Transform the bezier curve to a quadratic (3rd order) bezier curve
        return the object

        TODO: transform a 4th+ order to quadratic

        Example:

        >>> c = BCurve(2).addNode([Point(2,1),Point(4,3),Point(3,5),Point(2,4),Point(1,4)])
        >>> c.toQuadratic()
        >>> print([(round(item.x,2),round(item.y,2)) for item in c.getNodes()])
        [(2, 1), (3.33, 2.33), (3.67, 3.67), (3, 5), (2.33, 4.33), (1.67, 4.0), (1, 4)]
        """
        if self.order == 1:
            nodes = []
            for i in range(self.pathLen()-1):
                nodes.append(self.nodes[i])
                nodes.append(WPoints([(self.nodes[i],3),(self.nodes[i+1],1)]).barycenter())
                nodes.append(WPoints([(self.nodes[i],1),(self.nodes[i+1],3)]).barycenter())
            nodes.append(self.nodes[-1])
            self.order = 3
            self.nodes = nodes
        elif self.order == 2:
            nodes = []
            for i in range(self.pathLen()):
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

    def pathLen(self):
        """
        Return the number of bezier curve in the nodes list

        Example :
        
        >>> c = BCurve(2).addNode([Point(2,1),Point(4,3),Point(3,5),Point(2,4),Point(1,4)])
        >>> print(c.pathLen())
        2
        """
        return int(len(self.nodes)/self.order)

    def validPath(self):
        """
        Return True if the number of nodes is ok regarding to the order
        >>> c = BCurve(2).addNode([Point(2,1),Point(4,3),Point(3,5),Point(2,4)])
        >>> print(c.validPath())
        False
        >>> c.addNode(Point(1,4))
        >>> print(c.validPath())
        True
        """
        return (len(self.nodes) % self.order) == 1

    def length(self,n = 5):
        """
        return an approximate length of the Bezier curve using n points for each bezier curve
        n is an integer

        Example :
        
        >>> c = BCurve().addNode([Point(2,1),Point(4,3),Point(3,5),Point(2,4)])
        >>> print(round(c.length(),2))
        4.46
        >>> print(round(c.length(20),2))
        4.52
        """
        nb = n*self.pathLen()
        step = 1.0/n ## pour python 2.x
        d = 0
        o = self.start()
        for i in range(nb):
            e = self.get((i+1)*step)
            d += o.distance(e)
            o = e
        return d

    def toPolyline(self,approx = 5e-2):
        """
        Return a Polyline wich approximate the bezier curve
        approx is maximum distance between the curve and the polyline
        
        Example:

        >>> p = BCurve().addNode([Point(4,3),Point(4,1),Point(3,0),Point(1,0)])
        >>> q = p.toPolyline(0.2)
        >>> print([(item.x,item.y) for item in q.getNodes()])
        [(4.0, 3.0), (3.8125, 1.6875), (3.25, 0.75), (2.3125, 0.1875), (1.0, 0.0)]
        """
        n = max(int(self.length()/(2.0*approx)),5) ## at least 5 points
##        step = self.pathLen()/n ## pour python 3
        step = self.pathLen()/float(n) ## python 2.x
        l = Polyline()
        for i in range(n+1):
            l.addNode(self.get(i*step))
        return l.toPolyline(approx)

    def get(self,t):
        """
        Return the t parameter point in the bezier curve
        0 <= t <= 1 first Bezier curve
        1 < t < 2 second Bezier curve
        ...
        n-1 < t <= n last Bezier curve

        Example:

        >>> p = BCurve().addNode([Point(4,3),Point(4,1),Point(3,0),Point(1,0)])
        >>> m = p.get(0.5)
        >>> print(m.x,m.y)
        3.25 0.75
        """
        if (t > self.pathLen()):
            return None
        else:
            p = int(t)
            if p == self.pathLen():
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

    def startVector(self):
        """
        return a unit tangent vector to the arc at first point

        Example:

        >>> a = Arc(Point(2,3),4,2,0,0,math.pi/2)
        >>> v = a.startVector()
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
        
    def endVector(self):
        """
        return a unit tangent vector to the arc at first point

        Example:

        >>> a = Arc(Point(2,3),4,2,0,0,math.pi/2)
        >>> v = a.endVector()
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

    def toPolyline(self,approx = 5e-2):
        """
        Return a Polyline wich approximate the
        approx is maximum distance between the curve and the polyline

        Example:

        >>> a = Arc(Point(2,3),4,2,0,0,math.pi/2)
        >>> p = a.toPolyline(0.1)
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.getNodes()])
        [(6.0, 3.0), (5.78, 3.66), (4.83, 4.41), (3.74, 4.8), (2.0, 5.0)]
        """
        n = int(2*math.ceil(abs(self.a2-self.a1)*max(self.rx,self.ry)/(2*math.acos(1-approx/min(self.rx**2/float(self.ry),self.ry**2/float(self.rx))))))
        p = Polyline()
        for i in range(n):
            p.addNode(self.get(self.a1+i*(self.a2-self.a1)/n))
        p.addNode(self.end())
        return p.toPolyline(approx)

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

    >>> p = Polyline().addNode([Point(2,3),Point(3,5)])
    >>> b = BCurve().addNode([Point(5,3),Point(6,3),Point(7,2),Point(8,1)])
    >>> l = _link(p,b)
    >>> print([(round(item.x,2),round(item.y,2)) for item in l.getNodes()])
    [(3, 5), (3.76, 6.52), (3.3, 3.0), (5, 3)]
    """
    if smooth == None:
        smooth = NodeCurve.SmoothCoeff
        
    l= a.end().distance(b.start())
    if l < Coord.nullDistance:
        return None
    elif curveType == 'bcurve':
        s = BCurve()
        s.addNode(a.end().copy())
        l *= smooth
        s.addNode(Point(a.end().x+l*a.endVector().x,a.end().y+l*a.endVector().y))
        s.addNode(Point(b.start().x-l*b.startVector().x,b.start().y-l*b.startVector().y))
        s.addNode(b.start().copy())
        return s
    ###### add link with an arc
    else: ## line (polyline with 2 points) if curvetype != 'bcurve' and 'arc'
        s = Polyline()
        s.addNode(a.end().copy())
        s.addNode(b.start().copy())
        return s

class Path(object):
    """
    Path made of subPaths composed by GObj
    """

    def __init__(self):
        """
        Init the path
        clear all subpaths
        """
        self.clear()

    def clear(self):
        """
        clear all subpaths
        return the object
        """
        self.paths = []
        return self

    def newSubPath(self):
        """
        add a new subpath
        return subpath index (0 for the first subpath)

        Example:

        >>> p = Path()
        >>> idx = p.newSubPath()
        >>> print(idx)
        0
        """
        self.paths.append([])
        return len(self.paths)-1
        
    def subPathLen(self):
        """
        return the number of subpaths

        Example:

        >>> p = Path()
        >>> p.newSubPath()
        >>> print(p.subPathLen())
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
        >>> p.newSubPath()
        >>> c = BCurve().addNode([Point(0,0),Point(1,0),Point(2,1),Point(3,1)])
        >>> p.add(c)
        """
        if len(self.paths[subPath]):
            if not self.paths[subPath][-1].append(curve.copy()):
                self.paths[subPath].append(curve.copy())
        else:
            self.paths[subPath].append(curve.copy())
        return self

    def isLinked(self,subPath = -1):
        """
        return True if all curves in subpath are linked together else return False
        subpath is the subpath index (-1 : last by default)

        Example:

        >>> p = Path()
        >>> p.newSubPath()
        >>> c = BCurve().addNode([Point(0,0),Point(1,0),Point(2,1),Point(3,1)])
        >>> p.add(c)
        >>> d = Polyline().addNode([Point(3,1),Point(3,5)])
        >>> p.add(d)
        >>> print(p.isLinked())
        True
        >>> e = Polyline().addNode([Point(3,6),Point(1,3)])
        >>> p.add(e)
        >>> print(p.isLinked())
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
        >>> p.newSubPath()
        >>> d = Polyline().addNode([Point(0,1),Point(2,1)])
        >>> p.add(d)
        >>> e = Polyline().addNode([Point(3,4),Point(5,3)])
        >>> p.add(e)
        >>> p.link()
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][1].getNodes()])
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

    def isClosed(self,subPath = -1):
        """
        return True if all curves in subpath are linked together and subpath is closed else return False
        subpath is the subpath index (-1 : last by default)

        Example:

        >>> p = Path()
        >>> p.newSubPath()
        >>> d = Polyline().addNode([Point(3,1),Point(3,5),Point(1,0)])
        >>> p.add(d)
        >>> print(p.isClosed())
        False
        >>> e = Polyline().addNode([Point(1,0),Point(3,1)])
        >>> p.add(e)
        >>> print(p.isClosed())
        True
        """
        if not self.isLinked(subPath):
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
        >>> p.newSubPath()
        >>> d = Polyline().addNode([Point(3,1),Point(3,5),Point(1,0)])
        >>> p.add(d)
        >>> p.close(curveType='Polyline')
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][-1].getNodes()])
        [(3, 1), (3, 5), (1, 0), (3, 1)]
        """
        self.link(subPath,curveType,smooth)
        if len(self.paths[subPath]):
            j = _link(self.paths[subPath][-1],self.paths[subPath][0],curveType,smooth)
            if j:
                self.add(j,subPath)
        return self

    def toPolyline(self,approx = 5e-2):
        """
        return a path in wich all subpaths are transformed to polyline
        approx is maximum distance between the curve and the polyline

        Example:

        >>> p = Path()
        >>> p.newSubPath()
        >>> d = BCurve().addNode([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> r = p.toPolyline(0.1)
        >>> print([(round(item.x,2),round(item.y,2)) for item in r.paths[-1][-1].getNodes()])
        [(3.0, 1.0), (4.37, 1.3), (5.75, 2.25), (6.7, 3.63), (7.0, 5.0)]
        """
        polyPath = Path()
        for path in self.paths:
            polyPath.newSubPath()
            poly = Polyline()
            for subpath in path:
                poly.append(subpath.toPolyline(approx))
            polyPath.add(poly)
        return polyPath

    def translate(self,v):
        """
        translate the path
        v is a Vector
        return the object

        Example:

        >>> p = Path()
        >>> p.newSubPath()
        >>> d = BCurve().addNode([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> p.translate(Vector(2,3))
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][-1].getNodes()])
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
        >>> p.newSubPath()
        >>> d = BCurve().addNode([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> p.rotate(Point(0,2),math.pi/2)
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][-1].getNodes()])
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
        >>> p.newSubPath()
        >>> d = BCurve().addNode([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> p.scale(Point(1,1),2)
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][-1].getNodes()])
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
        >>> p.newSubPath()
        >>> d = BCurve().addNode([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> p.reflect(Point(1,0))
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][-1].getNodes()])
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
        >>> p.newSubPath()
        >>> d = BCurve().addNode([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> p.transform(TransformMatrix([1,0,0,-1,2,0]))
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][-1].getNodes()])
        [(5, -1), (7, -1), (9, -3), (9, -5)]
        """
        for path in self.paths:
            for subpath in path:
                subpath.transform(matrix)
        return self

    def fromSvgPath(self,svgPath,matrix = None):
        """
        import the path from svgPath
        svgpath string corresponds to 'd' field on inkscape
        return the path

        Example:

        >>> p = Path().fromSvgPath('M 10,0 L 20,30 L 40,15 z')
        >>> print([(round(item.x,2),round(item.y,2)) for item in p.paths[-1][-1].getNodes()])
        [(10.0, 0.0), (20.0, 30.0), (40.0, 15.0), (10.0, 0.0)]
        """
        svgList = svgPath.replace(',',' ').split()
        self.clear()
        cObj = None
        previousNode = Point(0,0)
        i = 0
        while i < len(svgList):
            if svgList[i] == 'M':
                self.newSubPath()
                previousNode = Point(float(svgList[i+1]),float(svgList[i+2]))
                i += 3
                while i < len(svgList) and _isNum(svgList[i]):
                    if not cObj:
                        cObj = Polyline()
                        cObj.addNode(previousNode)
                    previousNode = Point(float(svgList[i]),float(svgList[i+1]))
                    cObj.addNode(previousNode)
                    i += 2
                if cObj:
                    self.add(cObj)
                    cObj = None
            elif svgList[i] == 'm':
                self.newSubPath()
                previousNode = Point(previousNode.x+float(svgList[i+1]),previousNode.y+float(svgList[i+2]))
                i += 3
                while i < len(svgList) and _isNum(svgList[i]):
                    if not cObj:
                        cObj = Polyline()
                        cObj.addNode(previousNode)
                    previousNode = Point(previousNode.x+float(svgList[i]),previousNode.y+float(svgList[i+1]))
                    cObj.addNode(previousNode)
                    i += 2
                if cObj:
                    self.add(cObj)
                    cObj = None
            elif svgList[i] == 'L':
                cObj = Polyline()
                cObj.addNode(previousNode)
                i += 1
                while i < len(svgList) and _isNum(svgList[i]):
                    previousNode = Point(float(svgList[i]),float(svgList[i+1]))
                    cObj.addNode(previousNode)
                    i += 2
                self.add(cObj)
                cObj = None
            elif svgList[i] == 'l':
                cObj = Polyline()
                cObj.addNode(previousNode)
                i += 1
                while i < len(svgList) and _isNum(svgList[i]):
                    previousNode = Point(previousNode.x+float(svgList[i]),previousNode.y+float(svgList[i+1]))
                    cObj.addNode(previousNode)
                    i += 2
                self.add(cObj)
                cObj = None
            elif svgList[i] == 'z' or svgList[i] == 'Z':
                self.close(curveType = 'polyline')
                previousNode = self.paths[-1][-1].end()
                i += 1
            elif svgList[i] == 'C':
                cObj = BCurve()
                cObj.addNode(previousNode)
                i += 1
                while i < len(svgList) and _isNum(svgList[i]):
                    previousNode = Point(float(svgList[i]),float(svgList[i+1]))
                    cObj.addNode(previousNode)
                    i += 2
                self.add(cObj)
                cObj = None
            elif svgList[i] == 'c':
                cObj = BCurve()
                cObj.addNode(previousNode)
                i += 1
                while i < len(svgList) and _isNum(svgList[i]):
                    cObj.addNode(Point(previousNode.x+float(svgList[i]),previousNode.y+float(svgList[i+1])))
                    cObj.addNode(Point(previousNode.x+float(svgList[i+2]),previousNode.y+float(svgList[i+3])))
                    previousNode = Point(previousNode.x+float(svgList[i+4]),previousNode.y+float(svgList[i+5]))
                    cObj.addNode(previousNode)
                    i += 6
                self.add(cObj)
                cObj = None
            elif svgList[i] == 'A':
                i += 1
                while i < len(svgList) and _isNum(svgList[i]):
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
                while i < len(svgList) and _isNum(svgList[i]):
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
                return None

        if matrix:
            self.transform(matrix)

        return self

    def toSvgPath(self,digit = 3):
        """
        return a svgpath string corresponds to 'd' field on inkscape from the path
        digit integer, number of digits

        Example:

        >>> p = Path()
        >>> p.newSubPath()
        >>> d = BCurve().addNode([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> svgpath = p.toSvgPath()
        >>> print(svgpath)
        M 3,1 C 5,1 7,3 7,5 
        """
        path = ''
        for p in range(len(self.paths)):
            path += ''
            for obj in self.paths[p]:
                if p == 0 or obj.start().distance(self.paths[p-1].end()) > Coord.nullDistance:
                    path += 'M '+_strNum(obj.start().x,digit)+','+_strNum(obj.start().y,digit)+' '
                if type(obj) == Polyline:
                    path += 'L '
                    for i in range(1,len(obj.nodes)):
                        path += _strNum(obj.nodes[i].x,digit)+','+_strNum(obj.nodes[i].y,digit)+' '
                elif type(obj) == BCurve:
                    path += 'C '
                    for i in range(1,len(obj.nodes)):
                        path += _strNum(obj.nodes[i].x,digit)+','+_strNum(obj.nodes[i].y,digit)+' '
                elif type(obj) == Arc:
                    path += 'A '+_strNum(obj.rx,digit)+','+_strNum(obj.ry,digit)+' '+_strNum(degrees(obj.ax),digit)+' '
                    if abs(obj.a2-obj.a1) > math.pi:
                        path += '1 '
                    else:
                        path += '0 '
                    if obj.a2-obj.a1 > 0:
                        path += '1 '
                    else:
                        path += '0 '
                    path += _strNum(obj.end().x,digit)+','+_strNum(obj.end().y,digit)+' '
            if self.isClosed(p):
                path += 'z '
        return path

    def toScadPoly(self,approx = 5e-2 ,digit = 3):
        """
        return an approximate polygon string description from the path
        compatible with openscad

        Example:

        >>> p = Path()
        >>> p.newSubPath()
        >>> d = BCurve().addNode([Point(3,1),Point(5,1),Point(7,3),Point(7,5)])
        >>> p.add(d)
        >>> scadpoly = p.toScadPoly(approx=0.1,digit=2)
        >>> print(scadpoly)
        polygon(points=[[3,1],[4.37,1.3],[5.75,2.25],[6.7,3.63],[7,5]],paths=[[0,1,2,3,4]]);
        """
        i = 0
        for i in range(self.subPathLen()):
            self.close(i,'polyline')
        curve = self.toPolyline(approx)
        points = ''
        paths = ''
        i = 0
        for subPath in curve.paths:
            paths += '['
            for p in subPath[0].nodes[:-1]:
                points += '['+_strNum(p.x,digit)+','+_strNum(p.y,digit)+'],'
                paths += str(i)+','
                i += 1
            paths = paths[:-1]+'],'

        return 'polygon(points=['+points[:-1]+'],paths=['+paths[:-1]+']);'
