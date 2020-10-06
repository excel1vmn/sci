#!/usr/bin/env python3
# encoding: utf-8
from pyo import *

class Flexion(PyoObject):
    """
    Pyo Object Template.

    Description of your pyo object class and it's diverse use cases.

    :Parent: :py:class:`PyoObject`

    :Args: List of arguments and their description

        input : PyoObject
            Input signal to process.
        freq : float or PyoObject, optional
            Frequency, in cycles per second, of the modulator.
            Defaults to 100.

    >>> s = Server().boot()
    >>> s.start()
    >>> src = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=.3)
    >>> lfo = Sine(.25, phase=[0,.5], mul=.5, add=.5)
    >>> pot = Flexion(src, freq=[800,1000], mul=lfo).out()

    """
    def __init__(self, input, notein, cs, freq=500, outs=2, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._notein = notein
        self._cs = cs
        self._freq = freq
        self._in_fader = InputFader(input)
        in_fader,notein,cs,freq,mul,add,lmax = convertArgsToLists(self._in_fader,notein,cs,freq,mul,add)
        self._amp = MidiAdsr(notein['velocity'], attack=.01, decay=.1, sustain=.7, release=.1)
        self._env = [(0,0), (.1,.5), (.4,.4), (.8,.3), (1.5,1), (2,0)]
        self._midEnv1 = MidiLinseg(notein['velocity'], self._env, hold=4)

        self._check = Change(cs)
        self._trigenv = TrigLinseg(self._check, [(0,0),(.05,1),(1,.7),(2,.5),(5,0)])
        
        self._modulator = Sine(freq=10*self._midEnv1+1, mul=in_fader)
        self._panMod = Sine(freq=5*self._midEnv1+1, mul=.5, add=.5)
        self._pitchMod = Sine(freq=8*self._midEnv1+2, mul=self._midEnv1, add=-5)
        self._harmonizer = Harmonizer(self._modulator, transpo=self._midEnv1*-1, feedback=self._trigenv, winsize=0.05, mul=cs)
        self._comp = Compress(self._harmonizer, thresh=-12, ratio=4, knee=.5)
        self._mod = Pan(self._comp, outs=outs, pan=self._panMod, spread=.3)
        self._out = Sig(self._mod, mul=mul, add=add)
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

# Run the script to test the Flexion object.
if __name__ == "__main__":
    s = Server().boot()
    src = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=.3)
    lfo = Sine(.25, phase=[0,.5], mul=.5, add=.5)
    pot = Flexion(src, freq=[800,1000], mul=lfo).out()
    s.gui(locals())