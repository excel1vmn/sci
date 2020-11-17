#!/usr/bin/env python3
# encoding: utf-8
from pyo import *

class Drums:
    def __init__(self, paths, transpo=1, hfdamp=7000, lfofreq=0.2, audioIN=0, mul=1):
        self.paths = paths
        self.transpo = Sig(transpo)
        # self.tra = MToT(self.note['pitch']) * self.transpo
        # self.pit = MToF(self.note['pitch']) * self.transpo
        # self.amp = MidiAdsr(self.note, attack=.01, decay=.1, sustain=.7, release=.1)
        self.beat = Beat(.125, 16, w1=100, w2=25, w3=15, poly=10).play()
        self.env = CosTable([(0,0), (100,1), (500,.3), (8191,0)])
        self.amp = TrigEnv(self.beat, table=self.env)
        self.trmid = TrigXnoiseMidi(self.beat, dist=0, mrange=(40,41))

        self.tables = []
        self.selectors = []
        self.players = []

        for i in range(6):
            self.tables.append(SndTable(self.paths[i], initchnls=2))
            self.selectors.append(Select(self.trmid, value=36+i))
            self.players.append(TrigEnv(self.selectors[i], self.tables[i], dur=self.tables[i].getDur()/self.transpo, mul=self.amp.mix(1)))

        self.mix = Mix(self.players, voices=2)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.hp = ButHP(self.damp, 50).mix(2)
        self.comp = Compress(self.hp, thresh=-12, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp, outs=2, pan=[.4,.6], spread=.2, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

if __name__ == "__main__":
    s = Server()
    s.setOutputDevice(6)
    s.setMidiInputDevice(99)
    s.boot().start()

    src = []
    for i in range(6):
        src.append(SNDS_PATH+"/transparent.aif")
    drums = Drums(src)
    p = Pan(drums.sig()).out()
    s.gui(locals())