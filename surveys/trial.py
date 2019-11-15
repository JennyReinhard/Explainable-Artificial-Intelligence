from .fraction import reliatbilityFraction
import random
import numpy as np
from itertools import cycle

#Creates a list of package prices
packages = np.arange(2000, 5000, 200).tolist()

#Alternator for manual and automatic decisions
alternator = cycle(range(2))

class Trial:
    def __init__(self, blockfactor, trialfactor):

        # Set block attributes
        for level in blockfactor:
            self.__setattr__(level.set_factor.slug, level)

        # Set trial attribute
        for level in trialfactor:
            self.__setattr__(level.set_factor.slug, level)

        # Get reliability fraction and set vehicle experience
        numerator, denominator = reliatbilityFraction(int(self.reliability.value)/100)
        self.attempts = denominator
        self.errors = denominator - numerator

        # Chooses a randomly selected package price
        self.package = random.choice(packages)

        # Set base success to true
        self.success = True

        # Calculate profit based on the expected value (reliability)
        if next(alternator) == 0:
            if self.reliability.value < 90:
                self.manual = int((self.package * (int(self.reliability.value)/100)) * 1.1)
                self.suggestion = 'manual'
                self.best_choice = 'manual'
            elif self.reliability.value == 100:
                self.manual = int((self.package * (int(self.reliability.value)/100)) * 0.9)
                self.suggestion = 'automate'
                self.best_choice = 'automate'
            else:
                self.suggestion = 'None'
                self.best_choice = 'None'
        else:
            self.manual = int((self.package * (int(self.reliability.value)/100)) * 0.9)
            self.suggestion = 'automate'
            self.best_choice = 'automate'

    def __repr__(self):
        return "Trial -> Reliability: " + str(self.reliability.value) + "| Risk: " + str(self.risk.value) + "| Scenario: " + str(self.scenario.value) + "| Decision support system: " + str(self.dss.value)
