#!/usr/bin/env python3
# encoding: utf-8
from random import *
from pyo import *
import math

class Synth:
    def __init__(self, noteinput, trig, toggles, cs, transpo=1, hfdamp=7000, lfofreq=0.2, audioIN=0, mul=1):
        self.note = noteinput
        self.trig = trig
        self.toggles = toggles
        self.toggleCheck = Change(self.toggles)
        self.trigCheck = Select(self.trig, 1)
        self.trigChange = TrigFunc(self.trigCheck, self.changeParams)
        self.trigToggles = TrigFunc(self.toggleCheck, self.toggleFX)
        self.cs = cs
        self.transpo = Sig(transpo)
        self.input = Sig(audioIN).stop()

        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.1)

        self.sigRand = SigTo(TrigRand(self.note['trigon'], .01, 5))
        self.ampLfo = FastSine(self.sigRand * 20, quality=0, mul=.5, add=.5)
        self.te = ExpTable([(0,0),(4096,1),(8192,0)], exp=3, inverse=True)
        self.logOsc = Osc(table=self.te, freq=20*(self.cs[1]+2))
        self.fs = FastSine(freq=self.logOsc, mul=self.cs[1])

        # SIDECHAIN #
        self.inputFollow = Follower(self.input, freq=10).stop()
        self.talk = self.inputFollow > .005
        self.followAmp = Port(self.talk, risetime=.05, falltime=.1).stop()
        self.ampscl = Scale(self.followAmp, outmin=1, outmax=0.1)
        # self.upscl = Scale(self.inputFollow, outmin=1, outmax=-1)      
        # SIDECHAIN #

        self.osc1 = FastSine(self.sigRand, mul=self.cs[1])
        self.osc2 = FastSine(self.sigRand*.98, mul=self.cs[1])
        self.cfm = CrossFM(carrier=self.pit, ratio=Mix([self.osc1,self.osc2]), ind1=self.cs[0]*100, ind2=self.fs, mul=self.amp)
        self.mix = Mix(self.cfm, voices=2)

        self.lfoAmp = FastSine(.1, quality=0, mul=800, add=800)
        self.lfo = Sine(lfofreq, phase=[random.random(),random.random()], mul=self.lfoAmp, add=3000)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.notch = ButBR(self.damp, self.lfo).mix(2)
        self.hp = ButHP(self.notch, 50).mix(2)
        self.p = Pan(self.hp * self.ampscl, outs=2, pan=self.ampLfo, spread=.5, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

    def changeParams(self):
        print('works')

    def toggleFX(self):
        if Sig(self.toggles[0]).get() == 1:
            print('on 1')
            self.input.play()
            self.inputFollow.play()
            self.followAmp.play()
        else:
            print('off 1')
            self.input.stop()
            self.inputFollow.stop()
            self.followAmp.stop()

        if Sig(self.toggles[1]).get() == 1:
            print('on 2')
        else:
            print('off 2')

        if Sig(self.toggles[2]).get() == 1:
            print('on 3')
        else:
            print('off 3')

class FreakSynth:
    def __init__(self, noteinput, trig, toggles, cs, transpo=1, hfdamp=7000, lfofreq=0.2, audioIN=0, mul=1):
        self.note = noteinput
        self.trig = trig
        self.toggles = toggles
        self.toggleCheck = Change(self.toggles)
        self.trigCheck = Select(self.trig, 1)
        self.trigChange = TrigFunc(self.trigCheck, self.changeParams)
        self.trigToggles = TrigFunc(self.toggleCheck, self.toggleFX)
        self.cs = cs
        self.transpo = Sig(transpo)
        self.input = Sig(audioIN).stop()

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

        # SIDECHAIN #
        self.inputFollow = Follower(self.input, freq=10).stop()
        self.talk = self.inputFollow > .005
        self.followAmp = Port(self.talk, risetime=0.05, falltime=0.1).stop()
        self.ampscl = Scale(self.followAmp, outmin=1, outmax=0.1)
        # SIDECHAIN #

        self.lfo = Sine(lfofreq, phase=[random.random(), random.random()]).range(240, 4000)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.notch = ButBR(self.damp, self.lfo).mix(2)
        self.hp = ButHP(self.notch, 50).mix(2)
        self.p = Pan(self.hp * self.ampscl, outs=2, pan=self.ampLfo, spread=.5, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

    def changeParams(self):
        print('works')

    def toggleFX(self):
        if Sig(self.toggles[0]).get() == 1:
            print('on 1')
            self.input.play()
            self.inputFollow.play()
            self.followAmp.play()
        else:
            print('off 1')
            self.input.stop()
            self.inputFollow.stop()
            self.followAmp.stop()

        if Sig(self.toggles[1]).get() == 1:
            print('on 2')
        else:
            print('off 2')

        if Sig(self.toggles[2]).get() == 1:
            print('on 3')
        else:
            print('off 3')

class Simpler:
    def __init__(self, noteinput, paths, trig, toggles, cs, transpo=1, hfdamp=7000, lfofreq=0.2, autoswitch=False, withloop=False, audioIN=0, mul=1):
        self.note = noteinput
        self.paths = paths
        self.trig = trig
        self.toggles = toggles
        self.toggleCheck = Change(self.toggles)
        self.trigCheck = Select(self.trig, 1)
        self.trigChange = TrigFunc(self.trigCheck, self.shuffleSamples)
        self.trigToggles = TrigFunc(self.toggleCheck, self.toggleFX)
        self.cs = cs
        self.transpo = Sig(transpo)
        self.input = Sig(audioIN).stop()
        
        self.t = SndTable(self.paths[0], initchnls=2)
        self.freq = self.t.getRate()
        self.dur = self.t.getDur()

        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.1)

        self.veltrand = TrigRand(self.note['trigon'], self.note['velocity'], (self.note['velocity'] * 10))
        self.sigRand = SigTo(self.veltrand)
        self.ampLfo = FastSine(self.sigRand*((self.cs[0]*20)+1), quality=0, mul=.5, add=.5)

        self.ind = CosTable([(0,-1),(3072,-0.85),(4096,0),(5520,.85),(8192,1)])
        self.oscT = OscTrig(self.t, self.note['trigon'], (self.freq*self.tra), mul=self.amp).mix(1)

        self.fol = Follower((Mix(self.oscT))*(self.cs[0]*100)+1)
        # (self.cs[1]*2)-1
        self.look = Lookup(table=self.ind, index=Mix(self.oscT), mul=self.cs[1]).mix(2)

        self.mix = Mix(self.oscT)

        # SIDECHAIN #
        self.inputFollow = Follower(self.input, freq=10).stop()
        self.talk = self.inputFollow > .005
        self.followAmp = Port(self.talk, risetime=0.05, falltime=0.1).stop()
        self.ampscl = Scale(self.followAmp, outmin=1, outmax=0.1)
        # SIDECHAIN #

        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.lfo = Sine(lfofreq, phase=[random.random(), random.random()]).range(250, 4000)
        self.notch = ButBR(self.damp, self.lfo).mix(2)
        self.hp = ButHP(self.notch, 50).mix(2)
        self.comp = Compress(self.hp, thresh=-20, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp * self.ampscl, outs=2, pan=self.ampLfo, spread=.3, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

    def shuffleSamples(self):
        if type(self.paths) is list:
            self.newsound = math.floor(random.uniform(0,len(self.paths)))
            self.t.setSound(self.paths[self.newsound])
            print(self.paths[self.newsound])
            print(self.newsound)

    def toggleFX(self):
        if Sig(self.toggles[0]).get() == 1:
            print('on 1')
            self.input.play()
            self.inputFollow.play()
            self.followAmp.play()
        else:
            print('off 1')
            self.input.stop()
            self.inputFollow.stop()
            self.followAmp.stop()

        if Sig(self.toggles[1]).get() == 1:
            print('on 2')
        else:
            print('off 2')

        if Sig(self.toggles[2]).get() == 1:
            print('on 3')
        else:
            print('off 3')

class WaveShape:
    def __init__(self, noteinput, path, trig, toggles, cs, transpo=1, hfdamp=7000, lfofreq=0.2, audioIN=0, mul=1):
        self.note = noteinput
        self.path = path
        self.trig = trig
        self.toggles = toggles
        self.toggleCheck = Change(self.toggles)
        self.trigCheck = Select(self.trig, 1)
        self.trigChange = TrigFunc(self.trigCheck, self.changeParams)
        self.trigToggles = TrigFunc(self.toggleCheck, self.toggleFX)
        self.cs = cs
        self.transpo = Sig(transpo)
        self.input = Sig(audioIN).stop()

        self.snd = SndTable(self.path, initchnls=2)
        self.freq = self.snd.getRate()
        self.dur = self.snd.getDur()

        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.25)

        self.veltrand = TrigRand(self.note['trigon'], .1, self.note['velocity'] * 4)
        self.ampLfo = FastSine(self.veltrand, quality=0, mul=.5, add=.5)

        self.t = HarmTable([1,0,.33,0,.2,0,.143,0,.111,0,.091])
        self.lfo = Osc(self.t, (self.pit*self.tra) * self.veltrand, mul=self.cs[0])
        self.a1 = Osc(self.snd, self.freq*self.tra, mul=self.amp*(self.lfo+1)).mix(1)
        self.a2 = Osc(self.snd, (self.freq*.98)*self.tra, mul=self.amp*(self.lfo+1)).mix(1)

        # Stereo mix.
        self.mix = Mix([self.a1,self.a2], voices=2)

        # SIDECHAIN #
        self.inputFollow = Follower(self.input, freq=10).stop()
        self.talk = self.inputFollow > .005
        self.followAmp = Port(self.talk, risetime=0.05, falltime=0.1).stop()
        self.ampscl = Scale(self.followAmp, outmin=1, outmax=0.1)
        # SIDECHAIN #

        self.b = Lookup(table=self.t, index=self.mix).mix(2)
        self.dist = Disto(self.b, drive=.9, slope=self.lfo).mix(2)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.hp = ButHP(self.damp, 50).mix(2)
        self.comp = Compress(self.hp, thresh=-20, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp * self.ampscl, outs=2, pan=self.ampLfo, spread=.5, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

    def changeParams(self):
        print('works')

    def toggleFX(self):
        if Sig(self.toggles[0]).get() == 1:
            print('on 1')
            self.input.play()
            self.inputFollow.play()
            self.followAmp.play()
        else:
            print('off 1')
            self.input.stop()
            self.inputFollow.stop()
            self.followAmp.stop()

        if Sig(self.toggles[1]).get() == 1:
            print('on 2')
        else:
            print('off 2')

        if Sig(self.toggles[2]).get() == 1:
            print('on 3')
        else:
            print('off 3')

class Drums:
    def __init__(self, noteinput, paths, cs, transpo=1, hfdamp=7000, lfofreq=0.2, audioIN=0, mul=1):
        self.note = noteinput
        self.paths = paths
        self.cs = cs
        self.transpo = Sig(transpo)
        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.1)

        self.tables = []
        self.selectors = []
        self.amps = []
        self.players = []

        for i in range(len(self.paths)):
            self.tables.append(SndTable(self.paths[i], initchnls=2))
            self.selectors.append(Select(self.note['pitch'], value=36+i))
            # self.amps.append(MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.1))
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

class ReSampler:
    def __init__(self, noteinput, audioREC, trig, toggles, cs, transpo=1, hfdamp=7000, audioIN=0, mul=1):
        # self.deNorm = Noise(1e-24)
        self.note = noteinput
        self.audioREC = Mix(audioREC, voices=2)
        self.audioIN = Sig(audioIN)
        self.trig = trig
        self.toggles = toggles
        self.toggleCheck = Change(self.toggles)
        self.trigCheck = Select(self.trig, 1)
        self.trigChange = TrigFunc(self.trigCheck, self.rec)
        self.trigToggles = TrigFunc(self.toggleCheck, self.toggleFX)
        self.cs = cs
        self.transpo = Sig(transpo)
        self.input = Sig(audioIN).stop()
       
        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.2)

        self.valVel = SigTo(self.note['velocity'], .01)
        self.tabLenght = sampsToSec(48000)

        self.nt = NewTable(length=self.tabLenght, chnls=2, feedback=0)
        self.tr = TableRec(self.audioREC, table=self.nt, fadetime=.01).stop()
        self.trigLoop = TrigFunc(self.tr['trig'], self.playAftRec).stop()
        self.envGen = TrigFunc(self.note['trigon'], self.createPoints, arg=8).stop()
        self.ind = CosTable([(0,0), (8191,0)], size=8192)
        self.trMod = Osc(self.ind, self.nt.getRate() * self.tra, mul=self.cs[0]).mix(2).stop()

        self.check = Change(self.toggles)
        self.trigToggles = TrigFunc(self.check, self.toggleFX)
        
        # ADD RANDOMIZER ELEMENTS
        self.pitch1 = Choice(choice=[.25,.5,.75,1,1.25,1.5,1.75], freq=self.trMod).stop()
        self.pitch2 = Sig(self.tra)
        self.start = Phasor(freq=.2, mul=self.nt.getDur()-(self.nt.getDur()*1-self.toggles[1]))
        self.dur1 = Choice(choice=[.0625,.125,.125,.25,.33], freq=4)
        self.dur2 = self.nt.getDur()

        self.fs1 = FastSine(freq=self.trMod, quality=0, mul=self.valVel, add=.5)
        self.refSine = FastSine(freq=400).mix(2)

        self.loop = Looper(self.nt, Mix([self.pitch1,self.pitch2])*self.tra, start=self.start, dur=self.dur1+self.dur2, startfromloop=False, autosmooth=False, mul=self.amp).mix(2).stop()

        # SIDECHAIN #
        self.inputFollow = Follower(self.input, freq=10).stop()
        self.talk = self.inputFollow > .005
        self.followAmp = Port(self.talk, risetime=0.05, falltime=0.1).stop()
        self.ampscl = Scale(self.followAmp, outmin=1, outmax=0.1)
        # SIDECHAIN #

        self.dist = Disto(self.loop, drive=self.trMod, slope=self.trMod, mul=(self.cs[1])*2).mix(2)
        self.damp = ButLP(Mix([self.loop,self.dist]), freq=hfdamp).mix(2)
        self.bal = Balance(self.damp, self.refSine, freq=20).mix(2)
        self.comp = Compress(self.bal, thresh=-20, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(2)
        self.p = Pan(self.comp * self.ampscl, outs=2, pan=self.fs1, spread=self.valVel, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

    def rec(self):
        self.trigLoop.play()
        self.tr.play()
        self.envGen.stop()
        self.trMod.stop()

    def playAftRec(self):
        self.start.setPhase(self.nt.getDur())
        self.loop.play()
        self.tr.stop()
        self.trigLoop.stop()
        self.envGen.play()
        self.trMod.play()
        print('recorded')

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

    def toggleFX(self):
        if Sig(self.toggles[0]).get() == 1:
            print('on 1')
            self.input.play()
            self.inputFollow.play()
            self.followAmp.play()
        else:
            print('off 1')
            self.input.stop()
            self.inputFollow.stop()
            self.followAmp.stop()

        if Sig(self.toggles[1]).get() == 1:
            print('on 2')
            self.pitch1.play()
            self.pitch2.stop()
            self.dur1.play()
        else:
            print('off 2')
            self.pitch1.stop()
            self.pitch2.play()
            self.dur1.stop()

        if Sig(self.toggles[2]).get() == 1:
            print('on 3')
        else:
            print('off 3')

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
        