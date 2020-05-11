#!/usr/bin/env python3
# encoding: utf-8
from pyo import *

class GestesMus(PyoObject):
    """
    Gestes Musicales

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
        self._in_fader = InputFader(input)
        in_fader,cs,freq,mul,add,lmax = convertArgsToLists(self._in_fader,cs,freq,mul,add)
        self._rdur = RandDur(min=[.1,.3,.5,.7], max=[3,7,11,15])
        self._lfo = FastSine(freq=[cs[0]*self._rdur[0],cs[0]*self._rdur[1],cs[0]*self._rdur[2],cs[0]*self._rdur[3]], mul=.9*Pow(cs[0],3), add=.1)
        self._mod = MultiBand(in_fader, num=4, mul=self._lfo)
        self._dis = Disto(self._mod, drive=(.98*Pow(cs[0],3)), slope=.7, mul=cs[0]*.2)
        self._pan = Pan(self._mod, outs=outs, pan=in_fader*cs[3], spread=.3, mul=in_fader*cs[3])
        self._comp = Compress(Mix([self._mod,self._dis,self._pan], 2), thresh=-20, ratio=4, knee=0.5)
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
