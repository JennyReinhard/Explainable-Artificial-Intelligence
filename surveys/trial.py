from .fraction import reliatbilityFraction

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

    def __repr__(self):
        return "Trial -> Reliability: " + str(self.reliability.value) + "| Risk: " + str(self.risk.value) + "| Scenario: " + str(self.scenario.value) + "| Decision support system: " + str(self.dss.value)
