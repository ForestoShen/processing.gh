import glob
### matrix manipulation ###
def translate(*args):
    "translate CPLANE with (x,y,[z]) or Vector3d"
    cplane = glob.CPLANE
    if isinstance(args[0],Vector3d):
        cplane.Translate(Vector3d)
    else:
        print 'relative to plane',Point3d(*args)
        print 'True pt',cplane.PointAt(*args)
        cplane.Translate(Vector3d(cplane.PointAt(*args)-cplane.Origin))
def rotate(rad,axis=None,center=None):
    "return True if success"
    cplane = glob.CPLANE
    if not axis:
        axis = cplane.ZAxis
    if not center:
        center = cplane.Origin
    return cplane.Rotate(rad,axis,center)

def pushMatrix():
    glob._CPLANESTACK.append(Plane(glob.CPLANE))
def popMatrix():
    _CPLANESTACK = glob._CPLANESTACK
    if _CPLANESTACK:
        glob.CPLANE=_CPLANESTACK.pop()
def setMatrix(plane):
    "change CPLANE to plane"
    glob.CPLANE=plane)
