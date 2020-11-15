import random
from .block import Block
from itertools import product
class Set:
    def __init__(self, blockfactor_list, trialfactors_list, ntrials, ntraining):
        self.blocks = []

        # Create blocks based on the blockfactorlist by taking product
        for blockfactors in product(* blockfactor_list):
                block = Block(blockfactors, trialfactors_list, ntrials)
                self.blocks.append(block)

        # @TODO: Modularize for dynamic settings
        random.shuffle(block.trials)

        random.shuffle(self.blocks)

        #Sets the blockcounter
        for index, block in enumerate(self.blocks):
            block.blockcounter = len(self.blocks) - index

        # Training properties
        self.ntraining = ntraining

    # Pushes element onto the stack
    def push(self, block):
        self.blocks.append(block)

    # Removes element from the top
    def pop(self):
        return self.blocks.pop()

    # Returns size of stack
    def size(self):
        return len(self.blocks)

    # Prints stack in stack order
    def printSet(self):
        for block in reversed(self.blocks):
            print(block)

    # Checks if stack is empty
    def isEmpty(self):
        return self.blocks == []

    # returns the top of the stack
    def top(self):
        return self.blocks[-1]

# Prints a complete set
def showSet(set):
    TableCounter = 0
    BlockCounter = 0
    for i in range(set.size()):
        print(set.blocks[i])
        print(" | Blockcounter: {}".format(set.blocks[i].blockcounter))
        BlockCounter += 1
        for j in range(set.blocks[i].size()):
            print(set.blocks[i].trials[j])
            TableCounter += 1

    print(' \n\n')
    print('Total number of block: {}'.format(BlockCounter))
    print('Total number of table: {}'.format(TableCounter))
    print(' \n\n')
