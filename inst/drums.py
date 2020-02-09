#!/usr/bin/env python3
# encoding: utf-8
from pyo import *

class Drums:
    def __init__(self, paths, transpo=1, hfdamp=5000, channel=0, mul=1):
        self.paths = paths
        self.transpo = Sig(transpo)
        self.note = Notein(poly=16, scale=0, first=0, last=127, channel=channel)
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=0.001, decay=.1, sustain=.7, release=0.1, mul=1)

        self.t = []
        self.selectors = []
        self.players = []

        for i in range(len(self.paths)):
            self.t.append(SndTable(self.paths[i], initchnls=2))
            self.selectors.append(Select(self.note["pitch"], value=36+i))
            self.players.append(TrigEnv(self.selectors[i], self.t[i], dur=self.t[i].getDur() / self.transpo, mul=self.amp))

        # Stereo mix.
        self.mix = Mix(self.players, voices=2)
        self.damp = ButLP(self.mix, freq=hfdamp)
        self.hp = ButHP(self.damp, 40, mul=mul)

    def out(self):
        self.hp.out()
        return self

    def sig(self):
        return self.hp
