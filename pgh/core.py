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
from matrix import *
from primitive import *
from pvector import *
from rand import *
from style import *



# other useful buildin
def dist(pt1,pt2):
    return pt1.DistanceTo(pt2)
def map(value,a,b,c,d):
    "return remap value from (a,b) --> (c,d)"
    return (value-a)*(d-c)/(b-a) + c
def constrain_region( pt,geo):
    Max = geo.GetBoundingBox(glob.CPLANE).Max
    Min = geo.GetBoundingBox(glob.CPLANE).Min
    pt.X = Rhino.RhinoMath.Clamp(pt.X,Min.X,Max.X)
    pt.Y = Rhino.RhinoMath.Clamp(pt.Y,Min.Y,Max.Y)
    pt.Z = Rhino.RhinoMath.Clamp(pt.Z,Min.Z,Max.Z)
    return pt

def get_class():
    param = _ghenv.Component.Params.Input[1]
    for data in param.VolatileData.AllData(True):
        cls =  data.Value
        _ghenv.Script.SetVariable(cls.__name__, cls)
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


### time related ###
def frameRate(fps):
    ms = 1000/fps - 10
    print("Set Timer Interval to : %i ms" % (ms))
    return ms
def millis():
     return int((time.clock() - _time)*1000)


def _insureRightOutput():
    # slove multiply instance problem
    assign_to_gh('GeoOut',DataTree[object](_ghenv.Component.Params.Output[1].VolatileData))
    assign_to_gh("ColorOut",DataTree[object](_ghenv.Component.Params.Output[2].VolatileData))
def assign_to_gh(k,v):
    _ghenv.Script.SetVariable(k,v)
def send_all_name_to_gh():
    for k,v in globals().items():
        _ghenv.Script.SetVariable(k,v)
def recive_from_gh(ghenv):
    ## get ALL var overwrite this
    global_dict = globals()
    for name in ghenv.Script.GetVariableNames():
        global_dict.update({name:ghenv.Script.GetVariable(name)})
def setting(name = 'processing',autodisplay = True):
    global VIEWPORT
    send_all_name_to_gh()
    glob._time = time.clock()
    glob.isLoop = True
    VIEWPORT = Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.ActiveViewport
    glob.LOOP_COUNT = 0
    glob._CPLANESTACK = []
    glob.AUTO_DISPLAY = autodisplay
    _insureRightOutput()
    _clearOutput()
    get_class()

def noLoop():
    glob.isLoop = False
def GO(ghenv):
    global _ghenv
    _ghenv = ghenv
    param = _ghenv.Component.Params.Input[0]
    for data in param.VolatileData.AllData(True):
        RESET = data
    if RESET.Value == True:
        recive_from_gh()
        setting()
        setup()
    elif isLoop:
        glob.LOOP_COUNT += 1
        update_mouse()
        draw()
