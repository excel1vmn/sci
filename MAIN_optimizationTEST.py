#!/usr/bin/env python3
# encoding: utf-8
from pyo import *
from inst.instruments import *
from inst.Frottement import *
from inst.Accumulation import *
from inst.Rebond import *
from inst.Oscillation import *
from inst.Flux import *
from inst.Balancement import *
from inst.Flexion import *
from inst.PercussionResonance import *
# from gridHandler import *
import math, os, sys
# import threading
# import keyboard

###############################################
################ SERVER SETUP #################
###############################################
NAME = "MITÉ (Module d'interprétation de techniques d'écriture)"
NUMOUTS = 2
SOUND_CARD = 'EXT'

# SERVER SETUP
if NUMOUTS == 2:
    if SOUND_CARD == 'EXT':
        s = Server(sr=44100, buffersize=1024, nchnls=NUMOUTS, duplex=1, audio='pa')
        s.setInOutDevice(0)
        print('EXT')
    else:
        s = Server(sr=44100, buffersize=1024, nchnls=NUMOUTS, duplex=0, audio='pa')
        s.setOutputDevice(3)
        print('INT')
else:
    s = Server(sr=44100, buffersize=1024, nchnls=NUMOUTS, duplex=1, audio='jack')
    s.setJackAuto()
    s.setInOutDevice(1)
    print('JACK')

# LINUX AUDIO/MIDI CONFIG
def scanMidi():
    s.setMidiInputDevice(99)
    # s.setMidiOutputDevice(99)
    pa_list_devices()
    pm_list_devices()
    print('scanned')

scanMidi()
s.boot().start()
s.amp = 1
###############################################
################ SERVER SETUP #################
###############################################

# PATHS 
dir = r'/home/charlieb/sci'
os.chdir(dir)

items = os.listdir("snds")
snds = []
for names in items:
    if names.endswith(".aif") | names.endswith(".wav"):
        snds.append("snds/" + names)

itemK = os.listdir("drum_kit")
drum_kit = []
for names in itemK:
    if names.endswith(".aif") | names.endswith(".wav"):
        drum_kit.append("drum_kit/" + names)

impulseR = "snds/BatteryBenson.wav"

# print(snds)
# print(drum_kit)

###############################################
############### MIDI PARAMETERS ###############
###############################################
def ctl_scan(ctlnum, midichnl):
    print(ctlnum, midichnl)
    # print(HP.boost.get())
ctlscan = CtlScan2(ctl_scan, False)

def event(status, data1, data2):
    # print(status, data1, data2)
    if data1 == 105 and data2 == 127:
        scanMidi()
raw = RawMidi(event)

#--- LAUNCH CONTROL XL ---#
MULPOW = Pow(Midictl(ctlnumber=[77,78,79,80,81,82,83,84], init=0, channel=6), 5)
SIGSNB = Midictl(ctlnumber=[13,14,15,16,17,18,19,20,
                            29,30,31,32,33,34,35,36,
                            49,50,51,52,53,54,55,56],
                      init=[ 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0], channel=6)

transpo = Bendin(brange=2, scale=1, channel=1)
hfdamp = Midictl(ctlnumber=49, minscale=20, maxscale=18000, init=18000, channel=3)
lfdamp = Midictl(ctlnumber=48, minscale=20, maxscale=18000, init=20, channel=3)

#--- LAUNCHPAD MINI ---#
# Toggles certain parameters of ReSampler class instruments 
trigs = Midictl(ctlnumber=[0,1,2,3,4,5,6,7], channel=3)
toggles1 = Midictl(ctlnumber=[ 8,16,24], channel=3)
toggles2 = Midictl(ctlnumber=[ 9,17,25], channel=3)
toggles3 = Midictl(ctlnumber=[10,18,26], channel=3)
toggles4 = Midictl(ctlnumber=[11,19,27], channel=3)
toggles5 = Midictl(ctlnumber=[12,20,28], channel=3)
toggles6 = Midictl(ctlnumber=[13,21,29], channel=3)
toggles7 = Midictl(ctlnumber=[14,22,30], channel=3)
toggles8 = Midictl(ctlnumber=[15,23,31], channel=3)
toggles_row1 = Midictl(ctlnumber=[32,33,34,35,36,37,38,39], channel=3)
toggles_row2 = Midictl(ctlnumber=[40,41,42,43,44,45,46,47], channel=3)
#--- LAUNCHPAD MINI ---#

n1 = Notein(poly=10, scale=0, first=0, last=127, channel=1)
n2 = Notein(poly=10, scale=0, first=0, last=127, channel=2)
n10 = Notein(poly=10, scale=0, first=0, last=127, channel=10)
### Sert à manipuler les gestes musicaux / techniques d'écriture ### 
n0 = Notein(poly=4, scale=0, first=0, last=127, channel=0)
###############################################
############### MIDI PARAMETERS ###############
###############################################

pre_output = Mixer(outs=NUMOUTS, chnls=1)

a2 = FreakSynth(n2, trigs[1], toggles2, [SIGSNB[1],SIGSNB[9]], transpo, hfdamp=hfdamp, audioIN=Mix(pre_output, NUMOUTS), mul=MULPOW[1])

# r1 = ReSampler(3, Mix(pre_output, NUMOUTS), trigs[4], toggles5, [SIGSNB[4],SIGSNB[12]], transpo, hfdamp=hfdamp, audioIN=Mix(pre_output, NUMOUTS), mul=MULPOW[4])


prefx = Sig([a2.sig()], mul=toggles_row2)

fr = Frottement(Mix([prefx]), n0, SIGSNB[16], freq=[3,1.15,.5,.7,2.5,6,.04,15], outs=NUMOUTS)
ac = Accumulation(Mix([prefx]), n0, SIGSNB[17], delay=.025, outs=NUMOUTS)
re = Rebond(Mix([prefx]), n0, SIGSNB[18], base_interval=.21, outs=NUMOUTS)
oc = Oscillation(Mix([prefx]), n0, SIGSNB[19], freq=50, outs=NUMOUTS)
fl = Flux(Mix([prefx]), n0, SIGSNB[20], freq=50, outs=NUMOUTS)
ba = Balancement(Mix([prefx]), n0, SIGSNB[21], freq=50, outs=NUMOUTS)
fe = Flexion(Mix([prefx]), n0, SIGSNB[22], freq=50, outs=NUMOUTS)
pr = PercussionResonance(Mix([prefx]), n0, SIGSNB[23], ir=impulseR, freq=100, outs=NUMOUTS)

clean_sig = Compress(Mix([a2.sig()], NUMOUTS), thresh=-12, ratio=4, risetime=.01, falltime=.2, knee=.5)

COMP = Compress(Mix([fr,ac,oc,fl,ba,fe,pr,clean_sig], NUMOUTS), thresh=-12, ratio=4, knee=.5)
downmix = Mix(COMP, voices=NUMOUTS, mul=.3).out()

pre_output.addInput(0, downmix)
pre_output.setAmp(0, 0, 1)
pre_output.setAmp(0, 1, 1)

s.gui(locals())
