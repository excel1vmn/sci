#!/usr/bin/env python3
# encoding: utf-8
from pyo import *
from inst.instruments import *
import math
import os, sys

# SERVER SETUP
s = Server(sr=48000, nchnls=2, buffersize=1024, duplex=False)
s.setOutputDevice(16)
# s = Server(sr=48000, nchnls=2, buffersize=1024, duplex=False)
# s.setInOutDevice(6)
# LINUX AUDIO/MIDI CONFIG
s.setMidiInputDevice(99)
s.setMidiOutputDevice(99)
pa_list_devices()
pm_list_devices()

s.boot().start()
s.amp = .35

dir = r'/home/charlieb/git/sci'
os.chdir(dir)

# PATHS
items = os.listdir("snds")
snds = []
for names in items:
    if names.endswith(".aif") | names.endswith(".wav"):
        snds.append("snds/" + names)

itemD = os.listdir("sndsDrums")
sndsDrums = []
for names in itemD:
    if names.endswith(".aif") | names.endswith(".wav") | names.endswith(".WAV"):
        sndsDrums.append("sndsDrums/" + names)

itemSB = os.listdir("sndsSB")
sndsSB = []
for names in itemSB:
    if names.endswith(".aif") | names.endswith(".wav"):
        sndsSB.append("sndsSB/" + names)

itemK = os.listdir("kicks")
kicks = []
for names in itemK:
    if names.endswith(".aif") | names.endswith(".wav"):
        kicks.append("kicks/" + names)

# print(snds)
# print(sndsDrums)
# print(sndsSB)
# print(kicks)

# GLOBALS
MUL = []
MULPOW = []
SIGS = []
TRIGS = []
for i in range(16):
    MUL.append(SigTo(0))
    MULPOW.append(Pow(MUL[i], 3))
for i in range (40):
    SIGS.append(SigTo(0))
for i in range(16):
    TRIGS.append(Trig())

# INIT
MUL[0].value = 1
MUL[1].value = 1
MUL[2].value = 1
MUL[3].value = 1
MUL[4].value = 1
MUL[5].value = 1
MUL[6].value = 1
MUL[7].value = 1
SIGS[6].value = 1
# sender = OscDataSend("iffffff", 18032, '/spat/serv')

# CONTROL
def event(status, data1, data2):
    print(status, data1, data2)
    if status == 176:
        value = data2/127
        # VOLUMES
        if data1 == 0:
            MUL[0].setValue(value)
        if data1 == 1:
            MUL[1].setValue(value)
        if data1 == 2:
            MUL[2].setValue(value)
        if data1 == 3:
            MUL[3].setValue(value)
        if data1 == 4:
            MUL[4].setValue(value)
        if data1 == 5:
            MUL[5].setValue(value)
        if data1 == 6:
            MUL[6].setValue(value)
        if data1 == 7:
            MUL[7].setValue(value)
        if data1 == 8:
            SIGS[16].setValue(value)
        if data1 == 9:
            SIGS[17].setValue(value)
        if data1 == 10:
            SIGS[18].setValue(value)
        if data1 == 11:
            SIGS[19].setValue(value)
        if data1 == 12:
            SIGS[20].setValue(value)
        if data1 == 13:
            SIGS[21].setValue(value)
        if data1 == 14:
            SIGS[22].setValue(value)
        if data1 == 15:
            SIGS[23].setValue(value)
        if data1 == 16:
            SIGS[24].setValue(value)
        if data1 == 17:
            SIGS[25].setValue(value)
        if data1 == 18:
            SIGS[26].setValue(value)
        if data1 == 19:
            SIGS[27].setValue(value)
        if data1 == 20:
            SIGS[28].setValue(value)
        if data1 == 21:
            SIGS[29].setValue(value)
        if data1 == 22:
            SIGS[30].setValue(value)
        if data1 == 23:
            SIGS[31].setValue(value)
        if data1 == 24:
            SIGS[32].setValue(value)
        if data1 == 25:
            SIGS[33].setValue(value)
        if data1 == 26:
            SIGS[34].setValue(value)
        if data1 == 27:
            SIGS[35].setValue(value)
        if data1 == 28:
            SIGS[36].setValue(value)
        if data1 == 29:
            SIGS[37].setValue(value)
        if data1 == 30:
            SIGS[38].setValue(value)
        if data1 == 31:
            SIGS[39].setValue(value)

    if status == 178:
        value = data2/127
        if data1 == 10:
            SIGS[7].setValue(value)
        if data1 == 74:
            SIGS[8].setValue(value)
        if data1 == 71:
            SIGS[9].setValue(value)
        if data1 == 76:
            SIGS[10].setValue(value)
        if data1 == 77:
            SIGS[11].setValue(value)
        if data1 == 93:
            SIGS[12].setValue(value)
        if data1 == 73:
            SIGS[13].setValue(value)
        if data1 == 75:
            SIGS[15].setValue(value)
        # EFFECT VOLUMES
        if data1 == 72:
            MUL[8].setValue(value)
        # RESAMPLER MODS
        if data1 == 114:
            SIGS[0].setValue(value)
        if data1 == 18:
            SIGS[1].setValue(value)
        if data1 == 19:
            SIGS[2].setValue(value)
        if data1 == 16:
            SIGS[3].setValue(value)
        if data1 == 17:
            SIGS[4].setValue(value)
        if data1 == 91:
            SIGS[5].setValue(value)
            # GLOBAL LOWPASS
        if data1 == 79:
            SIGS[6].setValue(value)

