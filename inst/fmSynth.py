#!/usr/bin/env python3
# encoding: utf-8
from random import random
from pyo import *

class Synth:
    # Added some arguments that will be controlled with MIDI controllers.
    def __init__(self, transpo=1, hfdamp=5000, lfofreq=0.2, channel=0, mul=1):
        # Transposition factor.
        self.transpo = Sig(transpo)
        # Receive midi notes, convert pitch to Hz and manage 10 voices of polyphony.
        self.note = Notein(poly=10, scale=1, first=0, last=127, channel=channel)

        # Handle pitch and velocity (Notein outputs normalized amplitude (0 -> 1)).
        self.pit = self.note['pitch'] * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=0.001,
                            decay=.1, sustain=.7, release=0.1, mul=.1)

        # Anti-aliased stereo square waves, mixed from 10 streams to 1 stream
        # to avoid channel alternation on new notes.
        self.osc1 = LFO(self.pit, sharp=0.5, type=2, mul=self.amp).mix(1)
        self.osc2 = LFO(self.pit*0.997, sharp=0.5, type=2, mul=self.amp).mix(1)
        self.ind = LinTable([(0,20), (200,10), (1000,2), (8191,1)])
        self.tr = TrigEnv(self.note['trigon'], table=self.ind, dur=4)
        self.f1 = CrossFM(carrier=self.pit, ratio=self.osc1, ind1=self.tr, ind2=self.tr, mul=self.amp * 4).mix(1)
        self.f2 = CrossFM(carrier=self.pit, ratio=self.osc2, ind1=self.tr, ind2=self.tr, mul=self.amp * 4).mix(1)

        # Stereo mix.
        self.mix = Mix([self.f1, self.f2], voices=2)

        # High frequencies damping, use argument `hfdamp` to allow MIDI control.
        self.damp = ButLP(self.mix, freq=hfdamp)

        # Moving notches, use argument `lfofreq` to allow MIDI control.
        self.lfo = Sine(lfofreq, phase=[random(), random()]).range(250, 4000)
        self.notch = ButBR(self.damp, self.lfo, mul=mul)

    def out(self):
        "Sends the synth's signal to the audio output and return the object itself."
        self.notch.out()
        return self

    def sig(self):
        "Returns the synth's signal for future processing."
        return self.notch
