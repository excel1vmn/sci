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
    def __init__(self, input, cs, base_interval=.5, outs=2, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        self._input = input
        self._cs = cs
        self._base_interval = base_interval
        self._outs = outs
        self._in_fader = InputFader(input)
        in_fader,cs,base_interval,outs,mul,add,lmax = convertArgsToLists(self._in_fader,cs,base_interval,outs,mul,add)
        self._check = Change(cs)
        self._delay_seg = TrigLinseg(self._check, [(0,base_interval[0]),(3,base_interval[0] / 500)])
        # Certain random dans le line segment
        # Balayer un filtre en même temps 
        self._panner = FastSine(freq=.8*((self._delay_seg*20)+1), mul=.4, add=.5)
        self._count = Counter(self._check, min=5, max=10, dir=2)
        # modulation du feedback
        self._mod = SmoothDelay(in_fader, delay=self._delay_seg, feedback=self._count*.1, maxdelay=1, mul=cs)
        self._filt = Reson(self._mod, freq=self._delay_seg*1000, q=1)
        self._clean = Sig(in_fader, mul=1-cs[0])
        self._comp = Compress(Mix([self._filt,self._clean]), thresh=-12, ratio=4, knee=0.5)
        self._pan = Pan(self._comp, outs=outs[0], pan=self._panner*(self._delay_seg*10), spread=.3)
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
        Replace the `freq` attribute.

        :Args:

            x : float or PyoObject
                New `freq` attribute.

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