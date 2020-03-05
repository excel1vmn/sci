#!/usr/bin/env python3
# encoding: utf-8
from pyo import *

s = Server(sr=48000, nchnls=2, buffersize=1024, duplex=False, audio='pa')
s.setInOutDevice(6)
s.setMidiInputDevice(99)
s.setMidiOutputDevice(99)

s.boot().start()
s.amp = .2

class ReSampler:
    def __init__(self, noteinput, input, transpo=1, cs1=1, cs2=1, cs3=1, channel=0, mul=1):
        self.transpo = transpo
        self.cs1 = cs1
        self.cs2 = cs2
        self.cs3 = cs3

        self.note = noteinput
        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.2)
        self.valVel = SigTo(self.note['velocity'], .01)

        self.tabLenght = sampsToSec(49152)
        self.input = input
        self.nt = NewTable(length=self.tabLenght, chnls=2, feedback=0)
        self.tr = TableRec(self.input, table=self.nt, fadetime=.01)

        self.ind = LinTable([(0,0), (8191,0)], size=8192)
        self.ind.view()
        self.envGen = TrigFunc(self.note['trigon'], self.create_points)
        self.c = OscTrig(self.nt, self.note['trigon'], self.nt.getRate() * self.tra, mul=self.amp).mix(2)

        self.fs = FastSine(freq=(self.cs3 * 50) + .1, quality=0, mul=self.valVel*8, add=.5)
        self.refSine = FastSine(freq=100, mul=.12)
        self.trMod = TrigEnv(self.note['trigon'], table=self.ind, dur=2)

        self.fm = FM(carrier=self.pit, ratio=self.c, index=self.trMod, mul=self.amp).mix(2)
        self.bal = Balance(self.fm, self.refSine, freq=100).mix(2)
        self.p = Pan(self.bal, outs=2, pan=self.fs, spread=self.valVel, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

    def rec(self):
    	self.tr.play()

    def create_points(self):
        self.randPoints = [random.uniform(-10,10),random.uniform(-10,10),random.uniform(-10,10),random.uniform(-10,10)]
        self.randPositions = [random.randint(10, 1024),random.randint(1025, 2048),random.randint(2049, 4096),random.randint(4097, 8000)]
        # print(self.randPoints)
        self.lst = [(0, 0)]
        self.lst.append((self.randPositions[0], self.randPoints[0]))
        self.lst.append((self.randPositions[1], self.randPoints[1]))
        self.lst.append((self.randPositions[2], self.randPoints[2]))
        self.lst.append((self.randPositions[3], self.randPoints[3]))
        self.lst.append((8191, 0))

        self.ind.replace(self.lst)

n1 = Notein(poly=10, scale=0, first=0, last=127, channel=1)
transpo = Bendin(brange=2, scale=1)
sine = FM()

r1 = ReSampler(n1, sine, transpo, channel=1, mul=1).out()


s.gui(locals())