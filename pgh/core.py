import scriptcontext as sc
import Rhino
import Rhino.Geometry as rg
import rhinoscriptsyntax as rs
from Rhino.Geometry import *
import Grasshopper.Kernel.Data.GH_Path as Path
import Grasshopper.DataTree as DataTree
import Grasshopper.Kernel as gh
import ghpythonlib.components as gc
import System.Drawing
import time
import math
from processing import noise
import random
import System.Drawing.Color as Color
noise = noise.SimplexNoise.noise2
color = Color.FromArgb
PI = math.pi
thisDoc = Rhino.RhinoDoc.ActiveDoc
from processing.interact import *
clamp = Rhino.RhinoMath.Clamp
# accessible global var
width = 640
height = 800
_posInfo = rs.GetCursorPos()
mouseX = _posInfo[0].X
mouseY = _posInfo[0].Y
pmouseX = mouseX
pmouseY = mouseY

## global setting
if "DISPLAY" not in sc.sticky:
    sc.sticky["DISPLAY"] = Rhino.Display.CustomDisplay(True)
DISPLAY = sc.sticky["DISPLAY"]

## display setting
TORLERENCE = Rhino.RhinoDoc.ActiveDoc.PageAbsoluteTolerance
DISPLAY_ALL = True
OUTPUT = []
IS_FILL = False
IS_STROKE = True
STROKE_WEIGHT = 1
geometry_pipeline = []
BACKGROUND_COLOR = Color.FromArgb(180,180,180)
FILL_COLOR = Color.FromArgb(0,0,0)
STROKE_COLOR = Color.FromArgb(0,0,0)
## drawing setting
_MODE = "CPLANE"
LOOP_COUNT = 0
VIEWPORT = Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.ActiveViewport
_CPLANE = Plane.WorldXY
_CPLANESTACK = []

# buildin func
def show_grid(switch = False):
    " turn off cplane grid "
    VIEWPORT.ConstructionGridVisible = switch
    VIEWPORT.ConstructionAxesVisible = switch

def update_mouse():
    global mouseX,screenX,mouseY,screenY,pmouseX,pmouseY
    pmouseX = mouseX
    pmouseY = mouseY
    _posInfo = rs.GetCursorPos()
    mouseX = _posInfo[0].X
    screenX = _posInfo[1].X
    mouseY = _posInfo[0].Y
    screenY = _posInfo[1].Y
def get_class(ghenv):
    param = ghenv.Component.Params.Input[1]
    for data in param.VolatileData.AllData(True):
        cls =  data.Value
        globals().update({cls.__name__ : cls})
"""def get_class():
    for cls in CLASS:
        globals().update({cls.__name__:cls})"""

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

def newView(name,screenX = 0,screenY = 0,seperate = True):
    exist = Rhino.RhinoDoc.ActiveDoc.Views.Find(name,True)
    if not exist:
        exist = Rhino.RhinoDoc.ActiveDoc.Views.Add(
        name,
        Rhino.Display.DefinedViewportProjection.Top,
        System.Drawing.Rectangle(screenX,screenY,screenX+width,screenY+height),
        seperate)
        viewRect = Rectangle3d(_CPLANE,width,height)
        exist.ActiveViewport.ZoomBoundingBox(viewRect.BoundingBox)
    return exist
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
def background(*args):
    " clear OUTPUT, if has args, set backgound color(a,r,g,b) "
    global OUTPUT
    if len(args):
        c = Color.FromArgb(*args)
        Rhino.ApplicationSettings.AppearanceSettings.ViewportBackgroundColor = c
    DISPLAY.Clear()
    DISPLAY.Dispose
    OUTPUT = []
def size(w,h):
    " set size of new viewport "
    global width,height
    width = w
    height = h

####! todo:add outputShader(),outputCurve

def Fill(curve,colour=None,real = True,brep = False):
    " rhino version fill "
    if not colour:
        colour = FILL_COLOR
    if real:
        fill_geometry(curve,brep)
    else:
        fill_color(curve)
def noFill():
    global FILL_COLOR
    FILL_COLOR = Color.FromArgb(0,0,0,0)
def fill(*args):
    global FILL_COLOR
    FILL_COLOR = color(*args)
