'''
a example to create a particle system. though it seems lame,
we can combined it with all the rhino geometry function to achieve,
interesting result.
'''
#!! to make this more simple

import rhinoscriptsyntax as rs
from Rhino.Geometry import *
import Grasshopper.Kernel.Data.GH_Path as Path
import Grasshopper.DataTree as DataTree
import Rhino.RhinoMath.Clamp as clamp
import random
import Grasshopper.Kernel as gh
mousePos = rs.GetCursorPos
from interact import *

def constrain(pt,geo):
    Max = geo.GetBoundingBox(WORK_PLANE).Max
    Min = geo.GetBoundingBox(WORK_PLANE).Min
    pt.X = clamp(pt.X,Min.X,Max.X)
    pt.Y = clamp(pt.Y,Min.Y,Max.Y)
    pt.Z = clamp(pt.Z,Min.Z,Max.Z)
    return pt

def draw():
    mouse = mousePos()[0] # the mousePos return a tuple whose first element is a world coordination at active view 
    mouse.Z = 0
    # assign the inital velocity for every particle in list
    vlist = [Vector3d(0,0,0) for i in range(len(_clist))]
    for i,c in enumerate(_clist):
        vel = vlist[i]
        mass = c.Radius
        vec2p = c.Center - mouse
        vec2p.Unitize()
        d = rs.Distance(c.Center,mouse)
        # compute the movement
        G = 10
        acc =  G * vec2p * mass  / d
        vel += acc
        c.Center += vel
        acc = Vector3d(0,0,0)
        if region:
            c.Center = constrain(c.Center,region)
        for cir in _clist:
            if cir is not c and rs.Distance(c.Center,cir.Center) < 10:
                line.append(Line(c.Center,cir.Center))
    return _clist

#run the code 运行代码

if reset:
    # here we make a copy of these input circle to leave the orignal intact
    _clist = clist
    line = []
else:
    line = []
    a = draw()
    p = [c.Center for c in a]
    n = line
