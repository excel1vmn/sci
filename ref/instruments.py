#!/usr/bin/env python3
# encoding: utf-8
from random import random
from pyo import *

class Simpler:
    def __init__(self, path, transpo=1, hfdamp=3000, lfofreq=0.2, channel=0, mul=1, autoswitch=False):
        self.path = path
        self.t = SndTable(self.path, initchnls=2)
        self.freq = self.t.getRate()
        self.dur = self.t.getDur()

        self.transpo = Sig(transpo)
        self.note = Notein(poly=10, scale=1, first=0, last=127, channel=channel)
        self.pit = self.note['pitch'] * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=0.001, decay=.1, sustain=.7, release=0.1, mul=.5)

        self.tab = HannTable()
        # self.tab = LinTable([(0,20), (200,1), (1000,2), (8191,1)])
        self.tr = TrigEnv(self.note['trigon'], table=self.tab, dur=self.dur)

        ### self.tr ne devrait pas etre self.note['trigon'] ?
        self.trand = TrigRand(self.tr, 0.1 * self.note['velocity'], 1 * self.note['velocity'])

        if autoswitch == True:
            self.count = Counter(self.tr, 0, 16)
            self.se = Select(self.count, 15)
            self.tf = TrigFunc(self.se, self.changeSample, 'snds/voxyline.aif')
            print('works')

        ### Si la lecture ne doit pas boucler, j'irais avec TrigEnv
        self.osc11 = TrigEnv(self.note['trigon'], table=self.t, dur=self.t.getDur() / self.transpo)
        ### Si la lecture doit boucler et seulement etre relancee au debut sur une nouvelle note, tu y es presque!
        self.osc12 = OscTrig(self.t, self.note['trigon'], self.freq * transpo, mul=mul)

        self.osc1 = OscTrig(self.t, self.tr, self.freq * transpo, mul=mul)
        self.osc2 = OscTrig(self.t, self.tr, self.freq * transpo, mul=mul)

        self.f1 = CrossFM(carrier=(self.pit * 1.01) * self.freq, ratio=[1.01,0.99], ind1=self.osc1 * self.pit, ind2=self.osc1 * self.freq, mul=self.amp).mix(1)
        self.f2 = CrossFM(carrier=(self.pit * 0.99) * self.freq, ratio=[1.02,0.98], ind1=self.osc2 * self.pit, ind2=self.osc2 * self.freq, mul=self.amp).mix(1)

        self.mix = Mix([self.f1, self.f2], voices=2)
        self.damp = ButLP(self.mix, freq=hfdamp)

        self.lfo = Sine(lfofreq, phase=[random(), random()]).range(250, 4000)
        self.notch = ButBR(self.damp, self.lfo)
        self.hp = ButHP(self.notch, 50, mul=mul)

    def out(self):
        self.hp.out()
        return self

    def sig(self):
        return self.hp

    def changeSample(self, newpath):
        self.t.setSound(newpath)
        self.count.reset

class Synth:
    def __init__(self, transpo=1, hfdamp=4000, lfofreq=0.2, channel=0, mul=1):
        self.transpo = Sig(transpo)
        self.note = Notein(poly=10, scale=1, first=0, last=127, channel=channel)
        self.pit = self.note['pitch'] * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=0.001, decay=.1, sustain=.7, release=0.1, mul=.5)

        self.ind = LinTable([(0,20), (200,10), (1000,2), (8191,1)])
        self.tr = TrigEnv(self.note['trigon'], table=self.ind, dur=1)
        self.trand = TrigRand(self.tr, 0.1 * self.note['velocity'], 1 * self.note['velocity'])

        self.osc1 = LFO(self.pit, sharp=0.5, type=2, mul=self.amp)
        self.osc2 = LFO(self.pit*0.997, sharp=0.5, type=2, mul=self.amp)
        self.f1 = CrossFM(carrier=self.pit, ratio=self.osc1, ind1=self.tr * self.trand.min, ind2=self.tr * self.trand.max, mul=self.amp).mix(1)
        self.f2 = CrossFM(carrier=self.pit, ratio=self.osc2, ind1=self.tr, ind2=self.tr, mul=self.amp).mix(1)

        self.mix = Mix([self.f1, self.f2], voices=2)
        self.damp = ButLP(self.mix, freq=hfdamp)

        self.lfo = Sine(lfofreq, phase=[random(), random()]).range(250, 4000)
        self.notch = ButBR(self.damp, self.lfo)
        self.hp = ButHP(self.notch, 50, mul=mul)

    def out(self):
        self.hp.out()
        return self

    def sig(self):
        return self.hp
