from pyo import *

s = Server(sr=48000, nchnls=2, buffersize=1024, duplex=False)
s.setInOutDevice(3)
s.setMidiInputDevice(99)
s.boot().start()
s.amp = 1

l1 = [300, 350, 400, 450, 500, 550]
l2 = [300, 350, 450, 500, 550]
t = CosTable([(0,0), (50,1), (250,.3), (8191,0)])
met = Metro(time=.125, poly=2).play()
amp = TrigEnv(met, table=t, dur=.25, mul=.3)
it = Iter(met, choice=l1)
si = Sine(freq=it, mul=amp).out()

s.gui(locals)
