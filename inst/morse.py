from pyo import *

s = Server(sr=48000, nchnls=2, buffersize=1024, duplex=False)
s.setInOutDevice(2)
s.setMidiInputDevice(99)
s.boot().start()
s.amp = .2

i=0
morse = [0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1,1]
t = .2

def step():
	global i
	try:
		env.setMul(morse[i]*.4)
		env.play()
		i+=1
	except IndexError:
		s.stop()

met = Metro(time=t).play()
tab = CurveTable([(0,0),(3072,.4),(4096,.25),(6144,.4),(8192,0)], 0, 5)
tab.graph()
env = Osc(table=tab, freq=1/t, mul=0)

tf = TrigFunc(met, step)
a = Sine(440, mul=env).mix(2).out()

s.gui(locals)
