#!/usr/bin/env python3
# encoding: utf-8
from pyo import *
from inst.instruments import *
import math
import os, sys

# SERVER SETUP
s = Server(sr=48000, nchnls=2, buffersize=1024, duplex=False)
s.setOutputDevice(16)
# s = Server(sr=48000, nchnls=2, buffersize=1024, duplex=False, audio='pa')
# s.setInOutDevice(6)
# LINUX AUDIO/MIDI CONFIG
s.setMidiInputDevice(99)
s.setMidiOutputDevice(99)
# pa_list_devices()
pm_list_devices()

s.boot().start()
s.amp = .1

dir = r'/home/charlieb/sci'
os.chdir(dir)

# PATHS 
items = os.listdir("snds")  
snds = []
for names in items:
    if names.endswith(".aif") | names.endswith(".wav"):
        snds.append("snds/" + names)

# itemD = os.listdir("sndsDrums")
# sndsDrums = []
# for names in itemD:
#     if names.endswith(".aif") | names.endswith(".wav") | names.endswith(".WAV"):
#         sndsDrums.append("sndsDrums/" + names)

# itemSB = os.listdir("sndsSB")
# sndsSB = []
# for names in itemSB:
#     if names.endswith(".aif") | names.endswith(".wav"):
#         sndsSB.append("sndsSB/" + names)

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
# NOTES = Notein(poly=1, scale=0, first=0, last=127)
MUL = []
MULPOW = []
SIGSNB = []
SIGSAR = []
TRIGS = []
for i in range(8):
    MUL.append(SigTo(0))
    MULPOW.append(Pow(MUL[i], 3))
for i in range(24):
    SIGSNB.append(SigTo(0))
for i in range(16):
    SIGSAR.append(SigTo(0))
for i in range(16):
    TRIGS.append(Trig())

# INIT
MUL[0].value = 1
MUL[1].value = 0
MUL[2].value = 0
MUL[3].value = 0
MUL[4].value = 1
MUL[5].value = 0
MUL[6].value = 0
MUL[7].value = 0

sender = OscDataSend("iffffff", 18032, '/spat/serv')

# CONTROL
def event(status, data1, data2):
    # print(status, data1, data2)
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
            SIGSNB[0].setValue(value)
        if data1 == 9:
            SIGSNB[1].setValue(value)
        if data1 == 10:
            SIGSNB[2].setValue(value)
        if data1 == 11:
            SIGSNB[3].setValue(value)
        if data1 == 12:
            SIGSNB[4].setValue(value)
        if data1 == 13:
            SIGSNB[5].setValue(value)
        if data1 == 14:
            SIGSNB[6].setValue(value)
        if data1 == 15:
            SIGSNB[7].setValue(value)
        if data1 == 16:
            SIGSNB[8].setValue(value)
        if data1 == 17:
            SIGSNB[9].setValue(value)
        if data1 == 18:
            SIGSNB[10].setValue(value)
        if data1 == 19:
            SIGSNB[11].setValue(value)
        if data1 == 20:
            SIGSNB[12].setValue(value)
        if data1 == 21:
            SIGSNB[13].setValue(value)
        if data1 == 22:
            SIGSNB[14].setValue(value)
        if data1 == 23:
            SIGSNB[15].setValue(value)
        if data1 == 24:
            SIGSNB[16].setValue(value)
        if data1 == 25:
            SIGSNB[17].setValue(value)
        if data1 == 26:
            SIGSNB[18].setValue(value)
        if data1 == 27:
            SIGSNB[19].setValue(value)
        if data1 == 28:
            SIGSNB[20].setValue(value)
        if data1 == 29:
            SIGSNB[21].setValue(value)
        if data1 == 30:
            SIGSNB[22].setValue(value)
        if data1 == 31:
            SIGSNB[23].setValue(value)

    if status == 178:
        value = data2/127
        if data1 == 10:
            SIGSAR[0].setValue(value)
        if data1 == 74:
            SIGSAR[1].setValue(value)
        if data1 == 71:
            SIGSAR[2].setValue(value)
        if data1 == 76:
            SIGSAR[3].setValue(value)
        if data1 == 77:
            SIGSAR[4].setValue(value)
        if data1 == 93:
            SIGSAR[5].setValue(value)
        if data1 == 73:
            SIGSAR[6].setValue(value)
        if data1 == 75:
            SIGSAR[7].setValue(value)
        # EFFECT VOLUMES
        if data1 == 114:
            SIGSAR[8].setValue(value)
        if data1 == 18:
            SIGSAR[9].setValue(value)
        if data1 == 19:
            SIGSAR[10].setValue(value)
        if data1 == 16:
            SIGSAR[11].setValue(value)
        if data1 == 17:
            SIGSAR[12].setValue(value)
        if data1 == 91:
            SIGSAR[13].setValue(value)
            # GLOBAL LOWPASS
        if data1 == 79:
            SIGSAR[14].setValue(value)
        if data1 == 72:
            SIGSAR[15].setValue(value)
