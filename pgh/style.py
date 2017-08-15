#### add display
def _clearOutput():
    DISPLAY.Clear()
    DISPLAY.Dispose
    GeoOut.Clear()
    ColorOut.Clear()
def Display(anyCurve):
    " overall display "
    if GEOMETRY_OUTPUT:
        # add diffrent fill and outline to different GeoOut bracnch
        i = GeoOut.BranchCount
        GeoOut.Add(anyCurve,Path(i))
        ColorOut.Add(style.STROKE_COLOR,Path(i))
        if style.IS_FILL:
            GeoOut.Add(_fill_geometry(anyCurve),Path(i))
            ColorOut.Add(style.FILL_COLOR,Path(i))
    if COLOR_OUTPUT:
        _fill_color(anyCurve,style.IS_FILL,style.IS_STROKE)
def Fill(curve,colour=None,real = True,brep = False):
    " rhino version fill "
    if not colour:
        colour = style.FILL_COLOR
    if real:
        _fill_geometry(curve,brep)
    else:
        _fill_color(curve)
def noFill():
    style.FILL_COLOR = Color.FromArgb(0,0,0,0)
def fill(*args):
    if isinstance(args[0], Color):
        style.FILL_COLOR = args[0]
        return
    style.FILL_COLOR = color(*args)
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
    DISPLAY.AddPolygon(pline.ToArray(),style.FILL_COLOR,style.STROKE_COLOR,fill,False)
    if stroke:
        DISPLAY.AddCurve(pline.ToNurbsCurve(),style.FILL_COLOR,style.STROKE_WEIGHT)

def Stroke(curve,colour=None,weight=None):
    if not colour:
        colour=style.STROKE_COLOR
    if not weight:
        weight=style.STROKE_WEIGHT
    c = curve.ToNurbsCurve()
    DISPLAY.AddCurve(c,colour,weight)
def stroke(*args):
    style.STROKE_COLOR = color(*args)
def noStroke():
    style.STROKE_COLOR = Color.FromArgb(0,0,0,0)
def strokeWeight(weight):
    style.STROKE_WEIGHT = weight
def pushStyle():
    STYLESTACK.append(style)
def popStyle():
    global style
    if STYLESTACK:
        style = STYLESTACK.pop()
