from .species import Species


class Inert(Species):
    def __init__(self, T=None):
        self.mol_weight = None