def fill_geometry(planar_curve,brep = False):
    if brep:
        planar_curve = planar_curve.ToNurbsCurve()
        return Brep.CreatePlanarBreps(planar_curve)
    else:
        pline = ToPolyline(planar_curve)
        return Mesh.CreateFromClosedPolyline(pline)
def fill_color(pline,fill = True,stroke = True):
    if isinstance(pline,Polyline):
        pline = pline.ToArray()
    DISPLAY.AddPolygon(pline,FILL_COLOR,STROKE_COLOR,fill,stroke)

def Stroke(curve,colour=None,weight=None):
    global STROKE_WEIGHT,STROKE_COLOR
    if not colour:
        colour=STROKE_COLOR
    if not weight:
        weight=STROKE_WEIGHT
    c = curve.ToNurbsCurve()
    DISPLAY.AddCurve(c,colour,weight)
def stroke(*args):
    global STROKE_COLOR
    STROKE_COLOR = color(*args)
def noStroke():
    global STROKE_COLOR
    STROKE_COLOR = Color.FromArgb(0,0,0,0)
def strokeWeight(weight):
    global STROKE_WEIGHT
    STROKE_WEIGHT = weight

### create shape api ###
def beginShape(kind = None):
    #! add fiiled polygon
    num = len(_SHAPESTACK)
    _SHAPESTACK.append([])
    _CSHAPE = _SHAPESTACK[num]
def vertex(x,y,z):
    _CSHAPE.append(Point3d(x,y,z))
def endShape():
    plist = Polyline(_SHAPESTACK.pop())
    fill_color(plist)

### matrix manipulation ###
def translate(x,y,z=0):
    _CPLANE.Translate(_CPLANE.PointAt(x,y,z))
def pushMatrix():
    _CPLANESTACK.append(_CPLANE)
def popMatrix():
    _CPLANE = _CPLANESTACK.pop() if _CPLANESTACK else _CPLANE

### time related ###
def frameRate(fps):
    ms = 1000/fps
    print("Set Timer Interval to : %i ms" % (ms))
    return ms
def millis():
     return int((time.clock() - _time)*1000)

# other useful buildin
def dist(pt1,pt2):
    return pt1.DistanceTo(pt2)
def line(x1,y1,x2,y2):
    global OUTPUT
    pl = Plane(_CPLANE)
    ln = Line(pl.PointAt(x1,y1),pl.PointAt(x2,y2))
    OUTPUT.append(ln)
    return ln
def rect(x1,y1,x2,y2):
    global OUTPUT
    rec = Rectangle3d(_CPLANE,Point3d(x1,y1,0),Point3d(x2,y2,0))
    OUTPUT.append(rec)
    return rec
def ellipse(x,y,a,b):
    global OUTPUT
    pl = Plane(_CPLANE)
    pl.Translate(Vector3d(x,y,0))
    ell = Ellipse(pl,a,b)
    OUTPUT.append(ell)
    return ell
def text(content):
    te = TextEntity()
    TextEntity.Text = content
    TextEntity.Plane = _CPLANE

### help func?
def constrain_region( pt,geo):
    Max = geo.GetBoundingBox(_CPLANE).Max
    Min = geo.GetBoundingBox(_CPLANE).Min
    pt.X = Rhino.RhinoMath.Clamp(pt.X,Min.X,Max.X)
    pt.Y = Rhino.RhinoMath.Clamp(pt.Y,Min.Y,Max.Y)
    pt.Z = Rhino.RhinoMath.Clamp(pt.Z,Min.Z,Max.Z)
    return pt

### decorator for simplicity
def loop(fn):
    global LOOP_COUNT
    LOOP_COUNT += 1
    update_mouse()
    if _MODE == 'CPLANE' : _CPLANE.OriginZ += TORLERENCE
    def wrapped():
        fn()
    return wrapped

def setting(this,name = 'processing'):
    global LOOP_COUNT,_time
    _time = time.clock()
    OUTPUT = []
    LOOP_COUNT = 0
    get_class(this)
    newView(name)

"""
def setup():
    pass
def draw():
    pass
def GO(ghenv):
    param = ghenv.Component.Params.Input[0]
    for data in param.VolatileData.AllData(True):
        RESET = data
    if RESET:
        setting(this = ghenv)
        setup()
    else:
        draw()
"""
