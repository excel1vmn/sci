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
# from inst.RingMod import *
# from gridHandler import *
import math
import os, sys
# import threading
# import keyboard

NAME = "MITÉ (Module d'interprétation de techniques d'écriture)"
NUM_OUTS = 2
SOUND_CARD = 'EXT' 

# SERVER SETUP
if NUM_OUTS == 2:
    if SOUND_CARD == 'EXT':
        s = Server(sr=48000, buffersize=512, nchnls=NUM_OUTS, duplex=0, audio='pa')
        s.setInOutDevice(0)
        print('EXT')
    else:
        s = Server(sr=48000, buffersize=1024, nchnls=NUM_OUTS, duplex=0, audio='pa')
        s.setOutputDevice(2)
        print('INT')
else:
    s = Server(sr=48000, buffersize=1024, nchnls=NUM_OUTS, duplex=0, audio='pa')
    s.setInOutDevice(0)
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

dir = r'/home/charlieb/sci'
os.chdir(dir)

# PATHS 
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

print(snds)
print(drum_kit)

### MIDI PARAMETERS ###
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
# SIGTRIG = Midictl(ctlnumber=[41,42,43,44,57,58,59,60,
#                              73,74,75,76,89,90,91,92],
#                       init=[ 0, 0, 0, 0, 0, 0, 0, 0,
#                              0, 0, 0, 0, 0, 0, 0, 0,], channel=6)
#--- LAUNCH CONTROL XL ---#

# check = Change(SIGTRIG)
# p=Print(SIGTRIG, 1)

#--- NAKED BOARDS ---#
# MULPOW = Pow(Midictl(ctlnumber=[0,1,2,3,4,5,6,7], init=0, channel=1), 5)
# SIGSNB = Midictl(ctlnumber=[ 8, 9,10,11,12,13,14,15,
#                             16,17,18,19,20,21,22,23,
#                             24,25,26,27,28,29,30,31], 
#                       init=[ 0, 0, 0, 0, 0, 0, 0 ,0,
#                              0, 0, 0, 0, 0, 0, 0 ,0,
#                              0, 0, 0, 0, 0, 0, 0, 0], channel=1)
#--- NAKED BOARDS ---#

transpo = Bendin(brange=2, scale=1, channel=1)
# High frequency damping mapped to controller number 1.
hfdamp = Midictl(ctlnumber=49, minscale=20, maxscale=10000, init=10000, channel=3)
lfdamp = Midictl(ctlnumber=48, minscale=-24, maxscale=24, init=0, channel=3)
# Frequency of the LFO applied to the speed of the moving notches.
# lfofreq = Midictl(ctlnumber=13, minscale=0.1, maxscale=20, init=0.2, channel=6)
# Toggles certain parameters of ReSampler class instruments 
trigs = Midictl(ctlnumber=[0,1,2,3,4,5,6,7], channel=3)
toggles1 = Midictl(ctlnumber=[ 8,16], channel=3)
toggles2 = Midictl(ctlnumber=[ 9,17], channel=3)
toggles3 = Midictl(ctlnumber=[10,18], channel=3)
toggles4 = Midictl(ctlnumber=[11,19], channel=3)
toggles5 = Midictl(ctlnumber=[12,20], channel=3)
toggles6 = Midictl(ctlnumber=[13,21], channel=3)
toggles7 = Midictl(ctlnumber=[14,22], channel=3)
toggles8 = Midictl(ctlnumber=[15,23], channel=3)
fxtoggles = Midictl(ctlnumber=[24,25,26,27,28,29,30,31], channel=3)
gestetoggles = Midictl(ctlnumber=[32,33,34,35,36,37,38,39,
                                  40,41,42,43,44,45,46,47], channel=3)

n1 = Notein(poly=10, scale=0, first=0, last=127, channel=1)
n2 = Notein(poly=10, scale=0, first=0, last=127, channel=2)
n3 = Notein(poly=10, scale=0, first=0, last=127, channel=3)
n4 = Notein(poly=10, scale=0, first=0, last=127, channel=4)
n10 = Notein(poly=24, scale=0, first=0, last=127, channel=10)
### Sert à manipuler les gestes musicaux / techniques d'écriture ### 
n0 = Notein(poly=4, scale=0, first=0, last=127, channel=0)
### MIDI PARAMETERS ###


### EXTERNAL INPUT ###
# input1 = Input(chnl=0, mul=.7).mix(2)
# input2 = Input(chnl=1, mul=.7).mix(2)
### EXTERNAL INPUT ###

pre_output = Mixer(outs=NUM_OUTS, chnls=1)

drums = Drums(n10, drum_kit, cs=gestetoggles, transpo=transpo)