m = RawMidi(event)

def ctl_scan(ctlnum, midichnl):
    if midichnl == 3:
        # RESAMPLER
        if 20 <= ctlnum <= 31 or 52 <= ctlnum <= 55:
            # if ctlnum == 21:
            #     s.ctlout(20, 127, 3)
            for i in range(len(TRIGS)):
                TRIGS[i].stop()
            if ctlnum == 24: #STEP 5
                TRIGS[0].play()
            if ctlnum == 28: #Step 9
                TRIGS[1].play()
            if ctlnum == 52: #Step 13
                TRIGS[2].play()

a = CtlScan2(ctl_scan, False)

transpo = Bendin(brange=2, scale=1)
# High frequency damping mapped to controller number 1.
hfdamp = Midictl(ctlnumber=1, minscale=500, maxscale=10000, init=5000)
# Frequency of the LFO applied to the speed of the moving notches.
lfofreq = Midictl(ctlnumber=2, minscale=0.1, maxscale=8, init=0.2)

a1 = Synth(transpo, hfdamp, lfofreq, channel=1)

# a2 = Simpler(sndsSB[8], transpo, hfdamp, lfofreq, withloop=True, channel=2) # CONSERVER
a2 = Simpler(sndsSB[6], transpo, hfdamp, lfofreq, withloop=True, channel=2) # CONSERVER BEST
# a2 = Simpler(sndsSB[4], transpo, hfdamp, lfofreq, withloop=True, channel=2) # CONSERVER
# a2 = Simpler(sndsSB, transpo, hfdamp, lfofreq, autoswitch=True, withloop=True, channel=2) # CONSERVER

# a3 = Simpler(snds[2], transpo, hfdamp, lfofreq, withloop=True, autoswitch=True, channel=2)
# a3 = Simpler(snds[2], transpo, hfdamp, lfofreq, withloop=False, channel=2)

a4 = Simpler(snds[1], transpo, hfdamp, lfofreq, withloop=False, channel=2)

a5 = WaveShape(snds[9], transpo, hfdamp, channel=1)

a6 = FreakSynth(transpo, hfdamp, lfofreq, channel=1)

# p1 = Pads(sndsSB[6], transpo, hfdamp, channel=10)
# d1 = Drums(kicks, transpo, hfdamp, channel=10)

r1 = ReSampler(a1.sig() + a2.sig() + a4.sig() + a5.sig() + a6.sig(), TRIGS[0], SIGS[0], SIGS[1], transpo, channel=1)
r2 = ReSampler(a1.sig() + a2.sig() + a4.sig() + a5.sig() + a6.sig() + r1.sig(), TRIGS[1], SIGS[2], SIGS[3], transpo, channel=2)
r3 = ReSampler([a1.sig(), a2.sig(), a4.sig(), a5.sig(), a6.sig(), r1.sig(), r2.sig()], TRIGS[2], SIGS[4], SIGS[5], transpo, channel=10)

