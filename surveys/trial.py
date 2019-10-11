class Trial:
    def __init__(self, blockfactor, trialfactor):

        for level in blockfactor:
            self.__setattr__(level.set_factor.slug, level)

        for level in trialfactor:
            self.__setattr__(level.set_factor.slug, level)

    def __repr__(self):
        return "Trial -> Reliability: " + str(self.reliability.value) + "| Risk: " + str(self.risk.value) + "| Scenario: " + str(self.scenario.value) + "| Decision support system: " + str(self.dss.value)
