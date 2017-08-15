import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System.Drawing.Color as Color
# viewport size
width = 640
height = 800
## global setting
P2D = Rhino.Display.DefinedViewportProjection.Top
P3D = Rhino.Display.DefinedViewportProjection.Perspective
if "DISPLAY" not in sc.sticky:
    sc.sticky["DISPLAY"] = Rhino.Display.CustomDisplay(True)
DISPLAY = sc.sticky["DISPLAY"]

## display setting
IS_FILL = True
FILL_COLOR = Color.FromArgb(255,255,255)
IS_STROKE = True
STROKE_COLOR = Color.FromArgb(0,0,0,0)
STROKE_WEIGHT = 1
STYLESTACK = []


_CPLANESTACK = []
CPLANE = Rhino.Geometry.Plane.WorldXY
AUTO_DISPLAY = True
GEOMETRY_OUTPUT = True
COLOR_OUTPUT = False

## general setting
TORLERENCE = Rhino.RhinoDoc.ActiveDoc.PageAbsoluteTolerance
VIEWPORT = Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.ActiveViewport
thisDoc = Rhino.RhinoDoc.ActiveDoc
LOOP_COUNT = 0
isLoop = True

def send_all_name_to_gh(ghenv):
    for k,v in globals().items():
        ghenv.Script.SetVariable(k,v)
def recive_from_gh(ghenv):
    for name in ghenv.Script.GetVariableNames():
        globals().update({name:ghenv.Script.GetVariable(name)})
