import glob
import System.Drawing.Color as Color
import System.Drawing.Rectangle
from Rhino.Geometry import Rectangle3d
import Rhino
import Grasshopper.Kernel.Data.GH_Path as Path
## basic processing function ##
def show_grid(switch = False):
    " turn off cplane grid "
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.ActiveViewport.ConstructionGridVisible = switch
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.ActiveViewport.ConstructionAxesVisible = switch
def background(*args):
    " clear OUTPUT, if has args, set backgound color(a,r,g,b) "
    if len(args):
        c = color(*args)
        Rhino.ApplicationSettings.AppearanceSettings.ViewportBackgroundColor = c
    _clearOutput()
def size(w,h,mode=P2D,name='processing'):
    " set size of new viewport "
    glob.width =  w
    glob.height=h
    glob.VIEWPORT = NewView(name,mode).ActiveViewport)
def NewView(name,Projection,screenX = 0,screenY = 0,seperate = True):
    exist = Rhino.RhinoDoc.ActiveDoc.Views.Find(name,True)
    if not exist:
        exist = Rhino.RhinoDoc.ActiveDoc.Views.Add(
        name,
        Projection,
        System.Drawing.Rectangle(screenX,screenY,screenX+width,screenY+height),
        seperate)
        viewRect = Rectangle3d(glob.CPLANE,width,height)
        exist.ActiveViewport.ZoomBoundingBox(viewRect.BoundingBox)
    return exist
def toggleColor(state = False):
    "cancel color out mode"
    glob.COLOR_OUTPUT = state
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
    glob.DISPLAY.Clear()
    glob.DISPLAY.Dispose
    glob.GeoOut.Clear()
    glob.ColorOut.Clear()

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
def Display(anyCurve):
    " overall display "
    if glob.GEOMETRY_OUTPUT:
        # add diffrent fill and outline to different GeoOut bracnch
        i = glob.GeoOut.BranchCount
        glob.GeoOut.Add(anyCurve,Path(i))
        glob.ColorOut.Add(glob.STROKE_COLOR,Path(i))
        if IS_FILL:
            glob.GeoOut.Add(_fill_geometry(anyCurve),Path(i))
            glob.ColorOut.Add(glob.FILL_COLOR,Path(i))
    if glob.COLOR_OUTPUT:
        _fill_color(anyCurve,glob.IS_FILL,glob.IS_STROKE)



def Fill(curve,colour=None,real = True,brep = False):
    " rhino version fill "
    if not colour:
        colour = glob.FILL_COLOR
    if real:
        _fill_geometry(curve,brep)
    else:
        _fill_color(curve)
def noFill():
    glob.FILL_COLOR = Color.FromArgb(0,0,0,0)
def fill(*args):
    if isinstance(args[0], Color):
        glob.FILL_COLOR=args[0]
        return
    glob.FILL_COLOR=color(*args)
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
    glob.DISPLAY.AddPolygon(pline.ToArray(),FILL_COLOR,STROKE_COLOR,fill,False)
    if stroke:
        glob.DISPLAY.AddCurve(pline.ToNurbsCurve(),FILL_COLOR,STROKE_WEIGHT)

def Stroke(curve,colour=None,weight=None):
    if not colour:
        colour=STROKE_COLOR
    if not weight:
        weight=STROKE_WEIGHT
    c = curve.ToNurbsCurve()
    glob.DISPLAY.AddCurve(c,colour,weight)
def stroke(*args):
    glob.STROKE_COLOR=color(*args)
def noStroke():
    glob.STROKE_COLOR=Color.FromArgb(0,0,0,0)
def strokeWeight(weight):
    glob.STROKE_WEIGHT=weight
def pushStyle():
    glob.STYLESTACK.append(
                      (glob.FILL_COLOR,
                       glob.STROKE_COLOR,
                       glob.STROKE_WEIGHT,
                       glob.IS_FILL,
                       glob.IS_STROKE))
def popStyle():
    STYLESTACK = glob.STYLESTACK
    if STYLESTACK:
        (glob.FILL_COLOR,
         glob.STROKE_COLOR,
         glob.STROKE_WEIGHT,
         glob.IS_FILL,
         glob.IS_STROKE) = STYLESTACK.pop()
