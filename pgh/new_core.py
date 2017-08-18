import scriptcontext as sc
import Rhino
import rhinoscriptsyntax as rs
from Rhino.Geometry import * #?
import Grasshopper.Kernel.Data.GH_Path as Path
import Grasshopper.DataTree as DataTree
import time
import math
from math import * #!
PI = math.pi
constrain = Rhino.RhinoMath.Clamp
import System.Drawing.Color as Color
import System.Drawing.Rectangle
import pgh.perlin
from random import seed as randomSeed
from random import gauss as randomGaussian
from random import shuffle, choice
from random import uniform
from pgh.interact import *
Simplex = pgh.perlin.SimplexNoise()
import inspect
def random(a = 1,b = 0):
    "random(a,b)->[a,b], random(a)->[0,a], random()->[0,1]"
    return uniform(a,b)
def noise(*args):
    "Simplex noise 1,2,3d"
    if len(args) == 1:
        return Simplex.noise2(args[0],0)
    elif len(args) == 2:
        return Simplex.noise2(*args)
    else:
        return Simplex.noise3(*args)
def noiseDetial():
    raise NotImplemented

# accessible global var
width = 640
height = 800
P2D = Rhino.Display.DefinedViewportProjection.Top
P3D = Rhino.Display.DefinedViewportProjection.Perspective
## global setting
if "DISPLAY" not in sc.sticky:
    sc.sticky["DISPLAY"] = Rhino.Display.CustomDisplay(True)
DISPLAY = sc.sticky["DISPLAY"]
_ghenv = None
all_processing = {}
## display setting
class Style:
    def __init__(self):
        self.IS_FILL = True
        self.FILL_COLOR = Color.FromArgb(255,255,255)
        self.IS_STROKE = True
        self.STROKE_COLOR = Color.FromArgb(1,0,0,0)
        self.STROKE_WEIGHT = 1
class Info:
    def __init__(self):
        self.IS_LOOP = True
        self.LOOP_COUNT = 0
        self.TIME = 0
### dummy placeholder only for import
STYLE = Style()
STYLESTACK = []
_SHAPESTACK = []
_CPLANESTACK = []
CPLANE = Plane.WorldXY
AUTO_DISPLAY = True
GEOMETRY_OUTPUT = True
COLOR_OUTPUT = False
GeoOut = DataTree[object]()
ColorOut = DataTree[Color]()
INFO = Info()
VIEWPORT = Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.ActiveViewport
## general setting that persist over different instacnes
TORLERENCE = Rhino.RhinoDoc.ActiveDoc.PageAbsoluteTolerance
thisDoc = Rhino.RhinoDoc.ActiveDoc
# mouse variable that all instances share(not actually shared, but should be diffcult to notice)
_posInfo = rs.GetCursorPos()
mouseX = _posInfo[0].X
mouseY = _posInfo[0].Y
pmouseX = mouseX
pmouseY = mouseY
mousePressed = False
_pmousePressed = False
mouseMoved = False
mouseDragged = False
mouseClicked = False
def update_mouse():
    global mouseX,screenX,mouseY,screenY,pmouseX,pmouseY,\
           _pmousePressed,mousePressed,mouseMoved,mouseDragged,mouseClicked
    pmouseX = mouseX
    pmouseY = mouseY
    _pmousePressed = mousePressed
    _posInfo = rs.GetCursorPos()
    screenX = _posInfo[1].X
    screenY = _posInfo[1].Y
    client = thisDoc.Views.ActiveView.ActiveViewport.ClientToWorld(_posInfo[3])
    tup = Intersect.Intersection.LinePlane(client,CPLANE)
    if tup[0]:
        ptOnPlane = client.PointAt(tup[1])
        mouseX = ptOnPlane.X
        mouseY = ptOnPlane.Y
    else:
        mouseX = _posInfo[0].X
        mouseY = _posInfo[0].Y
    #? returned mouseX,Y is based on world coord but ellipse,rect...function is based on CPLANE so
    mouseX -= CPLANE.OriginX
    mouseY -= CPLANE.OriginY
    mousePressed = isMousePressed()
    mouseMoved = pmouseX != mouseX or pmouseY != mouseY
    mouseDragged = mouseMoved and mousePressed
    mouseClicked = _pmousePressed and not mousePressed

