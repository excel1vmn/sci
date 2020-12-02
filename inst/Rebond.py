#!/usr/bin/env python3
# encoding: utf-8
from pyo import *

class Rebond(PyoObject):
    """
    Rebond comme geste musicale.

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
    >>> pot = PyoObjectTemplate(src, freq=[800,1000], mul=lfo).out()

    """
    def __init__(self, input, notein, cs, base_interval=.5, outs=2, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._cs = cs
        self._base_interval = base_interval
        self._outs = outs
        self._in_fader = InputFader(input)
        in_fader,cs,base_interval,outs,mul,add,lmax = convertArgsToLists(self._in_fader,cs,base_interval,outs,mul,add)
        self._amp = MidiAdsr(notein['velocity'])
        self._pit = MToF(notein['pitch'])
        self._check = Change(cs)
        self._isON = Sig(cs) > .005
        self._delay_seg = TrigLinseg(self._check+notein['trigon'], [(0,base_interval[0]),(8,base_interval[0] / 200)])
        self._panner = FastSine((self._delay_seg*(cs*20))+1, quality=0, mul=.5, add=.5)
        self._filt = Reson(in_fader, freq=self._pit, q=5+(15*self._amp)).mix()
        self._mod = SmoothDelay(self._filt, delay=self._delay_seg*((self._amp*4)+1), feedback=Clip(cs, min=.2, max=.5), maxdelay=1, mul=Port(self._isON)).mix()
        self._pan = Pan(self._mod, outs=outs[0], pan=self._panner, spread=.2)
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

    def setInterval(self, x):
        """
        Replace the `base_interval` attribute.

        :Args:

            x : float or PyoObject
                New `base_interval` attribute.

        """
        self._base_interval = x

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
        self._map_list = [SLMap(10, 2000, "log", "interval", self._base_interval),
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
    def interval(self):
        """float or PyoObject. Frequency of the modulator."""
        return self._base_interval
    @interval.setter
    def interval(self, x):
        self.setInterval(x)

# Run the script to test the PyoObjectTemplate object.
if __name__ == "__main__":
    s = Server().boot()
    src = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=.3)
    lfo = Sine(.25, phase=[0,.5], mul=.5, add=.5)
    pot = Rebond(src, cs=lfo, mul=lfo).out()
    s.gui(locals())