class Trial:
    def __init__(self, blockfactor, trialfactor):

        for level in blockfactor:
            self.__setattr__(level.set_factor.name, level.value)

        for level in trialfactor:
            self.__setattr__(level.set_factor.name, level.value)
