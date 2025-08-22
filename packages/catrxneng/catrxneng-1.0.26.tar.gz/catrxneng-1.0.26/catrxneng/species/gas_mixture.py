import numpy as np
from catrxneng.species import CLASS_MAP
from catrxneng.quantities import *
from catrxneng import utils


class GasMixture:

    def __init__(self, y=None, p=None):
        self.update(y, p)

    def update(self, y=None, p=None):
        self.y = y
        self.p = p
        if y:
            comp_list = list(y.keys)
        if p:
            comp_list = list(p.keys)
            self.P = Pressure(si=np.sum([p.si]))
            self.y = utils.divide(p, self.P)
        active_comp_list = comp_list.copy()
        active_comp_list.remove("inert")
        self.components = {comp_id: CLASS_MAP[comp_id]() for comp_id in comp_list}
        sum_active = np.sum(
            [
                molfrac
                for comp_id, molfrac in zip(comp_list, self.y.si)
                if comp_id.lower() != "inert"
            ]
        )
        y_active = [self.y[comp_id].si for comp_id in active_comp_list]
        self.y_active = Unitless(
            si=utils.divide(y_active, sum_active), keys=active_comp_list
        )
        self.avg_mol_weight = np.sum(
            [
                self.components[comp_id].mol_weight * self.y_active[comp_id].si
                for comp_id in active_comp_list
            ]
        )
