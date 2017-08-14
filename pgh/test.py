class test:
    def __init__(self,t):
        self.x =t
mousePressed = [True]
T = test(50)
def toggle(state):
    global mousePressed
    mousePressed[0] = state
    T.x = state
