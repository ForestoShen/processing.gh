import perlin
from random import seed as randomSeed
from random import gauss as randomGaussian
from random import shuffle, choice
from random import uniform
from interact import *
Simplex = perlin.SimplexNoise()
def random(a = 1,b = 0):
    "random(a,b)->[a,b], random(a)->[0,a], random()->[0,1]"
    return uniform(a,b)
def noise(*args):
    "Simplex noise 1,2,3d"
    if len(args) == 1:
        return Simplex.noise2(args[0],0)
    elif len(args) == 2:
        return Simplex.noise2(*args)
    else:
        return Simplex.noise3(*args)
def noiseDetial():
    raise NotImplemented
