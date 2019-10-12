import random
from .block import Block
from itertools import product
class Set:
    def __init__(self, blockfactor_list, trialfactors_list):
        self.blocks = []

        for blockfactors in product(* blockfactor_list):
                block = Block(blockfactors, trialfactors_list)
                self.blocks.append(block)

        random.shuffle(self.blocks)




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

def showRandomSet(set):
    TableCounter = 0
    BlockCounter = 0
    for i in range(set.size()):
        print(set.blocks[i])
        BlockCounter += 1
        for j in range(set.blocks[i].size()):
            print(set.blocks[i].trials[j])
            TableCounter += 1

    print(' \n\n')
    print('Total number of block: {}'.format(BlockCounter))
    print('Total number of table: {}'.format(TableCounter))
    print(' \n\n')
