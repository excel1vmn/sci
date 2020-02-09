#!/usr/bin/env python3
# encoding: utf-8
from random import *
from pyo import *
import math

class Simpler:
    def __init__(self, paths, transpo=1, hfdamp=5000, lfofreq=0.2, cs1=1, cs2=1, cs3=1, autoswitch=False, withloop=False, channel=0, mul=1):
        self.transpo = Sig(transpo)
        self.cs1 = cs1
        self.cs2 = cs2
        self.cs3 = cs3
        self.cs1.setValue(.5)
        self.cs2.setValue(0)
        self.cs3.setValue(0)

        self.paths = paths
        self.t = SndTable(self.paths, initchnls=2)
        self.freq = self.t.getRate()
        self.dur = self.t.getDur()

        self.note = Notein(poly=8, scale=0, first=0, last=127, channel=channel)
        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.001, decay=.1, sustain=.7, release=.1)

        self.trand = TrigRand(self.note['trigon'], .01, 1)
        self.tf = TrigFunc(self.note['trigon'], self.randMod)
        self.veltrand = TrigRand(self.note['trigon'], self.note['velocity'], (self.note['velocity'] * 10))
        self.sigRand = SigTo(self.veltrand)
        self.ampLfo = FastSine(self.sigRand*((self.cs1*20)+1), quality=0, mul=.5, add=.5)

        self.tf = CosTable([(0,-1),(3072,-0.85),(4096,0),(5520,.85),(8192,1)])

        self.osc = OscTrig(self.t, self.note['trigon'], (self.freq*self.tra)*self.transpo)
        self.fol = Follower(self.osc*(self.cs1*100)+1, mul=(self.cs3*5)+.5)

        self.cfm = CrossFM(carrier=self.osc*self.pit, ratio=[(self.trand*0.98)*((self.cs2*20)+1), (self.trand*1.02)*((self.cs2*19)+1)], ind1=self.trand*((self.cs2*20)+1), ind2=(self.osc*self.trand)*((self.cs2*20)+1), mul=self.amp).mix(2)
        self.look = Lookup(table=self.tf, index=self.cfm*((self.cs3+.1)*10), mul=self.fol*(self.cs3*5)).mix(2)

        self.lfo = Sine(lfofreq, phase=[random.random(), random.random()]).range(250, 4000)

        self.mix = Mix(self.cfm*(self.look+1), voices=2)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.notch = ButBR(self.damp, self.lfo).mix(2)
        self.hp = ButHP(self.notch, 50).mix(2)
        self.comp = Compress(self.hp, thresh=-30, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.pan = Pan(self.comp, outs=2, pan=self.ampLfo, spread=.3, mul=mul)

    def out(self):
        self.pan.out()
        return self

    def sig(self):
        return self.pan

    def randMod(self):
        self.r = random.uniform(.2, 1)
        self.amp.setSustain(self.r)
        self.r = random.uniform(.2, 1)
        self.amp.setRelease(self.r)

    def changeSample(self, newpath):
        print(newpath)
        self.t.setSound(newpath)

class Synth:
    def __init__(self, transpo=1, hfdamp=5000, lfofreq=0.2, cs1=1, cs2=1, cs3=1, channel=0, mul=1):
        self.transpo = Sig(transpo)
        self.cs1 = cs1
        self.cs2 = cs2
        self.cs3 = cs3
        self.cs1.setValue(0)
        self.cs2.setValue(0)
        self.cs3.setValue(0)

        self.note = Notein(poly=8, scale=0, first=0, last=127, channel=channel)
        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=0.001, decay=.1, sustain=.1, release=.1)

        self.trand = TrigRand(self.note['trigon'], .01, 1)
        self.sigRand = SigTo(self.trand)
        # self.veltrand = TrigRand(self.note['trigon'], self.note['velocity'], (self.note['velocity'] * 10))
        self.ampLfo = FastSine(self.sigRand * 20, quality=0, mul=.5, add=.5)

        self.tf = TrigFunc(self.note['trigon'], self.randMod)

        self.osc1 = LFO(self.pit, sharp=self.trand, type=2, mul=self.amp)
        self.osc2 = LFO(self.pit*0.995, sharp=self.trand, type=2, mul=self.amp)

        self.fol = Follower(self.osc1 + self.osc2, mul=self.cs3*5)

        self.f1 = CrossFM(carrier=self.pit, ratio=self.osc1, ind1=self.amp * (self.trand * (self.fol+1)) * (self.cs1 * 101), ind2=(self.fol+1) * (self.trand * (self.cs1*.5)), mul=self.amp)
        self.f2 = CrossFM(carrier=self.pit, ratio=self.osc2, ind1=self.amp * (self.trand * (self.fol+1)) * (self.cs1 * 99), ind2=(self.fol+1) * (self.trand * (self.cs1*.5)), mul=self.amp)

        self.mix = Mix([self.f1, self.f2], voices=2)
        self.lfo = Sine(lfofreq, phase=[random.random(), random.random()]).range(240, 4000)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.notch = ButBR(self.damp, (self.lfo + 1)).mix(2)
        self.hp = ButHP(self.notch, 50).mix(2)
        self.comp = Compress(self.hp, thresh=-24, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp, outs=2, pan=self.ampLfo, spread=.2, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

    def randMod(self):
        self.r = random.uniform(.05, 1)
        self.amp.setSustain(self.r)
        self.r = random.uniform(.05, 1)
        self.amp.setRelease(self.r)
        # print(self.sigRand.get())

class FreakSynth:
    def __init__(self, transpo=1, hfdamp=5000, lfofreq=0.2, cs1=1, cs2=1, cs3=1, channel=0, mul=1):
        self.transpo = Sig(transpo)
        self.cs1 = cs1
        self.cs2 = cs2
        self.cs3 = cs3
        self.cs1.setValue(0)
        self.cs2.setValue(0)
        self.cs3.setValue(0)

        self.note = Notein(poly=8, scale=0, first=0, last=127, channel=channel)
        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=0.001, decay=.1, sustain=.7, release=.2)

        self.trand = TrigRand(self.note['trigon'], .01, 1)

        self.osc1 = LFO(self.pit, sharp=self.trand * ((self.cs2*45) + 1), type=2, mul=self.cs3)
        self.osc2 = LFO(self.pit*0.97, sharp=self.trand * ((self.cs2*55) + 1), type=2, mul=self.cs3)

        self.oscLfo = FastSine((self.pit * self.trand), quality=0, mul=self.trand*(self.cs2+1), add=1)
        self.ampLfo = FastSine(self.trand * ((self.cs2*50) + 1), quality=0, add=.5)

        self.blit = Blit(freq=[self.pit, self.pit*.97]*self.ampLfo, harms=self.oscLfo, mul=self.cs3+1)
        self.f1 = CrossFM(carrier=self.pit * (self.oscLfo*self.blit), ratio=self.oscLfo * (self.cs1*200.2), ind1=self.osc1*(self.cs1*2), ind2=(self.osc1 * self.trand)*(self.cs1*4), mul=self.amp).mix(2)
        self.f2 = CrossFM(carrier=self.pit * (self.oscLfo*self.blit), ratio=self.oscLfo * (self.cs1*200.1), ind1=self.osc2*(self.cs1*3), ind2=(self.osc2 * self.trand)*(self.cs1*5), mul=self.amp).mix(2)

        self.mix = Mix([self.f1, self.f2], voices=2)
        self.lfo = Sine(lfofreq, phase=[random.random(), random.random()]).range(240, 4000)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.notch = ButBR(self.damp, self.lfo).mix(2)
        self.hp = ButHP(self.notch, 50).mix(2)
        self.comp = Compress(self.hp, thresh=-30, ratio=8, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp, outs=2, pan=self.ampLfo, spread=.5, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

class WaveShape:
    def __init__(self, path, transpo=1, hfdamp=5000, lfofreq=0.2, cs1=1, cs2=1, cs3=1, channel=0, mul=1):
        self.transpo = Sig(transpo)
        self.cs1 = cs1
        self.cs2 = cs2
        self.cs3 = cs3
        self.cs1.setValue(0)
        self.cs2.setValue(0)
        self.cs3.setValue(0)

        self.path = path
        self.snd = SndTable(self.path, initchnls=2)
        self.freq = self.snd.getRate()
        self.dur = self.snd.getDur()

        self.note = Notein(poly=8, scale=0, first=0, last=127, channel=channel)
        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.001, decay=.1, sustain=.7, release=.25)
        self.sigto = SigTo(self.tra, .05)

        self.veltrand = TrigRand(self.note['trigon'], .1, self.note['velocity'] * 4)
        self.ampLfo = FastSine(self.veltrand, quality=0, mul=.5, add=.5)

        self.lfo = Sine(freq=[self.sigto, self.sigto * .5], mul=.25, add=.25)
        self.a = TrigEnv(self.note['trigon'], self.snd, (self.dur / self.transpo) / self.tra, mul=.5)
        self.t = CosTable([(0,-1),(3072,-0.85),(4096,0),(5520,.85),(7120,-.5),(8192,1)])
        # self.f = IRPulse(self.a, freq=MToF(self.note['pitch']), bw=50 * MToF(self.note['pitch']) * self.lfo, type=3, order=256)

        # Stereo mix.
        self.b = Lookup(table=self.t, index=self.a, mul=self.amp).mix(2)
        self.mix = Mix(self.b, voices=2)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.hp = ButHP(self.damp, 50).mix(2)
        self.comp = Compress(self.hp, thresh=-24, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp, outs=2, pan=self.ampLfo, spread=.5, mul=mul)

    def out(self):
        self.p.out()#peux-être ça
        return self

    def sig(self):
        return self.p

