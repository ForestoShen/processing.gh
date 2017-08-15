import ctypes
import System.Windows.Forms.Keys as Keys
user32 = ctypes.WinDLL('user32')

_keydict = {"ESC":Keys.Escape,
           "LSHIFT":Keys.LShiftKey,
           "RSHIFT":Keys.RShiftKey,
           "SHIFT":Keys.ShiftKey,
           "ENTER":Keys.Enter,
           "SPACE":Keys.Space,
           "CONTROL":Keys.ControlKey,
           "CTRL":Keys.ControlKey,
           "ALT":Keys.Alt,
           "DOWN":Keys.Down,
           "UP":Keys.Up,
           "LEFT":Keys.Left,
           "RIGHT":Keys.Right,
           "RETURN":Keys.Enter,
           "DELETE":Keys.Delete,
           "CAPS":Keys.Capital,
           "BACKSPACE":Keys.Back,
}
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
def keyPressed(key):
    try:
        a = ord(key.upper())
    except :
        a = _keydict[key.upper()]
    return bool(user32.GetKeyState(a) & 0x8000)

def isMousePressed():
    return bool(user32.GetKeyState(Keys.LButton) & 0x8000)
# mouse variable

def update_mouse():
    global mouseX,screenX,mouseY,screenY,pmouseX,pmouseY,\
           _pmousePressed,mousePressed,mouseMoved,mouseDragged,mouseClicked

    pmouseX = mouseX
    pmouseY = mouseY
    _pmousePressed = mousePressed
    _posInfo = rs.GetCursorPos()
    mouseX = _posInfo[0].X
    screenX = _posInfo[1].X
    mouseY = _posInfo[0].Y
    screenY = _posInfo[1].Y
    client = glob.VIEWPORT.ClientToWorld(_posInfo[3])
    tup = Intersect.Intersection.LinePlane(client,glob.CPLANE)
    if tup[0]:
        ptOnPlane = client.PointAt(tup[1])
        mouseX = ptOnPlane.X
        mouseY = ptOnPlane.Y
    mousePressed = isMousePressed()
    mouseMoved = pmouseX != mouseX \
                 or pmouseY != mouseY
    mouseDragged = mouseMoved and mousePressed
    mouseClicked = _pmousePressed and not mousePressed
