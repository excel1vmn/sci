class Drums:
    def __init__(self, paths, transpo=1, hfdamp=5000, channel=0, mul=1):
        self.paths = paths
        self.transpo = Sig(transpo)
        self.note = Notein(poly=1, scale=0, first=0, last=127, channel=channel)
        self.pit = MToF(self.note['pitch']) * self.transpo

        self.t = []
        self.amps = []
        self.selectors = []
        self.players = []

        # self.amps.append(MidiAdsr(self.note['velocity'], attack=.001, decay=.1, sustain=1, release=.1, mul=0.5))

        for i in range(len(self.paths)):
            self.t.append(SndTable(self.paths[i], initchnls=2))
            self.amps.append(MidiAdsr(self.note['velocity'], attack=.001, decay=.1, sustain=1, release=.1, mul=0.5))
            self.selectors.append(Select(self.note["pitch"], value=36+i))
            self.players.append(TrigEnv(self.selectors[i], self.t[i], dur=self.t[i].getDur() / self.transpo, mul=self.amps[i]).mix(2))

        # Stereo mix.
        self.mix = Mix(self.players, voices=2)
        self.damp = ButLP(self.mix, freq=hfdamp)
        self.hp = ButHP(self.damp, 50, mul=mul)

    def out(self):
        self.hp.out()#peut-être ça
        return self

    def sig(self):
        return self.hp
