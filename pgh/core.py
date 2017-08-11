import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import Rhino.Geometry as rg
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
from processing.interact import *

# accessible global var
width = 100
height = 100
_posInfo = rs.GetCursorPos()
mouseX = _posInfo[0].X
mouseY = _posInfo[0].Y
pmouseX = mouseX
pmouseY = mouseY

## global setting
if "display" not in sc.sticky:
    sc.sticky["display"] = Rhino.Display.CustomDisplay(True)
display = sc.sticky["display"]

## display setting
DISPLAY_ALL = True
OUTPUT = []
IS_FILL = False
IS_STROKE = True
LINE_WEIGHT = 1
geometry_pipeline = []
BACKGROUND_COLOR = Color.FromArgb(255,255,255)
FILL_COLOR = Color.FromArgb(0,0,0)
STROKE_COLOR = Color.FromArgb(0,0,0)
## drawing setting
DARW_MODE = ["SCREEN","CPLANE","WORLD"]
DRAW_Count = 0
VIEWPORT = Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.ActiveViewport
_CPLANE = Plane.WorldXY
_CPLANESTACK = []


# buildin func

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
    after = time.clock(
    return after - before
        
def newView(name,screenX = 0,screenY = 0):
    exist = Rhino.RhinoDoc.ActiveDoc.Views.Find(name,True)
    if not exist:
        exist = Rhino.RhinoDoc.ActiveDoc.Views.Add(
        name,
        Rhino.Display.DefinedViewportProjection.Top,
        System.Drawing.Rectangle(screenX,screenY,screenX+width,screenY+height),
        True)
    return exist

def convert_curve():
    pass
def convert_polyline(curve,maxAngleRadians = 0.1, tolerance = 0.1):
    return curve.ToPolyline(0,0,maxAngleRadians,0,0, tolerance,0.01,0,True)

def background(*args):
    global OUTPUT
    """ ,clear output, if has args, set color(a,r,g,b) """
    if len(args):
        c = Color.FromArgb(*args)
        Rhino.ApplicationSettings.AppearanceSettings.ViewportBackgroundColor = c
    display.Clear()
    display.Dispose
    OUTPUT = []
def size(w,h):
    global width,height
    width = w
    height = h
def noFill():
    FILL_COLOR = Color.FromArgb(0,0,0,0)
def fill(a,r,g,b):
    FILL_COLOR = color(a,r,g,b)
def fill_mesh(planar_curve):
    TryGetPolyline()
    try:
        return Mesh.CreateFromClosedPolyline(planar_curve)
    except:
        planar_curve = planar_curve.ToNurbsCurve()
        return Brep.CreatePlanarBreps(planar_curve)
def fill_color():
    rg.PointCloud()
def stroke(color = FILL_COLOR,wight = LINE_WEIGHT):
    STROKE_COLOR = color
def noStroke():
    STROKE_COLOR = Color.FromArgb(0,0,0,0)
def dist(pt1,pt2):
    return pt1.DistanceTo(pt2)

# helper function for consistent api
def line(x1,y1,x2,y2):
    global OUTPUT
    ln = Line(Point3d(x1,y1,0),Point3d(x2,y2,0))
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
def text():
    #! todo
    rs.AddText()
def translate(x,y,z=0):
    _CPLANE.Translate(Vector3d(x,y,z))
def strokeWeight(weight):
    LINE_WEIGHT = weight
def pushMatrix():
    _CPLANESTACK.append(_CPLANE)
def popMatrix():
    _CPLANE = _CPLANESTACK.pop() if _CPLANESTACK else Plane.WorldXY
def shape(polygon):
    #! add fiiled polygon
    display.AddPolygon(polygon.points,FILL_COLOR,STROKE_COLOR,True,True)
### help func
def constrain( pt,geo):
    Max = geo.GetBoundingBox(_CPLANE).Max
    Min = geo.GetBoundingBox(_CPLANE).Min
    pt.X = Rhino.RhinoMath.Clamp(pt.X,Min.X,Max.X)
    pt.Y = Rhino.RhinoMath.Clamp(pt.Y,Min.Y,Max.Y)
    pt.Z = Rhino.RhinoMath.Clamp(pt.Z,Min.Z,Max.Z)
    return pt

### main frame
def setting(draw_func,mode):## trace some hidden variable?
    global DRAW_Count
    DRAW_Count += 1
    if mode == CPLANE : _CPLANE.Z += 1
    time.clock()
    mouse = rs.GetCursorPos()[0]
    display.Clear()
    display.Dispose
    return draw_func

