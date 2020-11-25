#!/usr/bin/env python3
# encoding: utf-8
from random import *
from pyo import *
import math

class Synth:
    def __init__(self, noteinput, trig, toggles, cs, transpo=1, hfdamp=15000, lfofreq=0.2, audioIN=0, mul=1):
        self.note = noteinput
        self.trig = trig
        self.trigCheck = Select(self.trig, 1)
        self.trigChange = TrigFunc(self.trigCheck, self.changeParams)
        self.toggles = toggles
        self.toggleCheck = Change(self.toggles)
        self.toggleChange = TrigFunc(self.toggleCheck, self.toggleFX)
        self.cs = Sig(cs)
        self.transpo = Sig(transpo)
        self.input = Sig(audioIN).stop()

        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.1)

        self.sigRand = SigTo(TrigRand(self.note['trigon'], .01, 10))
        self.panLfo = FastSine(self.sigRand, quality=0, mul=.5, add=.5)
        self.te = ExpTable([(0,0),(4096,1),(8192,0)], exp=3, inverse=True)
        self.logOsc = Osc(table=self.te, freq=15*(self.cs[1]+2))
        self.fs = FastSine(freq=self.logOsc, mul=self.cs[1], add=1)

        # SIDECHAIN #
        self.inputFollow = Follower(self.input, freq=10).stop()
        self.talk = self.inputFollow > .005
        self.followAmp = Port(self.talk, risetime=.05, falltime=.1).stop()
        self.ampscl = Scale(self.followAmp, outmin=1, outmax=0.1)   
        # SIDECHAIN #

        self.osc1 = FastSine(self.sigRand, mul=self.cs[1])
        self.osc2 = FastSine(self.sigRand*.98, mul=self.cs[1])
        self.cfm = CrossFM(carrier=self.pit, ratio=Mix([self.osc1,self.osc2]), ind1=self.cs[0]*50, ind2=Sig(self.cs[0])*self.fs, mul=self.amp)

        # self.lfoAmp = FastSine(.1, quality=0, mul=800, add=800)
        self.lfo = Sine(lfofreq, phase=[random.random(),random.random()], mul=1, add=3000)
        self.damp = ButLP(self.cfm.mix(), freq=hfdamp).mix(1)
        self.notch = ButBR(self.damp, self.lfo).mix(1)
        self.hp = ButHP(self.notch, 50).mix(1)
        self.p = Pan(self.hp * self.ampscl, outs=2, pan=self.panLfo, spread=.1, mul=mul)

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
    def __init__(self, noteinput, trig, toggles, cs, transpo=1, hfdamp=5000, lfofreq=0.2, audioIN=0, mul=1):
        self.note = noteinput
        self.trig = trig
        self.trigCheck = Select(self.trig, 1)
        self.trigChange = TrigFunc(self.trigCheck, self.changeParams)
        self.toggles = toggles
        self.toggleCheck = Change(self.toggles)
        self.toggleChange = TrigFunc(self.toggleCheck, self.toggleFX)
        self.cs = Sig(cs)
        self.transpo = Sig(transpo)
        self.input = Sig(audioIN).stop()

        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.2)

        self.trand = TrigRand(self.note['trigon'], .01, 10)
        self.valVel = SigTo(self.note['velocity'], .01)

        self.blitLfo = FastSine(self.valVel * (self.cs[1]*500), quality=0, mul=self.cs[1]*2)
        self.harmLfo = FastSine(self.pit, quality=0, mul=(self.cs[1]*20)+1, add=(self.cs[1]*50)+20)
        self.panLFO = FastSine((self.valVel*50)*(self.trand*5), quality=0, mul=.5, add=.5)

        self.blit = Blit(freq=[self.pit,self.pit*.98]*self.blitLfo, harms=self.harmLfo).mix()
        self.cfm = CrossFM(carrier=self.pit, ratio=self.blit*((self.cs[0]*10)+1), ind1=self.cs[0]*2, ind2=self.cs[0]*5, mul=self.amp)

        # SIDECHAIN #
        self.inputFollow = Follower(self.input, freq=10).stop()
        self.talk = self.inputFollow > .005
        self.followAmp = Port(self.talk, risetime=0.05, falltime=0.1).stop()
        self.ampscl = Scale(self.followAmp, outmin=1, outmax=0.1)
        # SIDECHAIN #

        self.lfo = Sine(lfofreq, phase=[random.random(), random.random()]).range(240, 4000)
        self.damp = ButLP(self.cfm.mix(), freq=hfdamp).mix(1)
        self.notch = ButBR(self.damp, self.lfo).mix(1)
        self.hp = ButHP(self.notch, 50).mix(1)
        self.p = Pan(self.hp * self.ampscl, outs=2, pan=self.panLFO, spread=.2, mul=mul)

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
    def __init__(self, noteinput, paths, trig, toggles, cs, transpo=1, hfdamp=5000, lfofreq=0.2, autoswitch=False, withloop=False, audioIN=0, mul=1):
        self.note = noteinput
        self.paths = paths
        self.trig = trig
        self.trigCheck = Select(self.trig, 1)
        self.trigChange = TrigFunc(self.trigCheck, self.shuffleSamples)
        self.toggles = toggles
        self.toggleCheck = Change(self.toggles)
        self.toggleChange = TrigFunc(self.toggleCheck, self.toggleFX)
        self.cs = Sig(cs)
        self.transpo = Sig(transpo)
        self.input = Sig(audioIN).stop()
        
        self.bend = Bendin(brange=200, scale=1)
        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.1)
        self.ampLfo = FastSine(((self.cs[0]*20)+1), quality=0, mul=.5, add=.5)

        self.phasor = Phasor(freq=Sig(self.pit), mul=self.cs[1]*10)

        if type(self.paths) is list:
            print(self.paths)
            self.t = []
            self.voices = []
            self.toMorph = []
            for i in range(3):
                self.t.append(SndTable(self.paths[i], initchnls=2))
            self.lfo = Sine(self.tra*self.bend, mul=.5*self.phasor, add=.5)
            self.nt = NewTable(length=22050./44100, chnls=2)
            self.Tmorph = TableMorph(self.lfo, self.nt, self.t)
            self.oscT = OscTrig(self.nt, self.note['trigon'], self.tra, mul=self.amp)
            print('Simpler: is list')
        else: 
            self.t = SndTable(self.paths, initchnls=2)
            self.freq = self.t.getRate()
            self.dur = self.t.getDur()
            self.oscT = OscTrig(self.t, self.note['trigon'], (self.freq*self.tra), mul=self.amp)

        # SIDECHAIN #
        self.inputFollow = Follower(self.input, freq=10).stop()
        self.talk = self.inputFollow > .005
        self.followAmp = Port(self.talk, risetime=0.05, falltime=0.1).stop()
        self.ampscl = Scale(self.followAmp, outmin=1, outmax=0.1)
        # SIDECHAIN #

        self.damp = ButLP(self.oscT.mix(), freq=hfdamp).mix(1)
        self.lfo = Sine(lfofreq, phase=[random.random(), random.random()]).range(250, 4000)
        self.notch = ButBR(self.damp, self.lfo).mix(1)
        self.hp = ButHP(self.notch, 50).mix(1)
        self.comp = Compress(self.hp, thresh=-12, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(1)
        self.p = Pan(self.comp * self.ampscl, outs=2, pan=self.ampLfo, spread=.3, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

    def shuffleSamples(self):
        if type(self.paths) is list:
            for i in range(3):
                self.newsound = self.paths[math.floor(random.uniform(0,len(self.paths)))]
                self.t[i].setSound(self.newsound)
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
    def __init__(self, noteinput, path, trig, toggles, cs, transpo=1, hfdamp=5000, lfofreq=0.2, audioIN=0, mul=1):
        self.note = noteinput
        self.path = path
        self.trig = trig
        self.trigCheck = Select(self.trig, 1)
        self.trigChange = TrigFunc(self.trigCheck, self.changeParams)
        self.toggles = toggles
        self.toggleCheck = Change(self.toggles)
        self.toggleChange = TrigFunc(self.toggleCheck, self.toggleFX)
        self.cs = Sig(cs)
        self.transpo = Sig(transpo)
        self.input = Sig(audioIN).stop()

        self.snd = SndTable(self.path, initchnls=2)
        self.freq = self.snd.getRate()
        self.dur = self.snd.getDur()

        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.1, sustain=.7, release=.25)

        self.t = HarmTable([1,0,.33,0,.2,0,.143,0,.111])
        # self.t.graph()
        self.lfo = Osc(self.t, self.tra, mul=.5*self.cs[1], add=.5).mix()
        self.osc = Osc(self.snd, (self.freq*self.tra)*self.lfo, mul=self.amp).mix()

        # Waveshaped distortion
        self.table = ExpTable([(0,-.25),(4096,0),(8192,0)], exp=30)
        self.high_table = ExpTable([(0,1),(2000,1),(4096,0),(4598,1),(8192,0)],
                            exp=5, inverse=False)
        self.high_table.reverse()
        self.table.add(self.high_table)
        self.lookShape = Lookup(self.table, self.osc).mix()

        # SIDECHAIN #
        self.inputFollow = Follower(self.input, freq=10).stop()
        self.talk = self.inputFollow > .005
        self.followAmp = Port(self.talk, risetime=0.05, falltime=0.1).stop()
        self.ampscl = Scale(self.followAmp, outmin=1, outmax=0.1)
        # SIDECHAIN #

        self.veltrand = TrigRand(self.note['trigon'], .1, 10)
        self.ampLfo = FastSine(self.veltrand, quality=0, mul=.5, add=.5)
        self.interp = Interp(self.osc, self.lookShape, self.lfo*cs[0]).mix()
        self.damp = ButLP(self.interp, freq=hfdamp).mix()
        self.hp = ButHP(self.damp, 50).mix()
        self.comp = Compress(self.hp, thresh=-12, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix()
        self.p = Pan(self.comp * self.ampscl, outs=2, pan=self.ampLfo, spread=.2, mul=mul)

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
    def __init__(self, noteinput, paths, cs, transpo=1, hfdamp=5000, lfofreq=0.2, audioIN=0, mul=1):
        self.note = noteinput
        self.paths = paths
        self.cs = cs
        self.transpo = Sig(transpo)
        self.tra = MToT(self.note['pitch']) * self.transpo
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=.01, decay=.05, sustain=.8, release=.1)
        # self.beat = Beat(.125, 16, w1=100, w2=25, w3=15, poly=10).stop()
        # self.env = CosTable([(0,0), (100,1), (500,.3), (8191,0)])
        # self.amp = TrigEnv(self.beat, table=self.env)
        # self.trmid = TrigXnoiseMidi(self.beat, dist=0, mrange=(40,41))

        self.tables = []
        self.selectors = []
        self.players = []

        for i in range(6):
            self.tables.append(SndTable(self.paths[i], initchnls=2))
            self.selectors.append(Select(self.note['pitch'], value=36+i))
            self.players.append(TrigEnv(self.selectors[i], self.tables[i], dur=self.tables[i].getDur()/self.transpo, mul=self.amp.mix()))

        self.mix = Mix(self.players)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(1)
        self.hp = ButHP(self.damp, 50).mix(1)
        self.comp = Compress(self.hp, thresh=-12, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix(1)
        self.p = Pan(self.comp, outs=2, pan=[.4,.6], spread=.2, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p

    def play(self):
        self.beat.play()

class ReSampler:
    def __init__(self, notechannel, audioREC, trig, toggles, cs, transpo=1, hfdamp=7000, audioIN=0, mul=1):
        self.notes = Notein(poly=10, scale=0, first=0, last=127, channel=notechannel)
        self.audioREC = Sig(audioREC)
        self.audioIN = Sig(audioIN)
        self.trig = trig
        self.trigCheck = Select(self.trig, 1)
        self.trigChange = TrigFunc(self.trigCheck, self.rec)
        self.toggles = toggles
        self.toggleCheck = Change(self.toggles)
        self.toggleChange = TrigFunc(self.toggleCheck, self.toggleFX)
        self.cs = Sig(cs)
        self.transpo = Sig(transpo)
        self.input = Sig(audioIN).stop()
        self.check = Change(self.toggles)
        self.toggleChange = TrigFunc(self.check, self.toggleFX)
       
        self.tra = MToT(self.notes['pitch']) * self.transpo
        self.pit = MToF(self.notes['pitch']) * self.transpo

        self.envt = CosTable([(0,0), (50,1), (250,.3), (8191,0)])
        self.ingoreMIDI = False
        self.mids = [60]
        self.seq = Beat(time=.125, taps=16, w1=90, w2=40, w3=25).stop()
        self.auto = Iter(self.seq, self.mids).stop()
        self.trigenv = TrigEnv(self.seq, self.envt).stop()
        self.amp = MidiAdsr(self.notes['velocity'], attack=.01, decay=.1, sustain=.7, release=.2)
        self.tfon = TrigFunc(self.notes['trigon'], self.noteon, arg=list(range(10)))

        ### TABLE RECORD & PLAYBACK ###
        self.nt = NewTable(length=2., chnls=2, feedback=0)
        self.tr = TableRec(self.audioREC, table=self.nt, fadetime=.01).stop()
        self.trigLoop = TrigFunc(self.tr['trig'], self.playAftRec).stop()
        self.envGen = TrigFunc([self.notes['trigon'],self.seq], self.createPoints, arg=8).stop()
        self.ind = CosLogTable([(0,0), (8191,0)], size=8192)
        self.trMod = Osc(self.ind, self.pit*(self.tra+self.auto), mul=self.cs[0]).mix().stop()
        ### TABLE RECORD & PLAYBACK ###
        
        # PITCH RANDOMIZER #
        self.randPitches = [.25,.5,.75,1,1.25,1.5,1.75,2]
        self.pitch1 = Choice(choice=self.randPitches, freq=self.trMod).stop()
        self.pitch2 = Sig(self.tra+self.auto)
        self.start = Phasor(freq=.2, mul=self.nt.getDur()-(self.nt.getDur()*1-self.toggles[1]))
        self.dur1 = Choice(choice=[.03125,.0625,.125,.25,.33,.66], freq=3)
        self.dur2 = self.nt.getDur()
        # PITCH RANDOMIZER #
        self.loop = Looper(self.nt, (self.pitch1+self.pitch2)*(self.tra+self.auto), start=self.start, dur=(self.dur1+self.dur2), startfromloop=False, autosmooth=False, mul=self.amp+self.trigenv).mix().stop()

        # Waveshaped distortion
        self.table = ExpTable([(0,-.25),(4096,0),(8192,0)], exp=30)
        self.high_table = ExpTable([(0,1),(2000,1),(4096,0),(4598,-1),(8192,0)],
                            exp=5, inverse=False)
        self.high_table.reverse()
        self.table.add(self.high_table)
        self.lookShape = Lookup(self.table, self.loop)
        self.dist = Disto(self.lookShape, drive=Clip(self.cs[1],0,1), slope=.95*self.trMod).mix()

        # SIDECHAIN #
        self.inputFollow = Follower(self.input, freq=10).stop()
        self.talk = self.inputFollow > .005
        self.followAmp = Port(self.talk, risetime=0.05, falltime=0.1).stop()
        self.ampscl = Scale(self.followAmp, outmin=1, outmax=0.1)
        # SIDECHAIN #

        self.fs1 = FastSine(freq=.1+(10*self.trMod), quality=0, mul=(self.amp+self.trigenv)*.5, add=.5)
        self.refSine = FastSine(freq=440).mix()
        self.damp = ButLP(self.dist, freq=hfdamp).mix()
        self.bal = Balance(self.damp, self.refSine, freq=20).mix()
        self.comp = Compress(self.bal, thresh=-12, ratio=6, risetime=.01, falltime=.2, knee=0.5).mix()
        self.p = Pan(self.comp * self.ampscl, outs=2, pan=self.fs1, mul=mul)

        self.createPoints(8)

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
        self.randPositions = []
        self.randPoints = []
        self.lst = [(0, 0)]
        for i in range(value):
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
            for i in range(len(self.randPitches)):
                self.randPitches.pop(i)
                self.randPitches.insert(i, random.uniform(.01,4))
            print(self.randPitches)
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
            self.notes.stop()
            self.seq.play()
            self.auto.play()
            self.trigenv.play()
            self.ingoreMIDI = True
        else:
            print('off 3')
            self.notes.play()
            self.seq.stop()
            self.auto.stop()
            self.trigenv.stop()
            self.ingoreMIDI = False
            for i in range(len(self.mids) - 1):
                self.mids.pop()

    def noteon(self, voice):
        pitch = int(self.notes['pitch'].get(all=True)[voice])
        if self.ingoreMIDI != True:
            if(len(self.mids) <= 12):
                self.mids.append(midiToTranspo(pitch))
            else:
                self.mids.pop(0)
                self.mids.append(midiToTranspo(pitch))
        self.auto.setChoice(self.mids)
        # print(self.auto.choice)