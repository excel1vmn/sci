#!/usr/bin/env python3
# encoding: utf-8
from pyo import *
from inst.instruments import *
import math
import os, sys

# SERVER SETUP
s = Server(sr=44100, nchnls=2, buffersize=1024, duplex=False)
s.setOutputDevice(16)
# s = Server(sr=48000, nchnls=2, buffersize=1024, duplex=False)
# s.setInOutDevice(6)
# LINUX AUDIO/MIDI CONFIG
s.setMidiInputDevice(99)
s.setMidiOutputDevice(99)
pa_list_devices()
pm_list_devices()

s.boot().start()
s.amp = .15

dir = r'/home/charlieb/sci'
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

# GLOBALS
# NOTES = Notein(poly=1, scale=0, first=0, last=127)
MUL = []
MULPOW = []
SIGS = []
TRIGS = []
for i in range(16):
    MUL.append(SigTo(0))
    MULPOW.append(Pow(MUL[i], 3))
for i in range(40):
    SIGS.append(SigTo(0))
for i in range(16):
    TRIGS.append(Trig())

# INIT
MUL[0].value = 0
MUL[1].value = 0
MUL[2].value = 0
MUL[3].value = 0
MUL[4].value = 0
MUL[5].value = 0
MUL[6].value = 0
MUL[7].value = 0
SIGS[6].value = 1
# sender = OscDataSend("iffffff", 18032, '/spat/serv')

# CONTROL
def event(status, data1, data2):
    print(status, data1, data2)
    if status == 176:
        value = data2/100
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
            SIGS[8].setValue(value)
        if data1 == 9:
            SIGS[9].setValue(value)
        if data1 == 10:
            SIGS[10].setValue(value)
        if data1 == 11:
            SIGS[11].setValue(value)
        if data1 == 12:
            SIGS[12].setValue(value)
        if data1 == 13:
            SIGS[13].setValue(value)
        if data1 == 14:
            SIGS[14].setValue(value)
        if data1 == 15:
            SIGS[15].setValue(value)
        if data1 == 16:
            SIGS[16].setValue(value)
        if data1 == 17:
            SIGS[17].setValue(value)
        if data1 == 18:
            SIGS[18].setValue(value)
        if data1 == 19:
            SIGS[19].setValue(value)
        if data1 == 20:
            SIGS[20].setValue(value)
        if data1 == 21:
            SIGS[21].setValue(value)
        if data1 == 22:
            SIGS[22].setValue(value)
        if data1 == 23:
            SIGS[23].setValue(value)
        if data1 == 24:
            SIGS[24].setValue(value)
        if data1 == 25:
            SIGS[25].setValue(value)
        if data1 == 26:
            SIGS[26].setValue(value)
        if data1 == 27:
            SIGS[27].setValue(value)
        if data1 == 28:
            SIGS[28].setValue(value)
        if data1 == 29:
            SIGS[29].setValue(value)
        if data1 == 30:
            SIGS[30].setValue(value)
        if data1 == 31:
            SIGS[31].setValue(value)

    if status == 178:
        value = data2/127
        if data1 == 10:
            MUL[8].setValue(value)
        if data1 == 74:
            MUL[9].setValue(value)
        if data1 == 71:
            MUL[10].setValue(value)
        if data1 == 76:
            MUL[11].setValue(value)
        if data1 == 77:
            MUL[12].setValue(value)
        if data1 == 93:
            MUL[13].setValue(value)
        if data1 == 73:
            MUL[14].setValue(value)
        if data1 == 75:
            MUL[15].setValue(value)
        # EFFECT VOLUMES
        if data1 == 114:
            SIGS[32].setValue(value)
        if data1 == 18:
            SIGS[33].setValue(value)
        if data1 == 19:
            SIGS[34].setValue(value)
        if data1 == 16:
            SIGS[35].setValue(value)
        if data1 == 17:
            SIGS[36].setValue(value)
        if data1 == 91:
            SIGS[37].setValue(value)
            # GLOBAL LOWPASS
        if data1 == 79:
            SIGS[38].setValue(value)
        if data1 == 72:
            SIGS[39].setValue(value)
m = RawMidi(event)

def ctl_scan(ctlnum, midichnl):
    if midichnl == 3:
        # RESAMPLER
        if 20 <= ctlnum <= 31 or 52 <= ctlnum <= 55:
            # if ctlnum == 21:
            #     s.ctlout(20, 127, 3)
            for i in range(len(TRIGS)):
                TRIGS[i].stop()
            if ctlnum == 20: #STEP 1
                TRIGS[0].play()
            if ctlnum == 24: #STEP 5
                TRIGS[1].play()
            if ctlnum == 28: #Step 9
                TRIGS[2].play()
            if ctlnum == 52: #Step 13
                TRIGS[3].play()
a = CtlScan2(ctl_scan, False)

transpo = Bendin(brange=2, scale=1)
# High frequency damping mapped to controller number 1.
hfdamp = Midictl(ctlnumber=[0,1,2,3,4,5,6,7], minscale=100, maxscale=10000, init=5000, channel=1)
# hfdamp.ctrl()
# Frequency of the LFO applied to the speed of the moving notches.
lfofreq = Midictl(ctlnumber=[0,1,2,3,4,5,6,7], minscale=0.1, maxscale=8, init=0.2, channel=1)

a1 = Synth(transpo, hfdamp, lfofreq, SIGS[8], SIGS[16], SIGS[24], channel=1, mul=MULPOW[0]).out()

a2 = FreakSynth(transpo, hfdamp, lfofreq, SIGS[9], SIGS[17], SIGS[25], channel=1, mul=MULPOW[1]).out()

a3 = Simpler(snds[1], transpo, hfdamp, lfofreq, SIGS[10], SIGS[18], SIGS[26], channel=2, mul=MULPOW[2]).out()

a4 = WaveShape(snds[9], transpo, hfdamp, lfofreq, SIGS[11], SIGS[19], SIGS[27], channel=2, mul=MULPOW[3]).out() #Cause underrun

# p1 = Pads(sndsSB[6], transpo, hfdamp, channel=10).out()
# d1 = Drums(kicks, transpo, hfdamp, channel=10).out()

#Cause underrun
r1 = ReSampler(a1.sig() + a2.sig() + a3.sig() + a4.sig(), TRIGS[0], transpo, SIGS[12], SIGS[20], SIGS[28], channel=1, mul=MULPOW[4]).out()
r2 = ReSampler(a1.sig() + a2.sig() + a3.sig() + a4.sig() + r1.sig(), TRIGS[1], transpo, SIGS[13], SIGS[21], SIGS[29], channel=2, mul=MULPOW[5]).out()
r3 = ReSampler([a1.sig(), a2.sig(), a3.sig(), a4.sig(), r1.sig(), r2.sig()], TRIGS[2], transpo, SIGS[14], SIGS[22], SIGS[30], channel=1, mul=MULPOW[6]).out()
r4 = ReSampler([a1.sig(), a2.sig(), a3.sig(), a4.sig(), r1.sig(), r2.sig(), r3.sig()], TRIGS[3], transpo, SIGS[15], SIGS[23], SIGS[31], channel=2, mul=MULPOW[7]).out()
#Cause underrun

fx = EffectBox([a1.sig(), a2.sig(), a3.sig(), a4.sig(), r1.sig(), r2.sig(), r3.sig(), r4.sig()], SIGS[32], channel=10, mul=4).out()

a1.note.keyboard()
# a2.note.keyboard()
# a3.note.keyboard()
# a4.note.keyboard()

s.gui(locals())
