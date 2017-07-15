import time
import rhinoscriptsyntax as rs
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
import ghpythonlib.components as gc
from interact import keyPressed

def fill(planar_curve):
    return Brep.CreatePlanarBreps(planar_curve) or\
    Mesh.CreateFromClosedPolyline(planar_curve)



def setup():
		#initilize var here when click reset button (with global key word)
		pass
def draw():
		#constantly do some thing when the timer is on
		pass

if reset:
		setup()
else:
    draw()