m = RawMidi(event)

def ctl_scan(ctlnum, midichnl):
    if midichnl == 3:
        # RESAMPLER
        if 20 <= ctlnum <= 31 or 52 <= ctlnum <= 55 or 4 <= ctlnum <= 7:
            # if ctlnum == 21:
            #     s.ctlout(20, 127, 3)
            for i in range(len(TRIGS)):
                TRIGS[i].stop()
            if ctlnum == 20 or 4: #STEP 1
                TRIGS[0].play()
            if ctlnum == 24 or 5: #STEP 5
                TRIGS[1].play()
            if ctlnum == 28 or 6: #Step 9
                TRIGS[2].play()
            if ctlnum == 52 or 7: #Step 13
                TRIGS[3].play()
                
a = CtlScan2(ctl_scan, True)

transpo = Bendin(brange=2, scale=1)
# High frequency damping mapped to controller number 1.
hfdamp = Midictl(ctlnumber=[1], minscale=100, maxscale=10000, init=5000, channel=1)
# Frequency of the LFO applied to the speed of the moving notches.
lfofreq = Midictl(ctlnumber=[1], minscale=0.1, maxscale=8, init=0.2, channel=1)

#TEST
# m1 = Metro().play()
# m1.ctrl()
n1 = Notein(poly=10, scale=0, first=0, last=127, channel=1)
n2 = Notein(poly=10, scale=0, first=0, last=127, channel=2)
n3 = Notein(poly=10, scale=0, first=0, last=127, channel=3)
n10 = Notein(poly=16, scale=0, first=0, last=127, channel=10)
a1 = Synth(n1, transpo, hfdamp, lfofreq, SIGSNB[0], SIGSNB[8], SIGSNB[16], channel=1, mul=MULPOW[0]).out()

a2 = FreakSynth(n1, transpo, hfdamp, lfofreq, SIGSNB[1], SIGSNB[9], SIGSNB[17], channel=1, mul=MULPOW[1]).out()

a3 = Simpler(n2, snds[3], transpo, hfdamp, lfofreq, SIGSNB[2], SIGSNB[10], SIGSNB[18], channel=2, mul=MULPOW[2]).out()

a4 = WaveShape(n2, snds[9], transpo, hfdamp, lfofreq, SIGSNB[3], SIGSNB[11], SIGSNB[19], channel=2, mul=MULPOW[3]).out()

# p1 = Pads(sndsSB[6], transpo, hfdamp, channel=10).out()
# d1 = Drums(kicks, transpo, hfdamp, channel=10, mul=1).out()

# #Cause underrun
r1 = ReSampler(n1, a1.sig()+a2.sig()+a3.sig()+a4.sig(), TRIGS[0], transpo, SIGSNB[4], SIGSNB[12], SIGSNB[20], channel=1, mul=MULPOW[4]).out()
r2 = ReSampler(n2, a1.sig()+a2.sig()+a3.sig()+a4.sig()+r1.sig(), TRIGS[1], transpo, SIGSNB[5], SIGSNB[13], SIGSNB[21], channel=2, mul=MULPOW[5]).out()
r3 = ReSampler(n1, a1.sig()+a2.sig()+a3.sig()+a4.sig()+r1.sig()+r2.sig(), TRIGS[2], transpo, SIGSNB[6], SIGSNB[14], SIGSNB[22], channel=1, mul=MULPOW[6]).out()
r4 = ReSampler(n2, a1.sig()+a2.sig()+a3.sig()+a4.sig()+r1.sig()+r2.sig()+r3.sig(), TRIGS[3], transpo, SIGSNB[7], SIGSNB[15], SIGSNB[23], channel=2, mul=MULPOW[7]).out()
# #Cause underrun

fx = EffectBox(a1.sig()+a2.sig()+a3.sig()+a4.sig()+r1.sig()+r2.sig()+r3.sig()+r4.sig(), SIGSAR, channel=10, mul=2).out()

# a1.note.keyboard()
# a2.note.keyboard()
# a3.note.keyboard()
# a4.note.keyboard()

# msg = [0, 0, pi/2.1, 0.5, .2, 0, 0]
# sender.send(msg)
# msg = [1, 0, pi/2, 1, 0, 0, 0]
# sender.send(msg)
# msg = [2, 0, pi/4, 1.5, .3, 0, 0]
# sender.send(msg)
# msg = [3, 0, pi/2, 1, 0, 0, 0]
# sender.send(msg)
# msg = [4, pi*1.55, pi/2.15, 0.5, 0.25, 0, 0]
# sender.send(msg)
# msg = [5, pi/2.25, pi/2.15, 0.5, 0.25, 0, 0]
# sender.send(msg)
# msg = [6, 0, pi/2, 1, 0, 0, 0]
# sender.send(msg)

s.gui(locals())
