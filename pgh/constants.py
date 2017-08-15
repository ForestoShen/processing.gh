# viewport size
width = 640
height = 800
## global setting
P2D = Rhino.Display.DefinedViewportProjection.Top
P3D = Rhino.Display.DefinedViewportProjection.Perspective
if "DISPLAY" not in sc.sticky:
    sc.sticky["DISPLAY"] = Rhino.Display.CustomDisplay(True)
DISPLAY = sc.sticky["DISPLAY"]
