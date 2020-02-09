#!/usr/bin/env python3
# encoding: utf-8
from random import random
from pyo import *

class Synth:
    def __init__(self, transpo=1, hfdamp=5000, lfofreq=0.2, channel=0, mul=1):
        self.transpo = Sig(transpo)
        self.note = Notein(poly=10, scale=1, first=0, last=127, channel=channel)

        self.pit = self.note['pitch'] * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=0.001,
                            decay=.1, sustain=.7, release=0.1, mul=.1)

        self.osc1 = LFO(self.pit, sharp=0.5, type=2, mul=self.amp).mix(1)
        self.osc2 = LFO(self.pit*0.997, sharp=0.5, type=2, mul=self.amp).mix(1)
        self.ind = LinTable([(0,20), (200,10), (1000,2), (8191,1)])
        self.tr = TrigEnv(self.note['trigon'], table=self.ind, dur=4)
        self.f1 = CrossFM(carrier=self.pit, ratio=[1.02,0.98], ind1=self.osc1, ind2=self.osc1, mul=self.amp).mix(1)
        self.f2 = CrossFM(carrier=self.pit, ratio=[1.01,0.99], ind1=self.osc2, ind2=self.osc2, mul=self.amp).mix(1)

        self.mix = Mix([self.f1, self.f2], voices=2)

        self.damp = ButLP(self.mix, freq=hfdamp)

        self.lfo = Sine(lfofreq, phase=[random(), random()]).range(250, 4000)
        self.notch = ButBR(self.damp, self.lfo, mul=mul)

    def out(self):
        self.notch.out()
        return self

    def sig(self):
        return self.notch

class Simpler:
    def __init__(self, path, transpo=1, hfdamp=5000, lfofreq=0.2, channel=0, mul=1):
        self.path = path
        self.t = SndTable(self.path, initchnls=2)
        self.freq = self.t.getRate()
        self.transpo = Sig(transpo)

        self.note = Notein(poly=10, scale=1, first=0, last=127, channel=channel)

        self.pit = self.note['pitch'] * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=0.001,
                            decay=.1, sustain=.7, release=0.1, mul=.1)

        # self.tab = HannTable()
        self.tab = LinTable([(0,20), (200,1), (1000,2), (8191,1)])
        self.tr = TrigEnv(self.note['trigon'], table=self.tab, dur=1)

        self.osc1 = OscTrig(self.t, self.tr, self.pit * self.freq * transpo, mul=self.amp).mix(1)
        self.osc2 = OscTrig(self.t, self.tr, self.pit * self.freq * transpo, mul=self.amp).mix(1)

        self.f1 = CrossFM(carrier=self.pit, ratio=self.freq, ind1=self.osc1, ind2=self.osc1, mul=self.amp).mix(1)
        self.f2 = CrossFM(carrier=self.pit, ratio=self.freq, ind1=self.osc2, ind2=self.osc2, mul=self.amp).mix(1)

        # Stereo mix.
        self.mix = Mix([self.osc1, self.osc2], voices=2)

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
