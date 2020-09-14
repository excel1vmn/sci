#!/usr/bin/env python3
# encoding: utf-8
from pyo import *

class FXBox(PyoObject):
    """
    FXBox.

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
    def __init__(self, input, toggles, cs, outs=2, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._toggles = toggles
        self._check = Change(self._toggles)
        self._toggleChange = TrigFunc(self._check, self.toggleFX)
        self._cs = cs
        self._outs = outs
        self._fx = []
        self._in_fader = InputFader(input)
        self._voices = Mixer(outs=8)
        for i in range(8):
            self._voices.addInput(i, self._input[i])
            self._voices.setAmp(i,0,0)
        self._downmix = Mix(self._voices)
        in_fader,cs,outs,mul,add,lmax = convertArgsToLists(self._in_fader,cs,outs,mul,add)
        self._fx.append(Disto(self._downmix, drive=.9, slope=.8, mul=Pow(cs[0],3)))
        self._fx.append(FreqShift(self._downmix, shift=10, mul=Pow(cs[1],3)))
        self._fx.append(WGVerb(self._downmix, feedback=.85, bal=1, mul=Pow(cs[2],3)))
        # self._fx.append(MoogLP(self._downmix, Pow(6000*(cs[3]+.1),3), res=0, mul=Pow(cs[3],3)))

        self._mod = Sig(self._fx)
        self._comp = Compress(self._mod, thresh=-12, ratio=4, risetime=.01, falltime=.2, knee=0.5)
        self._pan = Pan(self._comp, outs=outs[0], pan=.5, spread=.4)
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

    def toggleFX(self):
        if Sig(self._toggles[0]).get() == 1:
            self._voices.setAmp(0,0,1)
            print('Effects on track : 1')
        else:
            self._voices.setAmp(0,0,0)

        if Sig(self._toggles[1]).get() == 1:
            self._voices.setAmp(1,0,1)
            print('Effects on track : 2')
        else:
            self._voices.setAmp(1,0,0)

        if Sig(self._toggles[2]).get() == 1:
            self._voices.setAmp(2,0,1)
            print('Effects on track : 3')
        else:
            self._voices.setAmp(2,0,0)

        if Sig(self._toggles[3]).get() == 1:
            self._voices.setAmp(3,0,1)
            print('Effects on track : 4')
        else:
            self._voices.setAmp(3,0,0)

        if Sig(self._toggles[4]).get() == 1:
            self._voices.setAmp(4,0,1)
            print('Effects on track : 5')
        else:
            self._voices.setAmp(4,0,0)

        if Sig(self._toggles[5]).get() == 1:
            self._voices.setAmp(5,0,1)
            print('Effects on track : 6')
        else:
            self._voices.setAmp(5,0,0)

        if Sig(self._toggles[6]).get() == 1:
            self._voices.setAmp(6,0,1)
            print('Effects on track : 7')
        else:
            self._voices.setAmp(6,0,0)

        if Sig(self._toggles[7]).get() == 1:
            self._voices.setAmp(7,0,1)
            print('Effects on track : 8')
        else:
            self._voices.setAmp(7,0,0)

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


# Run the script to test the PyoObjectTemplate object.
if __name__ == "__main__":
    s = Server().boot()
    src = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=.3)
    lfo = Sine(.25, phase=[0,.5], mul=.5, add=.5)
    pot = PyoObjectTemplate(src, freq=[800,1000], mul=lfo).out()
    s.gui(locals())