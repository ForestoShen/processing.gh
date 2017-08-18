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
_barray = (ctypes.c_byte * 256)()
_ptr = ctypes.pointer(_barray)

def keyPressed(*args):
    if len(args)==0:
        user32.GetKeyboardState(_barray)
        return sum(list(_barray))<0
    elif len(args)==1:
        key = args[0]
        try:
            a = ord(key.upper())
        except :
            a = _keydict[key.upper()]
        return bool(user32.GetKeyState(a) & 0x8000)
def isMousePressed():
    return bool(user32.GetKeyState(Keys.LButton) & 0x8000)