"""
#useless now
def _clear():
    for uniquevar in [var for var in globals().copy() if var[0] != "_"]:
        del globals()[uniquevar]
def _time_test(fn,arg,time = 1000):
    before = time.clock()
    for i in range(time):
        fn(*arg)
    after = time.clock()
    ms = (after - before)*1000
    print("cost %i ms for %i times"%(ms,count))
    return ms
"""
## helper
def convert_polyline(curve):
    " return a polyline, if convert fail, raise IndexOutOfBound "
    if isinstance(curve,Polyline):
        return curve
    else:
        nc = curve.ToNurbsCurve()
        return toPolyline(nc).TryGetPolyline()[1]
def toPolyline(curve,maxAngleRadians = 0.1, tolerance = 0.1):
    " simplify ToPolyline buildin "
    return curve.ToPolyline(0,0,maxAngleRadians,0,0, tolerance,0.01,0,True)

## basic processing function ##
def NewView(name,Projection,screenX = 0,screenY = 0,seperate = True):
    "create a new rhino viewport"
    exist = Rhino.RhinoDoc.ActiveDoc.Views.Find(name,True)
    if not exist:
        exist = Rhino.RhinoDoc.ActiveDoc.Views.Add(
        name,
        Projection,
        System.Drawing.Rectangle(screenX,screenY,screenX+width,screenY+height),
        seperate)
        viewRect = Rectangle3d(CPLANE,width,height)
        exist.ActiveViewport.ZoomBoundingBox(viewRect.BoundingBox)
    return exist
def background(*args):
    " clear OUTPUT, if has args, set backgound color(a,r,g,b) "
    if len(args):
        c = color(*args)
        Rhino.ApplicationSettings.AppearanceSettings.ViewportBackgroundColor = c
    _clearOutput()
def size(w,h,mode=P2D,name='processing'):
    " set size of new viewport "
    global width,height,VIEWPORT
    width = w
    height = h
    VIEWPORT = NewView(name,mode).ActiveViewport

def toggleColor(state = False):
    "cancel color out mode"
    global COLOR_OUTPUT
    COLOR_OUTPUT = state
def color(*args):
    "accept : (gray), (gray,alphy), (r,g,b), (r,g,b,a)\
    return : Color"
    length = len(args)
    if length == 1:
        if isinstance(args[0],Color):
            return args[0]
        else:
            return Color.FromArgb(args[0],args[0],args[0])
    elif length == 2:
        return Color.FromArgb(args[1],args[0],args[0],args[0])
    elif length == 3:
        return Color.FromArgb(*args)
    elif length == 4:
        return Color.FromArgb(args[3],args[0],args[1],args[2])
def _clearOutput():
    #!! need find a way to dispose display for each
    DISPLAY.Clear()
    DISPLAY.Dispose
    GeoOut.Clear()
    ColorOut.Clear()
def Display(anyCurve):
    " overall display "
    if GEOMETRY_OUTPUT:
        # add diffrent fill and outline to different GeoOut bracnch
        is_fill = STYLE.FILL_COLOR.A > 0
        is_stroke = STYLE.STROKE_COLOR.A > 0
        i = GeoOut.BranchCount
        if is_stroke:
            GeoOut.Add(anyCurve,Path(i))
            ColorOut.Add(STYLE.STROKE_COLOR,Path(i))

        if is_fill:
            GeoOut.Add(_fill_geometry(anyCurve),Path(i))
            ColorOut.Add(STYLE.FILL_COLOR,Path(i))
    if COLOR_OUTPUT:
        _fill_color(anyCurve,STYLE.IS_FILL,STYLE.IS_STROKE)
def Fill(curve,colour=None,real = True,brep = False):
    " rhino version fill "
    if not colour:
        colour = STYLE.FILL_COLOR
    if real:
        _fill_geometry(curve,brep)
    else:
        _fill_color(curve)
def noFill():
    STYLE.FILL_COLOR = Color.FromArgb(0,0,0,0)
def fill(*args):
    if isinstance(args[0], Color):
        STYLE.FILL_COLOR = args[0]
        return
    STYLE.FILL_COLOR = color(*args)
def _fill_geometry(planar_curve,brep = False):
    if brep:
        planar_curve = planar_curve.ToNurbsCurve()
        return Brep.CreatePlanarBreps(planar_curve)
    else:
        pline = convert_polyline(planar_curve)
        if not pline.IsClosed:
            pline.Add(pline.First)
        return Mesh.CreateFromClosedPolyline(pline)
