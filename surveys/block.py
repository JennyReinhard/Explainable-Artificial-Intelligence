from itertools import product
from .trial import Trial

class Block:
    def __init__(self, blockfactor, trialfactors_list):
        self.trials = []

        for level in blockfactor:
            self.__setattr__(level.set_factor.name, level.value)

        for trialfactor in product(* trialfactors_list):
            trial = Trial(blockfactor, trialfactor)
            self.trials.append(trial)

    def push(self, trial):
        self.block.append(trial)

    def pop(self):
        return self.trials.pop()

    def size(self):
        return len(self.trials)

    def printSet(self):
        for trial in reversed(self.trials):
            print(table)

    def isEmpty(self):
        return self.trials == []

    def top(self):
        return self.trials[-1]
