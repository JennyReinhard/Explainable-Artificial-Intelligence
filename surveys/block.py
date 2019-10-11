from itertools import product
from .trial import Trial
import random

class Block:
    def __init__(self, blockfactor, trialfactors_list):
        self.trials = []

        for level in blockfactor:
            self.__setattr__(level.set_factor.slug, level)

        for trialfactor in product(* trialfactors_list):
            trial = Trial(blockfactor, trialfactor)
            self.trials.append(trial)

        random.shuffle(self.trials)

    def __repr__(self):
        return " \n\nBlock with scenario " + self.scenario.value + " and decision support system " + self.dss.value + ". \n ---------------------------------------------------------"

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