# class Pads:
#     def __init__(self, path, transpo=1, hfdamp=8000, lfofreq=0.2, channel=0, mul=1):
#         self.path = path
#         self.transpo = Sig(transpo)
#         self.note = Notein(poly=16, scale=0, first=0, last=127, channel=channel)
#         self.vel = MToF(self.note['velocity']) * self.transpo
#
#         # random.randint(0, len(self.path)) - 1
#         self.table = SndTable(self.path, initchnls=2)
#         self.rate = self.table.getRate()
#         self.dur = self.table.getDur()
#
#         self.selectors = []
#         self.players = []
#         self.tones = []
#         self.amps = []
#
#         for i in range(16):
#             self.amps.append(MidiAdsr(self.note['velocity'], attack=0.001, decay=.1, sustain=1, release=.2, mul=.2))
#             self.selectors.append(Select(self.note["pitch"], value=36+i))
#             self.players.append(TrigEnv(self.selectors[i], self.table, dur=self.dur / self.transpo, mul=self.amps[i]))
#
#         self.follow = Follower(self.players)
#         self.tones = [Allpass(self.players[0], delay=[.0204,.02011], feedback=0.5, mul=self.amps[0]).mix(2),
#                      Tone(self.players[1], 5000, mul=self.amps[1]).mix(2),
#                      Freeverb(self.players[2], size=1, damp=.3, bal=.5, mul=self.amps[2]).mix(2),
#                      Disto(self.players[3], drive=.98, slope=.8, mul=self.amps[3] * .3).mix(2),
#                      Delay(self.players[4], delay=[self.vel * .01, self.vel * .02], feedback=.9, mul=self.amps[4]).mix(2)]
#
#         # self.f2 = CrossFM(carrier=self.pit * (self.oscLfo * -1), ratio=self.oscLfo, ind1=self.osc2 * self.trand.min, ind2=self.osc2 * self.trand.max, mul=self.amp).mix(1)
#
#         # Stereo mix.
#         self.mix = Mix(self.tones, voices=16)
#         self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
#         self.hp = ButHP(self.damp, 50).mix(2)
#         self.clip = Clip(self.hp, min=-1, max=mul * 2, mul=mul)
#
#     def out(self):
#         self.clip.out()
#         return self
#
#     def sig(self):
#         return self.clip

