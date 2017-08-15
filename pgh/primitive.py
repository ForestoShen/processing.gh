import glob
from style import Display
from Rhino.Geometry import *
# basic geometry drawing
def arc(x,y,w,h,start,stop,mode='PIE'):
    " construct a elliptic arc "
    CPLANE = glob.CPLANE
    if w == h:
        res = Arc(Circle(CPLANE,w),Interval(start,stop))
        spt = res.StartPoint
        ept = res.EndPoint
        cpt = CPLANE.Origin
    else:
        a = w/2
        b = h/2
        pl = Plane(CPLANE)
        pl.Translate(Vector3d(x,y,0))
        cpt = pl.Origin
        spt = pl.PointAt( a*math.cos(start),b*math.sin(start),0 )
        ept = pl.PointAt( a*math.cos(stop),b*math.sin(stop),0 )
        ellip = Ellipse(pl,a,b).ToNurbsCurve()
        t0 = ellip.ClosestPoint(spt)[1]
        t1 = ellip.ClosestPoint(ept)[1]
        res = ellip.Trim(t0,t1)
    if mode == "PIE":
        c1 = LineCurve(ept,cpt)
        c2 = LineCurve(cpt,spt)
        res = Curve.JoinCurves([res,c1,c2])[0]
    style.Display(res)
def line(x1,y1,x2,y2,z1=0,z2=0):
    " simple line "
    pl = Plane(glob.CPLANE)
    ln = Line(pl.PointAt(x1,y1,z1),pl.PointAt(x2,y2,z2))
    if glob.AUTO_DISPLAY:
        style.Display(ln)
    return ln

def rect(x1,y1,x2,y2):
    rec = Rectangle3d(glob.CPLANE,Point3d(x1,y1,0),Point3d(x2,y2,0))
    if glob.AUTO_DISPLAY:
        style.Display(rec)
    return rec
def ellipse(x,y,a,b):
    pl = Plane(glob.CPLANE)
    pl.Translate(Vector3d(x,y,0))
    ell = Ellipse(pl,a,b)
    if glob.AUTO_DISPLAY:
        style.Display(ell)
    return ell
def text(content,x,y,z=0,height=None):
    " !TODO add text to screen "
    te = TextEntity()
    te.Text = content
    te.Plane = glob.CPLANE
    if height:
        te.TextHeight = height
    te.Translate(Vector3d(glob.CPLANE.PointAt(x,y,z)))
    txtcrvs = Curve.JoinCurves(te.Explode())
    if glob.AUTO_DISPLAY:
        for crv in txtcrvs:
            style.Display(crv)
    return txtcrvs
### create shape api ###
class Shape(Curve):
    def __init__():
        shape = super(self,Shape).__init__()
        plist = []
def createShape():
    return Shape()
def beginShape(kind = None):
    #! add fiiled polygon
    _SHAPESTACK = glob._SHAPESTACK
    num = len(_SHAPESTACK)
    _SHAPESTACK.append([])
    glob._CSHAPE = _SHAPESTACK[num])
def vertex(x,y,z):
    glob._CSHAPE.append(Point3d(x,y,z))
def endShape():
    pline = Polyline(_SHAPESTACK.pop())
    if glob.AUTO_DISPLAY:
        style.Display(pline)
    return pline
