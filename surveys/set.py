import random
from .block import Block
from itertools import product
class Set:
    def __init__(self, blockfactor_list, trialfactors_list):
        self.blocks = []

        for blockfactors in product(* blockfactor_list):
                block = Block(blockfactors, trialfactors_list)
                self.blocks.append(block)


        # for blockfactor in blockfactors:
        #     blog = Blog(blockfactor, trialfactors)
        #     self.blocks.append(block)

        random.shuffle(self.blocks)
        print(self.size())

    def __repr__(self):
        return "One complete set"

    def __repr__(self):
        return "Block with block factor" + self.blockfactor

    def push(self, block):
        self.blocks.append(block)

    def pop(self):
        return self.blocks.pop()

    def size(self):
        return len(self.blocks)

    def printSet(self):
        for block in reversed(self.blocks):
            print(block)

    def isEmpty(self):
        return self.blocks == []

    def top(self):
        return self.blocks[-1]
