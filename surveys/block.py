from itertools import product
from .trial import Trial
import random

class Block:
    def __init__(self, blockfactor, trialfactors_list, ntrials):
        self.trials = []
        #Game stats
        self.blockcounter = 0
        self.max = 0

        # Gets blockfactors and sets attributes
        for level in blockfactor:
            self.__setattr__(level.set_factor.slug, level)

        # Creates trials by taking the product of the trialfactors in trialfactors_list
        for trialfactor in product(* trialfactors_list):
            for i in range(ntrials):
                trial = Trial(blockfactor, trialfactor)
                # Appends each trial to the trials stack
                self.trials.append(trial)

        # Shuffles trials in a block
        random.shuffle(self.trials)

    def __repr__(self):
        return "Block with attributes: "+str(self.__dict__)

    # Pushes element onto the stack
    def push(self, trial):
        self.block.append(trial)

    # Removes element from the top
    def pop(self):
        return self.trials.pop()

    # Returns size of stack
    def size(self):
        return len(self.trials)

    # Prints stack in stack order
    def printSet(self):
        for trial in reversed(self.trials):
            print(table)

    # Checks if stack is empty
    def isEmpty(self):
        return self.trials == []

    # returns the top of the stack
    def top(self):
        return self.trials[-1]
