import time
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
from Rhino.Geometry import *
import Grasshopper.Kernel.Data.GH_Path as Path
import Grasshopper.DataTree as DataTree
import Rhino
import perlin
noise = perlin.SimplexNoise.noise2
import random
import System.Drawing.Color as Color
color = Color.FromArgb
import math
PI = math.pi
import Grasshopper.Kernel as gh
import ghpythonlib.components as gc
from interact import *

## global setting


## display setting
LINE_WEIGHT = 1
DISPLAY_COLOR = Color.FromArgb(0,0,0)
BACKGROUND_COLOR = Color.FromArgb(255,255,255)

## drawing setting
DARW_MODE = ["SCREEN","CPLANE","WORLD"]
DRAW_Count = 0
VIEWPORT = ghdoc.Views.ActiveView.ActiveViewport
_CPLANE = Plane.WorldXY
_CPLANESTACK = []


def setting(draw_func):## trace some hidden variable?
    DRAW_Count += 1
    if mode = CPLANE : _cplane.Z += 1
	time.clock()
    mouse = rs.GetCursorPos()[0] 
    return draw_func

def fill(planar_curve):
    return Mesh.CreateFromClosedPolyline(planar_curve) or\
           Brep.CreatePlanarBreps(planar_curve)

### help func
def pushMatrix():
    _cplaneStack.append(_cplane)
def popMatrix():
    _cplane = _cplaneStack.pop()　if _cplaneStack else Plane.WorldXY
def constrain( pt,geo):
    Max = geo.GetBoundingBox(_CPLANE).Max
    Min = geo.GetBoundingBox(_CPLANE).Min
    pt.X = Rhino.RhinoMath.Clamp(pt.X,Min.X,Max.X)
    pt.Y = Rhino.RhinoMath.Clamp(pt.Y,Min.Y,Max.Y)
    pt.Z = Rhino.RhinoMath.Clamp(pt.Z,Min.Z,Max.Z)
    return pt

def initilize():
	#define class here for better tweaking
	pass

def setup():
	#initilize var here when click reset button (with global key word)
	pass

@setting()
def draw():
	#constantly do some thing when the timer is on
	pass

if reset:
	initilize()
	setup()
else:
    draw()
