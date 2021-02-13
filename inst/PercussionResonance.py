#!/usr/bin/env python3
# encoding: utf-8
from pyo import *

class PercussionResonance(PyoObject):
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
    >>> pot = PercussionResonance(src, freq=[800,1000], mul=lfo).out()

    """
    def __init__(self, input, notein, cs, freq=500, outs=2, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._cs = cs
        self._freq = freq
        self._in_fader = InputFader(input)
        in_fader,cs,freq,mul,add,lmax = convertArgsToLists(self._in_fader,cs,freq,mul,add)
        fol = Follower(in_fader) > .0001
        csCheck = Sig(cs) > .005
        self._isON = fol+csCheck == 2
        self._amp = MidiAdsr(notein['velocity'])
        self._logt = LogTable([(0,1), (128,50), (512,2), (8192,1)])
        self._trigt = TrigEnv(notein['trigon'], self._logt)
        self._bass = Sine((50*Clip(cs, .1, 1.2))*self._trigt, mul=self._amp)
        self._wubb = Sine((50*Clip(cs, .1, 1.2))*self._trigt, mul=self._amp*Clip(in_fader,0,1))
        
        # Waveshaped distortion
        self._table = ExpTable([(0,-.25),(4096,.5),(8192,0)], exp=30)
        self._high_table = ExpTable([(0,1),(2000,1),(4096,.3),(4598,-1),(8192,0)],
                            exp=5, inverse=False)
        self._high_table.reverse()
        self._table.add(self._high_table)
        self._table.view()
        self._lookShape = Lookup(self._table, Mix([self._bass,self._wubb]))
        self._dist = Disto(self._lookShape, Clip(cs,.5,.75), Clip(in_fader,.3,.5))
        self._eq = EQ(self._dist, freq=80, q=10, boost=30, type=0)

        self._inputFollow = Follower(self._trigt)
        self._talk = self._inputFollow > .005
        self._followAmp = Port(self._talk)
        self._ampscl = Scale(self._followAmp, outmin=1, outmax=.1)

        lfo = Sine(freq=[.2, .25], mul=1000*Follower(in_fader), add=1500)
        self._reson = Resonx(in_fader, freq=lfo, q=5+self._amp*10, mul=5*self._ampscl)
        self._comp = Compress(Mix([self._reson,self._eq]), thresh=-10)
        self._mod = Sig(self._comp, mul=Port(self._isON))
        self._pan = Pan(self._mod, outs=outs)
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

# Run the script to test the PercussionResonance object.
if __name__ == "__main__":
    s = Server().boot()
    src = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=.3)
    lfo = Sine(.25, phase=[0,.5], mul=.5, add=.5)
    pot = PercussionResonance(src, freq=[800,1000], mul=lfo).out()
    s.gui(locals())