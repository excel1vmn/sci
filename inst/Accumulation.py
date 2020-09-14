#!/usr/bin/env python3
# encoding: utf-8
from pyo import *

class Accumulation(PyoObject):
    """
    Accumulation comme geste musicale.

    Descriptions à écrire...

    :Parent: :py:class:`PyoObject`

    :Args:

        input : PyoObject
            Input signal to process.
        *args : 

    """
    def __init__(self, input, cs, delay=1, outs=2, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._cs = cs
        self._delay = delay
        self._outs = outs
        self._in_fader = InputFader(input)
        in_fader,cs,delay,outs,mul,add,lmax = convertArgsToLists(self._in_fader,cs,delay,outs,mul,add)
        self._onesample = 1.0 / 48000
        self._check = Change(cs[0])
        self._fade = TrigLinseg(self._check, [(.01,1),(.5,.7),(1,0)])
        self._rand = SigTo(RandDur(min=[self._delay,self._delay*1.04,self._delay*1.09,self._delay*1.13],max=[.31,.33,.36,.4], mul=self._fade))
        self._del1 = Delay(in_fader, delay=[delay[0]*1.02,delay[0]*2.1,delay[0]*2.8,delay[0]*4.2], feedback=[.51,.47], mul=cs[0])
        self._del2 = Delay(in_fader, delay=[delay[0]*.98,delay[0]*1.8,delay[0]*3.3,delay[0]*3.9], feedback=[.49,.53], mul=cs[0])
        self._mod = Sig([self._del1,self._del2])
        self._passes = []
        for i in range(4):
            if i%2 == 0:
                self._passes.append(Allpass(self._mod[0], self._rand[0]))
            else:
                self._passes.append(Allpass(self._mod[1], self._rand[1]))
        self._clean = Sig(in_fader, mul=1-cs[0])
        self._passesM = Mix(self._passes)
        self._comp = Compress(Mix([self._clean,self._passesM]), thresh=-12, ratio=4, knee=.5)
        self._pan = Pan(self._comp, outs=outs[0], pan=.5, spread=.3)
        self._out = Sig(self._pan, mul=mul, add=add)
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

    def setDelay(self, x):
        """
        Replace the `delay` attribute.

        :Args:

            x : float or PyoObject
                New `delay` attribute.

        """
        self._delay = x

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
        self._map_list = [SLMap(10, 2000, "log", "delay", self._delay),
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
    def delay(self):
        """float or PyoObject. Delay time in seconds."""
        return self._delay
    @delay.setter
    def delay(self, x):
        self.setDelay(x)
