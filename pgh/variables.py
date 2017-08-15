_posInfo = rs.GetCursorPos()
mouseX = _posInfo[0].X
mouseY = _posInfo[0].Y
pmouseX = mouseX
pmouseY = mouseY
mousePressed = False
_pmousePressed = False
mouseMoved = False
mouseDragged = False
mouseClicked = False

IS_FILL = True
FILL_COLOR = Color.FromArgb(255,255,255)
IS_STROKE = True
STROKE_COLOR = Color.FromArgb(0,0,0,0)
STROKE_WEIGHT = 1
STYLESTACK = []

CPLANESTACK = []
CPLANE = Plane.WorldXY
AUTO_DISPLAY = True
GEOMETRY_OUTPUT = True
COLOR_OUTPUT = False