# voxyLine = ManglerExpMulti([path7], TAPS, BPS, transp=1.8, segments=4, segdur=0.7, w1=100, w2=0, w3=0, bpoly=4, newyork=1, fFreq=200)

# a6.note.keyboard()

# verb = Freeverb(a1.sig() + a2.sig() + a4.sig() + a5.sig() + a6.sig() + d1.sig() + r1.sig() + r2.sig(), size=[.85,.86], damp=SIGS[6], bal=1, mul=.3).mix(2)
verb = STRev(a1.sig() + a2.sig() + a4.sig() + a5.sig() + a6.sig() + r1.sig() + r2.sig() + r3.sig(), inpos=[0.1, 0.9], cutoff=5000, bal=.7).mix(2)

wsList = [a1.sig(), a2.sig(), a4.sig(), a5.sig(), a6.sig(), r1.sig(), r2.sig(), r3.sig()]
dist = Disto(a1.sig() + a2.sig() + a4.sig() + a5.sig() + a6.sig() + r1.sig() + r2.sig() + r3.sig(), drive=0, slope=wsList[0]).mix(2)

# input1 = Input(chnl=0, mul=.7).mix(2).out()
# input2 = Input(chnl=1, mul=.7).mix(2).out()
# input3 = Input(chnl=2, mul=.7).mix(2).out()
# input4 = Input(chnl=3, mul=.7).mix(2).out()
# input5 = Input(chnl=4, mul=.7).mix(1).out()
# input6 = Input(chnl=5, mul=.7).mix(1).out(1)

mix1 = a1.sig()
mix2 = a2.sig()
mix3 = a4.sig()
mix4 = a5.sig()
mix5 = a6.sig()
mix6 = r1.sig()
mix7 = r2.sig()
mix8 = r3.sig()
mixverb = verb
mixdisto = dist
# mix9 = mass1.sig()
mix1.mul = MULPOW[0]
mix2.mul = MULPOW[1]
mix3.mul = MULPOW[2]
mix4.mul = MULPOW[3]
mix5.mul = MULPOW[4]
mix6.mul = MULPOW[5]
mix7.mul = MULPOW[6]
mix8.mul = MULPOW[7]
mixverb.revtime = MULPOW[8] * 4
mixverb.mul = MULPOW[8]
mixdisto.drive = MULPOW[9] - .01
mixdisto.mul = MULPOW[9]
# mix9.mul=1

mix = Mix(mix1 + mix2 + mix3 + mix4 + mix5 + mix6 + mix7 + mix8 + mixverb + mixdisto, voices=8)
glp = ButLP(mix + verb, freq=Pow(4000 * SIGS[6]))
ghp = ButHP(glp, 30)
# c = Clip(ghp, max=6, mul=.5).mix(2).out()
comp = Compress(ghp, thresh=-30, ratio=4, risetime=.01, falltime=.2, knee=0.5).mix(2).out()

# msg = [0, 0, pi/2.1, 0.5, .2, 0, 0]
# sender.send(msg)
# msg = [1, 0, pi/2.1, 0.5, .2, 0, 0]
# sender.send(msg)
# msg = [2, 0, pi/2, 1, 0, 0, 0]
# sender.send(msg)
# msg = [3, 0, pi/4, 1.5, .3, 0, 0]
# sender.send(msg)
# msg = [4, 0, pi/2, 1, 0, 0, 0]
# sender.send(msg)
# msg = [5, pi*1.55, pi/2.15, 0.5, 0.25, 0, 0]
# sender.send(msg)
# msg = [6, pi/2.25, pi/2.15, 0.5, 0.25, 0, 0]
# sender.send(msg)
# msg = [7, 0, pi/2, 1, 0, 0, 0]
# sender.send(msg)

# sp = Spectrum(mix1 + mix2 + mix3 + mix4 + mix5 + mix6 + mix7 + mix8)

s.gui(locals())
