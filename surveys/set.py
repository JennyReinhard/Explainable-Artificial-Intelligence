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
        BlockCounter += 1
        for j in range(set.blocks[i].size()):
            print(set.blocks[i].trials[j])
            TableCounter += 1

    print(' \n\n')
    print('Total number of block: {}'.format(BlockCounter))
    print('Total number of table: {}'.format(TableCounter))
    print(' \n\n')
