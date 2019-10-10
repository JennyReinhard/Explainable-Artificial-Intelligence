class FactorSet:
    def __init__(self, name, blockfactor):
        self.name = name
        self.factors = []
        self.blockfactor = blockfactor

    def addFactor(self, Factor):
        self.factors.append(Factor)

    @property
    def levels(self):
        return len(self.factors)

    def __repr__(self):
        return 'Factor "' + str(self.name) + '" with ' + str(self.levels) + ' levels.'

    def isBlockFactor(self):
        return self.blockfactor

class Factor:
    def __init__(self, name, value):
        self.name = name
        self.value = value
