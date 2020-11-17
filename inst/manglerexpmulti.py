from pyo import *
import random

class ManglerExpMulti:
    def __init__(self, paths, transpo=1, segments=8, segdur=0.125, fFreq=50, fRatio=2000, channel=0, mul=.01):
        self.transpo = Sig(transpo)
        self.note = Notein(poly=10, scale=1, first=0, last=127, channel=channel)
        self.pit = self.note['pitch'] * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=0.001, decay=.2, sustain=1, release=0.1)
        self.dur = []
        self.paths = paths
        self.segments = segments
        self.segdur = segdur
        self.fFreq = SigTo(value=fFreq, time=0.01)
        if self.fFreq.value <= 1:
            self.fFreq.value = (fFreq.value * fRatio) + 50
        self.isOn = 0
        for i in range(len(self.paths)):
            self.dur.append(sndinfo(self.paths[i])[1])

        self.whatTab = 0
        self.tab = [SndTable(initchnls=2), SndTable(initchnls=2)]
        # self.transpo = self.tab[self.whatTab].getRate()

        self.crossFade1 = SigTo(1, time=0.1)
        self.crossFade2 = SigTo(0, time=0.1)

        self.osc1 = OscTrig(self.tab[self.whatTab], self.note['trigon'], self.tab[self.whatTab].getRate()*self.transpo, mul=self.crossFade1)
        self.osc2 = OscTrig(self.tab[self.whatTab], self.note['trigon'], self.tab[self.whatTab].getRate()*self.transpo, mul=self.crossFade2)

        self.fol = Follower([self.osc1,self.osc2], freq=self.pit)
        self.lp = ButLP([self.osc1,self.osc2], freq=self.pit*self.fol).mix(2)
        self.hp = ButHP([self.osc1,self.osc2], freq=self.pit*self.fol).mix(2)
        self.pan = Pan([self.hp,self.lp], outs=2, mul=self.amp)

        self.generate(self.segments, self.segdur)
        self.stop()

    def out(self):
        self.pan.out()
        return self

    def sig(self):
        return self.pan

    def play(self):
        self.fFreq.play()
        self.osc1.play()
        self.osc2.play()
        self.fol.play()
        self.lp.play()
        self.hp.play()
        self.pan.play()

    def stop(self):
        self.fFreq.stop()
        self.osc1.stop()
        self.osc2.stop()
        self.fol.stop()
        self.lp.stop()
        self.hp.stop()
        self.pan.stop()

    def generate(self, segments, segdur):
        if self.whatTab == 0:
            self.crossFade1.value = 1
            self.crossFade2.value = 0
        else:
            self.crossFade2.value = 1
            self.crossFade1.value = 0
        start = random.uniform(0, self.dur[0]-segdur-1)
        stop = start + segdur
        self.tab[self.whatTab].setSound(self.paths[0], start, stop)
        for l in range(segments-1):
            if l >= len(self.dur):
                l = 0
            else:
                start = random.uniform(0, self.dur[l]-segdur-1)
                stop = start + segdur
                self.tab[self.whatTab].append(self.paths[l], 0.5, start, stop)
                l += 1

        newfreq = 1 / (segments * segdur)
        if self.whatTab == 0:
            self.osc1.freq = (newfreq * self.transpo) * self.pit
            self.whatTab = 1
        else:
            self.osc2.freq = (newfreq * self.transpo) * self.pit
            self.whatTab = 0
