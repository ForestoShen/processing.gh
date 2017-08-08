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

def _clear():
    for uniquevar in [var for var in globals().copy() if var[0] != "_"]:
        del globals()[uniquevar]

def _newView(name,screenX = 0,screenY = 0):
    ls = Rhino.RhinoDoc.ActiveDoc.Views.GetViewList(True,False)
    exist = Rhino.RhinoDoc.ActiveDoc.Views.Find(name,True)
    if not exist:
        exist = Rhino.RhinoDoc.ActiveDoc.Views.Add(
        name,
        Rhino.Display.DefinedViewportProjection.Top,
        System.Drawing.Rectangle(screenX,screenY,screenX+width,screenY+height),
        True)
    return exist
def _convert_polyline(curve):
    return curve.ToPolyline(-1,-1,0.1,0,0, 0.1,0.1,0,True)

def background(color):
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
    ln = Line(Point3d(x1,y1,0),Point3d(x2,y2,0))
    OUTPUT.append(ln)
    return ln
def rect(x1,y1,x2,y2):
    rec = Rectangle3d(_CPLANE,Point3d(x1,y1,0),Point3d(x2,y2,0))
    OUTPUT.append(rec)
    return rec
def ellipse(x,y,a,b):
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