def _fill_color(curve,fill = True,stroke = True):
    pline = convert_polyline(curve)
    DISPLAY.AddPolygon(pline.ToArray(),STYLE.FILL_COLOR,STYLE.STROKE_COLOR,fill,False)
    if stroke:
        DISPLAY.AddCurve(pline.ToNurbsCurve(),STYLE.FILL_COLOR,STYLE.STROKE_WEIGHT)

def Stroke(curve,colour=None,weight=None):
    if not colour:
        colour=STYLE.STROKE_COLOR
    if not weight:
        weight=STYLE.STROKE_WEIGHT
    c = curve.ToNurbsCurve()
    DISPLAY.AddCurve(c,colour,weight)
def stroke(*args):
    if isinstance(args[0], Color):
        STYLE.STROKE_COLOR = args[0]
        return
    STYLE.STROKE_COLOR = color(*args)
def noStroke():
    STYLE.STROKE_COLOR = Color.FromArgb(0,0,0,0)
def strokeWeight(weight):
    STYLE.STROKE_WEIGHT = weight
def pushStyle():
    STYLESTACK.append(STYLE)
def popStyle():
    global STYLE
    if STYLESTACK:
        STYLE = STYLESTACK.pop()

### create shape api ###
class Shape(Curve):
    def __init__():
        self.shape = super(self,Shape).__init__()
        self.plist = []
def createShape():
    return Shape()
def beginShape(kind = None):
    #! add fiiled polygon
    _SHAPESTACK.append( (kind,[]) )
def vertex(x,y,z=0):
    _SHAPESTACK[-1][1].append(Point3d(x,y,z))
def endShape():
    shape = _SHAPESTACK.pop()
    if shape[0]:
        pass
    pline = Polyline(shape[1])
    if AUTO_DISPLAY:
        Display(pline)
    return pline

def world_to_cplane(pt):
    "just pt - CPLANE.Origin"
    return CPLANE.RemapToPlaneSpace(pt)[1]
### matrix manipulation ###
def translate(*args):
    "translate CPLANE with (x,y,[z]) or Vector3d"
    if isinstance(args[0],Vector3d):
        CPLANE.Translate(Vector3d)
    else:
        CPLANE.Translate(CPLANE.PointAt(*args)-CPLANE.Origin)
def rotate(rad,axis=None,center=None):
    "return True if success"
    cplane = CPLANE
    if not axis:
        axis = cplane.ZAxis
    if not center:
        center = cplane.Origin
    return cplane.Rotate(rad,axis,center)

def pushMatrix():
    _CPLANESTACK.append(Plane(CPLANE))
def popMatrix():
    global CPLANE
    if _CPLANESTACK:
        CPLANE = _CPLANESTACK.pop()
def setMatrix(plane):
    "change CPLANE to plane"
    global CPLANE
    CPLANE = plane
### time related ###
def frameRate(fps):
    ms = 1000/fps
    print("Set Timer Interval to : %i ms" % (ms))
    return ms
def millis():
     return int((time.clock() - INFO.TIME)*1000)

# math buildin
def dist(pt1,pt2):
    return pt1.DistanceTo(pt2)
def map(value,a,b,c,d):
    "return remap value from (a,b) --> (c,d)"
    return (value-a)*(d-c)/(b-a) + c
class PVector(object):
    " processing PVector interface as Vector3d "
    def __init__(self,*args):
        relative = Vector3d(CPLANE.Origin)
        if len(args) == 0:
            self.__data = Vector3d.Zero-relative
        if len(args) == 1:
            self.__data = args[0]
        elif len(args) == 2:
            self.__data = Vector3d(args[0],args[1],0)-relative
        elif len(args) == 3:
            self.__data = Vector3d(*args)-relative
    def __repr__(self):
        return 'PVector'+repr(self.__data)
    def __str__(self):
        return str(self.__data)
    def __getattr__(self,attr):
        return getattr(self.__data,attr)
    def __radd__(self,other_v):
        return PVector(self.__data + other_v)
    def __add__(self,other):
        if isinstance(other,Vector3d):
            return PVector(self.__data + other)
        return PVector(self.__data + other.__data)
    def __sub__(self,other):
        if isinstance(other,Vector3d):
            return PVector(self.__data - other)
        return PVector(self.__data - other.__data)
    def __rsub__(self,other_v):
        return PVector(other_v - self.__data)
    def __div__(self,scalar):
        return PVector(self.__data / scalar)
    def __mul__(self,scalar):
        return PVector(self.__data * scalar)
    def __neg__(self):
        return PVector(-self.__data)
    def __cmp__(self, other):
        return self.__data.CompareTo(other.__data)
    def toVector(self):
        return self.__data
    def toPoint(self):
        return Point3d(self.__data)
    def get(self):
        return self.__data
    def set(self,v):
        self.__data = v
    def mag(self):
        return self.Length
    def add(self,v):
        return self + v
    def sub(self,v):
        return self-v
    def mult(self,s):
        return self*s
    def div(self,s):
        return self/s
    def dot(self,v):
        return self*v
    def cross(self,v):
        return Vector3d.CrossProduct(self,v)
    def normalize(self):
        return self.Unitize()
    def rotate(self,radians):
        self.Rotate(radians,CPLANE.ZAxis)
    def limit(self,s):
        self.Unitize()
        self *= s
    @property
    def x(self):
        return self.X
    @property
    def y(self):
        return self.Y
    @property
    def z(self):
        return self.Z
    @classmethod
    def angleBetween(cls,a,b):
        return Vector3d.VectorAngle(a,b,CPLANE)
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
##! TODO:image function
def loadImage(fpath):
    "load image"
    return Rhino.Display.DisplayBitmap.Load(fpath)
