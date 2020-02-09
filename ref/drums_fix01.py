#!/usr/bin/env python3
# encoding: utf-8
from random import random
from pyo import *

class Drums:
    def __init__(self, paths, transpo=1, hfdamp=5000, lfofreq=0.2, channel=0, mul=1):
        self.paths = paths
        self.t = []
        self.freqs = []
        self.kits = []
        self.transpo = Sig(transpo)
        ### Si tu veux detecter des notes MIDI, tu dois laisser scale=0
        self.note = Notein(poly=10, scale=0, first=0, last=127, channel=channel)
        ### Pour avoir la frequence en Hz, tu passes par MToF
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=0.001, decay=.1, sustain=.7, release=0.1, mul=.5)
        self.ind = LinTable([(0,20), (200,1), (1000,2), (8191,1)])
        self.tr = TrigEnv(self.note['trigon'], table=self.ind, dur=1)

        ### Pour les nouveaux besoin!
        self.selectors = []
        self.players = []

        for i in range(len(self.paths)):
            self.t.append(SndTable(self.paths[i], initchnls=2))
            #self.freqs.append(self.t[i].getRate())
            #self.kits.append(OscTrig(self.t[i], self.tr, self.freqs[i]*transpo, mul=self.amp).mix(1))
            ### Ensuite une combinaison de Select et TrigEnv devrait faire le travail
            self.selectors.append(Select(self.note["pitch"], value=36+i))
            self.players.append(TrigEnv(self.selectors[i], self.t[i], dur=self.t[i].getDur()/transpo, mul=self.amp.mix(1)))

        # Stereo mix.
        ### Et donc...
        self.mix = Mix(self.players, voices=2)
        #self.mix = Mix(self.kits[1], voices=2)

        # High frequencies damping, use argument `hfdamp` to allow MIDI control.
        self.damp = ButLP(self.mix, freq=hfdamp)

        # Moving notches, use argument `lfofreq` to allow MIDI control.
        self.lfo = Sine(lfofreq, phase=[random(), random()]).range(250, 4000)
        self.notch = ButBR(self.damp, self.lfo, mul=mul)

    def out(self):
        self.notch.out()
        return self

    def sig(self):
        return self.notch