class Drums:
    def __init__(self, paths, transpo=1, hfdamp=7000, lfofreq=0.2, channel=0, mul=1):
        self.paths = paths
        self.transpo = Sig(transpo)

        self.note = Notein(poly=16, scale=0, first=0, last=127, channel=channel)
        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=0.001, decay=.1, sustain=1, release=.1)

        self.tables = []
        self.selectors = []
        self.players = []

        for i in range(len(self.paths)):
            self.tables.append(SndTable(self.paths[i], initchnls=2))
            self.selectors.append(Select(self.note["pitch"], value=36+i))
            self.players.append(TrigEnv(self.selectors[i], self.tables[i], dur=self.tables[i].getDur() / self.transpo, mul=self.amp).mix(2))

        # Stereo mix.
        self.mix = Mix(self.players, voices=16)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.hp = ButHP(self.damp, 50).mix(2)
        self.comp = Compress(self.hp, thresh=-24, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp, outs=2, pan=[.25,.75], spread=.5, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

class ReSampler:
    def __init__(self, input, launch, transpo=1, cs1=1, cs2=1, cs3=1, channel=0, mul=1):
        self.transpo = transpo
        self.launch = launch
        self.cs1 = cs1
        self.cs2 = cs2
        self.cs3 = cs3
        self.cs1.setValue(0)
        self.cs2.setValue(0)
        self.cs3.setValue(.5)

        self.note = Notein(poly=8, scale=0, first=0, last=127, channel=channel)
        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=0.001, decay=.1, sustain=.7, release=.2)

        if type(input) is list:
            self.input = []
            for i in range(len(input)):
                self.input.append(input[i])
            self.input.append(input)
            # print(len(self.input))
            # self.r = []
            self.nt = []
            self.tr = []
            for i in range(len(self.input)):
                # self.r.append(TrigRand(self.note['trigon'], 0, 1))
                self.nt.append(NewTable(length=2, chnls=1, feedback=0))
                self.tr.append(TrigTableRec(self.input[i], trig=self.launch, table=self.nt[i]))

            self.morphSine = FastSine(self.cs2, mul=.5, add=.5)
            self.tm = NewTable(length=2, chnls=1, feedback=0)
            self.tf = TableMorph(self.morphSine, self.tm, self.nt)
            self.c = OscTrig(self.tm, self.note['trigon'], (self.tm.getRate() * self.tra) * self.transpo, mul=self.amp).mix(2)

        else:
            self.input = input
            self.nt = NewTable(length=2, chnls=1, feedback=0)
            self.tr = TrigTableRec(self.input, trig=self.launch, table=self.nt)
            self.c = OscTrig(self.nt, self.note['trigon'], (self.nt.getRate() * self.tra) * self.transpo, mul=self.amp).mix(2)

        # if channel == 10:
        #     self._tables = []
        #     self._selectors = []
        #     self._players = []
        #     self._ind = []
        #     self._fms = []
        #     for i in range(16):
        #         self._size = math.ceil(random.uniform(2048, 8192))
        #         self._intensity = random.uniform(.01,15)
        #         self._ind.append(LinTable([(0,self._intensity), (self._size/((random.random()+1)*4),self._intensity), (self._size/((random.random()+.5)*2),self._intensity), (self._size,1)], self._size))
        #         self._selectors.append(Select(self.note["pitch"], value=36+i))
        #         self._players.append(TrigEnv(self._selectors[i], self._ind[i], dur=1, mul=self.amp).mix(2))
        #         self._fms.append(FM(self.c, ratio=.25, index=self._players[i]))
        #     self.dist = Disto(self._fms, drive=self.cs1-.05, slope=self.cs1 * .8).mix(2)
        # else:
        #     self.dist = Disto(self.c, drive=self.cs1-.05, slope=self.cs1 * .8).mix(2)

        self.fs = FastSine(freq=(self.cs3 * 40) + .1, quality=0, mul=.5, add=.5)
        self.ind = LinTable([(0,3), (20,40), (300,10), (1000,5), (8191,3)])
        self.trMod = TrigEnv(self.note['trigon'], table=self.ind, dur=4)
        self.fm = FM(carrier=[self.cs3*1999,self.cs3*2000], ratio=self.cs2*200, index=self.trMod, mul=self.cs2)
        self.refSine = FastSine(freq=100, mul=.3)

        self.dist = Disto(self.c, drive=self.cs1-.05, slope=self.cs1*.9, mul=self.fs).mix(2)
        self.fmDist = Disto(self.c, drive=self.fm, slope=self.fm*(self.cs1*.9), mul=1).mix(2)
        self.lp = ButLP(self.dist+self.fmDist, 5000).mix(2)
        self.bp = ButBP(self.lp, freq=(self.pit * (self.cs1 + 1)), q=self.cs1 * 20).mix(2)
        self.hp = ButHP(self.bp, 50).mix(2)
        self.comp = Compress(self.hp, thresh=-20, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.bal = Balance(self.comp, self.refSine, freq=100).mix(2)
        self.p = Pan(self.bal, outs=2, pan=.5 * self.fs, spread=.4, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

class EffectBox:
    def __init__(self, inputs, cs, mul=1):
        if type(inputs) is list:
            self.ins = []
            for i in range(len(inputs)):
                self.ins.append(inputs[i])

        self.cs =[]
        self.fx =[]
        for i in range(16):
            self.cs.append(SigTo(0))
        self.fx.append(Disto(self.ins, drive=.5, slope=.5))
        self.t = CosTable([(0,-1),(3072,-0.85),(4096,0),(5520,.85),(8192,1)])
        self.b = Lookup(table=self.t, index=self.ins, mul=.5).out()

        self.m = Mix(self.fx)
        self.p = Pan(self.m, outs=len(self.ins), pan=.5, spread=.4, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p
