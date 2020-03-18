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
    def __init__(self, input, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._in_fader = InputFader(input)
        in_fader,mul,add,lmax = convertArgsToLists(self._in_fader,mul,add)
        self._mod = Sig(self._input)
        self._lfo = FastSine(freq=[.3,.4,.5,.6], mul=.5, add=add)
        self._mb = MultiBand(self._input, num=4, mul=self._lfo)
        self._base_objs = self._mod.getBaseObjects()

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
        self._map_list = [SLMap(10, 2000, "log"),
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