def image(img,x,y):
    "position image"
    pass

# basic geometry drawing
def arc(x,y,w,h,start,stop,mode='PIE'):
    " construct a elliptic arc "
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
    Display(res)
def line(x1,y1,x2,y2,z1=0,z2=0):
    " simple line "
    pl = Plane(CPLANE)
    ln = Line(pl.PointAt(x1,y1,z1),pl.PointAt(x2,y2,z2))
    if AUTO_DISPLAY:
        Display(ln)
    return ln
def list_to_point(lst,n=3):
    return [Point3d(*lst[i:i+n]) for i in range(0,len(lst),n)]
def curve(*args):
    "construct 3-degree InterpolatedCurve from (x1,y1,z1,...,xn,yn,zn,)\
    or (PT1,PT2,PT3)"
    ##! not on CPLANE yet
    if not isinstance(args[0],Point3d):
        assert len(args)%3 == 0, "argruments number not match"
        pts = list_to_point(args)
    rpts = [CPLANE.RemapToPlaneSpace(p)[1] for p in pts]

    crv = Curve.CreateInterpolatedCurve(rpts,3)
    if AUTO_DISPLAY:
        Display(crv)
    return crv
def rect(x1,y1,x2,y2):
    rec = Rectangle3d(CPLANE,Point3d(x1,y1,0),Point3d(x2,y2,0))
    if AUTO_DISPLAY:
        Display(rec)
    return rec
def ellipse(x,y,a,b):
    pl = Plane(CPLANE)
    pl.Translate(Vector3d(x,y,0))
    ell = Ellipse(pl,a,b)
    if AUTO_DISPLAY:
        Display(ell)
    return ell
def polygon(x,y,r,n=5):
    " draw polygon like the component "
    c = Circle(CPLANE.PointAt(x,y,0),r)
    pts = [c.PointAt(i*2*PI/n) for i in range(n+1)]
    pline = Polyline(pts)
    if AUTO_DISPLAY:
        Display(pline)
    return pline
def text(content,x,y,z=0,height=None):
    " add text to screen "
    te = TextEntity()
    te.Text = content
    te.Plane = CPLANE
    if height:
        te.TextHeight = height
    te.Translate(Vector3d(CPLANE.PointAt(x,y,z)))
    txtcrvs = Curve.JoinCurves(te.Explode())
    if AUTO_DISPLAY:
        for crv in txtcrvs:
            Display(crv)
    return txtcrvs

### help func?
def constrain_region( pt,geo):
    Max = geo.GetBoundingBox(CPLANE).Max
    Min = geo.GetBoundingBox(CPLANE).Min
    pt.X = Rhino.RhinoMath.Clamp(pt.X,Min.X,Max.X)
    pt.Y = Rhino.RhinoMath.Clamp(pt.Y,Min.Y,Max.Y)
    pt.Z = Rhino.RhinoMath.Clamp(pt.Z,Min.Z,Max.Z)
    return pt


"""def _insureRightOutput(ghenv):
    # slove multiply instance problem
    global GeoOut,ColorOut
    GeoOut = ghenv.LocalScope.GeoOut = DataTree[object](ghenv.Component.Params.Output[1].VolatileData)
    ColorOut = ghenv.LocalScope.ColorOut = DataTree[object](ghenv.Component.Params.Output[2].VolatileData)"""