a1 = Synth(n2, trigs[0], toggles1, [SIGSNB[0],SIGSNB[8]], transpo, hfdamp=hfdamp, audioIN=drums.sig(), mul=MULPOW[0])
a2 = FreakSynth(n2, trigs[1], toggles2, [SIGSNB[1],SIGSNB[9]], transpo, hfdamp=hfdamp, audioIN=drums.sig(), mul=MULPOW[1])
a3 = Simpler(n2, snds[1], trigs[2], toggles3, [SIGSNB[2],SIGSNB[10]], transpo, hfdamp=hfdamp, autoswitch=False, withloop=False, audioIN=drums.sig(), mul=MULPOW[2])
a4 = WaveShape(n2, snds[9], trigs[3], toggles4, [SIGSNB[3],SIGSNB[11]], transpo, hfdamp=hfdamp, audioIN=drums.sig(), mul=MULPOW[3])

### ADD : 1 autre bouton de changement de style de jeu
### Prend le signal traité avant la sorti ###
r1 = ReSampler(n3, Mix(pre_output, NUM_OUTS), trigs[4], toggles5, [SIGSNB[4],SIGSNB[12]], transpo, hfdamp=hfdamp, audioIN=drums.sig(), mul=MULPOW[4])
r2 = ReSampler(n3, Mix(pre_output, NUM_OUTS), trigs[5], toggles6, [SIGSNB[5],SIGSNB[13]], transpo, hfdamp=hfdamp, audioIN=drums.sig(), mul=MULPOW[5])
r3 = ReSampler(n3, Mix(pre_output, NUM_OUTS), trigs[6], toggles7, [SIGSNB[6],SIGSNB[14]], transpo, hfdamp=hfdamp, audioIN=drums.sig(), mul=MULPOW[6])
r4 = ReSampler(n3, Mix(pre_output, NUM_OUTS), trigs[7], toggles8, [SIGSNB[7],SIGSNB[15]], transpo, hfdamp=hfdamp, audioIN=drums.sig(), mul=MULPOW[7])

prefx = Mix([a1.sig(),a2.sig(),a3.sig(),a4.sig(),r1.sig(),r2.sig(),r3.sig(),r4.sig(),drums.sig()], voices=NUM_OUTS)

fader = Sig([1,1,1,1,1,1,1,1])
fader.ctrl()

### TECHNIQUE D'ÉCRITURE ###
fr = Frottement(Mix(prefx), n0, SIGSNB[16], freq=[3,1.15,.5,.7,2.5,6,.04], outs=NUM_OUTS, mul=fader[0])
### FIX : corriger le fonctionnement du traitement dans instruments
ac = Accumulation(Mix(prefx), n0, SIGSNB[17], delay=.005, outs=NUM_OUTS, mul=fader[1])
### ADD : ajout d'effet stylistique sur rebond
re = Rebond(Mix(prefx), n0, SIGSNB[18], base_interval=.3, outs=NUM_OUTS, mul=fader[2])

os = Oscillation(Mix(prefx), n0, SIGSNB[19], freq=50, outs=NUM_OUTS, mul=fader[3])

fl = Flux(Mix(prefx), n0, SIGSNB[20], freq=50, outs=NUM_OUTS, mul=fader[4])

ba = Balancement(Mix(prefx), n0, SIGSNB[21], freq=50, outs=NUM_OUTS, mul=fader[5])

fe = Flexion(Mix(prefx), n0, SIGSNB[22], freq=50, outs=NUM_OUTS, mul=fader[6])

pr = PercussionResonance(Mix(prefx), n0, SIGSNB[23], ir=impulseR, freq=MToF(n0['pitch']), outs=NUM_OUTS, mul=fader[7])
### TECHNIQUE D'ÉCRITURE ###

### SIDE CHAIN ###
inputFollow = Follower(Mix([fr,ac,re,os,fl,ba,fe,pr], NUM_OUTS), freq=20)
talk = inputFollow > .05
followAmp = Port(talk, risetime=.005, falltime=.001)
ampscl = Scale(followAmp, outmin=1, outmax=.05)

clean_sig = Compress(Mix([a1.sig(),a2.sig(),a3.sig(),a4.sig(),r1.sig(),r2.sig(),r3.sig(),r4.sig(),drums.sig()], voices=NUM_OUTS), thresh=-12, ratio=4, risetime=.01, falltime=.2, knee=.5, mul=ampscl)

### les techniques d'écritures influence-t-elle le jeu
## faire une compairson A/B avec technique / sans technique
### ajouter des jams
# LP = ButLP(Mix([fr,ac,re,os,fl,ba,fe,clean_sig], NUM_OUTS), freq=Pow((slider*5000)+20, 3))
HP = EQ(Mix([fr,ac,re,os,fl,ba,fe,pr,clean_sig],2), freq=500, q=.1, boost=lfdamp, type=1)
COMP = Compress(HP, thresh=-12, ratio=4, knee=.5)
downmix = Mix(COMP, voices=NUM_OUTS, mul=.3).out()
pre_output.addInput(0, downmix)
pre_output.setAmp(0, 0, 1)
pre_output.setAmp(0, 1, 1)
spectrum = Spectrum(downmix)

### SERVER GRIS ###
# sender = OscDataSend("iffffff", 18032, '/spat/serv')

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
### SERVER GRIS ###

### MONOME GRID ###
# t = threading.Thread(group=None, target=s.gui, args=[locals()])
# t.start()
# gridHandler = GridStudies(stepOn)
### MONOME GRID ###

s.gui(locals())
