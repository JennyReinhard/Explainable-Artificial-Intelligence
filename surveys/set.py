import random
from .block import Block
from itertools import product
class Set:
    def __init__(self, blockfactor_list, trialfactors_list, ntrials, training_counter):
        self.blocks = []

        for blockfactors in product(* blockfactor_list):
                block = Block(blockfactors, trialfactors_list, ntrials)
                self.blocks.append(block)



        for block in self.blocks:
            flag_low_reliability = 0
            flag_medium_reliability = 0
            for trial in block.trials:
                if trial.reliability.value == 60 and flag_low_reliability < 2 and trial.risk.value != 0:
                    trial.success = False
                    flag_low_reliability = flag_low_reliability +1

                if trial.reliability.value == 80 and flag_medium_reliability < 1 and trial.risk.value != 0:
                    trial.success = False
                    flag_medium_reliability = flag_medium_reliability +1


            random.shuffle(block.trials)

        random.shuffle(self.blocks)

        for index, block in enumerate(self.blocks):
            block.blockcounter = len(self.blocks) - index

        self.training_counter = training_counter
        self.training_balance = 0
        self.training_injuries = 0

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

def showFailTrials(set):
    low_reliability_fails = 0
    medium_reliability_fails = 0
    for i in range(set.size()):
        for j in range(set.blocks[i].size()):
            trial = set.blocks[i].trials[j]
            if trial.reliability.value == 60 and trial.success == False:
                low_reliability_fails = low_reliability_fails + 1

            if trial.reliability.value == 80 and trial.success == False:
                medium_reliability_fails = medium_reliability_fails + 1


    print(' \n\n')
    print('Total number of low reliability fails: {}'.format(low_reliability_fails))
    print('Total number of medium reliability fails: {}'.format(medium_reliability_fails))
    print(' \n\n')
