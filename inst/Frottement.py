#!/usr/bin/env python3
# encoding: utf-8
from pyo import *

class Frottement(PyoObject):
    """
    Frottement comme gestes musicales

    Descriptions à écrire...

    :Parent: :py:class:`PyoObject`

    :Args:

        input : PyoObject
            Input signal to process.
        *args : 

    """
    def __init__(self, input, cs, freq=100, outs=2, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._cs = cs
        self._freq = freq
        self._outs = outs
        self._in_fader = InputFader(input)
        in_fader,cs,freq,outs,mul,add,lmax = convertArgsToLists(self._in_fader,cs,freq,outs,mul,add)
        self._numINs = len(in_fader)
        self._rdur = RandDur(min=freq, max=freq*100)
        if type(freq) is list:
            self._lfoFreq = []
            for i in range(len(freq)):
                self._lfoFreq.append(cs[0]*self._rdur[i]*i)
            self._lfo = FastSine(freq=self._lfoFreq, mul=1*Pow(cs[0],3), add=1)
            self._mod = MultiBand(in_fader, num=len(freq), mul=self._lfo)
            print('is list')
        else:
            self._lfo = FastSine(freq=cs[0]*self._rdur[0], mul=.9*Pow(cs[0],3), add=.1)
            self._mod = MultiBand(in_fader, num=4, mul=self._lfo)
            print('is not list')
        self._dis = Disto(self._mod, drive=(.98*Pow(cs[0],3)), slope=self._lfo, mul=cs[0]*.7)
        self._pan = Pan(self._mod, outs=outs[0], pan=in_fader*cs[1], spread=.3, mul=in_fader*cs[1])
        self._comp = Compress(Mix([self._mod,self._dis,self._pan]), thresh=-20, ratio=4, knee=0.5)
        self._out = Sig(self._comp, mul=mul, add=add)
        self._base_objs = self._out.getBaseObjects()

    def setInput(self, x, fadetime=0.05):
        """
        Replace the `input` attribute.

        :Args:

            x : PyoObject
                New signal to process.
            fadetime : float, optional
                Crossfade time between old and new input. Defaults to 0.05.

        """
        self._input = x
        self._in_fader.setInput(x, fadetime)

    def setFreq(self, x):
        """
        Replace the `freq` attribute.

        :Args:

            x : float or PyoObject
                New `freq` attribute.

        """
        self._freq = x
        self._mod.freq = x

    def play(self, dur=0, delay=0):
        self._mod.play(dur, delay)
        return PyoObject.play(self, dur, delay)

    def stop(self, wait=0):
        self._mod.stop(wait)
        return PyoObject.stop(self, wait)

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._mod.play(dur, delay)
        return PyoObject.out(self, chnl, inc, dur, delay)

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(10, 2000, "log", "freq", self._freq),
                          SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property # getter
    def input(self):
        """PyoObject. Input signal to process."""
        return self._input
    @input.setter # setter
    def input(self, x):
        self.setInput(x)

    @property
    def freq(self):
        """float or PyoObject. Frequency of the modulator."""
        return self._freq
    @freq.setter
    def freq(self, x):
        self.setFreq(x)

if __name__ == "__main__":
    s = Server()
    s.setOutputDevice(6)
    s.setMidiInputDevice(99)
    s.boot().start()
    src = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=.3)
    lfo = Sine(.25, phase=[0,.5], mul=.5, add=.5)
    cs = Midictl(ctlnumber=[53,56], init=0, channel=6)
    pot = Frottement(src, freq=[.1,.3,.5,9], cs=[cs[0],cs[1]], mul=lfo).out()
    s.gui(locals())