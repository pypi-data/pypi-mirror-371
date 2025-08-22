from .quantity import Quantity
from catrxneng.utils import *


class WHSV(Quantity):

    def __init__(self, gas_mixture=None, **kwargs):
        super().__init__(**kwargs)
        self.gas_mixture = gas_mixture

    @property
    def molskgcat(self):
        return self.si

    @molskgcat.setter
    def molskgcat(self, value):
        self.si = to_float(value)

    @property
    def smLhgcat(self):
        return self.si * 3600 * 22.4

    @smLhgcat.setter
    def smLhgcat(self, value):
        self.si = to_float(value) / 3600 / 22.4

    @property
    def inv_h(self):
        try:
            return self.si / 1000 * self.gas_mixture.avg_mol_weight * 3600
        except AttributeError:
            raise AttributeError("WHSV has no gas mixture assigned.")

    @inv_h.setter
    def inv_h(self, value):
        try:
            self.si = value * 1000 / self.gas_mixture.avg_mol_weight / 3600
        except TypeError:
            raise AttributeError("WHSV has no gas mixture assigned.")

    @property
    def inv_s(self):
        try:
            return self.si / 1000 * self.gas_mixture.avg_mol_weight
        except TypeError:
            raise AttributeError("WHSV has no gas mixture assigned.")

    @inv_s.setter
    def inv_s(self, value):
        try:
            self.si = value * 1000 / self.gas_mixture.avg_mol_weight
        except TypeError:
            raise AttributeError("WHSV has no gax mixture assigned.")

    def __mul__(self, other):
        from .mass import Mass
        from .molar_flow_rate import MolarFlowRate

        if isinstance(other, Mass):
            si = self.si * other.si
            return MolarFlowRate(si=si)
        return super().__mul__(other)

    def __rmul__(self, other):
        from .mass import Mass
        from .molar_flow_rate import MolarFlowRate

        if isinstance(other, Mass):
            si = self.si * other.si
            return MolarFlowRate(si=si)
        return super().__rmul__(other)
