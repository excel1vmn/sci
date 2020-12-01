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
    def __init__(self, input, notein, cs, freq=100, outs=2, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._cs = cs
        self._freq = freq
        self._outs = outs
        self._in_fader = InputFader(input)
        in_fader,cs,freq,outs,mul,add,lmax = convertArgsToLists(self._in_fader,cs,freq,outs,mul,add)
        self._isON = Sig(cs) > .005
        self._check = Change(cs)
        self._centro = Centroid(in_fader, size=1024)
        self._port = Port(self._centro)
        self._trigran = TrigRand(Mix([self._check,notein['trigon']]), min=.25, max=4)
        self._trigenv = TrigLinseg(Mix([self._check,notein['trigon']]), [(0,0),(.05,1.5),(1,.9),(2,.5),(5,0)])

        # Waveshaped distortion
        self._noise = Allpass2(Noise(in_fader), freq=(self._port*self._trigenv)+1, bw=100*(100*self._trigenv)).mix()
        self._table = ExpTable([(0,-.25),(4096,0),(8192,0)], exp=30)
        self._high_table = ExpTable([(0,1),(2000,1),(4096,0),(4598,-1),(8192,0)],
                            exp=5, inverse=False)
        self._high_table.reverse()
        self._table.add(self._high_table)
        self._lookShape = Lookup(self._table, in_fader)
        self._dis = Disto(self._lookShape, drive=Clip(self._noise, 0, 1), slope=.8, mul=self._trigenv).mix()

        # Multiband chain
        self._lfoFreq = []
        for i in range(len(freq)):
            self._lfoFreq.append((freq[i]*self._trigran)*Scale(cs, outmin=.005, outmax=8.0))
        self._lfo = FastSine(self._lfoFreq, quality=0, mul=.5, add=.5)
        self._mod = MultiBand(self._dis, num=len(freq), mul=Port(self._lfo*self._isON)).mix()

        # Output chain
        self._panner = FastSine(freq=freq*self._trigenv, quality=0, mul=self._trigenv, add=.5)
        self._pan = Pan(self._mod, outs=outs[0], pan=self._panner, spread=.5)
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