from .fraction import reliatbilityFraction

import random
from itertools import cycle

packages = []
package = 2000

while package < 5000:
    packages.append(package)
    package = package + 200

alternator = cycle(range(2))

class Trial:


    def __init__(self, blockfactor, trialfactor):

        # Set block attributes
        for level in blockfactor:
            self.__setattr__(level.set_factor.slug, level)

        # Set trial attribute
        for level in trialfactor:
            self.__setattr__(level.set_factor.slug, level)

        # Get reliability fraction
        numerator, denominator = reliatbilityFraction(int(self.reliability.value)/100)

        self.attempts = denominator
        self.errors = denominator - numerator
        self.package = random.choice(packages)
        self.success = True

        if next(alternator) == 0:
            self.manual = int((self.package * (int(self.reliability.value)/100)) * 1.1)
            self.suggestion = 'manual'
            self.best_choice = 'manual'

        else:
            self.manual = int((self.package * (int(self.reliability.value)/100)) * 0.9)
            self.suggestion = 'automate'
            self.best_choice = 'automate'

        


    def __repr__(self):
        return "Trial -> Reliability: " + str(self.reliability.value) + "| Risk: " + str(self.risk.value) + "| Scenario: " + str(self.scenario.value) + "| Decision support system: " + str(self.dss.value)
