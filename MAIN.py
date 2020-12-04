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
SOUND_CARD = 'INT'

# SERVER SETUP
if NUMOUTS == 2:
    if SOUND_CARD == 'EXT':
        s = Server(sr=44100, buffersize=1024, nchnls=NUMOUTS, duplex=0, audio='pa')
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

# print(snds)
# print(drum_kit)

###############################################
############### MIDI PARAMETERS ###############
###############################################
# def ctl_scan(ctlnum, midichnl):
    # print(ctlnum, midichnl)
    # print(HP.boost.get())
# ctlscan = CtlScan2(ctl_scan, False)

def event(status, data1, data2):
    # print(status, data1, data2)
    if data1 == 105 and data2 == 127:
        scanMidi()
raw = RawMidi(event)

# check = Change(SIGTRIG)
# p=Print(SIGTRIG, 1)

#--- LAUNCH CONTROL XL ---#
MULPOW = Port(Pow(Midictl(ctlnumber=[77,78,79,80,81,82,83,84], init=0, channel=6), 3))
CS = Midictl(ctlnumber=[13,14,15,16,17,18,19,20,
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

#--- NAKED BOARDS ---#
# MULPOW = Pow(Midictl(ctlnumber=[0,1,2,3,4,5,6,7], init=0, channel=1), 5)
# CS = Midictl(ctlnumber=[ 8, 9,10,11,12,13,14,15,
#                         16,17,18,19,20,21,22,23,
#                         24,25,26,27,28,29,30,31], 
#                   init=[ 0, 0, 0, 0, 0, 0, 0 ,0,
#                          0, 0, 0, 0, 0, 0, 0 ,0,
#                          0, 0, 0, 0, 0, 0, 0, 0], channel=1)
#--- NAKED BOARDS ---#

transpo = Bendin(brange=2, scale=1, channel=1)
hfdamp = Midictl(ctlnumber=49, minscale=20, maxscale=15000, init=15000, channel=3)
lfdamp = Midictl(ctlnumber=48, minscale=20, maxscale=18000, init=20, channel=3)
# Frequency of the LFO applied to the speed of the moving notches.
# lfofreq = Midictl(ctlnumber=13, minscale=0.1, maxscale=20, init=0.2, channel=6)

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
# n3 = Notein(poly=10, scale=0, first=0, last=127, channel=3)
# n4 = Notein(poly=10, scale=0, first=0, last=127, channel=4)
n10 = Notein(poly=10, scale=0, first=0, last=127, channel=10)
### Sert à manipuler les gestes musicaux / techniques d'écriture ### 
n0 = Notein(poly=4, scale=0, first=0, last=127, channel=0)
###############################################
############### MIDI PARAMETERS ###############
###############################################

### EXTERNAL INPUT ###
# input1 = Input(chnl=0, mul=.7)
# input2 = Input(chnl=1, mul=.7)
### EXTERNAL INPUT ###

pre_output = Mixer(outs=NUMOUTS, chnls=1)

###############################################
################# INSTRUMENTS #################
###############################################
dn = Noise(1e-24) # low-level noise for denormals

drums = Drums(n10, drum_kit, toggles_row1, dn, transpo=transpo)

a1 = Synth(n2, trigs[0], toggles1, [CS[0],CS[8]], dn, transpo, hfdamp=hfdamp, audioIN=Mix(pre_output, NUMOUTS), mul=MULPOW[0])
a2 = FreakSynth(n2, trigs[1], toggles2, [CS[1],CS[9]], dn, transpo, hfdamp=hfdamp, audioIN=Mix(pre_output, NUMOUTS), mul=MULPOW[1])
a3 = Simpler(n2, snds, trigs[2], toggles3, [CS[2],CS[10]], dn, transpo, hfdamp=hfdamp, autoswitch=False, withloop=False, audioIN=Mix(pre_output, NUMOUTS), mul=MULPOW[2])
a4 = WaveShape(n2, snds[10], trigs[3], toggles4, [CS[3],CS[11]], dn, transpo, hfdamp=hfdamp, audioIN=Mix(pre_output, NUMOUTS), mul=MULPOW[3])

### ADD : 1 autre bouton de changement de style de jeu!!
r1 = ReSampler(3, Mix(pre_output, NUMOUTS), trigs[4], toggles5, [CS[4],CS[12]], dn, transpo, hfdamp=hfdamp, mul=MULPOW[4])
r2 = ReSampler(3, Mix(pre_output, NUMOUTS), trigs[5], toggles6, [CS[5],CS[13]], dn, transpo, hfdamp=hfdamp, mul=MULPOW[5])
r3 = ReSampler(3, Mix(pre_output, NUMOUTS), trigs[6], toggles7, [CS[6],CS[14]], dn, transpo, hfdamp=hfdamp, mul=MULPOW[6])
r4 = ReSampler(3, Mix(pre_output, NUMOUTS), trigs[7], toggles8, [CS[7],CS[15]], dn, transpo, hfdamp=hfdamp, mul=MULPOW[7])

prefx = Sig([a1.sig(),a2.sig(),a3.sig(),a4.sig(),r1.sig(),r2.sig(),r3.sig(),r4.sig()], mul=toggles_row2)
###############################################
################# INSTRUMENTS #################
###############################################

###############################################
############ TECHNIQUE D'ÉCRITURE #############
###############################################
fr = Frottement(Mix(prefx+dn), n0, CS[16], freq=[3,1.15,.5,.7,2.5,6,.04,15], outs=NUMOUTS)
ac = Accumulation(Mix(prefx+dn), n0, CS[17], delay=.025, outs=NUMOUTS)
re = Rebond(Mix(prefx+dn), n0, CS[18], base_interval=.21, outs=NUMOUTS)
oc = Oscillation(Mix(prefx+dn), n0, CS[19], freq=20, outs=NUMOUTS)
fl = Flux(Mix(prefx+dn), n0, CS[20], freq=50, outs=NUMOUTS)
ba = Balancement(Mix(prefx+dn), n0, CS[21], freq=50, outs=NUMOUTS)
fe = Flexion(Mix(prefx+dn), n0, CS[22], freq=50, outs=NUMOUTS)
pr = PercussionResonance(Mix(prefx+dn), n0, CS[23], freq=MToF(n0['pitch']), outs=NUMOUTS)
###############################################
############ TECHNIQUE D'ÉCRITURE #############
###############################################

# isUsedCheck = Select(MULPOW, .05)
# trigInsts = TrigFunc(isUsedCheck, playInst)

### SIDE CHAIN ###
# inputFollow = Follower(Mix([fr,ac,re,oc,fl,ba,fe,pr], NUMOUTS, mul=toggles_row2))
# talk = inputFollow > .1
# followAmp = Port(talk, risetime=.005, falltime=.001)
# ampscl = Scale([followAmp,followAmp], outmin=1, outmax=.1)
### SIDE CHAIN ###

###############################################
################ SIGNAL PATH ##################
###############################################
clean_sig = Compress(Mix([a1.sig(),a2.sig(),a3.sig(),a4.sig(),r1.sig(),r2.sig(),r3.sig(),r4.sig(),drums.sig()], voices=NUMOUTS), thresh=-12, ratio=4, risetime=.01, falltime=.2, knee=.5)

### les techniques d'écritures influence-t-elle le jeu
## faire une compairson A/B avec technique / sans technique
HP = EQ(Mix([fr,ac,re,oc,fl,ba,fe,pr,clean_sig],NUMOUTS), freq=lfdamp, q=.5, boost=-30, type=1)
LP = EQ(Mix(HP,NUMOUTS), freq=hfdamp, q=.2, boost=-40, type=2)
HP.ctrl()
LP.ctrl()
COMP = Compress(LP, thresh=-10, ratio=4, knee=.5)
downmix = Mix(COMP, voices=NUMOUTS, mul=.3).out()
pre_output.addInput(0, downmix)
pre_output.setAmp(0, 0, 1)
pre_output.setAmp(0, 1, 1)
# spectrum = Spectrum(downmix)
###############################################
################ SIGNAL PATH ##################
###############################################

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

### RECORDING SCRIPT ###
path = os.path.join(os.path.expanduser("~"), "Desktop", "synth.wav")
s.recordOptions(dur=-1, filename=path, fileformat=0, sampletype=1)
s.recstart()
### RECORDING SCRIPT ###

s.gui(locals())