# buildin func
def show_grid(switch = False):
    " turn off cplane grid "
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.ActiveViewport.ConstructionGridVisible = switch
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.ActiveViewport.ConstructionAxesVisible = switch
def get_class(ghenv):
    param = ghenv.Component.Params.Input[1]
    for data in param.VolatileData.AllData(True):
        cls =  data.Value
        ghenv.Script.SetVariable(cls.__name__, cls)
def get_option(ghenv):
    param = ghenv.Component.Params.Input[2]
    for data in param.VolatileData.AllData(True):
        option = data.Value
        ghenv.Script.SetVariable(cls.__name__, cls)

def glob():
    return globals()

def recive_from_gh(_ghenv):
    ## get ALL var overwrite this
    source = _ghenv.Component.Code.replace('from pgh.core import *','').replace('GO(ghenv)','').replace('\r','')
    exec(source)
    globals().update(locals())

def noLoop():
    INFO.IS_LOOP = False
def setup():
    "run once when RESET == True"
    noLoop()
def draw():
    "continuous run when RESET == False"
    noLoop()
def GO(ghenv):
    if ghenv not in all_processing:
        this_p = Processing(ghenv)
        all_processing[ghenv] = this_p
    else:
        this_p = all_processing[ghenv]
    if ghenv != _ghenv:
        this_p.switch()
    param = ghenv.Component.Params.Input[0]
    RESET = True
    for data in param.VolatileData.AllData(True):
        RESET = data.Value
    if RESET:
        this_p.initialize()# restore the global var to this process
        setup()#run setup
    elif INFO.IS_LOOP:
        INFO.LOOP_COUNT += 1
        update_mouse()
        #print 'before draw',ghenv.LocalScope.GeoOut
        draw()
    #print "final",ghenv.LocalScope.GeoOut
class Processing:
    "store the runing state of every instance"
    count = 0
    def __init__(self,ghenv):
        Processing.count += 1
        print("create new p, %s in total"%(Processing.count))
        self.env = ghenv
        # placeholder for instance
        self.STYLE = Style()
        self.STYLESTACK = []
        self._CPLANESTACK = []
        self.CPLANE = Plane.WorldXY
        self.AUTO_DISPLAY = True
        self.GEOMETRY_OUTPUT = True
        self.COLOR_OUTPUT = False
        self.GeoOut = DataTree[object]()
        self.ColorOut = DataTree[Color]()
        self.INFO = Info()
        self._SHAPESTACK = []
    def initialize(self,name = 'processing',autodisplay = True,geometry_output = True,color_output = False):
        # initilize placeholder
        global INFO,AUTO_DISPLAY,\
               CPLANE,_CPLANESTACK,\
               STYLE,STYLESTACK,\
               GeoOut,ColorOut,\
               GEOMETRY_OUTPUT,COLOR_OUTPUT,\
               _SHAPESTACK
        INFO = Info()
        INFO.TIME = time.clock()
        _CPLANESTACK = []
        CPLANE = Plane.WorldXY
        _SHAPESTACK = []
        STYLESTACK = []
        STYLE = Style()
        AUTO_DISPLAY = autodisplay
        GEOMETRY_OUTPUT = geometry_output
        COLOR_OUTPUT = color_output
        GeoOut = self.env.LocalScope.GeoOut
        ColorOut = self.env.LocalScope.ColorOut
        _clearOutput()
        get_class(self.env)
        recive_from_gh(self.env)
        print("environment was reseted")
    def switch(self):
        # retain this instance's envonriment
        global INFO,AUTO_DISPLAY,\
               CPLANE,_CPLANESTACK,\
               STYLE,STYLESTACK,\
               GeoOut,ColorOut,\
               GEOMETRY_OUTPUT,COLOR_OUTPUT,\
               _SHAPESTACK
        CPLANE = self.CPLANE
        _CPLANESTACK = self._CPLANESTACK
        STYLE = self.STYLE
        STYLESTACK = self.STYLESTACK
        INFO = self.INFO
        #! why theses are diffrent?
        GeoOut = self.env.LocalScope.GeoOut = self.GeoOut
        ColorOut = self.env.LocalScope.ColorOut = self.ColorOut
        GEOMETRY_OUTPUT = self.GEOMETRY_OUTPUT
        COLOR_OUTPUT = self.COLOR_OUTPUT
        AUTO_DISPLAY = self.AUTO_DISPLAY
        _SHAPESTACK = self._SHAPESTACK
        recive_from_gh(self.env)
    def __del__(self):
        Processing.count -= 1
        super(Processing.self).__del__()
