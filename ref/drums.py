class Drums:
    def __init__(self, paths, transpo=1, hfdamp=8000, lfofreq=0.2, channel=0, mul=1):
        self.paths = paths
        self.transpo = Sig(transpo)

        self.note = Notein(poly=16, scale=0, first=0, last=127, channel=channel)
        self.pit = MToF(self.note['pitch']) * self.transpo
        self.amp = MidiAdsr(self.note['velocity'], attack=0.001, decay=.1, sustain=1, release=0.1)

        self.tables = []
        self.selectors = []
        self.players = []

        for i in range(len(self.paths)):
            self.tables.append(SndTable(self.paths[i], initchnls=2))
            self.selectors.append(Select(self.note["pitch"], value=36+i))
            self.players.append(TrigEnv(self.selectors[i], self.tables[i], dur=self.tables[i].getDur() / transpo, mul=self.amp).mix(2))

        # Stereo mix.
        self.mix = Mix(self.players, voices=16)
        self.damp = ButLP(self.mix, freq=hfdamp).mix(2)
        self.hp = ButHP(self.damp, 50).mix(2)
        self.p = Pan(self.hp, outs=2, pan=[.2,.8], spread=.2, mul=mul)

    def out(self):
        self.p.out()
        return self

    def sig(self):
        return self.p
