#!/usr/bin/env python3
# encoding: utf-8
from pyo import *
from inst.instruments import *
from inst.GestesMus import *
from inst.RingMod import *
import math
import os, sys

# SERVER SETUP
# s = Server(sr=48000)
# s.setOutputDevice(16)
# s = Server(sr=48000, audio='jack')
# s.setOutputDevice(17)
s = Server(sr=48000, duplex=0)
s.setInOutDevice(6)
# s.setOutputDevice(6)
# LINUX AUDIO/MIDI CONFIG
s.setMidiInputDevice(99)
# s.setMidiOutputDevice(99)
pa_list_devices()
# pm_list_devices()

s.boot().start()
s.amp = .5

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

def ctl_scan(ctlnum, midichnl):
    if midichnl == 3:
        # RESAMPLER
        # if 20 <= ctlnum <= 31 or 52 <= ctlnum <= 55 or 4 <= ctlnum <= 7:
            # if ctlnum == 21:
            #     s.ctlout(20, 127, 3)
            # For beatstep pro 20, 24, 28, 52
        if ctlnum == 4: #STEP 1
            r1.rec()
        if ctlnum == 5: #STEP 5
            r2.rec()
        if ctlnum == 6: #Step 9
            r3.rec()
        if ctlnum == 7: #Step 13
            r4.rec()
                
a = CtlScan2(ctl_scan, False)

# MULPOW = Pow(Midictl(ctlnumber=[0,1,2,3,4,5,6,7], init=0, channel=1), 3)
# SIGSNB = Midictl(ctlnumber=[8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31], init=0, channel=1)

MULPOW = Pow(Midictl(ctlnumber=[77,78,79,80,81,82,83,84], init=0, channel=1), 3)
SIGSNB = Midictl(ctlnumber=[13,14,15,16,17,18,19,20,29,30,31,32,33,34,35,36,49,50,51,52,53,54,55,56], init=0, channel=1)

transpo = Bendin(brange=2, scale=1, channel=1)
# High frequency damping mapped to controller number 1.
hfdamp = Midictl(ctlnumber=[27,52], minscale=50, maxscale=7000, init=7000, channel=1)
# Frequency of the LFO applied to the speed of the moving notches.
lfofreq = Midictl(ctlnumber=[28,53], minscale=0.1, maxscale=20, init=0.2, channel=1)
# Toggles certain parameters of ReSampler class instruments 
toggles1 = Midictl(ctlnumber=[8,16,24], channel=3)
toggles2 = Midictl(ctlnumber=[9,17,25], channel=3)
toggles3 = Midictl(ctlnumber=[10,18,26], channel=3)
toggles4 = Midictl(ctlnumber=[11,19,27], channel=3)
toggles5 = Midictl(ctlnumber=[12,20,28], channel=3)
toggles6 = Midictl(ctlnumber=[13,21,29], channel=3)
toggles7 = Midictl(ctlnumber=[14,22,30], channel=3)
toggles8 = Midictl(ctlnumber=[15,23,31], channel=3)

n1 = Notein(poly=10, scale=0, first=0, last=127, channel=1)
# n2 = Notein(poly=10, scale=0, first=0, last=127, channel=2)
# n3 = Notein(poly=10, scale=0, first=0, last=127, channel=3)
n10 = Notein(poly=16, scale=0, first=0, last=127, channel=10)

# d1 = Drums(kicks, n10, transpo, hfdamp, mul=1).out()

a1 = Synth(n1, transpo, hfdamp, lfofreq, [SIGSNB[0],SIGSNB[8]], mul=MULPOW[0])
a2 = FreakSynth(n1, transpo, hfdamp, lfofreq, [SIGSNB[1],SIGSNB[9]], mul=MULPOW[1])
a3 = Simpler(n1, snds[6], transpo, hfdamp, lfofreq, [SIGSNB[2],SIGSNB[10]], mul=MULPOW[2])
a4 = WaveShape(n1, snds[9], transpo, hfdamp, lfofreq, [SIGSNB[3],SIGSNB[11]], mul=MULPOW[3])

#Cause underrun
r1 = ReSampler(n1, toggles5, [SIGSNB[4],SIGSNB[12]], [a1.sig(),a2.sig(),a3.sig(),a4.sig()], transpo, hfdamp, mul=MULPOW[4])
r2 = ReSampler(n1, toggles6, [SIGSNB[5],SIGSNB[13]], [a1.sig(),a2.sig(),a3.sig(),a4.sig(),r1.sig()], transpo, hfdamp, mul=MULPOW[5])
r3 = ReSampler(n1, toggles7, [SIGSNB[6],SIGSNB[14]], [a1.sig(),a2.sig(),a3.sig(),a4.sig(),r1.sig(),r2.sig()], transpo, hfdamp, mul=MULPOW[6])
r4 = ReSampler(n1, toggles8, [SIGSNB[7],SIGSNB[15]], [a1.sig(),a2.sig(),a3.sig(),a4.sig(),r1.sig(),r2.sig(),r3.sig()], transpo, hfdamp, mul=MULPOW[7])
#Cause underrun

fx = EffectBox([a1.sig(), a2.sig(), a3.sig(), a4.sig(), r1.sig(), r2.sig(), r3.sig(), r4.sig()], [SIGSNB[16],SIGSNB[17],SIGSNB[18]], channel=10, mul=2)

gm = GestesMus(Mix([a1.sig(), a2.sig(), a3.sig(), a4.sig(), r1.sig(), r2.sig(), r3.sig(), r4.sig(), fx.sig()], voices=2), [SIGSNB[20],SIGSNB[21],SIGSNB[22],SIGSNB[23]]).out()

# rm = RingMod(Mix([a1.sig(), a2.sig(), a3.sig(), a4.sig(), r1.sigw(), r2.sig(), r3.sig(), r4.sig(), fx.sig()], voices=2)).out()

# sender = OscDataSend("iffffff", 18032, '/spat/serv')

# if s.audio == 'jack':
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
