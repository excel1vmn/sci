#!/usr/bin/env python3
# encoding: utf-8
from random import *
from pyo import *
import math

class Synth:
    def __init__(self, noteinput, transpo=1, hfdamp=7000, lfofreq=0.2, cs=[0,0], mul=1):
        self.note = noteinput
        self.transpo = Sig(transpo)
        self.cs = cs

        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.1)

        self.sigRand = SigTo(TrigRand(self.note['trigon'], .01, 5))
        self.ampLfo = FastSine(self.sigRand * 20, quality=0, mul=.5, add=.5)
        self.te = ExpTable([(0,0),(4096,1),(8192,0)], exp=3, inverse=True)
        self.logOsc1 = Osc(table=self.te, freq=20*(self.cs[1]+2))
        self.logOsc2 = Osc(table=self.te, freq=20*(self.cs[1]+2))
        self.fs = FastSine(freq=[self.logOsc1,self.logOsc2], mul=self.cs[1])

        self.osc1 = LFO(self.sigRand, sharp=self.sigRand*.99, type=2, mul=self.fs)
        self.osc2 = LFO(self.sigRand*0.99, sharp=self.sigRand, type=2, mul=self.fs)
        self.cfm = CrossFM(carrier=self.pit, ratio=Mix([self.osc1,self.osc2]), ind1=self.cs[0]*10, ind2=self.fs, mul=self.amp).mix(2)

        self.mix = Mix(self.cfm, voices=2)
        self.lfo = Sine(lfofreq, phase=[random.random(), random.random()]).range(240, 4000)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.notch = ButBR(self.damp, self.lfo).mix(2)
        self.hp = ButHP(self.notch, 50).mix(2)
        self.comp = Compress(self.hp, thresh=-20, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp, outs=2, pan=self.ampLfo, spread=.5, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

class FreakSynth:
    def __init__(self, noteinput, transpo=1, hfdamp=7000, lfofreq=0.2, cs=[0,0], channel=0, mul=1):
        self.note = noteinput
        self.transpo = Sig(transpo)
        self.cs = cs

        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.2)

        self.trand = TrigRand(self.note['trigon'], .01, 10)
        self.valVel = SigTo(self.note['velocity'], .01)

        self.blitLfo = FastSine(self.valVel * (self.cs[1]*500), quality=0, mul=self.cs[1]*2)
        self.harmLfo = FastSine(self.pit, quality=0, mul=(self.cs[1]*20)+1, add=(self.cs[1]*50)+20)
        self.ampLfo = FastSine((self.valVel*50)*(self.trand*5), quality=0, add=.5)

        self.blit = Blit(freq=[self.pit,self.pit*.98]*self.blitLfo, harms=self.harmLfo).mix(2)
        self.cfm = CrossFM(carrier=self.pit, ratio=self.blit*((self.cs[0]*10)+1), ind1=self.cs[0]*2, ind2=self.cs[0]*5, mul=self.amp).mix(2)

        self.mix = Mix(self.cfm, voices=2)
        self.lfo = Sine(lfofreq, phase=[random.random(), random.random()]).range(240, 4000)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.notch = ButBR(self.damp, self.lfo).mix(2)
        self.hp = ButHP(self.notch, 50).mix(2)
        self.comp = Compress(self.hp, thresh=-20, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp, outs=2, pan=self.ampLfo, spread=.5, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

class Simpler:
    def __init__(self, noteinput, paths, transpo=1, hfdamp=7000, lfofreq=0.2, cs=[0,0], autoswitch=False, withloop=False, channel=0, mul=1):
        self.transpo = Sig(transpo)
        self.cs = cs

        self.paths = paths
        self.t = SndTable(self.paths, initchnls=2)
        self.freq = self.t.getRate()
        self.dur = self.t.getDur()

        self.note = noteinput
        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.1)

        self.trand = TrigRand(self.note['trigon'], .01, 1)
        self.veltrand = TrigRand(self.note['trigon'], self.note['velocity'], (self.note['velocity'] * 10))
        self.sigRand = SigTo(self.veltrand)
        self.ampLfo = FastSine(self.sigRand*((self.cs[0]*20)+1), quality=0, mul=.5, add=.5)

        self.ind = CosTable([(0,-1),(3072,-0.85),(4096,0),(5520,.85),(8192,1)])

        self.osc1 = OscTrig(self.t, self.note['trigon'], (self.freq*self.tra), mul=self.amp).mix(1)
        self.osc2 = OscTrig(self.t, self.note['trigon'], (self.freq*self.tra), mul=self.amp).mix(1)

        self.fol = Follower((Mix([self.osc1,self.osc2]))*(self.cs[0]*100)+1, mul=self.cs[0])

        self.cfm = CrossFM(carrier=Mix([self.osc1,self.osc2])*self.pit, ratio=[(self.trand*0.98)*((self.cs[1]*20)+1), (self.trand*1.02)*((self.cs[1]*19)+1)], ind1=self.trand*((self.cs[1]*20)+1), ind2=(self.osc1*self.trand)*((self.cs[1]*20)+1), mul=self.cs[1]).mix(2)

        self.look = Lookup(table=self.ind, index=(self.cs[1]+1)*10, mul=self.fol*(self.cs[1]*5)).mix(2).out()

        self.lfo = Sine(lfofreq, phase=[random.random(), random.random()]).range(250, 4000)

        self.mix = Mix([self.osc1,self.osc2,self.cfm], voices=2)#
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.notch = ButBR(self.damp, self.lfo).mix(2)
        self.hp = ButHP(self.notch, 50).mix(2)
        self.comp = Compress(self.hp, thresh=-20, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp, outs=2, pan=self.ampLfo, spread=.3, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

    def changeSample(self, newpath):
        print(newpath)
        self.t.setSound(newpath)

class WaveShape:
    def __init__(self, noteinput, path, transpo=1, hfdamp=7000, lfofreq=0.2, cs=[0,0], channel=0, mul=1):
        self.note = noteinput
        self.path = path
        self.transpo = Sig(transpo)
        self.cs = cs

        self.snd = SndTable(self.path, initchnls=2)
        self.freq = self.snd.getRate()
        self.dur = self.snd.getDur()

        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.25)

        self.veltrand = TrigRand(self.note['trigon'], .1, self.note['velocity'] * 4)
        self.ampLfo = FastSine(self.veltrand, quality=0, mul=.5, add=.5)

        self.t = CosTable([(0,-2),(3072,-0.85),(3584,1),(4096,0),(5520,.85),(6320,-1),(7120,-.5),(8192,2)])

        # self.lfo = Sine(freq=self.freq, mul=self.cs1)
        self.lfo = Osc(self.t, self.freq*self.tra, mul=self.cs[0])
        self.a1 = Osc(self.snd, self.freq*self.tra, mul=self.amp*(self.lfo+1)).mix(2)
        self.a2 = Osc(self.snd, (self.freq*.98)*self.tra, mul=self.amp*(self.lfo+1)).mix(2)

        # Stereo mix.
        self.mix = Mix([self.a1,self.a2], voices=2)
        self.b = Lookup(table=self.t, index=self.mix).mix(2)
        self.dist = Disto(self.b, drive=.9, slope=self.lfo).mix(2)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.hp = ButHP(self.damp, 50).mix(2)
        self.comp = Compress(self.hp, thresh=-20, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp, outs=2, pan=self.ampLfo, spread=.5, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

class Drums:
    def __init__(self, paths, noteinput, transpo=1, hfdamp=7000, lfofreq=0.2, mul=1):
        self.paths = paths
        self.note = noteinput
        self.transpo = Sig(transpo)
        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.1)

        self.tables = []
        self.selectors = []
        self.players = []

        for i in range(len(self.paths)):
            self.tables.append(SndTable(self.paths[i], initchnls=2))
            self.selectors.append(Select(self.note["pitch"], value=36+i))
            self.players.append(TrigEnv(self.selectors[i], self.tables[i], dur=self.tables[i].getDur()/self.transpo, mul=self.amp.mix(1)))

        # Stereo mix.
        self.mix = Mix(self.players, voices=2)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.hp = ButHP(self.damp, 50).mix(2)
        self.comp = Compress(self.hp, thresh=-20, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp, outs=2, pan=[.25,.75], spread=.5, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

class ReSampler:
    def __init__(self, noteinput, midictls, cs, input, transpo=1, hfdamp=7000, mul=1):
        # self.deNorm = Noise(1e-24)
        self.note = noteinput
        self.midictls = midictls
        self.cs = cs
        self.input = Mix(input, voices=2)
        self.transpo = Sig(transpo)
       
        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.2)

        self.valVel = SigTo(self.note['velocity'], .01)
        self.tabLenght = sampsToSec(48000)

        self.nt = NewTable(length=self.tabLenght, chnls=2, feedback=0)
        self.tr = TableRec(self.input, table=self.nt, fadetime=.01)
        self.trigLoop = TrigFunc(self.tr['trig'], self.playAftRec)
        self.envGen = TrigFunc(self.note['trigon'], self.createPoints, arg=8)
        self.ind = CosTable([(0,0), (8191,0)], size=8192)
        # self.trMod = TrigEnv(self.note['trigon'], table=self.ind, dur=self.nt.getRate() * self.tra, mul=self.cs[1]).mix(2)
        self.trMod = Osc(self.ind, self.nt.getRate() * self.tra, mul=self.cs[0]).mix(2)

        # self.c = OscTrig(self.nt, self.note['trigon'], self.nt.getRate() * self.tra, mul=self.amp).mix(2)
        
        self.pitch1 = Choice(choice=[.25,.5,.75,1,1.25,1.5,1.75], freq=[self.valVel*2,self.valVel*8], mul=self.midictls[0])
        self.pitch2 = Sig(self.tra, mul=1-self.midictls[0])
        self.start = Phasor(freq=.2, mul=self.nt.getDur()-(self.nt.getDur()*1-self.midictls[0]))
        self.dur1 = Choice(choice=[.0625,.125,.125,.25,.33], freq=4, mul=self.midictls[0])
        self.dur2 = self.nt.getDur()

        self.fs1 = FastSine(freq=self.trMod, quality=0, mul=self.valVel*4, add=.5)
        self.refSine = FastSine(freq=400, mul=1).mix(2)

        self.loop = Looper(self.nt, (self.pitch1+self.pitch2)*self.tra, start=self.start, dur=self.dur1+self.dur2, startfromloop=False, autosmooth=False, mul=self.amp).mix(2).stop()
        self.dist = Disto(self.loop, drive=self.trMod, slope=self.trMod, mul=(self.cs[1])*2).mix(2)
        self.damp = ButLP(Mix([self.loop,self.dist]), freq=hfdamp).mix(2)
        self.bal = Balance(self.damp, self.refSine, freq=20).mix(2)
        self.comp = Compress(self.bal, thresh=-20, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp, outs=2, pan=self.fs1, spread=self.valVel, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

    def rec(self):
        self.tr.play()

    def playAftRec(self):
        self.start.setPhase(self.nt.getDur())
        self.loop.play()

    def createPoints(self, value):
        self.value = value
        self.randPositions = []
        self.randPoints = []
        self.lst = [(0, 0)]
        # self.randPositions.append([random.randint(10, 1024),random.randint(1025, 2048),random.randint(2049, 4096),random.randint(4097, 8000)])

        for i in range(self.value):
            self.randPositions.append(math.floor(8192*((i+1)*.1)))
            self.randPoints.append(random.uniform(-5,5))
            self.lst.append((self.randPositions[i], self.randPoints[i]))

        self.lst.append((8191, 0))
        self.ind.replace(self.lst)

class EffectBox:
    def __init__(self, input, cs, channel=1, mul=1):
        self.input = Mix(input, voices=2)
        self.cs = cs
        self.fx = []

        self.fx.append(Disto(self.input, drive=.95, slope=.8, mul=Pow(self.cs[0]*8,3)))
        self.fx.append(FreqShift(Mix(self.input+self.fx[0]), shift=10*((self.fx[0]*.2)+1), mul=Pow(self.cs[1]*8,3)))
        self.pva = PVAnal(self.input+self.fx, size=4096)
        self.pvg = PVGate(self.pva, thresh=-36, damp=0)
        self.pvv = PVVerb(self.pvg, revtime=.90, damp=.90)
        self.fx.append(PVSynth(self.pvv, mul=Pow(self.cs[2],3)))

        self.mix = Mix(self.fx, voices=2)
        self.comp = Compress(Mix(self.fx, voices=2), thresh=-20, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp, outs=2, pan=.5, spread=.4, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

# class GestesMus:
#     def __init__(self, input, mul=1):
#         self._input = input
#         self._in_fader = InputFader(input)

#         self.lfo = FastSine(freq=[.3,.4,.5,.6], mul=.5, add=.5)
#         self.mb = MultiBand(self._input, num=4, mul=self.lfo).mix(2)
#         self.p = Pan(self.mb, outs=2, pan=.5, spread=.4, mul=mul)

#     def out(self):
#         self.p.out()
#         return self

#     def sig(self):
#         return self.p