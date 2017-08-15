from Rhino.Geometry import Vector3d
import glob
class PVector():
    " processing PVector interface as Vector3d "
    def __init__(self,*args):
        __data = Vector3d(glob.CPLANE.PointAt(*args))
    def __repr__(self):
        return '__data'
    def __str__(self):
        return str(__data)
    def __getattr__(self,attr):
        return getattr(__data,attr)
    def mag(self):
        return Length
    def add(self,v):
        return self + v
    def sub(self,v):
        return self-v
    def mult(self,s):
        return self-s
    def div(self,s):
        return self/s
    def dot(self,v):
        return self*v
    def cross(self,v):
        return Vector3d.CrossProduct(self,v)
    def normalize(self):
        return Unitize()
    def rotate(self,radians):
        Rotate(radians,glob.CPLANE.ZAxis)
    @classmethod
    def angleBetween(cls,a,b):
        return Vector3d.VectorAngle(a,b,glob.CPLANE)
    @classmethod
    def random2D(cls):
        theta = uniform(0,2*PI)
        return Vector3d(math.cos(theta),math.sin(theta),0)
    @classmethod
    def random3D(cls):
        z = uniform(-1,1)
        theta = uniform(0,2*PI)
        v = PVector.random2D() * (1-z*z)**0.5
        return Vector3d(v.X,v.Y,z)
