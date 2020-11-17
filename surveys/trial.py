
import random



class Trial:
    def __init__(self, blockfactor, trialfactor):

        # Set block attributes
        for level in blockfactor:
            self.__setattr__(level.set_factor.slug, level)

        # Set trial attribute
        for level in trialfactor:
            self.__setattr__(level.set_factor.slug, level)

    def __repr__(self):
        return "Trial"
